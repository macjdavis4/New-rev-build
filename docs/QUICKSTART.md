# Quick Start Guide

## Installation

```bash
pip install revenue-builder
```

## Basic Usage

### 1. Simple Forecast

```python
from revenue_builder import RevenueModel

# Initialize and load data
model = RevenueModel(business_type='saas')
model.load_data('data.csv')

# Train and predict
model.train()
forecast = model.predict(periods=12)

# Export
model.export_report('forecast.xlsx')
```

### 2. Command Line

```bash
# Generate forecast
revenue-builder forecast data.csv -b saas -p 12 -o output.xlsx

# Generate sample data
revenue-builder generate-sample -b saas -o sample.csv

# Validate data
revenue-builder validate data.csv
```

### 3. REST API

Start server:
```bash
python -m revenue_builder.api.rest_api
```

Make requests:
```python
import requests

# Create model
requests.post('http://localhost:5000/api/v1/models', json={
    'model_id': 'my_model',
    'business_type': 'saas'
})

# Train and predict
# ... (see API documentation)
```

## Configuration

Create config file:
```bash
revenue-builder create-config config.yaml
```

Use with model:
```python
model = RevenueModel(config='config.yaml')
```

## Examples

See `notebooks/` directory for detailed examples:
- `saas_forecast_example.ipynb`: Complete SaaS forecasting workflow
- More examples coming soon!

## Next Steps

- Read the full documentation
- Explore business model templates
- Try different forecasting methods
- Customize configuration
