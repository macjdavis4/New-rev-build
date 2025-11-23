"""
Cohort analysis and retention modeling.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from .base_model import BaseModel
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class CohortModel(BaseModel):
    """
    Cohort-based revenue forecasting model.

    Analyzes customer cohorts grouped by acquisition period and models
    retention curves and revenue per cohort over time.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.cohort_data = None
        self.retention_curves = None
        self.revenue_per_cohort = None
        self.avg_cohort_size = None
        self.avg_initial_revenue = None

    def fit(
        self,
        data: pd.DataFrame,
        cohort_column: str,
        period_column: str,
        customers_column: str,
        revenue_column: str,
        **kwargs
    ) -> 'CohortModel':
        """
        Train cohort model.

        Args:
            data: Historical cohort data
            cohort_column: Column identifying cohort (e.g., acquisition month)
            period_column: Column for period/age of cohort
            customers_column: Column for number of customers
            revenue_column: Column for revenue
            **kwargs: Additional parameters

        Returns:
            Self
        """
        logger.info("Training CohortModel")

        self.cohort_data = data.copy()

        # Calculate retention rates for each cohort
        self.retention_curves = self._calculate_retention_curves(
            data, cohort_column, period_column, customers_column
        )

        # Calculate revenue per cohort over time
        self.revenue_per_cohort = self._calculate_revenue_per_cohort(
            data, cohort_column, period_column, revenue_column, customers_column
        )

        # Calculate average cohort metrics
        initial_cohorts = data[data[period_column] == 0]
        self.avg_cohort_size = initial_cohorts[customers_column].mean()
        self.avg_initial_revenue = initial_cohorts[revenue_column].mean()

        self.is_trained = True

        logger.info(f"Cohort model trained with {len(data[cohort_column].unique())} cohorts")
        logger.info(f"Average cohort size: {self.avg_cohort_size:.0f}")
        logger.info(f"Average initial revenue per cohort: ${self.avg_initial_revenue:.2f}")

        return self

    def _calculate_retention_curves(
        self,
        data: pd.DataFrame,
        cohort_column: str,
        period_column: str,
        customers_column: str
    ) -> pd.DataFrame:
        """Calculate average retention curve across cohorts."""

        retention_data = []

        for cohort in data[cohort_column].unique():
            cohort_df = data[data[cohort_column] == cohort].sort_values(period_column)

            if len(cohort_df) > 0:
                initial_customers = cohort_df[cohort_df[period_column] == 0][customers_column].values

                if len(initial_customers) > 0:
                    initial_count = initial_customers[0]

                    for _, row in cohort_df.iterrows():
                        retention_rate = row[customers_column] / initial_count if initial_count > 0 else 0
                        retention_data.append({
                            'cohort': cohort,
                            'period': row[period_column],
                            'retention_rate': retention_rate
                        })

        retention_df = pd.DataFrame(retention_data)

        # Calculate average retention by period
        avg_retention = retention_df.groupby('period')['retention_rate'].mean().reset_index()

        return avg_retention

    def _calculate_revenue_per_cohort(
        self,
        data: pd.DataFrame,
        cohort_column: str,
        period_column: str,
        revenue_column: str,
        customers_column: str
    ) -> pd.DataFrame:
        """Calculate average revenue per customer by cohort age."""

        revenue_data = []

        for cohort in data[cohort_column].unique():
            cohort_df = data[data[cohort_column] == cohort].sort_values(period_column)

            for _, row in cohort_df.iterrows():
                revenue_per_customer = (
                    row[revenue_column] / row[customers_column]
                    if row[customers_column] > 0 else 0
                )
                revenue_data.append({
                    'cohort': cohort,
                    'period': row[period_column],
                    'revenue_per_customer': revenue_per_customer
                })

        revenue_df = pd.DataFrame(revenue_data)

        # Calculate average revenue per customer by period
        avg_revenue = revenue_df.groupby('period')['revenue_per_customer'].mean().reset_index()

        return avg_revenue

    def predict(
        self,
        periods: int,
        new_cohorts_per_period: int = 1,
        cohort_size: Optional[float] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate cohort-based revenue forecasts.

        Args:
            periods: Number of periods to forecast
            new_cohorts_per_period: Number of new cohorts per period
            cohort_size: Size of new cohorts (uses avg if None)
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        cohort_size = cohort_size or self.avg_cohort_size

        forecasts = []

        # Track all active cohorts
        active_cohorts = []

        for period in range(1, periods + 1):
            # Add new cohorts for this period
            for _ in range(new_cohorts_per_period):
                active_cohorts.append({
                    'start_period': period,
                    'size': cohort_size,
                    'age': 0
                })

            # Calculate revenue for this period
            period_revenue = 0

            for cohort in active_cohorts:
                cohort_age = period - cohort['start_period']
                cohort['age'] = cohort_age

                # Get retention rate for this age
                retention_rate = self._get_retention_rate(cohort_age)

                # Get revenue per customer for this age
                revenue_per_customer = self._get_revenue_per_customer(cohort_age)

                # Calculate cohort contribution
                retained_customers = cohort['size'] * retention_rate
                cohort_revenue = retained_customers * revenue_per_customer

                period_revenue += cohort_revenue

            forecasts.append({
                'period': period,
                'revenue': period_revenue,
                'active_cohorts': len(active_cohorts),
                'new_cohorts': new_cohorts_per_period
            })

        self.predictions = pd.DataFrame(forecasts)

        return self.predictions

    def _get_retention_rate(self, period: int) -> float:
        """Get retention rate for a given period."""
        if self.retention_curves is None or len(self.retention_curves) == 0:
            # Default decay curve
            return np.exp(-0.1 * period)

        # Find retention rate for period
        rate_row = self.retention_curves[self.retention_curves['period'] == period]

        if len(rate_row) > 0:
            return rate_row['retention_rate'].values[0]
        else:
            # Extrapolate using last known rate
            last_period = self.retention_curves['period'].max()
            last_rate = self.retention_curves[self.retention_curves['period'] == last_period]['retention_rate'].values[0]

            # Apply decay
            decay_rate = 0.95
            periods_beyond = period - last_period
            return last_rate * (decay_rate ** periods_beyond)

    def _get_revenue_per_customer(self, period: int) -> float:
        """Get revenue per customer for a given period."""
        if self.revenue_per_cohort is None or len(self.revenue_per_cohort) == 0:
            # Default constant revenue
            return 100.0

        # Find revenue for period
        revenue_row = self.revenue_per_cohort[self.revenue_per_cohort['period'] == period]

        if len(revenue_row) > 0:
            return revenue_row['revenue_per_customer'].values[0]
        else:
            # Use last known value
            return self.revenue_per_cohort['revenue_per_customer'].iloc[-1]

    def get_retention_matrix(self) -> pd.DataFrame:
        """
        Get retention matrix showing retention rates by cohort age.

        Returns:
            DataFrame with retention matrix
        """
        return self.retention_curves

    def get_cohort_revenue_matrix(self) -> pd.DataFrame:
        """
        Get revenue matrix showing revenue per customer by cohort age.

        Returns:
            DataFrame with revenue matrix
        """
        return self.revenue_per_cohort


class SurvivalModel(BaseModel):
    """
    Survival analysis model for customer lifetime and churn prediction.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.survival_function = None
        self.median_lifetime = None

    def fit(
        self,
        data: pd.DataFrame,
        duration_column: str,
        event_column: str,
        **kwargs
    ) -> 'SurvivalModel':
        """
        Train survival model.

        Args:
            data: Customer data
            duration_column: Column for customer lifetime/tenure
            event_column: Column for event indicator (1=churned, 0=active)
            **kwargs: Additional parameters

        Returns:
            Self
        """
        try:
            from lifelines import KaplanMeierFitter
        except ImportError:
            raise ImportError("lifelines is required. Install with: pip install lifelines")

        logger.info("Training SurvivalModel")

        kmf = KaplanMeierFitter()
        kmf.fit(
            durations=data[duration_column],
            event_observed=data[event_column]
        )

        self.model = kmf
        self.survival_function = kmf.survival_function_
        self.median_lifetime = kmf.median_survival_time_

        self.is_trained = True

        logger.info(f"Survival model trained successfully")
        logger.info(f"Median customer lifetime: {self.median_lifetime:.2f} periods")

        return self

    def predict(self, periods: int, **kwargs) -> pd.DataFrame:
        """
        Predict survival probabilities.

        Args:
            periods: Number of periods to predict
            **kwargs: Additional parameters

        Returns:
            DataFrame with survival probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Get survival probabilities
        times = list(range(1, periods + 1))
        survival_probs = []

        for t in times:
            if t in self.survival_function.index:
                prob = self.survival_function.loc[t].values[0]
            else:
                # Interpolate
                prob = self.model.predict(t)

            survival_probs.append(prob)

        self.predictions = pd.DataFrame({
            'period': times,
            'survival_probability': survival_probs,
            'churn_probability': [1 - p for p in survival_probs]
        })

        return self.predictions
