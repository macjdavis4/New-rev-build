"""
Scenario planning and sensitivity analysis module.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ScenarioPlanner:
    """
    Scenario planning, sensitivity analysis, and Monte Carlo simulation.
    """

    def __init__(self, base_forecast: pd.DataFrame, config: Optional[Dict] = None):
        """
        Initialize ScenarioPlanner.

        Args:
            base_forecast: Base case forecast
            config: Configuration dictionary
        """
        self.base_forecast = base_forecast
        self.config = config or {}
        self.scenarios = {}

    def create_scenarios(
        self,
        variables: Dict[str, List[float]],
        scenario_names: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Create multiple scenarios with different assumptions.

        Args:
            variables: Dictionary of variable names to list of values
            scenario_names: Names for scenarios (default: base, optimistic, pessimistic)

        Returns:
            Dictionary of scenario name to forecast DataFrame
        """
        logger.info(f"Creating scenarios with variables: {list(variables.keys())}")

        if scenario_names is None:
            # Default to base, optimistic, pessimistic
            scenario_names = ['base', 'optimistic', 'pessimistic']

        scenarios = {
            'base': self.base_forecast.copy()
        }

        # Create optimistic scenario (use max values)
        optimistic = self.base_forecast.copy()
        for var, values in variables.items():
            if var in optimistic.columns:
                adjustment_factor = max(values) / optimistic[var].mean() if optimistic[var].mean() != 0 else 1
                optimistic[var] = optimistic[var] * adjustment_factor

        scenarios['optimistic'] = optimistic

        # Create pessimistic scenario (use min values)
        pessimistic = self.base_forecast.copy()
        for var, values in variables.items():
            if var in pessimistic.columns:
                adjustment_factor = min(values) / pessimistic[var].mean() if pessimistic[var].mean() != 0 else 1
                pessimistic[var] = pessimistic[var] * adjustment_factor

        scenarios['pessimistic'] = pessimistic

        self.scenarios = scenarios

        logger.info(f"Created {len(scenarios)} scenarios")

        return scenarios

    def monte_carlo_simulation(
        self,
        n_simulations: int,
        variables: Dict[str, Tuple[float, float]],
        distribution: str = 'normal'
    ) -> pd.DataFrame:
        """
        Run Monte Carlo simulation.

        Args:
            n_simulations: Number of simulations to run
            variables: Dict of variable name to (mean, std) tuples
            distribution: Distribution type ('normal', 'uniform', 'triangular')

        Returns:
            DataFrame with simulation results
        """
        logger.info(f"Running Monte Carlo simulation with {n_simulations} iterations")

        results = []

        for i in range(n_simulations):
            simulation = self.base_forecast.copy()

            # Apply random variations to variables
            for var, (mean, std) in variables.items():
                if var in simulation.columns:
                    if distribution == 'normal':
                        factor = np.random.normal(mean, std, len(simulation))
                    elif distribution == 'uniform':
                        factor = np.random.uniform(mean - std, mean + std, len(simulation))
                    elif distribution == 'triangular':
                        factor = np.random.triangular(mean - std, mean, mean + std, len(simulation))
                    else:
                        factor = mean

                    simulation[var] = simulation[var] * factor

            # Calculate total revenue for this simulation
            if 'revenue' in simulation.columns:
                total_revenue = simulation['revenue'].sum()
            elif 'forecast' in simulation.columns:
                total_revenue = simulation['forecast'].sum()
            else:
                total_revenue = 0

            results.append({
                'simulation': i + 1,
                'total_revenue': total_revenue,
                'final_revenue': simulation[simulation.columns[-1]].iloc[-1] if len(simulation) > 0 else 0
            })

        results_df = pd.DataFrame(results)

        # Calculate statistics
        self._calculate_simulation_statistics(results_df)

        logger.info("Monte Carlo simulation completed")

        return results_df

    def _calculate_simulation_statistics(self, results: pd.DataFrame):
        """Calculate and log statistics from simulation results."""
        revenue_col = 'total_revenue' if 'total_revenue' in results.columns else results.columns[1]

        stats = {
            'mean': results[revenue_col].mean(),
            'median': results[revenue_col].median(),
            'std': results[revenue_col].std(),
            'min': results[revenue_col].min(),
            'max': results[revenue_col].max(),
            'p10': results[revenue_col].quantile(0.10),
            'p25': results[revenue_col].quantile(0.25),
            'p75': results[revenue_col].quantile(0.75),
            'p90': results[revenue_col].quantile(0.90),
        }

        logger.info(f"Simulation statistics: Mean={stats['mean']:.2f}, "
                   f"Median={stats['median']:.2f}, Std={stats['std']:.2f}")

    def sensitivity_analysis(
        self,
        variable: str,
        range_pct: float = 0.20,
        n_points: int = 10
    ) -> pd.DataFrame:
        """
        Perform sensitivity analysis on a variable.

        Args:
            variable: Variable to analyze
            range_pct: Range as percentage of base value (e.g., 0.20 for ±20%)
            n_points: Number of points to test

        Returns:
            DataFrame with sensitivity results
        """
        logger.info(f"Performing sensitivity analysis on {variable}")

        if variable not in self.base_forecast.columns:
            raise ValueError(f"Variable '{variable}' not found in forecast")

        base_value = self.base_forecast[variable].mean()

        # Create range of values
        min_val = base_value * (1 - range_pct)
        max_val = base_value * (1 + range_pct)
        test_values = np.linspace(min_val, max_val, n_points)

        results = []

        for test_val in test_values:
            # Create modified forecast
            modified = self.base_forecast.copy()
            adjustment_factor = test_val / base_value if base_value != 0 else 1
            modified[variable] = modified[variable] * adjustment_factor

            # Calculate resulting revenue
            if 'revenue' in modified.columns:
                total_revenue = modified['revenue'].sum()
            elif 'forecast' in modified.columns:
                total_revenue = modified['forecast'].sum()
            else:
                total_revenue = 0

            results.append({
                'variable': variable,
                'value': test_val,
                'pct_change': (test_val - base_value) / base_value,
                'total_revenue': total_revenue,
                'revenue_change_pct': (total_revenue - self.base_forecast.get('revenue', self.base_forecast.get('forecast', pd.Series([0]))).sum()) /
                                      self.base_forecast.get('revenue', self.base_forecast.get('forecast', pd.Series([1]))).sum()
            })

        results_df = pd.DataFrame(results)

        logger.info(f"Sensitivity analysis completed for {variable}")

        return results_df

    def what_if_analysis(
        self,
        changes: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Perform what-if analysis with specific changes.

        Args:
            changes: Dictionary of variable name to multiplier

        Returns:
            Modified forecast DataFrame
        """
        logger.info(f"Performing what-if analysis with changes: {changes}")

        modified = self.base_forecast.copy()

        for var, multiplier in changes.items():
            if var in modified.columns:
                modified[var] = modified[var] * multiplier
            else:
                logger.warning(f"Variable '{var}' not found in forecast")

        return modified

    def stress_test(
        self,
        scenarios: Dict[str, Dict[str, float]]
    ) -> Dict[str, pd.DataFrame]:
        """
        Perform stress testing with extreme scenarios.

        Args:
            scenarios: Dict of scenario name to variable changes

        Returns:
            Dictionary of scenario results
        """
        logger.info(f"Running stress tests: {list(scenarios.keys())}")

        stress_results = {}

        for scenario_name, changes in scenarios.items():
            stressed = self.what_if_analysis(changes)
            stress_results[scenario_name] = stressed

        return stress_results

    def confidence_intervals(
        self,
        confidence_levels: List[float] = [0.10, 0.25, 0.50, 0.75, 0.90]
    ) -> pd.DataFrame:
        """
        Calculate confidence intervals from Monte Carlo results.

        Args:
            confidence_levels: List of confidence levels

        Returns:
            DataFrame with confidence intervals
        """
        # Run Monte Carlo if not already done
        n_sims = self.config.get('monte_carlo_simulations', 10000)

        # Estimate variables and their standard deviations
        variables = {}
        for col in self.base_forecast.columns:
            if pd.api.types.is_numeric_dtype(self.base_forecast[col]):
                mean = self.base_forecast[col].mean()
                std = self.base_forecast[col].std() * 0.1  # 10% variation
                if not np.isnan(mean) and not np.isnan(std):
                    variables[col] = (1.0, 0.1)  # Mean multiplier, std multiplier

        mc_results = self.monte_carlo_simulation(n_sims, variables)

        # Calculate intervals
        intervals = []

        for level in confidence_levels:
            value = mc_results['total_revenue'].quantile(level)
            intervals.append({
                'confidence_level': level,
                'revenue': value
            })

        intervals_df = pd.DataFrame(intervals)

        logger.info(f"Calculated confidence intervals for {len(confidence_levels)} levels")

        return intervals_df

    def compare_scenarios(self) -> pd.DataFrame:
        """
        Compare all created scenarios.

        Returns:
            DataFrame with scenario comparison
        """
        if not self.scenarios:
            logger.warning("No scenarios to compare")
            return pd.DataFrame()

        comparison = []

        for name, forecast in self.scenarios.items():
            if 'revenue' in forecast.columns:
                total = forecast['revenue'].sum()
                avg = forecast['revenue'].mean()
            elif 'forecast' in forecast.columns:
                total = forecast['forecast'].sum()
                avg = forecast['forecast'].mean()
            else:
                total = 0
                avg = 0

            comparison.append({
                'scenario': name,
                'total_revenue': total,
                'avg_revenue': avg,
            })

        comparison_df = pd.DataFrame(comparison)

        logger.info(f"Compared {len(comparison)} scenarios")

        return comparison_df

    def get_scenario(self, name: str) -> pd.DataFrame:
        """
        Get a specific scenario.

        Args:
            name: Scenario name

        Returns:
            Scenario forecast DataFrame
        """
        if name not in self.scenarios:
            raise ValueError(f"Scenario '{name}' not found")

        return self.scenarios[name]
