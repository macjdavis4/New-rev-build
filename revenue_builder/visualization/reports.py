"""
Report generation module for creating comprehensive forecast reports.
"""

import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.logger import setup_logger
from ..utils.helpers import format_currency, format_percentage

logger = setup_logger(__name__)


class ReportGenerator:
    """
    Generates comprehensive forecast reports with commentary.
    """

    def __init__(self):
        """Initialize ReportGenerator."""
        pass

    def generate_executive_summary(
        self,
        forecast: pd.DataFrame,
        metrics: Dict[str, Any],
        business_type: Optional[str] = None
    ) -> str:
        """
        Generate executive summary with automated commentary.

        Args:
            forecast: Forecast data
            metrics: Calculated metrics
            business_type: Type of business

        Returns:
            Executive summary text
        """
        summary = []

        summary.append("=" * 70)
        summary.append("EXECUTIVE SUMMARY - REVENUE FORECAST")
        summary.append("=" * 70)
        summary.append("")

        # Overview
        summary.append("OVERVIEW")
        summary.append("-" * 70)

        if business_type:
            summary.append(f"Business Model: {business_type.upper()}")

        if 'forecast' in forecast.columns or 'revenue' in forecast.columns:
            rev_col = 'forecast' if 'forecast' in forecast.columns else 'revenue'
            total_forecast = forecast[rev_col].sum()
            avg_forecast = forecast[rev_col].mean()

            summary.append(f"Total Forecasted Revenue: {format_currency(total_forecast)}")
            summary.append(f"Average Monthly Revenue: {format_currency(avg_forecast)}")

        summary.append("")

        # Key metrics
        summary.append("KEY METRICS")
        summary.append("-" * 70)

        key_metric_names = [
            ('mom_growth_rate', 'Month-over-Month Growth Rate'),
            ('yoy_growth_rate', 'Year-over-Year Growth Rate'),
            ('cagr', 'Compound Annual Growth Rate'),
            ('ltv_cac_ratio', 'LTV:CAC Ratio'),
            ('gross_margin', 'Gross Margin'),
            ('rule_of_40', 'Rule of 40'),
        ]

        for metric_key, metric_label in key_metric_names:
            if metric_key in metrics:
                value = metrics[metric_key]

                if 'rate' in metric_key or 'ratio' in metric_key or 'margin' in metric_key or 'rule' in metric_key:
                    formatted = format_percentage(value)
                else:
                    formatted = f"{value:.2f}"

                summary.append(f"{metric_label}: {formatted}")

        summary.append("")

        # Growth trajectory
        summary.append("GROWTH TRAJECTORY")
        summary.append("-" * 70)

        if 'mom_growth_rate' in metrics:
            growth = metrics['mom_growth_rate']

            if growth > 0.10:
                trajectory = "strong growth trajectory"
            elif growth > 0.05:
                trajectory = "healthy growth trajectory"
            elif growth > 0:
                trajectory = "moderate growth trajectory"
            else:
                trajectory = "declining trend"

            summary.append(f"The business is showing a {trajectory} with an average")
            summary.append(f"month-over-month growth rate of {format_percentage(growth)}.")

        summary.append("")

        # Key insights
        summary.append("KEY INSIGHTS")
        summary.append("-" * 70)

        insights = self._generate_insights(metrics, business_type)

        for i, insight in enumerate(insights, 1):
            summary.append(f"{i}. {insight}")

        summary.append("")
        summary.append("=" * 70)

        return "\n".join(summary)

    def _generate_insights(
        self,
        metrics: Dict[str, Any],
        business_type: Optional[str]
    ) -> list:
        """Generate automated insights from metrics."""
        insights = []

        # LTV:CAC insights
        if 'ltv_cac_ratio' in metrics:
            ratio = metrics['ltv_cac_ratio']

            if ratio >= 3:
                insights.append(
                    f"Excellent unit economics with LTV:CAC ratio of {ratio:.1f}x, "
                    "indicating strong customer value relative to acquisition cost."
                )
            elif ratio >= 2:
                insights.append(
                    f"Healthy unit economics with LTV:CAC ratio of {ratio:.1f}x. "
                    "Consider optimizing to reach 3x for best-in-class performance."
                )
            elif ratio >= 1:
                insights.append(
                    f"Unit economics need improvement. Current LTV:CAC ratio of {ratio:.1f}x "
                    "suggests customer acquisition may not be efficient."
                )

        # Churn insights (SaaS)
        if 'avg_churn_rate' in metrics and business_type == 'saas':
            churn = metrics['avg_churn_rate']

            if churn <= 0.05:
                insights.append(
                    f"Best-in-class churn rate of {format_percentage(churn)} "
                    "indicates strong product-market fit and customer satisfaction."
                )
            elif churn <= 0.07:
                insights.append(
                    f"Churn rate of {format_percentage(churn)} is acceptable but "
                    "there's opportunity to improve retention further."
                )
            else:
                insights.append(
                    f"Churn rate of {format_percentage(churn)} is above industry benchmarks. "
                    "Focus on retention initiatives to improve unit economics."
                )

        # Growth rate insights
        if 'yoy_growth_rate' in metrics:
            yoy_growth = metrics['yoy_growth_rate']

            if yoy_growth > 1.0:
                insights.append(
                    f"Exceptional year-over-year growth of {format_percentage(yoy_growth)} "
                    "demonstrates strong market demand and execution."
                )
            elif yoy_growth > 0.5:
                insights.append(
                    f"Strong year-over-year growth of {format_percentage(yoy_growth)} "
                    "positions the business well for continued expansion."
                )

        # Rule of 40 (SaaS)
        if 'rule_of_40' in metrics and business_type == 'saas':
            rule = metrics['rule_of_40']

            if rule >= 40:
                insights.append(
                    f"Exceeding the Rule of 40 benchmark with a score of {rule:.0f}%, "
                    "indicating a healthy balance of growth and profitability."
                )
            else:
                insights.append(
                    f"Rule of 40 score of {rule:.0f}% is below benchmark. "
                    "Consider optimizing the balance between growth and profitability."
                )

        if not insights:
            insights.append("Comprehensive analysis of key metrics shows stable performance.")

        return insights

    def generate_assumptions_report(
        self,
        assumptions: Dict[str, Any]
    ) -> str:
        """
        Generate report documenting forecast assumptions.

        Args:
            assumptions: Dictionary of assumptions

        Returns:
            Assumptions report text
        """
        report = []

        report.append("=" * 70)
        report.append("FORECAST ASSUMPTIONS")
        report.append("=" * 70)
        report.append("")

        for category, values in assumptions.items():
            report.append(f"{category.upper()}")
            report.append("-" * 70)

            if isinstance(values, dict):
                for key, value in values.items():
                    formatted_key = key.replace('_', ' ').title()

                    if isinstance(value, float) and value < 1:
                        formatted_value = format_percentage(value)
                    elif isinstance(value, (int, float)):
                        formatted_value = f"{value:,.2f}"
                    else:
                        formatted_value = str(value)

                    report.append(f"  {formatted_key}: {formatted_value}")

            else:
                report.append(f"  {values}")

            report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def generate_model_performance_report(
        self,
        model_metrics: pd.DataFrame
    ) -> str:
        """
        Generate model performance comparison report.

        Args:
            model_metrics: DataFrame with model metrics

        Returns:
            Performance report text
        """
        report = []

        report.append("=" * 70)
        report.append("MODEL PERFORMANCE COMPARISON")
        report.append("=" * 70)
        report.append("")

        if model_metrics.empty:
            report.append("No model performance data available.")
            return "\n".join(report)

        # Sort by RMSE (lower is better)
        if 'rmse' in model_metrics.columns:
            sorted_models = model_metrics.sort_values('rmse')

            report.append("Models ranked by RMSE (lower is better):")
            report.append("-" * 70)

            for i, row in sorted_models.iterrows():
                model_name = row.get('model', 'Unknown')
                rmse = row.get('rmse', 0)
                mae = row.get('mae', 0)
                r2 = row.get('r2', 0)

                report.append(f"\n{model_name.upper()}")
                report.append(f"  RMSE: {rmse:,.2f}")
                report.append(f"  MAE: {mae:,.2f}")
                report.append(f"  R²: {r2:.4f}")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def export_full_report(
        self,
        output_path: str,
        forecast: pd.DataFrame,
        metrics: Dict[str, Any],
        scenarios: Optional[Dict[str, pd.DataFrame]] = None,
        model_performance: Optional[pd.DataFrame] = None,
        business_type: Optional[str] = None
    ):
        """
        Export comprehensive report to file.

        Args:
            output_path: Output file path
            forecast: Forecast data
            metrics: Metrics dictionary
            scenarios: Optional scenarios data
            model_performance: Optional model performance data
            business_type: Type of business
        """
        logger.info(f"Generating comprehensive report to {output_path}")

        path = Path(output_path)

        with open(path, 'w') as f:
            # Executive summary
            f.write(self.generate_executive_summary(forecast, metrics, business_type))
            f.write("\n\n")

            # Model performance
            if model_performance is not None and not model_performance.empty:
                f.write(self.generate_model_performance_report(model_performance))
                f.write("\n\n")

            # Forecast details
            f.write("=" * 70 + "\n")
            f.write("DETAILED FORECAST\n")
            f.write("=" * 70 + "\n\n")
            f.write(forecast.to_string())
            f.write("\n\n")

            # Scenarios
            if scenarios:
                f.write("=" * 70 + "\n")
                f.write("SCENARIO ANALYSIS\n")
                f.write("=" * 70 + "\n\n")

                for name, scenario_df in scenarios.items():
                    f.write(f"\n{name.upper()} SCENARIO\n")
                    f.write("-" * 70 + "\n")
                    f.write(scenario_df.head(10).to_string())
                    f.write("\n\n")

        logger.info(f"Report generated successfully: {output_path}")
