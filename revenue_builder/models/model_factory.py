"""
Model factory for creating and managing forecasting models.
"""

from typing import Dict, Any, Optional, List, Union
import pandas as pd
from ..utils.logger import setup_logger
from .base_model import BaseModel
from .bottom_up import UnitEconomicsModel, CustomerBasedModel, SalesFunnelModel
from .time_series import ARIMAModel, ProphetModel, LSTMModel
from .ml_ensemble import XGBoostModel, RandomForestModel, NeuralNetworkModel, EnsembleModel
from .cohort import CohortModel, SurvivalModel

logger = setup_logger(__name__)


class ModelFactory:
    """
    Factory for creating and managing forecasting models.
    """

    AVAILABLE_MODELS = {
        'unit_economics': UnitEconomicsModel,
        'customer_based': CustomerBasedModel,
        'sales_funnel': SalesFunnelModel,
        'arima': ARIMAModel,
        'prophet': ProphetModel,
        'lstm': LSTMModel,
        'xgboost': XGBoostModel,
        'random_forest': RandomForestModel,
        'neural_network': NeuralNetworkModel,
        'cohort': CohortModel,
        'survival': SurvivalModel,
        'ensemble': EnsembleModel,
    }

    MODEL_CATEGORIES = {
        'bottom_up': ['unit_economics', 'customer_based', 'sales_funnel'],
        'time_series': ['arima', 'prophet', 'lstm'],
        'machine_learning': ['xgboost', 'random_forest', 'neural_network'],
        'cohort_based': ['cohort', 'survival'],
    }

    @staticmethod
    def create_model(model_type: str, config: Optional[Dict] = None) -> BaseModel:
        """
        Create a forecasting model.

        Args:
            model_type: Type of model to create
            config: Configuration dictionary

        Returns:
            Instantiated model

        Raises:
            ValueError: If model type is not recognized
        """
        if model_type not in ModelFactory.AVAILABLE_MODELS:
            raise ValueError(
                f"Unknown model type: {model_type}. "
                f"Available models: {list(ModelFactory.AVAILABLE_MODELS.keys())}"
            )

        model_class = ModelFactory.AVAILABLE_MODELS[model_type]
        logger.info(f"Creating {model_type} model")

        return model_class(config)

    @staticmethod
    def create_multiple_models(
        model_types: List[str],
        config: Optional[Dict] = None
    ) -> Dict[str, BaseModel]:
        """
        Create multiple models.

        Args:
            model_types: List of model types to create
            config: Configuration dictionary

        Returns:
            Dictionary of model name to model instance
        """
        models = {}

        for model_type in model_types:
            try:
                models[model_type] = ModelFactory.create_model(model_type, config)
            except Exception as e:
                logger.warning(f"Failed to create {model_type} model: {e}")

        logger.info(f"Created {len(models)} models: {list(models.keys())}")

        return models

    @staticmethod
    def create_ensemble(
        models: Dict[str, BaseModel],
        weights: Optional[Dict[str, float]] = None,
        config: Optional[Dict] = None
    ) -> EnsembleModel:
        """
        Create an ensemble from existing models.

        Args:
            models: Dictionary of trained models
            weights: Dictionary of model weights (equal weights if None)
            config: Configuration dictionary

        Returns:
            Ensemble model
        """
        ensemble = EnsembleModel(config)

        if weights is None:
            # Equal weights
            weights = {name: 1.0 for name in models.keys()}

        for name, model in models.items():
            weight = weights.get(name, 1.0)
            ensemble.add_model(name, model, weight)

        logger.info(f"Created ensemble with {len(models)} models")

        return ensemble

    @staticmethod
    def get_models_by_category(category: str) -> List[str]:
        """
        Get list of models in a category.

        Args:
            category: Category name ('bottom_up', 'time_series', 'machine_learning', 'cohort_based')

        Returns:
            List of model names
        """
        if category not in ModelFactory.MODEL_CATEGORIES:
            raise ValueError(
                f"Unknown category: {category}. "
                f"Available categories: {list(ModelFactory.MODEL_CATEGORIES.keys())}"
            )

        return ModelFactory.MODEL_CATEGORIES[category]

    @staticmethod
    def auto_select_models(
        data: pd.DataFrame,
        business_type: Optional[str] = None
    ) -> List[str]:
        """
        Automatically select appropriate models based on data and business type.

        Args:
            data: Historical data
            business_type: Type of business

        Returns:
            List of recommended model types
        """
        recommended = []

        # Check data size
        n_samples = len(data)

        # Time series models work well with sufficient history
        if n_samples >= 24:
            recommended.append('prophet')
            recommended.append('arima')

        if n_samples >= 36:
            recommended.append('lstm')

        # ML models need more data
        if n_samples >= 50:
            recommended.append('xgboost')
            recommended.append('random_forest')

        # Business type specific recommendations
        if business_type == 'saas':
            recommended.append('customer_based')
            recommended.append('cohort')

        elif business_type == 'ecommerce':
            recommended.append('unit_economics')

        elif business_type == 'enterprise':
            recommended.append('sales_funnel')

        # Always include at least one model
        if not recommended:
            recommended.append('prophet')

        logger.info(f"Auto-selected models: {recommended}")

        return recommended

    @staticmethod
    def compare_models(
        models: Dict[str, BaseModel],
        test_data: pd.DataFrame,
        target_column: str
    ) -> pd.DataFrame:
        """
        Compare model performance on test data.

        Args:
            models: Dictionary of trained models
            test_data: Test dataset
            target_column: Target column name

        Returns:
            DataFrame with model comparison metrics
        """
        results = []

        for name, model in models.items():
            try:
                # Get predictions
                if hasattr(model, 'predict'):
                    predictions = model.predict(periods=len(test_data))

                    if 'forecast' in predictions.columns:
                        pred_values = predictions['forecast']

                        # Calculate metrics
                        metrics = model.calculate_accuracy_metrics(
                            test_data[target_column],
                            pred_values
                        )

                        results.append({
                            'model': name,
                            **metrics
                        })

            except Exception as e:
                logger.warning(f"Error evaluating {name}: {e}")

        comparison_df = pd.DataFrame(results)

        if not comparison_df.empty:
            # Sort by RMSE (lower is better)
            comparison_df = comparison_df.sort_values('rmse')

        logger.info(f"Model comparison completed for {len(results)} models")

        return comparison_df

    @staticmethod
    def get_best_model(
        models: Dict[str, BaseModel],
        test_data: pd.DataFrame,
        target_column: str,
        metric: str = 'rmse'
    ) -> str:
        """
        Get the best performing model.

        Args:
            models: Dictionary of trained models
            test_data: Test dataset
            target_column: Target column name
            metric: Metric to use for selection ('rmse', 'mae', 'mape', 'r2')

        Returns:
            Name of best model
        """
        comparison = ModelFactory.compare_models(models, test_data, target_column)

        if comparison.empty:
            raise ValueError("No models could be evaluated")

        # For R2, higher is better; for others, lower is better
        if metric == 'r2':
            best_model = comparison.loc[comparison[metric].idxmax(), 'model']
        else:
            best_model = comparison.loc[comparison[metric].idxmin(), 'model']

        logger.info(f"Best model: {best_model} (by {metric})")

        return best_model
