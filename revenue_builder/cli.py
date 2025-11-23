"""
Command-line interface for Revenue Builder.
"""

import click
import sys
from pathlib import Path
from .core.revenue_model import RevenueModel
from .business_models.templates import BusinessModelTemplates
from .utils.logger import setup_logger

logger = setup_logger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Revenue Builder - ML-Powered Revenue Forecasting System

    A comprehensive tool for building revenue forecasts using multiple
    forecasting methodologies and business model templates.
    """
    pass


@cli.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--business-type', '-b', type=click.Choice([
    'saas', 'ecommerce', 'marketplace', 'freemium', 'enterprise', 'usage_based', 'hybrid', 'homebuilder'
]), help='Type of business model')
@click.option('--periods', '-p', default=12, help='Number of periods to forecast')
@click.option('--models', '-m', multiple=True, help='Models to use (can specify multiple)')
@click.option('--output', '-o', default='forecast_output.xlsx', help='Output file path')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file')
@click.option('--scenarios/--no-scenarios', default=True, help='Generate scenario analysis')
def forecast(data_file, business_type, periods, models, output, config, scenarios):
    """
    Generate revenue forecasts from historical data.

    Example:
        revenue-builder forecast data.csv -b saas -p 36 -o forecast.xlsx
    """
    click.echo("=" * 70)
    click.echo("Revenue Builder - Forecast Generation")
    click.echo("=" * 70)
    click.echo()

    try:
        # Initialize model
        click.echo(f"Initializing {business_type or 'general'} revenue model...")
        model = RevenueModel(business_type=business_type, config=config)

        # Load data
        click.echo(f"Loading data from {data_file}...")
        model.load_data(data_file)

        click.echo(f"✓ Loaded {len(model.processed_data)} rows")
        click.echo()

        # Train models
        if models:
            methods = list(models)
            click.echo(f"Training models: {', '.join(methods)}...")
        else:
            click.echo("Auto-selecting and training models...")
            methods = None

        model.train(methods=methods)
        click.echo(f"✓ Trained {len(model.trained_models)} models")
        click.echo()

        # Generate forecast
        click.echo(f"Generating forecast for {periods} periods...")
        forecast = model.predict(periods=periods)
        click.echo(f"✓ Forecast generated")
        click.echo()

        # Calculate metrics
        click.echo("Calculating metrics...")
        metrics = model.calculate_metrics()
        click.echo(f"✓ Calculated {len(metrics)} metrics")
        click.echo()

        # Scenario analysis
        if scenarios:
            click.echo("Running scenario analysis...")
            model.scenario_analysis()
            click.echo("✓ Scenarios generated")
            click.echo()

        # Export report
        click.echo(f"Exporting report to {output}...")
        model.export_report(output)
        click.echo(f"✓ Report saved to {output}")
        click.echo()

        # Display summary
        click.echo("FORECAST SUMMARY")
        click.echo("-" * 70)

        if 'forecast' in forecast.columns:
            total = forecast['forecast'].sum()
            avg = forecast['forecast'].mean()
            click.echo(f"Total Forecasted Revenue: ${total:,.2f}")
            click.echo(f"Average Period Revenue: ${avg:,.2f}")

        if 'mom_growth_rate' in metrics:
            click.echo(f"Average Growth Rate: {metrics['mom_growth_rate']:.1%}")

        click.echo()
        click.echo("✓ Forecast complete!")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--business-type', '-b', required=True, type=click.Choice([
    'saas', 'ecommerce', 'marketplace', 'freemium', 'enterprise', 'usage_based', 'hybrid'
]), help='Type of business model')
@click.option('--periods', '-p', default=36, help='Number of periods')
@click.option('--output', '-o', default='sample_data.csv', help='Output file path')
def generate_sample(business_type, periods, output):
    """
    Generate sample data for testing.

    Example:
        revenue-builder generate-sample -b saas -p 36 -o saas_data.csv
    """
    click.echo(f"Generating sample {business_type} data...")

    try:
        data = BusinessModelTemplates.generate_sample_data(
            business_type=business_type,
            periods=periods
        )

        data.to_csv(output, index=False)

        click.echo(f"✓ Generated {len(data)} rows of sample data")
        click.echo(f"✓ Saved to {output}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('data_file', type=click.Path(exists=True))
def validate(data_file):
    """
    Validate data quality and structure.

    Example:
        revenue-builder validate data.csv
    """
    click.echo("Validating data...")

    try:
        from .data.ingestion import DataIngestion
        from .data.validator import DataValidator

        # Load data
        ingestion = DataIngestion()
        data = ingestion.load_data(data_file)

        # Validate
        validator = DataValidator()
        is_valid, results = validator.validate(data)

        # Display report
        click.echo()
        click.echo(validator.get_validation_report())

        if is_valid:
            click.echo()
            click.echo("✓ Data validation passed")
        else:
            click.echo()
            click.echo("✗ Data validation found issues")
            sys.exit(1)

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_models():
    """
    List all available forecasting models.
    """
    from .models.model_factory import ModelFactory

    click.echo("Available Forecasting Models:")
    click.echo("=" * 70)
    click.echo()

    for category, models in ModelFactory.MODEL_CATEGORIES.items():
        click.echo(f"{category.upper().replace('_', ' ')}:")

        for model in models:
            click.echo(f"  • {model}")

        click.echo()


@cli.command()
@click.option('--business-type', '-b', type=click.Choice([
    'saas', 'ecommerce', 'marketplace', 'freemium', 'enterprise', 'usage_based', 'hybrid', 'homebuilder'
]), help='Type of business model')
def show_template(business_type):
    """
    Show business model template details.

    Example:
        revenue-builder show-template -b saas
    """
    if not business_type:
        click.echo("Available Business Model Templates:")
        click.echo("=" * 70)
        click.echo("  • saas")
        click.echo("  • ecommerce")
        click.echo("  • marketplace")
        click.echo("  • freemium")
        click.echo("  • enterprise")
        click.echo("  • usage_based")
        click.echo("  • hybrid")
        click.echo("  • homebuilder")
        return

    try:
        template = BusinessModelTemplates.get_template(business_type)

        click.echo(f"{business_type.upper()} Business Model Template")
        click.echo("=" * 70)
        click.echo()

        click.echo(f"Revenue Model: {template['revenue_model']}")
        click.echo()

        click.echo("Key Metrics:")
        for metric in template['key_metrics']:
            click.echo(f"  • {metric}")

        click.echo()

        click.echo("Required Data Columns:")
        for col in template['required_columns']:
            click.echo(f"  • {col}")

        click.echo()

        click.echo("Recommended Models:")
        for model in template['recommended_models']:
            click.echo(f"  • {model}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('config_file', type=click.Path())
def create_config(config_file):
    """
    Create a default configuration file.

    Example:
        revenue-builder create-config config.yaml
    """
    from .core.config import Config

    try:
        config = Config()
        config.save(config_file)

        click.echo(f"✓ Created default configuration file: {config_file}")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
