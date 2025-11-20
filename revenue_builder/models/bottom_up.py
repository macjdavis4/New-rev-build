"""
Bottom-up forecasting models (unit economics, customer-based).
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from .base_model import BaseModel
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class UnitEconomicsModel(BaseModel):
    """
    Unit economics model: Revenue = Quantity × Price

    Forecasts revenue based on quantity and price projections.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.quantity_growth_rate = None
        self.price_growth_rate = None
        self.historical_data = None

    def fit(
        self,
        data: pd.DataFrame,
        quantity_column: str,
        price_column: str,
        **kwargs
    ) -> 'UnitEconomicsModel':
        """
        Train the unit economics model.

        Args:
            data: Historical data
            quantity_column: Column name for quantity/units
            price_column: Column name for price/ASP
            **kwargs: Additional parameters

        Returns:
            Self
        """
        logger.info("Training UnitEconomicsModel")

        self.historical_data = data.copy()

        # Calculate historical growth rates
        self.quantity_growth_rate = data[quantity_column].pct_change().mean()
        self.price_growth_rate = data[price_column].pct_change().mean()

        # Calculate revenue if not present
        if 'revenue' not in data.columns:
            data['revenue'] = data[quantity_column] * data[price_column]

        self.is_trained = True

        logger.info(f"Quantity growth rate: {self.quantity_growth_rate:.2%}")
        logger.info(f"Price growth rate: {self.price_growth_rate:.2%}")

        return self

    def predict(
        self,
        periods: int,
        quantity_growth: Optional[float] = None,
        price_growth: Optional[float] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate revenue forecasts.

        Args:
            periods: Number of periods to forecast
            quantity_growth: Override quantity growth rate
            price_growth: Override price growth rate
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Use provided growth rates or default to historical
        qty_growth = quantity_growth if quantity_growth is not None else self.quantity_growth_rate
        price_growth = price_growth if price_growth is not None else self.price_growth_rate

        # Get last values
        last_quantity = self.historical_data.iloc[-1]['quantity'] if 'quantity' in self.historical_data.columns else 1000
        last_price = self.historical_data.iloc[-1]['price'] if 'price' in self.historical_data.columns else 100

        # Generate forecasts
        forecasts = []
        for i in range(1, periods + 1):
            forecasted_quantity = last_quantity * ((1 + qty_growth) ** i)
            forecasted_price = last_price * ((1 + price_growth) ** i)
            forecasted_revenue = forecasted_quantity * forecasted_price

            forecasts.append({
                'period': i,
                'quantity': forecasted_quantity,
                'price': forecasted_price,
                'revenue': forecasted_revenue
            })

        self.predictions = pd.DataFrame(forecasts)

        return self.predictions


class CustomerBasedModel(BaseModel):
    """
    Customer-based model: Revenue = New Customers + Retained Customers

    Forecasts revenue based on customer acquisition and retention.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.avg_new_customers = None
        self.retention_rate = None
        self.arpu = None
        self.historical_data = None

    def fit(
        self,
        data: pd.DataFrame,
        new_customers_column: str,
        churn_rate_column: Optional[str] = None,
        arpu_column: Optional[str] = None,
        **kwargs
    ) -> 'CustomerBasedModel':
        """
        Train the customer-based model.

        Args:
            data: Historical data
            new_customers_column: Column name for new customers per period
            churn_rate_column: Column name for churn rate (optional)
            arpu_column: Column name for ARPU (optional)
            **kwargs: Additional parameters

        Returns:
            Self
        """
        logger.info("Training CustomerBasedModel")

        self.historical_data = data.copy()

        # Calculate average new customers
        self.avg_new_customers = data[new_customers_column].mean()

        # Calculate retention/churn rate
        if churn_rate_column and churn_rate_column in data.columns:
            avg_churn = data[churn_rate_column].mean()
            self.retention_rate = 1 - avg_churn
        else:
            # Default retention rate
            self.retention_rate = 0.90

        # Calculate ARPU
        if arpu_column and arpu_column in data.columns:
            self.arpu = data[arpu_column].mean()
        else:
            # Estimate ARPU from revenue and customers
            if 'revenue' in data.columns and 'total_customers' in data.columns:
                self.arpu = (data['revenue'] / data['total_customers']).mean()
            else:
                self.arpu = 100  # Default

        self.is_trained = True

        logger.info(f"Average new customers: {self.avg_new_customers:.0f}")
        logger.info(f"Retention rate: {self.retention_rate:.2%}")
        logger.info(f"ARPU: ${self.arpu:.2f}")

        return self

    def predict(
        self,
        periods: int,
        new_customers_per_period: Optional[float] = None,
        retention_rate: Optional[float] = None,
        arpu: Optional[float] = None,
        starting_customers: Optional[int] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate revenue forecasts.

        Args:
            periods: Number of periods to forecast
            new_customers_per_period: Override new customers
            retention_rate: Override retention rate
            arpu: Override ARPU
            starting_customers: Starting customer base
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Use provided values or defaults
        new_cust = new_customers_per_period if new_customers_per_period is not None else self.avg_new_customers
        retention = retention_rate if retention_rate is not None else self.retention_rate
        arpu_val = arpu if arpu is not None else self.arpu

        # Starting customer base
        if starting_customers is None:
            if 'total_customers' in self.historical_data.columns:
                current_customers = self.historical_data['total_customers'].iloc[-1]
            else:
                current_customers = new_cust * 10  # Estimate

        else:
            current_customers = starting_customers

        # Generate forecasts
        forecasts = []
        for i in range(1, periods + 1):
            # Retained customers from previous period
            retained_customers = current_customers * retention

            # Add new customers
            current_customers = retained_customers + new_cust

            # Calculate revenue
            revenue = current_customers * arpu_val

            forecasts.append({
                'period': i,
                'new_customers': new_cust,
                'retained_customers': retained_customers,
                'total_customers': current_customers,
                'arpu': arpu_val,
                'revenue': revenue
            })

        self.predictions = pd.DataFrame(forecasts)

        return self.predictions


class SalesFunnelModel(BaseModel):
    """
    Sales funnel model with conversion rates at each stage.

    Revenue = Leads × Conversion Rates × Deal Size
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.conversion_rates = {}
        self.avg_deal_size = None
        self.avg_leads = None

    def fit(
        self,
        data: pd.DataFrame,
        funnel_stages: Dict[str, str],
        deal_size_column: str,
        **kwargs
    ) -> 'SalesFunnelModel':
        """
        Train the sales funnel model.

        Args:
            data: Historical data
            funnel_stages: Dict mapping stage names to column names
            deal_size_column: Column name for deal size
            **kwargs: Additional parameters

        Returns:
            Self
        """
        logger.info("Training SalesFunnelModel")

        # Calculate conversion rates between stages
        stage_names = list(funnel_stages.keys())

        for i in range(len(stage_names) - 1):
            current_stage = funnel_stages[stage_names[i]]
            next_stage = funnel_stages[stage_names[i + 1]]

            if current_stage in data.columns and next_stage in data.columns:
                conversion = (data[next_stage] / data[current_stage]).mean()
                self.conversion_rates[f"{stage_names[i]}_to_{stage_names[i+1]}"] = conversion

        # Calculate average deal size
        if deal_size_column in data.columns:
            self.avg_deal_size = data[deal_size_column].mean()

        # Calculate average leads
        first_stage = funnel_stages[stage_names[0]]
        if first_stage in data.columns:
            self.avg_leads = data[first_stage].mean()

        self.is_trained = True

        logger.info(f"Conversion rates: {self.conversion_rates}")
        logger.info(f"Average deal size: ${self.avg_deal_size:.2f}")

        return self

    def predict(
        self,
        periods: int,
        leads_per_period: Optional[float] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate revenue forecasts.

        Args:
            periods: Number of periods to forecast
            leads_per_period: Override leads per period
            **kwargs: Additional parameters

        Returns:
            DataFrame with forecasts
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        leads = leads_per_period if leads_per_period is not None else self.avg_leads

        # Calculate end-to-end conversion rate
        total_conversion = 1.0
        for rate in self.conversion_rates.values():
            total_conversion *= rate

        # Calculate deals closed
        deals_closed = leads * total_conversion

        # Calculate revenue
        revenue_per_period = deals_closed * self.avg_deal_size

        # Generate forecasts
        forecasts = []
        for i in range(1, periods + 1):
            forecasts.append({
                'period': i,
                'leads': leads,
                'deals_closed': deals_closed,
                'conversion_rate': total_conversion,
                'avg_deal_size': self.avg_deal_size,
                'revenue': revenue_per_period
            })

        self.predictions = pd.DataFrame(forecasts)

        return self.predictions
