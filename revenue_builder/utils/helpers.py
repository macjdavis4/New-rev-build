"""
Utility helper functions.
"""

import numpy as np
import pandas as pd
from typing import Union, List, Dict, Any
from datetime import datetime, timedelta


def ensure_datetime(date_col: pd.Series) -> pd.Series:
    """
    Ensure a column is in datetime format.

    Args:
        date_col: Series to convert

    Returns:
        Series in datetime format
    """
    if not pd.api.types.is_datetime64_any_dtype(date_col):
        return pd.to_datetime(date_col)
    return date_col


def calculate_growth_rate(series: pd.Series, periods: int = 1) -> pd.Series:
    """
    Calculate period-over-period growth rate.

    Args:
        series: Time series data
        periods: Number of periods to shift

    Returns:
        Growth rate series
    """
    return series.pct_change(periods=periods)


def calculate_cagr(start_value: float, end_value: float, periods: int) -> float:
    """
    Calculate Compound Annual Growth Rate.

    Args:
        start_value: Starting value
        end_value: Ending value
        periods: Number of periods

    Returns:
        CAGR as a decimal
    """
    if start_value <= 0 or end_value <= 0 or periods <= 0:
        return 0.0
    return (end_value / start_value) ** (1 / periods) - 1


def detect_outliers(data: pd.Series, threshold: float = 3.0) -> pd.Series:
    """
    Detect outliers using z-score method.

    Args:
        data: Series to analyze
        threshold: Z-score threshold

    Returns:
        Boolean series indicating outliers
    """
    z_scores = np.abs((data - data.mean()) / data.std())
    return z_scores > threshold


def generate_date_range(
    start_date: Union[str, datetime],
    periods: int,
    freq: str = 'M'
) -> pd.DatetimeIndex:
    """
    Generate a date range.

    Args:
        start_date: Starting date
        periods: Number of periods
        freq: Frequency ('D', 'W', 'M', 'Q', 'Y')

    Returns:
        DatetimeIndex
    """
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)

    return pd.date_range(start=start_date, periods=periods, freq=freq)


def interpolate_missing(
    data: pd.Series,
    method: str = 'linear'
) -> pd.Series:
    """
    Interpolate missing values.

    Args:
        data: Series with missing values
        method: Interpolation method

    Returns:
        Series with interpolated values
    """
    return data.interpolate(method=method)


def winsorize(data: pd.Series, limits: tuple = (0.05, 0.05)) -> pd.Series:
    """
    Winsorize data to handle outliers.

    Args:
        data: Series to winsorize
        limits: Lower and upper percentile limits

    Returns:
        Winsorized series
    """
    from scipy.stats import mstats
    return pd.Series(
        mstats.winsorize(data, limits=limits),
        index=data.index
    )


def moving_average(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate moving average.

    Args:
        data: Series to smooth
        window: Window size

    Returns:
        Moving average series
    """
    return data.rolling(window=window, min_periods=1).mean()


def exponential_smoothing(data: pd.Series, alpha: float = 0.3) -> pd.Series:
    """
    Apply exponential smoothing.

    Args:
        data: Series to smooth
        alpha: Smoothing parameter (0-1)

    Returns:
        Smoothed series
    """
    return data.ewm(alpha=alpha, adjust=False).mean()


def safe_divide(numerator: Union[float, pd.Series],
                denominator: Union[float, pd.Series],
                default: float = 0.0) -> Union[float, pd.Series]:
    """
    Safely divide, handling zero division.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value for zero division

    Returns:
        Result of division or default
    """
    if isinstance(numerator, pd.Series) or isinstance(denominator, pd.Series):
        result = numerator / denominator
        if isinstance(result, pd.Series):
            result = result.replace([np.inf, -np.inf], default)
            result = result.fillna(default)
        return result
    else:
        return numerator / denominator if denominator != 0 else default


def format_currency(value: float, symbol: str = '$', decimals: int = 2) -> str:
    """
    Format a value as currency.

    Args:
        value: Value to format
        symbol: Currency symbol
        decimals: Number of decimal places

    Returns:
        Formatted currency string
    """
    if value >= 1e9:
        return f"{symbol}{value/1e9:.{decimals}f}B"
    elif value >= 1e6:
        return f"{symbol}{value/1e6:.{decimals}f}M"
    elif value >= 1e3:
        return f"{symbol}{value/1e3:.{decimals}f}K"
    else:
        return f"{symbol}{value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a value as percentage.

    Args:
        value: Value to format (as decimal, e.g., 0.15 for 15%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"
