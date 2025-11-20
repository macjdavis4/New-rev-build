"""
REST API for Revenue Builder.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from io import StringIO
from typing import Dict, Any

from ..core.revenue_model import RevenueModel
from ..business_models.templates import BusinessModelTemplates
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    CORS(app)

    # Store active models
    active_models = {}

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'service': 'revenue-builder'})

    @app.route('/api/v1/models', methods=['POST'])
    def create_model():
        """
        Create a new revenue model.

        Request body:
        {
            "model_id": "unique_id",
            "business_type": "saas",
            "config": {}
        }
        """
        try:
            data = request.get_json()

            model_id = data.get('model_id')
            business_type = data.get('business_type')
            config = data.get('config')

            if not model_id:
                return jsonify({'error': 'model_id is required'}), 400

            # Create model
            model = RevenueModel(business_type=business_type, config=config)
            active_models[model_id] = model

            logger.info(f"Created model: {model_id}")

            return jsonify({
                'model_id': model_id,
                'business_type': business_type,
                'status': 'created'
            })

        except Exception as e:
            logger.error(f"Error creating model: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/models/<model_id>/data', methods=['POST'])
    def load_data(model_id):
        """
        Load data into a model.

        Request body:
        {
            "data": [...],  # Array of records or CSV string
            "format": "json" or "csv"
        }
        """
        try:
            if model_id not in active_models:
                return jsonify({'error': 'Model not found'}), 404

            model = active_models[model_id]
            request_data = request.get_json()

            data_format = request_data.get('format', 'json')
            data_content = request_data.get('data')

            # Convert to DataFrame
            if data_format == 'json':
                df = pd.DataFrame(data_content)
            elif data_format == 'csv':
                df = pd.read_csv(StringIO(data_content))
            else:
                return jsonify({'error': 'Invalid format'}), 400

            # Load data
            model.load_data(df)

            logger.info(f"Loaded data for model: {model_id}")

            return jsonify({
                'model_id': model_id,
                'rows': len(df),
                'columns': list(df.columns),
                'status': 'data_loaded'
            })

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/models/<model_id>/train', methods=['POST'])
    def train_model(model_id):
        """
        Train forecasting models.

        Request body:
        {
            "methods": ["prophet", "xgboost"],
            "target_column": "revenue"
        }
        """
        try:
            if model_id not in active_models:
                return jsonify({'error': 'Model not found'}), 404

            model = active_models[model_id]
            request_data = request.get_json()

            methods = request_data.get('methods')
            target_column = request_data.get('target_column', 'revenue')

            # Train models
            trained = model.train(methods=methods, target_column=target_column)

            logger.info(f"Trained models for: {model_id}")

            return jsonify({
                'model_id': model_id,
                'trained_models': list(trained.keys()),
                'status': 'trained'
            })

        except Exception as e:
            logger.error(f"Error training models: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/models/<model_id>/predict', methods=['POST'])
    def predict(model_id):
        """
        Generate forecasts.

        Request body:
        {
            "periods": 12,
            "confidence_level": 0.95
        }
        """
        try:
            if model_id not in active_models:
                return jsonify({'error': 'Model not found'}), 404

            model = active_models[model_id]
            request_data = request.get_json()

            periods = request_data.get('periods', 12)
            confidence_level = request_data.get('confidence_level', 0.95)

            # Generate forecast
            forecast = model.predict(periods=periods, confidence_level=confidence_level)

            logger.info(f"Generated forecast for: {model_id}")

            return jsonify({
                'model_id': model_id,
                'forecast': forecast.to_dict(orient='records'),
                'status': 'forecast_generated'
            })

        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/models/<model_id>/metrics', methods=['GET'])
    def get_metrics(model_id):
        """Get calculated metrics."""
        try:
            if model_id not in active_models:
                return jsonify({'error': 'Model not found'}), 404

            model = active_models[model_id]

            # Calculate metrics
            metrics = model.calculate_metrics()

            return jsonify({
                'model_id': model_id,
                'metrics': metrics
            })

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/models/<model_id>/scenarios', methods=['POST'])
    def create_scenarios(model_id):
        """
        Run scenario analysis.

        Request body:
        {
            "variables": {"revenue": [0.8, 1.0, 1.2]},
            "monte_carlo": true,
            "n_simulations": 10000
        }
        """
        try:
            if model_id not in active_models:
                return jsonify({'error': 'Model not found'}), 404

            model = active_models[model_id]
            request_data = request.get_json()

            variables = request_data.get('variables')
            monte_carlo = request_data.get('monte_carlo', True)
            n_simulations = request_data.get('n_simulations', 10000)

            # Run scenario analysis
            scenarios = model.scenario_analysis(
                variables=variables,
                monte_carlo=monte_carlo,
                n_simulations=n_simulations
            )

            # Convert scenarios to JSON-serializable format
            scenario_results = {}
            for name, scenario_df in scenarios.items():
                if isinstance(scenario_df, pd.DataFrame):
                    scenario_results[name] = scenario_df.to_dict(orient='records')

            return jsonify({
                'model_id': model_id,
                'scenarios': scenario_results
            })

        except Exception as e:
            logger.error(f"Error creating scenarios: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/models/<model_id>', methods=['DELETE'])
    def delete_model(model_id):
        """Delete a model."""
        try:
            if model_id not in active_models:
                return jsonify({'error': 'Model not found'}), 404

            del active_models[model_id]

            logger.info(f"Deleted model: {model_id}")

            return jsonify({
                'model_id': model_id,
                'status': 'deleted'
            })

        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/v1/templates', methods=['GET'])
    def list_templates():
        """List available business model templates."""
        templates = [
            'saas', 'ecommerce', 'marketplace', 'freemium',
            'enterprise', 'usage_based', 'hybrid'
        ]

        return jsonify({'templates': templates})

    @app.route('/api/v1/templates/<business_type>', methods=['GET'])
    def get_template(business_type):
        """Get business model template details."""
        try:
            template = BusinessModelTemplates.get_template(business_type)

            return jsonify({
                'business_type': business_type,
                'template': template
            })

        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return jsonify({'error': str(e)}), 404

    @app.route('/api/v1/sample-data/<business_type>', methods=['GET'])
    def generate_sample(business_type):
        """Generate sample data for a business type."""
        try:
            periods = request.args.get('periods', 36, type=int)

            data = BusinessModelTemplates.generate_sample_data(
                business_type=business_type,
                periods=periods
            )

            return jsonify({
                'business_type': business_type,
                'data': data.to_dict(orient='records')
            })

        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            return jsonify({'error': str(e)}), 500

    return app


def run_api(host='0.0.0.0', port=5000, debug=False):
    """
    Run the API server.

    Args:
        host: Host address
        port: Port number
        debug: Debug mode
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_api(debug=True)
