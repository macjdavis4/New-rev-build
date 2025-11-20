"""
Business model templates for different industries and revenue models.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BusinessModelTemplates:
    """
    Pre-configured templates for common business models.
    """

    @staticmethod
    def get_template(business_type: str) -> Dict[str, Any]:
        """
        Get a business model template.

        Args:
            business_type: Type of business model

        Returns:
            Template configuration dictionary
        """
        templates = {
            'saas': BusinessModelTemplates.saas_template(),
            'ecommerce': BusinessModelTemplates.ecommerce_template(),
            'marketplace': BusinessModelTemplates.marketplace_template(),
            'freemium': BusinessModelTemplates.freemium_template(),
            'enterprise': BusinessModelTemplates.enterprise_b2b_template(),
            'usage_based': BusinessModelTemplates.usage_based_template(),
            'hybrid': BusinessModelTemplates.hybrid_template(),
        }

        if business_type not in templates:
            raise ValueError(
                f"Unknown business type: {business_type}. "
                f"Available: {list(templates.keys())}"
            )

        logger.info(f"Retrieved template for {business_type} business model")

        return templates[business_type]

    @staticmethod
    def saas_template() -> Dict[str, Any]:
        """
        SaaS/Subscription business model template.

        Key metrics: MRR, ARR, Churn, Expansion Revenue
        """
        return {
            'business_type': 'saas',
            'revenue_model': 'subscription',
            'key_metrics': [
                'mrr',  # Monthly Recurring Revenue
                'arr',  # Annual Recurring Revenue
                'new_mrr',  # New MRR from new customers
                'expansion_mrr',  # MRR from upgrades/expansions
                'contraction_mrr',  # MRR from downgrades
                'churned_mrr',  # MRR from churned customers
                'net_mrr_growth',  # Net MRR growth
                'churn_rate',  # Customer churn rate
                'revenue_churn_rate',  # Revenue churn rate
                'net_retention_rate',  # Net revenue retention
                'gross_retention_rate',  # Gross revenue retention
                'cac',  # Customer Acquisition Cost
                'ltv',  # Customer Lifetime Value
                'ltv_cac_ratio',  # LTV:CAC ratio
                'cac_payback_months',  # CAC payback period
                'arpu',  # Average Revenue Per User
                'magic_number',  # Sales efficiency
                'rule_of_40',  # Growth + Margin
            ],
            'required_columns': [
                'date',
                'new_customers',
                'churned_customers',
                'total_customers',
                'mrr',
                'cac',
            ],
            'recommended_models': [
                'customer_based',
                'cohort',
                'prophet',
                'xgboost',
            ],
            'forecast_components': {
                'new_mrr': 'New customer MRR',
                'expansion': 'Expansion from existing customers',
                'churn': 'Revenue lost to churn',
            },
            'seasonality': 'low',  # SaaS typically has low seasonality
            'growth_drivers': [
                'new_customer_acquisition',
                'expansion_upsells',
                'churn_reduction',
                'pricing_changes',
            ]
        }

    @staticmethod
    def ecommerce_template() -> Dict[str, Any]:
        """
        E-commerce business model template.

        Key metrics: GMV, AOV, Repeat Purchase Rate
        """
        return {
            'business_type': 'ecommerce',
            'revenue_model': 'transaction',
            'key_metrics': [
                'gmv',  # Gross Merchandise Value
                'revenue',  # Net revenue
                'orders',  # Number of orders
                'aov',  # Average Order Value
                'unique_customers',  # Unique customers
                'new_customers',  # New customers
                'repeat_customers',  # Repeat customers
                'repeat_purchase_rate',  # % customers who repurchase
                'purchase_frequency',  # Orders per customer
                'cac',  # Customer Acquisition Cost
                'ltv',  # Customer Lifetime Value
                'gross_margin',  # Gross margin %
                'conversion_rate',  # Visitor to purchase conversion
                'cart_abandonment_rate',  # Cart abandonment %
            ],
            'required_columns': [
                'date',
                'orders',
                'revenue',
                'customers',
                'aov',
            ],
            'recommended_models': [
                'unit_economics',
                'cohort',
                'prophet',
                'lstm',
            ],
            'forecast_components': {
                'orders': 'Number of orders',
                'aov': 'Average order value',
                'conversion': 'Conversion rate',
            },
            'seasonality': 'high',  # E-commerce often has strong seasonality
            'growth_drivers': [
                'traffic_growth',
                'conversion_optimization',
                'aov_increase',
                'repeat_purchase',
            ]
        }

    @staticmethod
    def marketplace_template() -> Dict[str, Any]:
        """
        Marketplace/Platform business model template.

        Key metrics: GMV, Take Rate, Both Sides of Market
        """
        return {
            'business_type': 'marketplace',
            'revenue_model': 'commission',
            'key_metrics': [
                'gmv',  # Gross Merchandise Value
                'revenue',  # Commission revenue
                'take_rate',  # Revenue / GMV
                'transactions',  # Number of transactions
                'buyers',  # Active buyers
                'sellers',  # Active sellers
                'new_buyers',  # New buyers
                'new_sellers',  # New sellers
                'repeat_transaction_rate',  # % buyers who return
                'avg_transaction_value',  # Average transaction size
                'buyer_retention',  # Buyer retention rate
                'seller_retention',  # Seller retention rate
                'liquidity',  # Supply-demand balance
            ],
            'required_columns': [
                'date',
                'gmv',
                'transactions',
                'buyers',
                'sellers',
                'take_rate',
            ],
            'recommended_models': [
                'unit_economics',
                'cohort',
                'xgboost',
                'prophet',
            ],
            'forecast_components': {
                'gmv': 'Gross merchandise value',
                'take_rate': 'Commission percentage',
                'buyer_side': 'Buyer activity',
                'seller_side': 'Seller activity',
            },
            'seasonality': 'medium',
            'growth_drivers': [
                'buyer_acquisition',
                'seller_acquisition',
                'transaction_frequency',
                'take_rate_optimization',
            ]
        }

    @staticmethod
    def freemium_template() -> Dict[str, Any]:
        """
        Freemium business model template.

        Key metrics: Conversion Rate, Free to Paid Funnel
        """
        return {
            'business_type': 'freemium',
            'revenue_model': 'freemium',
            'key_metrics': [
                'total_users',  # Total registered users
                'free_users',  # Free tier users
                'paid_users',  # Paid subscribers
                'conversion_rate',  # Free to paid conversion
                'time_to_convert',  # Days to convert to paid
                'mrr',  # Monthly Recurring Revenue
                'arpu_paid',  # ARPU for paid users
                'churn_rate_paid',  # Churn rate of paid users
                'activation_rate',  # % users who activate
                'engagement_score',  # User engagement metric
                'upgrade_rate',  # Free to paid upgrade rate
            ],
            'required_columns': [
                'date',
                'new_free_users',
                'free_users',
                'paid_users',
                'conversions',
                'mrr',
            ],
            'recommended_models': [
                'sales_funnel',
                'customer_based',
                'cohort',
                'xgboost',
            ],
            'forecast_components': {
                'user_acquisition': 'New free users',
                'conversion': 'Free to paid conversion',
                'retention': 'Paid user retention',
            },
            'seasonality': 'low',
            'growth_drivers': [
                'user_acquisition',
                'conversion_optimization',
                'feature_adoption',
                'paid_retention',
            ]
        }

    @staticmethod
    def enterprise_b2b_template() -> Dict[str, Any]:
        """
        Enterprise B2B business model template.

        Key metrics: Pipeline, Deal Size, Sales Cycle
        """
        return {
            'business_type': 'enterprise',
            'revenue_model': 'enterprise_b2b',
            'key_metrics': [
                'pipeline_value',  # Total pipeline value
                'qualified_leads',  # Sales qualified leads
                'opportunities',  # Active opportunities
                'closed_won',  # Closed won deals
                'closed_lost',  # Closed lost deals
                'win_rate',  # Win rate %
                'avg_deal_size',  # Average contract value (ACV)
                'sales_cycle_days',  # Average sales cycle length
                'pipeline_velocity',  # Pipeline velocity
                'quota_attainment',  # Sales quota attainment
                'expansion_rate',  # Account expansion rate
                'logo_retention',  # Customer logo retention
            ],
            'required_columns': [
                'date',
                'pipeline',
                'closed_won_deals',
                'revenue',
                'avg_deal_size',
            ],
            'recommended_models': [
                'sales_funnel',
                'customer_based',
                'prophet',
            ],
            'forecast_components': {
                'pipeline': 'Sales pipeline',
                'conversion': 'Win rate',
                'deal_size': 'Average contract value',
            },
            'seasonality': 'medium',  # Often quarterly patterns
            'growth_drivers': [
                'pipeline_generation',
                'win_rate_improvement',
                'deal_size_growth',
                'sales_cycle_reduction',
            ]
        }

    @staticmethod
    def usage_based_template() -> Dict[str, Any]:
        """
        Usage-based pricing model template.

        Key metrics: Usage Units, Price per Unit
        """
        return {
            'business_type': 'usage_based',
            'revenue_model': 'usage_based',
            'key_metrics': [
                'total_usage',  # Total usage units
                'active_customers',  # Active customers
                'usage_per_customer',  # Average usage per customer
                'price_per_unit',  # Price per usage unit
                'revenue',  # Total revenue
                'high_usage_customers',  # Power users
                'usage_growth_rate',  # Usage growth rate
                'customer_expansion',  # Usage expansion in cohorts
            ],
            'required_columns': [
                'date',
                'usage_units',
                'customers',
                'price_per_unit',
                'revenue',
            ],
            'recommended_models': [
                'unit_economics',
                'customer_based',
                'prophet',
                'xgboost',
            ],
            'forecast_components': {
                'usage': 'Total usage units',
                'price': 'Price per unit',
                'customers': 'Active customers',
            },
            'seasonality': 'medium',
            'growth_drivers': [
                'customer_acquisition',
                'usage_per_customer',
                'pricing_changes',
            ]
        }

    @staticmethod
    def hybrid_template() -> Dict[str, Any]:
        """
        Hybrid business model template.

        Combines multiple revenue streams.
        """
        return {
            'business_type': 'hybrid',
            'revenue_model': 'hybrid',
            'key_metrics': [
                'total_revenue',  # Total revenue
                'subscription_revenue',  # Subscription component
                'transaction_revenue',  # Transaction component
                'usage_revenue',  # Usage-based component
                'revenue_mix',  # Revenue composition
                'customers',  # Total customers
                'arpu',  # Average revenue per user
            ],
            'required_columns': [
                'date',
                'total_revenue',
                'customers',
            ],
            'recommended_models': [
                'customer_based',
                'xgboost',
                'prophet',
                'ensemble',
            ],
            'forecast_components': {
                'subscription': 'Recurring revenue',
                'transaction': 'Transaction revenue',
                'usage': 'Usage-based revenue',
            },
            'seasonality': 'medium',
            'growth_drivers': [
                'customer_growth',
                'revenue_per_customer',
                'revenue_mix_optimization',
            ]
        }

    @staticmethod
    def generate_sample_data(
        business_type: str,
        periods: int = 36,
        start_date: str = '2022-01-01'
    ) -> pd.DataFrame:
        """
        Generate sample data for a business model.

        Args:
            business_type: Type of business
            periods: Number of periods
            start_date: Start date

        Returns:
            DataFrame with sample data
        """
        template = BusinessModelTemplates.get_template(business_type)

        dates = pd.date_range(start=start_date, periods=periods, freq='M')

        if business_type == 'saas':
            data = BusinessModelTemplates._generate_saas_data(dates)
        elif business_type == 'ecommerce':
            data = BusinessModelTemplates._generate_ecommerce_data(dates)
        elif business_type == 'marketplace':
            data = BusinessModelTemplates._generate_marketplace_data(dates)
        else:
            # Generic data
            data = pd.DataFrame({
                'date': dates,
                'revenue': np.cumsum(np.random.normal(10000, 1000, periods)),
                'customers': np.cumsum(np.random.normal(100, 10, periods)),
            })

        logger.info(f"Generated sample data for {business_type}: {len(data)} periods")

        return data

    @staticmethod
    def _generate_saas_data(dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Generate sample SaaS data."""
        periods = len(dates)
        base_customers = 1000
        growth_rate = 0.05

        data = []
        total_customers = base_customers

        for i, date in enumerate(dates):
            new_customers = int(base_customers * growth_rate * (1 + i * 0.01))
            churn_rate = 0.03
            churned_customers = int(total_customers * churn_rate)

            total_customers = total_customers + new_customers - churned_customers

            arpu = 100 + i * 2  # Growing ARPU
            mrr = total_customers * arpu

            data.append({
                'date': date,
                'new_customers': new_customers,
                'churned_customers': churned_customers,
                'total_customers': total_customers,
                'arpu': arpu,
                'mrr': mrr,
                'churn_rate': churn_rate,
                'cac': 500,
            })

        return pd.DataFrame(data)

    @staticmethod
    def _generate_ecommerce_data(dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Generate sample e-commerce data."""
        periods = len(dates)

        data = []

        for i, date in enumerate(dates):
            # Add seasonality
            month = date.month
            seasonality = 1.0 + 0.3 * np.sin(2 * np.pi * month / 12)

            base_orders = 1000
            orders = int(base_orders * (1 + i * 0.03) * seasonality)

            aov = 150 + i * 2
            revenue = orders * aov

            data.append({
                'date': date,
                'orders': orders,
                'aov': aov,
                'revenue': revenue,
                'customers': int(orders * 0.8),  # Some repeat customers
            })

        return pd.DataFrame(data)

    @staticmethod
    def _generate_marketplace_data(dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Generate sample marketplace data."""
        periods = len(dates)

        data = []
        buyers = 5000
        sellers = 500

        for i, date in enumerate(dates):
            buyers += int(buyers * 0.04)
            sellers += int(sellers * 0.03)

            transactions = int(buyers * 0.3)  # 30% transaction rate
            avg_transaction = 200 + i * 3

            gmv = transactions * avg_transaction
            take_rate = 0.15
            revenue = gmv * take_rate

            data.append({
                'date': date,
                'gmv': gmv,
                'revenue': revenue,
                'transactions': transactions,
                'buyers': buyers,
                'sellers': sellers,
                'take_rate': take_rate,
            })

        return pd.DataFrame(data)
