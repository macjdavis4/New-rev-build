"""
Metrics calculation engine for financial and business metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from ..utils.logger import setup_logger
from ..utils.helpers import safe_divide, calculate_cagr

logger = setup_logger(__name__)


class MetricsCalculator:
    """
    Calculate key financial and business metrics.
    """

    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Initialize MetricsCalculator.

        Args:
            data: Historical data
        """
        self.data = data
        self.metrics = {}

    def calculate_all_metrics(self, business_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate all relevant metrics for the business type.

        Args:
            business_type: Type of business

        Returns:
            Dictionary of calculated metrics
        """
        if self.data is None:
            raise ValueError("No data provided")

        logger.info(f"Calculating metrics for {business_type or 'general'} business")

        # Growth metrics
        self.metrics.update(self.calculate_growth_metrics())

        # Revenue metrics
        self.metrics.update(self.calculate_revenue_metrics())

        # Business-specific metrics
        if business_type == 'saas':
            self.metrics.update(self.calculate_saas_metrics())
        elif business_type == 'ecommerce':
            self.metrics.update(self.calculate_ecommerce_metrics())

        # Customer metrics
        self.metrics.update(self.calculate_customer_metrics())

        # Efficiency metrics
        self.metrics.update(self.calculate_efficiency_metrics())

        logger.info(f"Calculated {len(self.metrics)} metrics")

        return self.metrics

    def calculate_growth_metrics(self) -> Dict[str, float]:
        """Calculate growth-related metrics."""
        metrics = {}

        if 'revenue' in self.data.columns:
            revenue = self.data['revenue']

            # MoM growth
            mom_growth = revenue.pct_change().mean()
            metrics['mom_growth_rate'] = mom_growth

            # YoY growth (if enough data)
            if len(revenue) >= 12:
                yoy_growth = revenue.pct_change(periods=12).mean()
                metrics['yoy_growth_rate'] = yoy_growth

            # CAGR
            if len(revenue) >= 12:
                periods_years = len(revenue) / 12
                cagr = calculate_cagr(revenue.iloc[0], revenue.iloc[-1], periods_years)
                metrics['cagr'] = cagr

            # Latest growth rate
            if len(revenue) >= 2:
                metrics['latest_growth_rate'] = (revenue.iloc[-1] - revenue.iloc[-2]) / revenue.iloc[-2]

        return metrics

    def calculate_revenue_metrics(self) -> Dict[str, float]:
        """Calculate revenue-related metrics."""
        metrics = {}

        if 'revenue' in self.data.columns:
            revenue = self.data['revenue']

            metrics['total_revenue'] = revenue.sum()
            metrics['avg_revenue'] = revenue.mean()
            metrics['median_revenue'] = revenue.median()
            metrics['revenue_std'] = revenue.std()
            metrics['revenue_cv'] = safe_divide(revenue.std(), revenue.mean())

        return metrics

    def calculate_saas_metrics(self) -> Dict[str, Any]:
        """Calculate SaaS-specific metrics."""
        metrics = {}

        # MRR/ARR
        if 'mrr' in self.data.columns:
            mrr = self.data['mrr'].iloc[-1]
            metrics['current_mrr'] = mrr
            metrics['current_arr'] = mrr * 12

        # Churn rate
        if 'churn_rate' in self.data.columns:
            metrics['avg_churn_rate'] = self.data['churn_rate'].mean()

        # Retention rates
        if 'churned_customers' in self.data.columns and 'total_customers' in self.data.columns:
            churn_rate = safe_divide(
                self.data['churned_customers'],
                self.data['total_customers']
            ).mean()
            metrics['gross_retention_rate'] = 1 - churn_rate

        # Net retention
        if all(col in self.data.columns for col in ['expansion_mrr', 'contraction_mrr', 'churned_mrr']):
            starting_mrr = self.data['mrr'].shift(1)
            net_mrr_change = self.data['expansion_mrr'] - self.data['contraction_mrr'] - self.data['churned_mrr']
            net_retention = safe_divide(
                (starting_mrr + net_mrr_change),
                starting_mrr
            ).mean()
            metrics['net_retention_rate'] = net_retention

        # CAC and LTV
        if 'cac' in self.data.columns:
            metrics['avg_cac'] = self.data['cac'].mean()

        if 'arpu' in self.data.columns and 'churn_rate' in self.data.columns:
            arpu = self.data['arpu'].mean()
            churn = self.data['churn_rate'].mean()
            ltv = safe_divide(arpu, churn, default=0)
            metrics['ltv'] = ltv

            if 'cac' in self.data.columns:
                cac = self.data['cac'].mean()
                metrics['ltv_cac_ratio'] = safe_divide(ltv, cac, default=0)
                metrics['cac_payback_months'] = safe_divide(cac, arpu, default=0)

        # Magic Number
        if 'new_mrr' in self.data.columns and 'sales_marketing_spend' in self.data.columns:
            new_mrr = self.data['new_mrr']
            spend = self.data['sales_marketing_spend']
            magic_number = safe_divide(
                new_mrr.diff(),
                spend.shift(1)
            ).mean()
            metrics['magic_number'] = magic_number

        # Rule of 40
        if 'yoy_growth_rate' in metrics and 'gross_margin' in self.data.columns:
            growth_rate = metrics['yoy_growth_rate'] * 100
            margin = self.data['gross_margin'].mean() * 100
            metrics['rule_of_40'] = growth_rate + margin

        return metrics

    def calculate_ecommerce_metrics(self) -> Dict[str, Any]:
        """Calculate e-commerce specific metrics."""
        metrics = {}

        # AOV
        if 'revenue' in self.data.columns and 'orders' in self.data.columns:
            aov = safe_divide(self.data['revenue'], self.data['orders']).mean()
            metrics['avg_order_value'] = aov

        # Purchase frequency
        if 'orders' in self.data.columns and 'customers' in self.data.columns:
            freq = safe_divide(self.data['orders'], self.data['customers']).mean()
            metrics['purchase_frequency'] = freq

        # Repeat purchase rate
        if 'repeat_customers' in self.data.columns and 'customers' in self.data.columns:
            repeat_rate = safe_divide(
                self.data['repeat_customers'],
                self.data['customers']
            ).mean()
            metrics['repeat_purchase_rate'] = repeat_rate

        return metrics

    def calculate_customer_metrics(self) -> Dict[str, Any]:
        """Calculate customer-related metrics."""
        metrics = {}

        if 'total_customers' in self.data.columns:
            metrics['current_customers'] = self.data['total_customers'].iloc[-1]
            metrics['avg_customers'] = self.data['total_customers'].mean()

        if 'new_customers' in self.data.columns:
            metrics['avg_new_customers'] = self.data['new_customers'].mean()
            metrics['total_new_customers'] = self.data['new_customers'].sum()

        # Customer growth rate
        if 'total_customers' in self.data.columns:
            growth = self.data['total_customers'].pct_change().mean()
            metrics['customer_growth_rate'] = growth

        # ARPU
        if 'revenue' in self.data.columns and 'total_customers' in self.data.columns:
            arpu = safe_divide(self.data['revenue'], self.data['total_customers']).mean()
            metrics['arpu'] = arpu

        return metrics

    def calculate_efficiency_metrics(self) -> Dict[str, Any]:
        """Calculate efficiency metrics."""
        metrics = {}

        # Gross margin
        if 'revenue' in self.data.columns and 'cogs' in self.data.columns:
            gross_profit = self.data['revenue'] - self.data['cogs']
            gross_margin = safe_divide(gross_profit, self.data['revenue']).mean()
            metrics['gross_margin'] = gross_margin

        # Operating margin
        if all(col in self.data.columns for col in ['revenue', 'operating_expenses']):
            op_income = self.data['revenue'] - self.data['operating_expenses']
            op_margin = safe_divide(op_income, self.data['revenue']).mean()
            metrics['operating_margin'] = op_margin

        # Revenue per employee
        if 'revenue' in self.data.columns and 'employees' in self.data.columns:
            rev_per_emp = safe_divide(self.data['revenue'], self.data['employees']).mean()
            metrics['revenue_per_employee'] = rev_per_emp

        return metrics

    def calculate_metric(self, metric_name: str, **kwargs) -> float:
        """
        Calculate a specific metric.

        Args:
            metric_name: Name of metric to calculate
            **kwargs: Additional parameters

        Returns:
            Calculated metric value
        """
        if self.data is None:
            raise ValueError("No data provided")

        # Map metric names to calculation methods
        metric_functions = {
            'mrr': self._calc_mrr,
            'arr': self._calc_arr,
            'churn_rate': self._calc_churn_rate,
            'ltv': self._calc_ltv,
            'cac': self._calc_cac,
            'ltv_cac_ratio': self._calc_ltv_cac_ratio,
            'growth_rate': self._calc_growth_rate,
            'arpu': self._calc_arpu,
        }

        if metric_name in metric_functions:
            return metric_functions[metric_name](**kwargs)
        else:
            logger.warning(f"Unknown metric: {metric_name}")
            return 0.0

    def _calc_mrr(self) -> float:
        """Calculate Monthly Recurring Revenue."""
        if 'mrr' in self.data.columns:
            return self.data['mrr'].iloc[-1]
        elif 'revenue' in self.data.columns:
            return self.data['revenue'].iloc[-1]
        return 0.0

    def _calc_arr(self) -> float:
        """Calculate Annual Recurring Revenue."""
        return self._calc_mrr() * 12

    def _calc_churn_rate(self) -> float:
        """Calculate churn rate."""
        if 'churn_rate' in self.data.columns:
            return self.data['churn_rate'].mean()
        elif 'churned_customers' in self.data.columns and 'total_customers' in self.data.columns:
            return safe_divide(
                self.data['churned_customers'],
                self.data['total_customers']
            ).mean()
        return 0.0

    def _calc_ltv(self) -> float:
        """Calculate Customer Lifetime Value."""
        arpu = self._calc_arpu()
        churn = self._calc_churn_rate()
        return safe_divide(arpu, churn, default=0)

    def _calc_cac(self) -> float:
        """Calculate Customer Acquisition Cost."""
        if 'cac' in self.data.columns:
            return self.data['cac'].mean()
        return 0.0

    def _calc_ltv_cac_ratio(self) -> float:
        """Calculate LTV:CAC ratio."""
        ltv = self._calc_ltv()
        cac = self._calc_cac()
        return safe_divide(ltv, cac, default=0)

    def _calc_growth_rate(self) -> float:
        """Calculate growth rate."""
        if 'revenue' in self.data.columns:
            return self.data['revenue'].pct_change().mean()
        return 0.0

    def _calc_arpu(self) -> float:
        """Calculate Average Revenue Per User."""
        if 'arpu' in self.data.columns:
            return self.data['arpu'].mean()
        elif 'revenue' in self.data.columns and 'total_customers' in self.data.columns:
            return safe_divide(self.data['revenue'], self.data['total_customers']).mean()
        return 0.0

    def get_metrics_summary(self) -> pd.DataFrame:
        """
        Get a summary of all calculated metrics.

        Returns:
            DataFrame with metrics
        """
        if not self.metrics:
            self.calculate_all_metrics()

        summary = pd.DataFrame([
            {'metric': k, 'value': v}
            for k, v in self.metrics.items()
        ])

        return summary

    def export_metrics(self, path: str):
        """
        Export metrics to file.

        Args:
            path: Output file path
        """
        summary = self.get_metrics_summary()
        summary.to_csv(path, index=False)
        logger.info(f"Metrics exported to {path}")
