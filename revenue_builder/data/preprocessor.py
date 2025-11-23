"""
Data preprocessing module for cleaning and transforming data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from ..utils.logger import setup_logger
from ..utils.helpers import (
    ensure_datetime,
    interpolate_missing,
    detect_outliers,
    winsorize
)

logger = setup_logger(__name__)


class DataPreprocessor:
    """
    Handles data preprocessing including cleaning, transformation, and feature engineering.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize DataPreprocessor.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.scalers = {}
        self.transformations_applied = []

    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply full preprocessing pipeline.

        Args:
            data: Raw DataFrame

        Returns:
            Preprocessed DataFrame
        """
        logger.info("Starting data preprocessing")

        df = data.copy()

        # Convert date column to datetime
        date_col = self.config.get('date_column', 'date')
        if date_col in df.columns:
            df = self._convert_date_column(df, date_col)

        # Handle missing values
        df = self._handle_missing_values(df)

        # Remove duplicates
        df = self._remove_duplicates(df)

        # Handle outliers
        if self.config.get('outlier_detection', True):
            df = self._handle_outliers(df)

        # Sort by date
        if date_col in df.columns:
            df = df.sort_values(date_col).reset_index(drop=True)

        # Engineer basic features
        df = self._engineer_features(df)

        logger.info(f"Preprocessing complete. Final shape: {df.shape}")

        return df

    def _convert_date_column(self, data: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Convert date column to datetime."""
        logger.info(f"Converting '{date_col}' to datetime")

        df = data.copy()
        df[date_col] = ensure_datetime(df[date_col])

        self.transformations_applied.append(f"Converted {date_col} to datetime")

        return df

    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values based on configuration.

        Strategies:
        - interpolate: Linear interpolation
        - forward_fill: Forward fill
        - backward_fill: Backward fill
        - mean: Fill with column mean
        - median: Fill with column median
        - drop: Drop rows with missing values
        """
        df = data.copy()
        strategy = self.config.get('missing_data_strategy', 'interpolate')

        missing_before = df.isnull().sum().sum()

        if missing_before == 0:
            logger.info("No missing values to handle")
            return df

        logger.info(f"Handling {missing_before} missing values using strategy: {strategy}")

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if strategy == 'interpolate':
            for col in numeric_cols:
                if df[col].isnull().any():
                    df[col] = interpolate_missing(df[col], method='linear')

        elif strategy == 'forward_fill':
            df = df.fillna(method='ffill')

        elif strategy == 'backward_fill':
            df = df.fillna(method='bfill')

        elif strategy == 'mean':
            for col in numeric_cols:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(df[col].mean())

        elif strategy == 'median':
            for col in numeric_cols:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(df[col].median())

        elif strategy == 'drop':
            df = df.dropna()

        else:
            logger.warning(f"Unknown missing data strategy: {strategy}. Using interpolation.")
            for col in numeric_cols:
                if df[col].isnull().any():
                    df[col] = interpolate_missing(df[col])

        missing_after = df.isnull().sum().sum()

        logger.info(f"Missing values reduced from {missing_before} to {missing_after}")

        self.transformations_applied.append(
            f"Handled missing values: {strategy} (before: {missing_before}, after: {missing_after})"
        )

        return df

    def _remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        df = data.copy()
        n_before = len(df)
        df = df.drop_duplicates()
        n_after = len(df)

        if n_before > n_after:
            logger.info(f"Removed {n_before - n_after} duplicate rows")
            self.transformations_applied.append(f"Removed {n_before - n_after} duplicates")

        return df

    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handle outliers using winsorization.

        Args:
            data: DataFrame with potential outliers

        Returns:
            DataFrame with outliers handled
        """
        df = data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        threshold = self.config.get('outlier_threshold', 3.0)

        outliers_handled = []

        for col in numeric_cols:
            if col in df.columns:
                outliers = detect_outliers(df[col].dropna(), threshold)
                n_outliers = outliers.sum()

                if n_outliers > 0:
                    # Winsorize at 5th and 95th percentiles
                    df[col] = winsorize(df[col], limits=(0.05, 0.05))
                    outliers_handled.append(col)

        if outliers_handled:
            logger.info(f"Handled outliers in {len(outliers_handled)} columns: {outliers_handled}")
            self.transformations_applied.append(f"Winsorized outliers in {len(outliers_handled)} columns")

        return df

    def _engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer basic time-based features.

        Args:
            data: DataFrame with date column

        Returns:
            DataFrame with engineered features
        """
        df = data.copy()
        date_col = self.config.get('date_column', 'date')

        if date_col not in df.columns:
            return df

        logger.info("Engineering time-based features")

        # Extract time components
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['quarter'] = df[date_col].dt.quarter
        df['day_of_week'] = df[date_col].dt.dayofweek
        df['day_of_year'] = df[date_col].dt.dayofyear
        df['week_of_year'] = df[date_col].dt.isocalendar().week

        # Add cyclical encodings for seasonality
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['quarter_sin'] = np.sin(2 * np.pi * df['quarter'] / 4)
        df['quarter_cos'] = np.cos(2 * np.pi * df['quarter'] / 4)

        self.transformations_applied.append("Engineered time-based features")

        return df

    def create_lag_features(
        self,
        data: pd.DataFrame,
        columns: List[str],
        lags: List[int]
    ) -> pd.DataFrame:
        """
        Create lagged features.

        Args:
            data: DataFrame
            columns: Columns to create lags for
            lags: List of lag periods

        Returns:
            DataFrame with lag features
        """
        df = data.copy()

        for col in columns:
            if col in df.columns:
                for lag in lags:
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)

        logger.info(f"Created lag features for {len(columns)} columns with lags: {lags}")

        return df

    def create_rolling_features(
        self,
        data: pd.DataFrame,
        columns: List[str],
        windows: List[int],
        aggregations: List[str] = ['mean', 'std']
    ) -> pd.DataFrame:
        """
        Create rolling window features.

        Args:
            data: DataFrame
            columns: Columns to create rolling features for
            windows: List of window sizes
            aggregations: List of aggregation functions

        Returns:
            DataFrame with rolling features
        """
        df = data.copy()

        for col in columns:
            if col in df.columns:
                for window in windows:
                    for agg in aggregations:
                        col_name = f'{col}_rolling_{window}_{agg}'
                        df[col_name] = df[col].rolling(window=window, min_periods=1).agg(agg)

        logger.info(f"Created rolling features for {len(columns)} columns")

        return df

    def scale_features(
        self,
        data: pd.DataFrame,
        columns: List[str],
        method: str = 'standard'
    ) -> pd.DataFrame:
        """
        Scale numeric features.

        Args:
            data: DataFrame
            columns: Columns to scale
            method: Scaling method ('standard' or 'minmax')

        Returns:
            DataFrame with scaled features
        """
        df = data.copy()

        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")

        for col in columns:
            if col in df.columns:
                df[col] = scaler.fit_transform(df[[col]])
                self.scalers[col] = scaler

        logger.info(f"Scaled {len(columns)} columns using {method} scaling")

        return df

    def create_growth_features(
        self,
        data: pd.DataFrame,
        columns: List[str],
        periods: List[int] = [1, 3, 6, 12]
    ) -> pd.DataFrame:
        """
        Create growth rate features.

        Args:
            data: DataFrame
            columns: Columns to create growth features for
            periods: List of periods for growth calculation

        Returns:
            DataFrame with growth features
        """
        df = data.copy()

        for col in columns:
            if col in df.columns:
                for period in periods:
                    growth_col = f'{col}_growth_{period}p'
                    df[growth_col] = df[col].pct_change(periods=period)

        logger.info(f"Created growth features for {len(columns)} columns")

        return df

    def get_transformations_log(self) -> List[str]:
        """Get list of transformations applied."""
        return self.transformations_applied

    def reset_transformations_log(self):
        """Reset transformations log."""
        self.transformations_applied = []
