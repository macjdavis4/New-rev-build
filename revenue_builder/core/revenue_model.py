"""
Main RevenueModel class - the primary interface for revenue forecasting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .config import Config
from ..data.ingestion import DataIngestion
from ..data.validator import DataValidator
from ..data.preprocessor import DataPreprocessor
from ..models.model_factory import ModelFactory
from ..business_models.templates import BusinessModelTemplates
from ..metrics.calculator import MetricsCalculator
from ..scenarios.planner import ScenarioPlanner
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class RevenueModel:
    """
    Main revenue forecasting model class.

    This is the primary interface for building revenue forecasts. It orchestrates
    data ingestion, preprocessing, model training, forecasting, and scenario planning.

    Example:
        ```python
        model = RevenueModel(business_type='saas')
        model.load_data('historical_data.csv')
        model.train(methods=['bottom_up', 'time_series', 'ensemble'])
        forecast = model.predict(periods=36)
        model.export_report('forecast_report.xlsx')
        ```
    """

    def __init__(
        self,
        business_type: Optional[str] = None,
        config: Optional[Union[str, Dict, Config]] = None
    ):
        """
        Initialize RevenueModel.

        Args:
            business_type: Type of business ('saas', 'ecommerce', 'marketplace', etc.)
            config: Configuration (file path, dict, or Config object)
        """
        # Initialize configuration
        if isinstance(config, Config):
            self.config = config
        elif isinstance(config, str):
            self.config = Config(config_path=config)
        elif isinstance(config, dict):
            self.config = Config(config_dict=config)
        else:
            self.config = Config()

        # Set business type
        self.business_type = business_type
        if business_type:
            self.config.set('business_model.type', business_type)

        # Initialize components
        self.data_ingestion = DataIngestion()
        self.data_validator = DataValidator(self.config.to_dict()['data'])
        self.data_preprocessor = DataPreprocessor(self.config.to_dict()['data'])

        # Data storage
        self.raw_data = None
        self.processed_data = None
        self.validation_results = None

        # Models
        self.models = {}
        self.trained_models = {}
        self.best_model = None

        # Results
        self.forecasts = {}
        self.metrics = {}
        self.scenarios = None

        logger.info(f"Initialized RevenueModel (business_type={business_type})")

    def load_data(
        self,
        source: Union[str, pd.DataFrame],
        validate: bool = True,
        preprocess: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load and prepare data for forecasting.

        Args:
            source: Data source (file path or DataFrame)
            validate: Whether to validate data
            preprocess: Whether to preprocess data
            **kwargs: Additional parameters for data loading

        Returns:
            Processed DataFrame
        """
        logger.info("Loading data...")

        # Load data
        self.raw_data = self.data_ingestion.load_data(source, **kwargs)

        logger.info(f"Loaded {len(self.raw_data)} rows, {len(self.raw_data.columns)} columns")

        # Validate data
        if validate:
            logger.info("Validating data...")
            is_valid, self.validation_results = self.data_validator.validate(self.raw_data)

            if not is_valid:
                logger.warning("Data validation found errors:")
                logger.warning(self.data_validator.get_validation_report())
            else:
                logger.info("Data validation passed")

        # Preprocess data
        if preprocess:
            logger.info("Preprocessing data...")
            self.processed_data = self.data_preprocessor.preprocess(self.raw_data)
            logger.info(f"Preprocessing applied: {self.data_preprocessor.get_transformations_log()}")
        else:
            self.processed_data = self.raw_data.copy()

        return self.processed_data

    def train(
        self,
        methods: Optional[List[str]] = None,
        target_column: str = 'revenue',
        auto_select: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train forecasting models.

        Args:
            methods: List of model types to train (e.g., ['prophet', 'xgboost', 'cohort'])
                     If None, auto-selects based on data and business type
            target_column: Target column to forecast
            auto_select: Whether to auto-select models if methods is None
            **kwargs: Additional parameters for model training

        Returns:
            Dictionary of trained models
        """
        if self.processed_data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        logger.info("Training models...")

        # Auto-select models if needed
        if methods is None and auto_select:
            methods = ModelFactory.auto_select_models(
                self.processed_data,
                self.business_type
            )
            logger.info(f"Auto-selected models: {methods}")

        elif methods is None:
            methods = ['prophet']  # Default

        # Expand method categories
        expanded_methods = []
        for method in methods:
            if method in ['bottom_up', 'time_series', 'machine_learning', 'cohort_based']:
                # It's a category
                expanded_methods.extend(ModelFactory.get_models_by_category(method))
            else:
                expanded_methods.append(method)

        # Create and train models
        for method in expanded_methods:
            try:
                logger.info(f"Training {method} model...")
                model = ModelFactory.create_model(method, self.config.to_dict())

                # Train based on model type
                if method in ['prophet', 'arima', 'lstm']:
                    date_col = self.config.get('data.date_column', 'date')
                    model.fit(
                        self.processed_data,
                        date_column=date_col,
                        target_column=target_column,
                        **kwargs
                    )

                elif method in ['xgboost', 'random_forest', 'neural_network']:
                    # ML models need features
                    feature_columns = [col for col in self.processed_data.columns
                                      if col != target_column and
                                      pd.api.types.is_numeric_dtype(self.processed_data[col])]

                    if len(feature_columns) > 0:
                        model.fit(
                            self.processed_data,
                            target_column=target_column,
                            feature_columns=feature_columns,
                            **kwargs
                        )
                    else:
                        logger.warning(f"Skipping {method}: no numeric features found")
                        continue

                elif method in ['unit_economics', 'customer_based', 'sales_funnel']:
                    # Bottom-up models need specific columns
                    # Use template requirements
                    if self.business_type:
                        template = BusinessModelTemplates.get_template(self.business_type)
                        req_cols = template.get('required_columns', [])

                        if all(col in self.processed_data.columns for col in req_cols):
                            model.fit(self.processed_data, **kwargs)
                        else:
                            logger.warning(f"Skipping {method}: missing required columns")
                            continue
                    else:
                        logger.warning(f"Skipping {method}: business_type not specified")
                        continue

                else:
                    # Generic fit
                    model.fit(self.processed_data, target_column=target_column, **kwargs)

                self.trained_models[method] = model
                logger.info(f"{method} model trained successfully")

            except Exception as e:
                logger.error(f"Error training {method} model: {e}")
                continue

        logger.info(f"Training complete. Trained {len(self.trained_models)} models.")

        return self.trained_models

    def predict(
        self,
        periods: int = 12,
        confidence_level: float = 0.95,
        model: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate revenue forecasts.

        Args:
            periods: Number of periods to forecast
            confidence_level: Confidence level for intervals
            model: Specific model to use (if None, uses best or ensemble)
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.trained_models:
            raise ValueError("No trained models. Call train() first.")

        logger.info(f"Generating forecasts for {periods} periods...")

        # Use specific model or select best
        if model:
            if model not in self.trained_models:
                raise ValueError(f"Model '{model}' not found in trained models")

            selected_model = self.trained_models[model]
            logger.info(f"Using specified model: {model}")

        else:
            # Use ensemble or best model
            if len(self.trained_models) > 1:
                # Create ensemble
                selected_model = ModelFactory.create_ensemble(self.trained_models)
                selected_model.fit(self.processed_data, target_column='revenue')
                logger.info("Using ensemble of all trained models")
            else:
                # Use the only model
                selected_model = list(self.trained_models.values())[0]
                logger.info(f"Using single trained model: {list(self.trained_models.keys())[0]}")

        # Generate forecasts
        try:
            forecast = selected_model.predict(
                periods=periods,
                confidence_level=confidence_level,
                **kwargs
            )

            self.forecasts['base'] = forecast

            logger.info("Forecasts generated successfully")

            return forecast

        except Exception as e:
            logger.error(f"Error generating forecasts: {e}")
            raise

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate business and financial metrics.

        Returns:
            Dictionary of calculated metrics
        """
        if self.processed_data is None:
            raise ValueError("No data loaded")

        logger.info("Calculating metrics...")

        calculator = MetricsCalculator(self.processed_data)
        self.metrics = calculator.calculate_all_metrics(self.business_type)

        logger.info(f"Calculated {len(self.metrics)} metrics")

        return self.metrics

    def scenario_analysis(
        self,
        variables: Optional[Dict[str, List[float]]] = None,
        monte_carlo: bool = True,
        n_simulations: int = 10000,
        **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Perform scenario analysis and Monte Carlo simulation.

        Args:
            variables: Dictionary of variables to vary
            monte_carlo: Whether to run Monte Carlo simulation
            n_simulations: Number of Monte Carlo simulations
            **kwargs: Additional parameters

        Returns:
            Dictionary of scenarios
        """
        if 'base' not in self.forecasts:
            raise ValueError("No base forecast available. Call predict() first.")

        logger.info("Performing scenario analysis...")

        base_forecast = self.forecasts['base']

        self.scenarios = ScenarioPlanner(base_forecast, self.config.to_dict())

        # Create scenarios
        if variables:
            scenarios = self.scenarios.create_scenarios(variables)
        else:
            # Default scenarios
            scenarios = self.scenarios.create_scenarios({
                'revenue': [0.8, 1.0, 1.2],
            })

        # Run Monte Carlo if requested
        if monte_carlo:
            logger.info(f"Running Monte Carlo simulation with {n_simulations} iterations...")

            # Estimate variable distributions
            mc_variables = {}
            for col in base_forecast.columns:
                if pd.api.types.is_numeric_dtype(base_forecast[col]):
                    mean = 1.0
                    std = 0.1  # 10% standard deviation
                    mc_variables[col] = (mean, std)

            mc_results = self.scenarios.monte_carlo_simulation(
                n_simulations,
                mc_variables
            )

            scenarios['monte_carlo'] = mc_results

        logger.info(f"Scenario analysis complete: {len(scenarios)} scenarios")

        return scenarios

    def export_report(
        self,
        path: str,
        include_visuals: bool = True,
        include_commentary: bool = True,
        **kwargs
    ):
        """
        Export comprehensive forecast report.

        Args:
            path: Output file path
            include_visuals: Whether to include visualizations
            include_commentary: Whether to include automated commentary
            **kwargs: Additional parameters
        """
        logger.info(f"Exporting report to {path}...")

        output_path = Path(path)
        format_type = output_path.suffix.lower()

        if format_type == '.xlsx':
            self._export_excel_report(output_path, include_visuals, include_commentary)
        elif format_type == '.csv':
            self._export_csv_report(output_path)
        elif format_type == '.json':
            self._export_json_report(output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        logger.info(f"Report exported successfully to {path}")

    def _export_excel_report(self, path: Path, include_visuals: bool, include_commentary: bool):
        """Export report to Excel format."""
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            # Forecasts
            if self.forecasts:
                for name, forecast in self.forecasts.items():
                    forecast.to_excel(writer, sheet_name=f'Forecast_{name}', index=False)

            # Metrics
            if self.metrics:
                metrics_df = pd.DataFrame([
                    {'Metric': k, 'Value': v}
                    for k, v in self.metrics.items()
                ])
                metrics_df.to_excel(writer, sheet_name='Metrics', index=False)

            # Scenarios
            if self.scenarios and self.scenarios.scenarios:
                for name, scenario in self.scenarios.scenarios.items():
                    scenario.to_excel(writer, sheet_name=f'Scenario_{name}', index=False)

            # Historical data
            if self.processed_data is not None:
                self.processed_data.to_excel(writer, sheet_name='Historical_Data', index=False)

    def _export_csv_report(self, path: Path):
        """Export base forecast to CSV."""
        if 'base' in self.forecasts:
            self.forecasts['base'].to_csv(path, index=False)

    def _export_json_report(self, path: Path):
        """Export report to JSON format."""
        import json

        report = {
            'forecasts': {name: forecast.to_dict(orient='records')
                         for name, forecast in self.forecasts.items()},
            'metrics': self.metrics,
        }

        with open(path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

    def get_model_performance(self) -> pd.DataFrame:
        """
        Get performance metrics for all trained models.

        Returns:
            DataFrame with model performance
        """
        if not self.trained_models:
            return pd.DataFrame()

        performance = []

        for name, model in self.trained_models.items():
            metrics = model.get_metrics()
            metrics['model'] = name
            performance.append(metrics)

        return pd.DataFrame(performance)

    def get_feature_importance(self, model: Optional[str] = None) -> Dict[str, float]:
        """
        Get feature importance from models.

        Args:
            model: Specific model name (if None, returns all)

        Returns:
            Dictionary of feature importance
        """
        if model:
            if model not in self.trained_models:
                raise ValueError(f"Model '{model}' not found")

            return self.trained_models[model].get_feature_importance()

        else:
            # Return combined feature importance
            all_importance = {}

            for name, trained_model in self.trained_models.items():
                importance = trained_model.get_feature_importance()
                for feature, score in importance.items():
                    if feature in all_importance:
                        all_importance[feature] += score
                    else:
                        all_importance[feature] = score

            return all_importance

    def summary(self) -> str:
        """
        Get a summary of the model state.

        Returns:
            Summary string
        """
        lines = [
            "=" * 60,
            "REVENUE FORECASTING MODEL SUMMARY",
            "=" * 60,
            f"Business Type: {self.business_type or 'Not specified'}",
            f"Data Loaded: {'Yes' if self.processed_data is not None else 'No'}",
        ]

        if self.processed_data is not None:
            lines.append(f"Data Shape: {self.processed_data.shape}")

        lines.append(f"Trained Models: {len(self.trained_models)}")

        if self.trained_models:
            lines.append(f"Models: {', '.join(self.trained_models.keys())}")

        lines.append(f"Forecasts Generated: {'Yes' if self.forecasts else 'No'}")
        lines.append(f"Metrics Calculated: {len(self.metrics)}")

        lines.append("=" * 60)

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"RevenueModel(business_type='{self.business_type}', models={len(self.trained_models)})"
