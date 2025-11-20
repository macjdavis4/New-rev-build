# API Documentation

## Python API

### RevenueModel Class

Main interface for revenue forecasting.

#### Methods

**__init__(business_type, config)**
- `business_type`: 'saas', 'ecommerce', 'marketplace', etc.
- `config`: Configuration file path or dict

**load_data(source, validate, preprocess)**
- Load and prepare data for forecasting
- Returns: DataFrame

**train(methods, target_column, auto_select)**
- Train forecasting models
- `methods`: List of model types
- Returns: Dict of trained models

**predict(periods, confidence_level, model)**
- Generate forecasts
- `periods`: Number of periods
- Returns: DataFrame with forecasts

**calculate_metrics()**
- Calculate business metrics
- Returns: Dict of metrics

**scenario_analysis(variables, monte_carlo, n_simulations)**
- Run scenario analysis
- Returns: Dict of scenarios

**export_report(path, include_visuals, include_commentary)**
- Export comprehensive report

## REST API

### Endpoints

**POST /api/v1/models**
Create a new model

Request:
```json
{
  "model_id": "unique_id",
  "business_type": "saas"
}
```

**POST /api/v1/models/{model_id}/data**
Load data into model

**POST /api/v1/models/{model_id}/train**
Train models

**POST /api/v1/models/{model_id}/predict**
Generate forecasts

**GET /api/v1/models/{model_id}/metrics**
Get metrics

**GET /api/v1/templates**
List available templates

See full API reference for details.
