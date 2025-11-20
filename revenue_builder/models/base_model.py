"""
Base model class for all forecasting models.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for all forecasting models.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize base model.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.is_trained = False
        self.model = None
        self.feature_importance = {}
        self.training_metrics = {}
        self.predictions = None

    @abstractmethod
    def fit(self, data: pd.DataFrame, target_column: str, **kwargs) -> 'BaseModel':
        """
        Train the model.

        Args:
            data: Training data
            target_column: Name of target column
            **kwargs: Additional parameters

        Returns:
            Self
        """
        pass

    @abstractmethod
    def predict(self, periods: int, **kwargs) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            periods: Number of periods to forecast
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        pass

    def get_metrics(self) -> Dict[str, float]:
        """
        Get model performance metrics.

        Returns:
            Dictionary of metrics
        """
        return self.training_metrics

    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.

        Returns:
            Dictionary of feature importance
        """
        return self.feature_importance

    def calculate_accuracy_metrics(
        self,
        actual: pd.Series,
        predicted: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate standard accuracy metrics.

        Args:
            actual: Actual values
            predicted: Predicted values

        Returns:
            Dictionary of metrics
        """
        # Remove NaN values
        mask = ~(actual.isna() | predicted.isna())
        actual = actual[mask]
        predicted = predicted[mask]

        if len(actual) == 0:
            return {}

        # Mean Absolute Error
        mae = np.mean(np.abs(actual - predicted))

        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100

        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))

        # R-squared
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - actual.mean()) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Mean Squared Error
        mse = np.mean((actual - predicted) ** 2)

        return {
            'mae': float(mae),
            'mape': float(mape),
            'rmse': float(rmse),
            'r2': float(r2),
            'mse': float(mse)
        }

    def create_confidence_intervals(
        self,
        predictions: pd.Series,
        confidence_level: float = 0.95,
        std_error: Optional[float] = None
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Create confidence intervals for predictions.

        Args:
            predictions: Point forecasts
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            std_error: Standard error (if None, estimated from data)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        from scipy import stats

        if std_error is None:
            # Estimate standard error as 10% of predictions
            std_error = predictions.std() * 0.1

        # Calculate z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence_level) / 2)

        # Calculate bounds
        margin = z_score * std_error
        lower_bound = predictions - margin
        upper_bound = predictions + margin

        return lower_bound, upper_bound

    def save_model(self, path: str):
        """
        Save model to disk.

        Args:
            path: Path to save model
        """
        import pickle

        with open(path, 'wb') as f:
            pickle.dump(self, f)

        logger.info(f"Model saved to {path}")

    @staticmethod
    def load_model(path: str) -> 'BaseModel':
        """
        Load model from disk.

        Args:
            path: Path to load model from

        Returns:
            Loaded model
        """
        import pickle

        with open(path, 'rb') as f:
            model = pickle.load(f)

        logger.info(f"Model loaded from {path}")

        return model

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(trained={self.is_trained})"
