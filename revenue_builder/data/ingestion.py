"""
Data ingestion module supporting multiple formats and sources.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Optional, Dict, Any
import json
import sqlalchemy
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class DataIngestion:
    """
    Handles data ingestion from multiple sources and formats.

    Supports:
    - CSV files
    - Excel files (.xlsx, .xls)
    - JSON files
    - Database connections (SQL)
    - Pandas DataFrames
    """

    def __init__(self):
        """Initialize DataIngestion."""
        self.data = None
        self.metadata = {}

    def load_data(
        self,
        source: Union[str, pd.DataFrame],
        source_type: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from various sources.

        Args:
            source: Data source (file path, DataFrame, or connection string)
            source_type: Type of source ('csv', 'excel', 'json', 'sql', 'dataframe')
            **kwargs: Additional parameters for specific loaders

        Returns:
            Loaded DataFrame
        """
        if isinstance(source, pd.DataFrame):
            logger.info("Loading data from DataFrame")
            self.data = source.copy()
            self.metadata['source_type'] = 'dataframe'
            return self.data

        if source_type is None:
            source_type = self._detect_source_type(source)

        logger.info(f"Loading data from {source_type}: {source}")

        loaders = {
            'csv': self._load_csv,
            'excel': self._load_excel,
            'json': self._load_json,
            'sql': self._load_sql,
        }

        if source_type not in loaders:
            raise ValueError(f"Unsupported source type: {source_type}")

        self.data = loaders[source_type](source, **kwargs)
        self.metadata['source'] = source
        self.metadata['source_type'] = source_type
        self.metadata['shape'] = self.data.shape
        self.metadata['columns'] = list(self.data.columns)

        logger.info(f"Data loaded successfully: {self.data.shape[0]} rows, {self.data.shape[1]} columns")

        return self.data

    def _detect_source_type(self, source: str) -> str:
        """Detect source type from file extension or path."""
        if isinstance(source, str):
            path = Path(source)
            extension = path.suffix.lower()

            if extension == '.csv':
                return 'csv'
            elif extension in ['.xlsx', '.xls']:
                return 'excel'
            elif extension == '.json':
                return 'json'
            elif source.startswith(('postgresql://', 'mysql://', 'sqlite://', 'mssql://')):
                return 'sql'

        raise ValueError(f"Could not detect source type for: {source}")

    def _load_csv(self, path: str, **kwargs) -> pd.DataFrame:
        """Load data from CSV file."""
        default_params = {
            'parse_dates': True,
            'infer_datetime_format': True,
        }
        default_params.update(kwargs)

        return pd.read_csv(path, **default_params)

    def _load_excel(self, path: str, **kwargs) -> pd.DataFrame:
        """Load data from Excel file."""
        default_params = {
            'sheet_name': kwargs.get('sheet_name', 0),
        }
        default_params.update(kwargs)

        return pd.read_excel(path, **default_params)

    def _load_json(self, path: str, **kwargs) -> pd.DataFrame:
        """Load data from JSON file."""
        default_params = {
            'orient': kwargs.get('orient', 'records'),
        }
        default_params.update(kwargs)

        return pd.read_json(path, **default_params)

    def _load_sql(self, connection_string: str, query: Optional[str] = None, table: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        Load data from SQL database.

        Args:
            connection_string: Database connection string
            query: SQL query to execute
            table: Table name (if no query provided)
            **kwargs: Additional parameters

        Returns:
            DataFrame with query results
        """
        engine = sqlalchemy.create_engine(connection_string)

        if query:
            return pd.read_sql_query(query, engine, **kwargs)
        elif table:
            return pd.read_sql_table(table, engine, **kwargs)
        else:
            raise ValueError("Either 'query' or 'table' must be provided for SQL sources")

    def load_multiple_files(self, file_paths: list, concat_axis: int = 0) -> pd.DataFrame:
        """
        Load and concatenate multiple files.

        Args:
            file_paths: List of file paths
            concat_axis: Axis to concatenate (0 for rows, 1 for columns)

        Returns:
            Concatenated DataFrame
        """
        logger.info(f"Loading {len(file_paths)} files")

        dataframes = []
        for path in file_paths:
            df = self.load_data(path)
            dataframes.append(df)

        self.data = pd.concat(dataframes, axis=concat_axis, ignore_index=(concat_axis == 0))

        logger.info(f"Concatenated data: {self.data.shape[0]} rows, {self.data.shape[1]} columns")

        return self.data

    def load_from_config(self, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Load data based on configuration dictionary.

        Args:
            config: Configuration with data source information

        Returns:
            Loaded DataFrame
        """
        source = config.get('source')
        source_type = config.get('type')
        params = config.get('params', {})

        return self.load_data(source, source_type, **params)

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about loaded data."""
        return self.metadata

    def preview(self, n: int = 5) -> pd.DataFrame:
        """
        Preview the first n rows of data.

        Args:
            n: Number of rows to show

        Returns:
            First n rows
        """
        if self.data is None:
            raise ValueError("No data loaded")

        return self.data.head(n)

    def get_data_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the loaded data.

        Returns:
            Dictionary with data statistics and information
        """
        if self.data is None:
            raise ValueError("No data loaded")

        info = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'missing_percentage': (self.data.isnull().sum() / len(self.data) * 100).to_dict(),
            'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.data.select_dtypes(include=['object', 'category']).columns),
            'datetime_columns': list(self.data.select_dtypes(include=['datetime64']).columns),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # Add summary statistics for numeric columns
        if info['numeric_columns']:
            info['numeric_summary'] = self.data[info['numeric_columns']].describe().to_dict()

        return info

    def save_data(self, path: str, format: Optional[str] = None, **kwargs):
        """
        Save loaded data to file.

        Args:
            path: Output file path
            format: Output format ('csv', 'excel', 'json')
            **kwargs: Additional parameters for saving
        """
        if self.data is None:
            raise ValueError("No data to save")

        if format is None:
            format = self._detect_source_type(path)

        logger.info(f"Saving data to {format}: {path}")

        if format == 'csv':
            self.data.to_csv(path, index=False, **kwargs)
        elif format == 'excel':
            self.data.to_excel(path, index=False, **kwargs)
        elif format == 'json':
            self.data.to_json(path, **kwargs)
        else:
            raise ValueError(f"Unsupported output format: {format}")

        logger.info("Data saved successfully")
