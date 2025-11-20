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
            'homebuilder': BusinessModelTemplates.homebuilder_template(),
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
    def homebuilder_template() -> Dict[str, Any]:
        """
        Homebuilder business model template.

        For residential construction companies like Lennar, DR Horton, Toll Brothers.
        Key metrics: Closings, ASP, Backlog, Absorption Rate, Gross Margin
        """
        return {
            'business_type': 'homebuilder',
            'revenue_model': 'home_closings',
            'key_metrics': [
                # Volume Metrics
                'closings',  # Homes closed (delivered)
                'net_orders',  # New contracts signed
                'cancellations',  # Contract cancellations
                'cancellation_rate',  # Cancellation rate %
                'backlog',  # Homes under contract (not yet closed)
                'backlog_value',  # Total value of backlog ($)
                'starts',  # New home construction starts
                'specs',  # Spec homes (started before contract)
                'spec_ratio',  # Spec homes as % of inventory

                # Pricing Metrics
                'asp',  # Average Selling Price
                'base_price',  # Base home price
                'options_revenue',  # Revenue from upgrades/options
                'incentives',  # Buyer incentives and concessions
                'net_asp',  # ASP after incentives

                # Revenue Metrics
                'home_sales_revenue',  # Revenue from home closings
                'land_sales_revenue',  # Revenue from land/lot sales
                'total_revenue',  # Total revenue
                'revenue_per_closing',  # Average revenue per closing

                # Profitability Metrics
                'gross_margin',  # Gross profit margin %
                'gross_profit_per_closing',  # Average gross profit per home
                'cogs_per_closing',  # Cost of goods sold per home
                'land_cost_per_lot',  # Average land cost per lot
                'construction_cost_per_home',  # Direct construction costs

                # Operational Metrics
                'active_communities',  # Number of active selling communities
                'avg_communities',  # Average selling communities
                'closings_per_community',  # Closings per community
                'absorption_rate',  # Monthly sales pace per community
                'cycle_time',  # Days from start to close
                'inventory_months',  # Months of supply

                # Land/Lot Metrics
                'lots_owned',  # Owned lots
                'lots_controlled',  # Optioned lots
                'total_lots',  # Total lot position
                'years_supply',  # Years of lot supply
                'lot_acquisition_cost',  # Cost to acquire new lots

                # Market/External Factors
                'mortgage_rate',  # Average 30-year mortgage rate
                'interest_rate_impact',  # Impact of rate changes
                'market_home_prices',  # Local market prices
                'competitor_incentives',  # Competitor incentive levels
                'buyer_traffic',  # Prospective buyer visits

                # Financial Metrics
                'revenue_per_community',  # Revenue per active community
                'return_on_inventory',  # Return on inventory invested
                'inventory_turnover',  # Inventory turns per year
                'days_to_sell',  # Average days to sell from listing
            ],
            'required_columns': [
                'date',
                'closings',  # Number of homes closed
                'asp',  # Average selling price
                'net_orders',  # Net new orders
                'backlog',  # Backlog units
                'starts',  # New starts
                'active_communities',  # Active selling communities
                'gross_margin',  # Gross margin %
            ],
            'optional_columns': [
                'incentives',  # Incentive amounts or %
                'cancellation_rate',  # Cancellation rate
                'mortgage_rate',  # Current mortgage rates
                'options_revenue',  # Upgrade/options revenue
                'specs',  # Spec inventory
                'lots_owned',  # Owned lot inventory
                'cycle_time',  # Build cycle time in days
                'land_cost_per_lot',  # Land cost per lot
                'construction_cost_per_home',  # Direct costs
            ],
            'recommended_models': [
                'unit_economics',  # Closings × ASP
                'customer_based',  # Orders → Backlog → Closings funnel
                'prophet',  # Seasonal patterns
                'xgboost',  # Factor-based forecasting
                'ensemble',  # Combine multiple approaches
            ],
            'forecast_components': {
                'closings': 'Number of home deliveries',
                'asp': 'Average selling price',
                'absorption': 'Sales pace per community',
                'communities': 'Active community count',
                'backlog_conversion': 'Backlog to closings',
                'incentives': 'Incentive levels',
                'margin': 'Gross margin percentage',
            },
            'seasonality': 'high',  # Strong seasonal patterns in homebuilding
            'growth_drivers': [
                'community_openings',  # New community additions
                'absorption_rate_improvement',  # Faster sales pace
                'asp_growth',  # Price appreciation
                'spec_strategy',  # Spec vs pre-sold mix
                'incentive_optimization',  # Managing incentives
                'cycle_time_reduction',  # Faster builds
                'lot_acquisition',  # Land pipeline
                'market_share_gain',  # Taking share from competitors
                'margin_expansion',  # Cost efficiency
            ],
            'external_factors': [
                'mortgage_rates',  # 30-year mortgage rates
                'employment',  # Local employment levels
                'household_formation',  # Demographics
                'existing_home_inventory',  # Competition from resale market
                'building_material_costs',  # Input cost inflation
                'labor_availability',  # Construction labor supply
                'permit_approval_time',  # Regulatory timeline
                'land_availability',  # Developable land supply
            ],
            'key_ratios': [
                'backlog_to_closings',  # Backlog coverage (months)
                'net_orders_to_closings',  # Order-to-closing ratio
                'specs_to_total_starts',  # Spec strategy
                'incentives_to_asp',  # Incentive level as % of price
                'closings_to_starts',  # Build-to-close conversion
                'lots_to_annual_closings',  # Land supply (years)
            ],
            'forecast_methodology': {
                'bottom_up': 'Communities × Absorption Rate × ASP',
                'backlog_based': 'Existing Backlog + New Orders - Cancellations',
                'capacity_based': 'Active Communities × Capacity per Community',
                'cohort_based': 'Track cohorts from order to closing',
            }
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
        elif business_type == 'homebuilder':
            data = BusinessModelTemplates._generate_homebuilder_data(dates)
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

    @staticmethod
    def _generate_homebuilder_data(dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Generate sample homebuilder data."""
        periods = len(dates)

        # Initialize baseline values
        base_closings_per_community = 3.5  # Monthly absorption rate
        base_communities = 25
        base_asp = 425000
        base_mortgage_rate = 3.5
        base_incentive_pct = 0.02

        data = []
        backlog = 250  # Starting backlog

        for i, date in enumerate(dates):
            # Seasonal patterns (stronger in spring/summer)
            month = date.month
            seasonal_factor = 1.0 + 0.25 * np.sin(2 * np.pi * (month - 3) / 12)

            # Simulate mortgage rate changes (started low, increased 2022-2023)
            if i < 12:  # 2022 - low rates
                mortgage_rate = base_mortgage_rate + np.random.normal(0, 0.1)
            elif i < 24:  # 2023 - rising rates
                mortgage_rate = base_mortgage_rate + 3.0 + np.random.normal(0, 0.2)
            else:  # 2024+ - elevated rates
                mortgage_rate = base_mortgage_rate + 3.5 + np.random.normal(0, 0.15)

            # Interest rate impact on demand (higher rates = lower demand)
            rate_impact = max(0.5, 1.0 - (mortgage_rate - base_mortgage_rate) * 0.08)

            # Active communities (gradual expansion)
            active_communities = int(base_communities * (1 + i * 0.015))

            # Absorption rate (sales per community per month)
            base_absorption = base_closings_per_community * seasonal_factor * rate_impact
            absorption_rate = max(1.5, base_absorption + np.random.normal(0, 0.3))

            # Net orders (new contracts)
            gross_orders = int(active_communities * absorption_rate)
            cancellation_rate = 0.08 + (mortgage_rate - base_mortgage_rate) * 0.02  # Higher rates = more cancellations
            cancellations = int(gross_orders * cancellation_rate)
            net_orders = gross_orders - cancellations

            # Update backlog
            backlog = backlog + net_orders

            # Closings (deliveries from backlog)
            # Assume 4-6 month cycle time
            closings = int(backlog * 0.20)  # 20% of backlog closes each month
            backlog = backlog - closings

            # Starts (new construction begins)
            # Balance between pre-sold and specs
            spec_ratio = 0.30  # 30% specs
            starts = int(closings * 1.1)  # Start slightly more than closing
            specs = int(starts * spec_ratio)

            # Pricing
            # ASP grows but slows with higher rates
            asp_growth = 0.003 * (1.0 - (mortgage_rate - base_mortgage_rate) * 0.05)
            asp = base_asp * (1 + asp_growth) ** i

            # Incentives increase with higher rates
            incentive_pct = base_incentive_pct + (mortgage_rate - base_mortgage_rate) * 0.005
            incentives = asp * incentive_pct
            net_asp = asp - incentives

            # Revenue
            home_sales_revenue = closings * net_asp

            # Options/upgrades revenue (15% of base)
            options_revenue = closings * (asp * 0.15)

            total_revenue = home_sales_revenue + options_revenue

            # Costs and margins
            # Base costs
            land_cost_per_lot = asp * 0.20  # Land typically 20% of price
            construction_cost = asp * 0.50  # Construction ~50% of price
            total_cost = land_cost_per_lot + construction_cost

            # Gross margin (compressed by incentives and rising costs)
            gross_profit = net_asp - total_cost
            gross_margin = gross_profit / net_asp if net_asp > 0 else 0.15
            gross_margin = max(0.10, min(0.25, gross_margin))  # Cap between 10-25%

            # Lot inventory
            lots_owned = int(active_communities * 50)  # ~50 lots per community
            years_supply = lots_owned / (closings * 12) if closings > 0 else 5.0

            # Backlog value
            backlog_value = backlog * asp

            data.append({
                'date': date,
                'closings': closings,
                'net_orders': net_orders,
                'gross_orders': gross_orders,
                'cancellations': cancellations,
                'cancellation_rate': cancellation_rate,
                'backlog': backlog,
                'backlog_value': backlog_value,
                'starts': starts,
                'specs': specs,
                'spec_ratio': spec_ratio,
                'asp': asp,
                'incentives': incentives,
                'incentive_pct': incentive_pct,
                'net_asp': net_asp,
                'options_revenue': options_revenue,
                'home_sales_revenue': home_sales_revenue,
                'total_revenue': total_revenue,
                'revenue': total_revenue,  # For compatibility
                'active_communities': active_communities,
                'absorption_rate': absorption_rate,
                'closings_per_community': closings / active_communities if active_communities > 0 else 0,
                'gross_margin': gross_margin,
                'gross_profit_per_closing': gross_profit,
                'land_cost_per_lot': land_cost_per_lot,
                'construction_cost_per_home': construction_cost,
                'lots_owned': lots_owned,
                'years_supply': years_supply,
                'mortgage_rate': mortgage_rate,
                'cycle_time': 150,  # ~5 months average
            })

        return pd.DataFrame(data)
