"""
Data validation module for revenue forecasting data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from ..utils.logger import setup_logger
from ..utils.helpers import detect_outliers

logger = setup_logger(__name__)


class DataValidator:
    """
    Validates data quality and structure for revenue forecasting.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize DataValidator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.validation_results = {}

    def validate(self, data: pd.DataFrame, required_columns: Optional[List[str]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Perform comprehensive data validation.

        Args:
            data: DataFrame to validate
            required_columns: List of required column names

        Returns:
            Tuple of (is_valid, validation_results)
        """
        logger.info("Starting data validation")

        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': {}
        }

        # Check for empty data
        results['checks']['empty_check'] = self._check_empty(data, results)

        # Check required columns
        if required_columns:
            results['checks']['columns_check'] = self._check_required_columns(data, required_columns, results)

        # Check for missing values
        results['checks']['missing_values'] = self._check_missing_values(data, results)

        # Check data types
        results['checks']['data_types'] = self._check_data_types(data, results)

        # Check for duplicates
        results['checks']['duplicates'] = self._check_duplicates(data, results)

        # Check for outliers
        results['checks']['outliers'] = self._check_outliers(data, results)

        # Check date column continuity
        date_column = self.config.get('date_column', 'date')
        if date_column in data.columns:
            results['checks']['date_continuity'] = self._check_date_continuity(data, date_column, results)

        # Check numeric ranges
        results['checks']['numeric_ranges'] = self._check_numeric_ranges(data, results)

        self.validation_results = results

        logger.info(f"Validation complete: {len(results['errors'])} errors, {len(results['warnings'])} warnings")

        return results['is_valid'], results

    def _check_empty(self, data: pd.DataFrame, results: Dict) -> bool:
        """Check if data is empty."""
        if data.empty:
            results['errors'].append("Data is empty")
            results['is_valid'] = False
            return False
        return True

    def _check_required_columns(self, data: pd.DataFrame, required_columns: List[str], results: Dict) -> bool:
        """Check if all required columns are present."""
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            results['errors'].append(f"Missing required columns: {missing_columns}")
            results['is_valid'] = False
            return False

        return True

    def _check_missing_values(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Check for missing values."""
        missing = data.isnull().sum()
        missing_pct = (missing / len(data) * 100).round(2)

        columns_with_missing = missing[missing > 0]

        check_result = {
            'total_missing': int(missing.sum()),
            'columns_with_missing': columns_with_missing.to_dict(),
            'missing_percentage': missing_pct[missing_pct > 0].to_dict()
        }

        # Warning if any column has > 50% missing
        high_missing = missing_pct[missing_pct > 50]
        if not high_missing.empty:
            results['warnings'].append(
                f"Columns with >50% missing values: {high_missing.to_dict()}"
            )

        # Error if critical columns have any missing
        revenue_col = self.config.get('revenue_column', 'revenue')
        date_col = self.config.get('date_column', 'date')

        if revenue_col in data.columns and data[revenue_col].isnull().any():
            results['warnings'].append(f"Revenue column '{revenue_col}' has missing values")

        if date_col in data.columns and data[date_col].isnull().any():
            results['errors'].append(f"Date column '{date_col}' has missing values")
            results['is_valid'] = False

        return check_result

    def _check_data_types(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Check data types of columns."""
        dtypes = data.dtypes.to_dict()

        check_result = {
            'dtypes': {k: str(v) for k, v in dtypes.items()}
        }

        # Check if date column is datetime
        date_col = self.config.get('date_column', 'date')
        if date_col in data.columns:
            if not pd.api.types.is_datetime64_any_dtype(data[date_col]):
                results['warnings'].append(
                    f"Date column '{date_col}' is not datetime type. Current type: {data[date_col].dtype}"
                )

        # Check if revenue column is numeric
        revenue_col = self.config.get('revenue_column', 'revenue')
        if revenue_col in data.columns:
            if not pd.api.types.is_numeric_dtype(data[revenue_col]):
                results['errors'].append(
                    f"Revenue column '{revenue_col}' is not numeric. Current type: {data[revenue_col].dtype}"
                )
                results['is_valid'] = False

        return check_result

    def _check_duplicates(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Check for duplicate rows."""
        duplicates = data.duplicated()
        n_duplicates = duplicates.sum()

        check_result = {
            'n_duplicates': int(n_duplicates),
            'duplicate_percentage': float(n_duplicates / len(data) * 100)
        }

        if n_duplicates > 0:
            results['warnings'].append(
                f"Found {n_duplicates} duplicate rows ({check_result['duplicate_percentage']:.2f}%)"
            )

        return check_result

    def _check_outliers(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Check for outliers in numeric columns."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        threshold = self.config.get('outlier_threshold', 3.0)

        outliers_info = {}

        for col in numeric_cols:
            outliers = detect_outliers(data[col].dropna(), threshold)
            n_outliers = outliers.sum()

            if n_outliers > 0:
                outliers_info[col] = {
                    'count': int(n_outliers),
                    'percentage': float(n_outliers / len(data) * 100)
                }

        check_result = {
            'threshold': threshold,
            'outliers_by_column': outliers_info
        }

        if outliers_info:
            results['warnings'].append(
                f"Outliers detected in {len(outliers_info)} columns using {threshold} std threshold"
            )

        return check_result

    def _check_date_continuity(self, data: pd.DataFrame, date_col: str, results: Dict) -> Dict:
        """Check if dates are continuous without large gaps."""
        if date_col not in data.columns:
            return {}

        dates = pd.to_datetime(data[date_col]).sort_values()
        date_diffs = dates.diff()

        # Detect frequency
        most_common_diff = date_diffs.mode()[0] if not date_diffs.mode().empty else None

        check_result = {
            'start_date': str(dates.min()),
            'end_date': str(dates.max()),
            'n_periods': len(dates),
            'inferred_frequency': str(most_common_diff) if most_common_diff else 'Unknown'
        }

        # Check for gaps
        if most_common_diff:
            gaps = date_diffs[date_diffs > most_common_diff * 1.5]
            if not gaps.empty:
                results['warnings'].append(
                    f"Found {len(gaps)} date gaps larger than expected frequency"
                )
                check_result['n_gaps'] = len(gaps)

        return check_result

    def _check_numeric_ranges(self, data: pd.DataFrame, results: Dict) -> Dict:
        """Check if numeric values are in reasonable ranges."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        range_info = {}

        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) == 0:
                continue

            range_info[col] = {
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'mean': float(col_data.mean()),
                'median': float(col_data.median())
            }

            # Check for negative values in revenue column
            revenue_col = self.config.get('revenue_column', 'revenue')
            if col == revenue_col and (col_data < 0).any():
                results['warnings'].append(
                    f"Revenue column '{revenue_col}' contains negative values"
                )

        return range_info

    def get_validation_report(self) -> str:
        """
        Generate a human-readable validation report.

        Returns:
            Validation report as string
        """
        if not self.validation_results:
            return "No validation results available"

        report = ["=" * 60]
        report.append("DATA VALIDATION REPORT")
        report.append("=" * 60)

        results = self.validation_results

        report.append(f"\nOverall Status: {'PASSED' if results['is_valid'] else 'FAILED'}")
        report.append(f"Errors: {len(results['errors'])}")
        report.append(f"Warnings: {len(results['warnings'])}")

        if results['errors']:
            report.append("\nERRORS:")
            for i, error in enumerate(results['errors'], 1):
                report.append(f"  {i}. {error}")

        if results['warnings']:
            report.append("\nWARNINGS:")
            for i, warning in enumerate(results['warnings'], 1):
                report.append(f"  {i}. {warning}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)
