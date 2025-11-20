"""
Machine learning ensemble models for revenue forecasting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from .base_model import BaseModel
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class XGBoostModel(BaseModel):
    """
    XGBoost model for revenue forecasting.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.feature_columns = None
        self.target_column = None

    def fit(
        self,
        data: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        **kwargs
    ) -> 'XGBoostModel':
        """
        Train XGBoost model.

        Args:
            data: Training data
            target_column: Target variable column
            feature_columns: List of feature columns (if None, use all numeric)
            **kwargs: Additional XGBoost parameters

        Returns:
            Self
        """
        try:
            import xgboost as xgb
        except ImportError:
            raise ImportError("xgboost is required. Install with: pip install xgboost")

        logger.info("Training XGBoostModel")

        self.target_column = target_column

        # Select features
        if feature_columns is None:
            feature_columns = [col for col in data.select_dtypes(include=[np.number]).columns
                               if col != target_column]

        self.feature_columns = feature_columns

        X = data[feature_columns]
        y = data[target_column]

        # XGBoost parameters
        params = {
            'objective': 'reg:squarederror',
            'max_depth': kwargs.get('max_depth', 6),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'n_estimators': kwargs.get('n_estimators', 100),
            'random_state': kwargs.get('random_state', 42)
        }

        # Train model
        self.model = xgb.XGBRegressor(**params)
        self.model.fit(X, y)

        self.is_trained = True

        # Get feature importance
        self.feature_importance = dict(zip(
            feature_columns,
            self.model.feature_importances_
        ))

        # Calculate training metrics
        predictions = self.model.predict(X)
        self.training_metrics = self.calculate_accuracy_metrics(y, pd.Series(predictions))

        logger.info(f"XGBoost model trained successfully")
        logger.info(f"Training RMSE: {self.training_metrics.get('rmse', 0):.2f}")
        logger.info(f"Top 3 features: {sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]}")

        return self

    def predict(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            data: DataFrame with feature columns
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        X = data[self.feature_columns]
        predictions = self.model.predict(X)

        self.predictions = pd.DataFrame({
            'period': range(1, len(predictions) + 1),
            'forecast': predictions
        })

        return self.predictions


class RandomForestModel(BaseModel):
    """
    Random Forest model for revenue forecasting.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.feature_columns = None
        self.target_column = None

    def fit(
        self,
        data: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        **kwargs
    ) -> 'RandomForestModel':
        """
        Train Random Forest model.

        Args:
            data: Training data
            target_column: Target variable column
            feature_columns: List of feature columns
            **kwargs: Additional Random Forest parameters

        Returns:
            Self
        """
        from sklearn.ensemble import RandomForestRegressor

        logger.info("Training RandomForestModel")

        self.target_column = target_column

        # Select features
        if feature_columns is None:
            feature_columns = [col for col in data.select_dtypes(include=[np.number]).columns
                               if col != target_column]

        self.feature_columns = feature_columns

        X = data[feature_columns]
        y = data[target_column]

        # Random Forest parameters
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'max_depth': kwargs.get('max_depth', 10),
            'min_samples_split': kwargs.get('min_samples_split', 5),
            'random_state': kwargs.get('random_state', 42),
            'n_jobs': kwargs.get('n_jobs', -1)
        }

        # Train model
        self.model = RandomForestRegressor(**params)
        self.model.fit(X, y)

        self.is_trained = True

        # Get feature importance
        self.feature_importance = dict(zip(
            feature_columns,
            self.model.feature_importances_
        ))

        # Calculate training metrics
        predictions = self.model.predict(X)
        self.training_metrics = self.calculate_accuracy_metrics(y, pd.Series(predictions))

        logger.info(f"Random Forest model trained successfully")
        logger.info(f"Training RMSE: {self.training_metrics.get('rmse', 0):.2f}")

        return self

    def predict(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            data: DataFrame with feature columns
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        X = data[self.feature_columns]
        predictions = self.model.predict(X)

        self.predictions = pd.DataFrame({
            'period': range(1, len(predictions) + 1),
            'forecast': predictions
        })

        return self.predictions


class NeuralNetworkModel(BaseModel):
    """
    Neural Network model for revenue forecasting.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.feature_columns = None
        self.target_column = None
        self.scaler_X = None
        self.scaler_y = None

    def fit(
        self,
        data: pd.DataFrame,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        hidden_layers: List[int] = [64, 32],
        epochs: int = 100,
        batch_size: int = 32,
        **kwargs
    ) -> 'NeuralNetworkModel':
        """
        Train Neural Network model.

        Args:
            data: Training data
            target_column: Target variable column
            feature_columns: List of feature columns
            hidden_layers: List of hidden layer sizes
            epochs: Number of training epochs
            batch_size: Batch size
            **kwargs: Additional parameters

        Returns:
            Self
        """
        try:
            from tensorflow import keras
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            raise ImportError("tensorflow and scikit-learn required. Install with: pip install tensorflow scikit-learn")

        logger.info("Training NeuralNetworkModel")

        self.target_column = target_column

        # Select features
        if feature_columns is None:
            feature_columns = [col for col in data.select_dtypes(include=[np.number]).columns
                               if col != target_column]

        self.feature_columns = feature_columns

        X = data[feature_columns].values
        y = data[target_column].values.reshape(-1, 1)

        # Scale features
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()

        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y)

        # Build neural network
        self.model = Sequential()
        self.model.add(Dense(hidden_layers[0], activation='relu', input_shape=(X_scaled.shape[1],)))
        self.model.add(Dropout(0.2))

        for units in hidden_layers[1:]:
            self.model.add(Dense(units, activation='relu'))
            self.model.add(Dropout(0.2))

        self.model.add(Dense(1))

        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        # Train model
        history = self.model.fit(
            X_scaled, y_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=0
        )

        self.is_trained = True

        # Calculate training metrics
        predictions_scaled = self.model.predict(X_scaled, verbose=0)
        predictions = self.scaler_y.inverse_transform(predictions_scaled).flatten()

        self.training_metrics = self.calculate_accuracy_metrics(
            pd.Series(y.flatten()),
            pd.Series(predictions)
        )

        logger.info(f"Neural Network model trained successfully")
        logger.info(f"Training RMSE: {self.training_metrics.get('rmse', 0):.2f}")

        return self

    def predict(
        self,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            data: DataFrame with feature columns
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        X = data[self.feature_columns].values
        X_scaled = self.scaler_X.transform(X)

        predictions_scaled = self.model.predict(X_scaled, verbose=0)
        predictions = self.scaler_y.inverse_transform(predictions_scaled).flatten()

        self.predictions = pd.DataFrame({
            'period': range(1, len(predictions) + 1),
            'forecast': predictions
        })

        return self.predictions


class EnsembleModel(BaseModel):
    """
    Ensemble model combining multiple forecasting models.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.models = {}
        self.weights = {}

    def add_model(self, name: str, model: BaseModel, weight: float = 1.0):
        """
        Add a model to the ensemble.

        Args:
            name: Model name
            model: Trained model instance
            weight: Model weight in ensemble
        """
        if not model.is_trained:
            raise ValueError(f"Model '{name}' must be trained before adding to ensemble")

        self.models[name] = model
        self.weights[name] = weight

        logger.info(f"Added {name} to ensemble with weight {weight}")

    def fit(self, data: pd.DataFrame, target_column: str, **kwargs) -> 'EnsembleModel':
        """
        Ensemble doesn't need separate training - models should be pre-trained.

        Args:
            data: Historical data
            target_column: Target column
            **kwargs: Additional parameters

        Returns:
            Self
        """
        if not self.models:
            raise ValueError("No models in ensemble. Add models using add_model()")

        self.is_trained = True
        return self

    def predict(self, periods: int, **kwargs) -> pd.DataFrame:
        """
        Generate ensemble forecasts.

        Args:
            periods: Number of periods to forecast
            **kwargs: Additional parameters

        Returns:
            DataFrame with ensemble forecasts
        """
        if not self.is_trained:
            raise ValueError("Ensemble must have trained models")

        # Normalize weights
        total_weight = sum(self.weights.values())
        normalized_weights = {k: v / total_weight for k, v in self.weights.items()}

        # Get predictions from each model
        all_predictions = []

        for name, model in self.models.items():
            try:
                pred = model.predict(periods=periods, **kwargs)

                if 'forecast' in pred.columns:
                    weighted_pred = pred['forecast'] * normalized_weights[name]
                    all_predictions.append(weighted_pred)
            except Exception as e:
                logger.warning(f"Error getting predictions from {name}: {e}")

        if not all_predictions:
            raise ValueError("No valid predictions from ensemble models")

        # Combine predictions
        ensemble_forecast = sum(all_predictions)

        self.predictions = pd.DataFrame({
            'period': range(1, periods + 1),
            'forecast': ensemble_forecast
        })

        return self.predictions
