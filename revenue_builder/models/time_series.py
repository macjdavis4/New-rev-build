"""
Time series forecasting models (ARIMA, Prophet, LSTM).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from .base_model import BaseModel
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ARIMAModel(BaseModel):
    """
    ARIMA (AutoRegressive Integrated Moving Average) model.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.order = None
        self.seasonal_order = None
        self.historical_data = None

    def fit(
        self,
        data: pd.DataFrame,
        target_column: str,
        order: Optional[Tuple[int, int, int]] = None,
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
        **kwargs
    ) -> 'ARIMAModel':
        """
        Train ARIMA model.

        Args:
            data: Historical data
            target_column: Target variable column
            order: (p, d, q) order for ARIMA
            seasonal_order: (P, D, Q, s) seasonal order
            **kwargs: Additional parameters

        Returns:
            Self
        """
        try:
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            from statsmodels.tsa.stattools import adfuller
        except ImportError:
            raise ImportError("statsmodels is required for ARIMA. Install with: pip install statsmodels")

        logger.info("Training ARIMAModel")

        self.historical_data = data[[target_column]].copy()

        # Auto-detect order if not provided
        if order is None:
            order = self._auto_arima_order(data[target_column])

        self.order = order
        self.seasonal_order = seasonal_order or (0, 0, 0, 0)

        # Fit SARIMAX model
        try:
            self.model = SARIMAX(
                data[target_column],
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            self.model = self.model.fit(disp=False)
            self.is_trained = True

            # Calculate metrics on training data
            fitted_values = self.model.fittedvalues
            self.training_metrics = self.calculate_accuracy_metrics(
                data[target_column],
                fitted_values
            )

            logger.info(f"ARIMA{self.order} model trained successfully")
            logger.info(f"Training RMSE: {self.training_metrics.get('rmse', 0):.2f}")

        except Exception as e:
            logger.error(f"Error training ARIMA model: {e}")
            raise

        return self

    def _auto_arima_order(self, series: pd.Series) -> Tuple[int, int, int]:
        """
        Automatically determine ARIMA order.

        Returns:
            Tuple of (p, d, q)
        """
        from statsmodels.tsa.stattools import adfuller

        # Test for stationarity
        result = adfuller(series.dropna())
        d = 0 if result[1] < 0.05 else 1

        # Default values for p and q
        p = 1
        q = 1

        return (p, d, q)

    def predict(
        self,
        periods: int,
        confidence_level: float = 0.95,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            periods: Number of periods to forecast
            confidence_level: Confidence level for intervals
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts and confidence intervals
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Generate forecast
        forecast_result = self.model.get_forecast(steps=periods)
        forecast_mean = forecast_result.predicted_mean

        # Get confidence intervals
        alpha = 1 - confidence_level
        forecast_ci = forecast_result.conf_int(alpha=alpha)

        # Create forecast dataframe
        self.predictions = pd.DataFrame({
            'period': range(1, periods + 1),
            'forecast': forecast_mean.values,
            'lower_bound': forecast_ci.iloc[:, 0].values,
            'upper_bound': forecast_ci.iloc[:, 1].values
        })

        return self.predictions


class ProphetModel(BaseModel):
    """
    Facebook Prophet model for time series forecasting.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.date_column = None
        self.target_column = None

    def fit(
        self,
        data: pd.DataFrame,
        date_column: str,
        target_column: str,
        **kwargs
    ) -> 'ProphetModel':
        """
        Train Prophet model.

        Args:
            data: Historical data
            date_column: Date column name
            target_column: Target variable column
            **kwargs: Additional Prophet parameters

        Returns:
            Self
        """
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("prophet is required. Install with: pip install prophet")

        logger.info("Training ProphetModel")

        self.date_column = date_column
        self.target_column = target_column

        # Prepare data in Prophet format
        df_prophet = data[[date_column, target_column]].copy()
        df_prophet.columns = ['ds', 'y']

        # Initialize and fit model
        prophet_params = {
            'seasonality_mode': kwargs.get('seasonality_mode', 'multiplicative'),
            'yearly_seasonality': kwargs.get('yearly_seasonality', True),
            'weekly_seasonality': kwargs.get('weekly_seasonality', False),
            'daily_seasonality': kwargs.get('daily_seasonality', False),
        }

        self.model = Prophet(**prophet_params)
        self.model.fit(df_prophet)

        self.is_trained = True

        logger.info("Prophet model trained successfully")

        return self

    def predict(
        self,
        periods: int,
        freq: str = 'M',
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            periods: Number of periods to forecast
            freq: Frequency ('D', 'W', 'M', 'Q', 'Y')
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq=freq)

        # Generate forecast
        forecast = self.model.predict(future)

        # Extract forecasts for future periods only
        n_historical = len(future) - periods
        forecast_future = forecast.iloc[n_historical:]

        self.predictions = pd.DataFrame({
            'period': range(1, periods + 1),
            'date': forecast_future['ds'].values,
            'forecast': forecast_future['yhat'].values,
            'lower_bound': forecast_future['yhat_lower'].values,
            'upper_bound': forecast_future['yhat_upper'].values,
            'trend': forecast_future['trend'].values,
        })

        return self.predictions


class LSTMModel(BaseModel):
    """
    LSTM (Long Short-Term Memory) neural network model.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.scaler = None
        self.lookback = None
        self.historical_data = None

    def fit(
        self,
        data: pd.DataFrame,
        target_column: str,
        lookback: int = 12,
        epochs: int = 50,
        batch_size: int = 32,
        **kwargs
    ) -> 'LSTMModel':
        """
        Train LSTM model.

        Args:
            data: Historical data
            target_column: Target variable column
            lookback: Number of previous timesteps to use
            epochs: Number of training epochs
            batch_size: Batch size for training
            **kwargs: Additional parameters

        Returns:
            Self
        """
        try:
            from tensorflow import keras
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from sklearn.preprocessing import MinMaxScaler
        except ImportError:
            raise ImportError("tensorflow and scikit-learn required. Install with: pip install tensorflow scikit-learn")

        logger.info("Training LSTMModel")

        self.lookback = lookback
        self.historical_data = data[[target_column]].copy()

        # Scale data
        self.scaler = MinMaxScaler()
        scaled_data = self.scaler.fit_transform(data[[target_column]])

        # Prepare sequences
        X, y = self._create_sequences(scaled_data, lookback)

        if len(X) == 0:
            raise ValueError(f"Not enough data for lookback={lookback}. Need at least {lookback + 1} samples.")

        # Build LSTM model
        self.model = Sequential([
            LSTM(50, activation='relu', return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(50, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])

        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        # Train model
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=0
        )

        self.is_trained = True

        # Calculate training metrics
        predictions_scaled = self.model.predict(X, verbose=0)
        predictions = self.scaler.inverse_transform(predictions_scaled)
        actuals = self.scaler.inverse_transform(y)

        self.training_metrics = self.calculate_accuracy_metrics(
            pd.Series(actuals.flatten()),
            pd.Series(predictions.flatten())
        )

        logger.info(f"LSTM model trained successfully")
        logger.info(f"Training RMSE: {self.training_metrics.get('rmse', 0):.2f}")

        return self

    def _create_sequences(self, data: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []

        for i in range(lookback, len(data)):
            X.append(data[i - lookback:i, 0])
            y.append(data[i, 0])

        return np.array(X), np.array(y)

    def predict(
        self,
        periods: int,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate forecasts.

        Args:
            periods: Number of periods to forecast
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Get last lookback values
        scaled_data = self.scaler.transform(self.historical_data)
        last_sequence = scaled_data[-self.lookback:].reshape(1, self.lookback, 1)

        # Generate forecasts
        forecasts = []

        for i in range(periods):
            # Predict next value
            pred_scaled = self.model.predict(last_sequence, verbose=0)

            # Inverse transform
            pred = self.scaler.inverse_transform(pred_scaled)[0, 0]
            forecasts.append(pred)

            # Update sequence
            last_sequence = np.roll(last_sequence, -1, axis=1)
            last_sequence[0, -1, 0] = pred_scaled[0, 0]

        self.predictions = pd.DataFrame({
            'period': range(1, periods + 1),
            'forecast': forecasts
        })

        return self.predictions
