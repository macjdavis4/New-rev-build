"""
Visualization and dashboard generation module.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import matplotlib.pyplot as plt
import seaborn as sns
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class Dashboard:
    """
    Creates visualizations and dashboards for revenue forecasting.
    """

    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Initialize Dashboard.

        Args:
            data: Historical or forecast data
        """
        self.data = data
        self.figures = {}

    def plot_revenue_forecast(
        self,
        historical: pd.DataFrame,
        forecast: pd.DataFrame,
        date_column: str = 'date',
        revenue_column: str = 'revenue',
        forecast_column: str = 'forecast',
        show_confidence: bool = True,
        title: str = 'Revenue Forecast'
    ) -> plt.Figure:
        """
        Plot revenue forecast with historical data.

        Args:
            historical: Historical data
            forecast: Forecast data
            date_column: Date column name
            revenue_column: Historical revenue column
            forecast_column: Forecast column
            show_confidence: Whether to show confidence intervals
            title: Plot title

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot historical
        if date_column in historical.columns:
            ax.plot(historical[date_column], historical[revenue_column],
                   label='Historical', color='#2E86AB', linewidth=2)
        else:
            ax.plot(historical.index, historical[revenue_column],
                   label='Historical', color='#2E86AB', linewidth=2)

        # Plot forecast
        if 'date' in forecast.columns:
            ax.plot(forecast['date'], forecast[forecast_column],
                   label='Forecast', color='#A23B72', linewidth=2, linestyle='--')

            # Confidence intervals
            if show_confidence and 'lower_bound' in forecast.columns and 'upper_bound' in forecast.columns:
                ax.fill_between(
                    forecast['date'],
                    forecast['lower_bound'],
                    forecast['upper_bound'],
                    alpha=0.3,
                    color='#A23B72',
                    label='95% Confidence Interval'
                )
        else:
            # Use period numbers
            forecast_index = range(len(historical), len(historical) + len(forecast))
            ax.plot(forecast_index, forecast[forecast_column],
                   label='Forecast', color='#A23B72', linewidth=2, linestyle='--')

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Revenue', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        self.figures['revenue_forecast'] = fig

        return fig

    def plot_revenue_waterfall(
        self,
        components: Dict[str, float],
        title: str = 'Revenue Waterfall'
    ) -> plt.Figure:
        """
        Create a waterfall chart showing revenue components.

        Args:
            components: Dictionary of component names to values
            title: Plot title

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        categories = list(components.keys())
        values = list(components.values())

        # Calculate cumulative values
        cumulative = np.cumsum([0] + values)

        # Plot bars
        colors = ['#2E86AB' if v >= 0 else '#E63946' for v in values]

        for i, (cat, val) in enumerate(zip(categories, values)):
            ax.bar(i, val, bottom=cumulative[i], color=colors[i], edgecolor='black', linewidth=1)

            # Add value labels
            y_pos = cumulative[i] + val / 2
            ax.text(i, y_pos, f'${val:,.0f}', ha='center', va='center',
                   fontweight='bold', fontsize=10)

        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_ylabel('Revenue', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        self.figures['waterfall'] = fig

        return fig

    def plot_cohort_heatmap(
        self,
        cohort_data: pd.DataFrame,
        title: str = 'Cohort Retention Heatmap'
    ) -> plt.Figure:
        """
        Create cohort retention heatmap.

        Args:
            cohort_data: Cohort analysis data
            title: Plot title

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        sns.heatmap(
            cohort_data,
            annot=True,
            fmt='.1%',
            cmap='RdYlGn',
            center=0.5,
            ax=ax,
            cbar_kws={'label': 'Retention Rate'}
        )

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Cohort Age (Months)', fontsize=12)
        ax.set_ylabel('Cohort', fontsize=12)

        plt.tight_layout()

        self.figures['cohort_heatmap'] = fig

        return fig

    def plot_metrics_dashboard(
        self,
        metrics: Dict[str, float],
        title: str = 'Key Metrics Dashboard'
    ) -> plt.Figure:
        """
        Create a dashboard with key metrics.

        Args:
            metrics: Dictionary of metrics
            title: Dashboard title

        Returns:
            Matplotlib figure
        """
        # Select key metrics to display
        key_metrics = [
            'current_mrr', 'current_arr', 'avg_churn_rate', 'ltv_cac_ratio',
            'mom_growth_rate', 'yoy_growth_rate', 'gross_margin', 'rule_of_40'
        ]

        display_metrics = {k: v for k, v in metrics.items() if k in key_metrics}

        if not display_metrics:
            # Use any available metrics
            display_metrics = dict(list(metrics.items())[:8])

        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()

        for i, (metric, value) in enumerate(display_metrics.items()):
            if i >= len(axes):
                break

            ax = axes[i]

            # Format value
            if 'rate' in metric or 'ratio' in metric or 'margin' in metric:
                display_value = f"{value:.1%}"
            elif value > 1000:
                display_value = f"${value:,.0f}"
            else:
                display_value = f"{value:.2f}"

            # Display metric
            ax.text(0.5, 0.5, display_value,
                   ha='center', va='center',
                   fontsize=24, fontweight='bold',
                   color='#2E86AB')

            ax.text(0.5, 0.2, metric.replace('_', ' ').title(),
                   ha='center', va='center',
                   fontsize=10)

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

        # Hide unused subplots
        for i in range(len(display_metrics), len(axes)):
            axes[i].axis('off')

        fig.suptitle(title, fontsize=16, fontweight='bold')

        plt.tight_layout()

        self.figures['metrics_dashboard'] = fig

        return fig

    def plot_scenario_comparison(
        self,
        scenarios: Dict[str, pd.DataFrame],
        revenue_column: str = 'revenue',
        title: str = 'Scenario Comparison'
    ) -> plt.Figure:
        """
        Compare multiple scenarios.

        Args:
            scenarios: Dictionary of scenario name to forecast
            revenue_column: Revenue column name
            title: Plot title

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

        for i, (name, forecast) in enumerate(scenarios.items()):
            if revenue_column in forecast.columns or 'forecast' in forecast.columns:
                col = revenue_column if revenue_column in forecast.columns else 'forecast'

                ax.plot(
                    range(len(forecast)),
                    forecast[col],
                    label=name.title(),
                    color=colors[i % len(colors)],
                    linewidth=2,
                    marker='o',
                    markersize=4
                )

        ax.set_xlabel('Period', fontsize=12)
        ax.set_ylabel('Revenue', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        self.figures['scenario_comparison'] = fig

        return fig

    def plot_monte_carlo_distribution(
        self,
        results: pd.DataFrame,
        value_column: str = 'total_revenue',
        title: str = 'Monte Carlo Simulation Results'
    ) -> plt.Figure:
        """
        Plot Monte Carlo simulation distribution.

        Args:
            results: Simulation results
            value_column: Column to plot
            title: Plot title

        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Histogram
        ax1.hist(results[value_column], bins=50, color='#2E86AB',
                alpha=0.7, edgecolor='black')

        # Add percentile lines
        percentiles = [10, 25, 50, 75, 90]
        colors_p = ['#E63946', '#F18F01', '#2E86AB', '#F18F01', '#E63946']

        for p, color in zip(percentiles, colors_p):
            value = results[value_column].quantile(p / 100)
            ax1.axvline(value, color=color, linestyle='--', linewidth=2,
                       label=f'P{p}: ${value:,.0f}')

        ax1.set_xlabel('Revenue', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Distribution', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(axis='y', alpha=0.3)

        # Cumulative distribution
        sorted_values = np.sort(results[value_column])
        cumulative = np.arange(1, len(sorted_values) + 1) / len(sorted_values)

        ax2.plot(sorted_values, cumulative, color='#2E86AB', linewidth=2)

        ax2.set_xlabel('Revenue', fontsize=12)
        ax2.set_ylabel('Cumulative Probability', fontsize=12)
        ax2.set_title('Cumulative Distribution', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        fig.suptitle(title, fontsize=14, fontweight='bold')

        plt.tight_layout()

        self.figures['monte_carlo'] = fig

        return fig

    def plot_feature_importance(
        self,
        importance: Dict[str, float],
        top_n: int = 10,
        title: str = 'Feature Importance'
    ) -> plt.Figure:
        """
        Plot feature importance.

        Args:
            importance: Dictionary of feature to importance score
            top_n: Number of top features to show
            title: Plot title

        Returns:
            Matplotlib figure
        """
        # Sort and select top N
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:top_n]
        features, scores = zip(*sorted_features)

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = plt.cm.viridis(np.linspace(0, 1, len(features)))

        ax.barh(range(len(features)), scores, color=colors, edgecolor='black', linewidth=1)

        ax.set_yticks(range(len(features)))
        ax.set_yticklabels(features)
        ax.set_xlabel('Importance Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        self.figures['feature_importance'] = fig

        return fig

    def save_all_figures(self, directory: str, format: str = 'png', dpi: int = 300):
        """
        Save all generated figures.

        Args:
            directory: Output directory
            format: Image format ('png', 'pdf', 'svg')
            dpi: Image resolution
        """
        from pathlib import Path

        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        for name, fig in self.figures.items():
            output_path = output_dir / f"{name}.{format}"
            fig.savefig(output_path, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"Saved figure: {output_path}")

        logger.info(f"Saved {len(self.figures)} figures to {directory}")

    def close_all_figures(self):
        """Close all figures to free memory."""
        plt.close('all')
        self.figures = {}
