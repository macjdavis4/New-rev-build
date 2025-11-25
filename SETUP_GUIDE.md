# Revenue Builder - Complete Setup Guide

## Step-by-Step Installation and First Run

This guide will walk you through installing Revenue Builder from scratch and running your first forecast.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Verify Installation](#verify-installation)
4. [Quick Test](#quick-test)
5. [Your First Forecast](#your-first-forecast)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

#### 1. Python (3.8 or higher)

**Check if Python is installed:**
```bash
python --version
# or
python3 --version
```

**If you don't have Python, install it:**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Mac**:
  ```bash
  brew install python@3.10
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update
  sudo apt install python3.10 python3-pip python3-venv
  ```

#### 2. pip (Python Package Manager)

**Check if pip is installed:**
```bash
pip --version
# or
pip3 --version
```

**If pip is not installed:**
```bash
python -m ensurepip --upgrade
```

---

## Installation

### Option 1: Install from Source (Recommended for Development)

This is the best option since you have the code repository.

#### Step 1: Navigate to the Project Directory

```bash
cd /path/to/New-rev-build
# Example: cd /home/user/New-rev-build
```

#### Step 2: Create a Virtual Environment (Recommended)

**Why?** Keeps dependencies isolated from other Python projects.

**Create virtual environment:**
```bash
python3 -m venv venv
```

**Activate virtual environment:**

- **Linux/Mac**:
  ```bash
  source venv/bin/activate
  ```

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

You should see `(venv)` in your terminal prompt.

#### Step 3: Upgrade pip and setuptools

```bash
pip install --upgrade pip setuptools wheel
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**This will take 5-10 minutes** as it downloads and installs all required packages:
- pandas, numpy, scikit-learn
- Prophet, statsmodels
- XGBoost, TensorFlow
- matplotlib, seaborn
- Flask, Click
- And more...

**If you encounter errors**, see the [Troubleshooting](#troubleshooting) section below.

#### Step 5: Install Revenue Builder in Development Mode

```bash
pip install -e .
```

The `-e` flag installs in "editable" mode, meaning changes to the code are immediately available.

---

### Option 2: Quick Install (If you just want to use it)

If you just want to use the package without modifying code:

```bash
cd /path/to/New-rev-build
pip install .
```

---

## Verify Installation

### Test 1: Check if package is installed

```bash
pip list | grep revenue-builder
```

You should see:
```
revenue-builder    1.0.0
```

### Test 2: Import in Python

```bash
python3 -c "from revenue_builder import RevenueModel; print('✓ Revenue Builder installed successfully!')"
```

If successful, you'll see:
```
✓ Revenue Builder installed successfully!
```

### Test 3: Check CLI

```bash
revenue-builder --help
```

You should see the help menu with available commands.

---

## Quick Test

### Generate and Forecast Sample Data

Let's run a complete test with sample homebuilder data:

#### Step 1: Generate Sample Data

```bash
# Create a test directory
mkdir -p ~/revenue_builder_test
cd ~/revenue_builder_test

# Generate sample homebuilder data
python3 << 'EOF'
from revenue_builder.business_models import BusinessModelTemplates
data = BusinessModelTemplates.generate_sample_data('homebuilder', periods=36)
data.to_csv('homebuilder_sample.csv', index=False)
print("✓ Sample data created: homebuilder_sample.csv")
print(f"  Rows: {len(data)}, Columns: {len(data.columns)}")
EOF
```

#### Step 2: Run Your First Forecast

```bash
python3 << 'EOF'
from revenue_builder import RevenueModel

print("Initializing homebuilder model...")
model = RevenueModel(business_type='homebuilder')

print("Loading data...")
model.load_data('homebuilder_sample.csv')

print("Training models...")
model.train(methods=['prophet'])  # Start with just Prophet for speed

print("Generating 12-month forecast...")
forecast = model.predict(periods=12)

print("\n" + "="*60)
print("FORECAST RESULTS")
print("="*60)
print(forecast[['period', 'forecast']].head(12))

print("\n✓ Forecast complete!")
print(f"  Total forecasted revenue: ${forecast['forecast'].sum():,.0f}")
EOF
```

**Expected output:**
```
Initializing homebuilder model...
Loading data...
Preprocessing data...
Training models...
Generating 12-month forecast...

============================================================
FORECAST RESULTS
============================================================
   period      forecast
0       1  93500000.00
1       2  94200000.00
2       3  95100000.00
...

✓ Forecast complete!
  Total forecasted revenue: $1,138,450,000
```

---

## Your First Forecast

Now let's do a complete workflow with all features:

### Full Example Script

Create a file called `my_first_forecast.py`:

```python
#!/usr/bin/env python3
"""
My First Revenue Builder Forecast
Complete example for homebuilders
"""

from revenue_builder import RevenueModel
from revenue_builder.business_models import BusinessModelTemplates

print("="*70)
print("REVENUE BUILDER - HOMEBUILDER FORECAST")
print("="*70)
print()

# Step 1: Generate sample data
print("Step 1: Generating sample data...")
data = BusinessModelTemplates.generate_sample_data(
    business_type='homebuilder',
    periods=36,  # 3 years of monthly data
    start_date='2022-01-01'
)
data.to_csv('homebuilder_data.csv', index=False)
print(f"✓ Generated {len(data)} months of data")
print(f"  Columns: {list(data.columns)[:5]}... (and {len(data.columns)-5} more)")
print()

# Step 2: Initialize model
print("Step 2: Initializing homebuilder model...")
model = RevenueModel(business_type='homebuilder')
print("✓ Model initialized")
print()

# Step 3: Load data
print("Step 3: Loading and validating data...")
model.load_data('homebuilder_data.csv', validate=True, preprocess=True)
print(f"✓ Data loaded: {len(model.processed_data)} rows")
print()

# Step 4: Train models
print("Step 4: Training forecasting models...")
print("  This may take 1-2 minutes...")
model.train(methods=['prophet', 'xgboost'])
print(f"✓ Trained {len(model.trained_models)} models")
print()

# Step 5: Generate forecast
print("Step 5: Generating 24-month forecast...")
forecast = model.predict(periods=24, confidence_level=0.95)
print("✓ Forecast generated")
print()

# Step 6: Calculate metrics
print("Step 6: Calculating key metrics...")
metrics = model.calculate_metrics()
print("✓ Metrics calculated")
print()

# Step 7: Display results
print("="*70)
print("RESULTS SUMMARY")
print("="*70)
print()

print("FORECAST (First 12 months):")
print(forecast[['period', 'forecast']].head(12).to_string(index=False))
print()

print("KEY METRICS:")
if 'mom_growth_rate' in metrics:
    print(f"  Average Growth Rate: {metrics['mom_growth_rate']:.1%}")
if 'total_revenue' in metrics:
    print(f"  Historical Total Revenue: ${metrics['total_revenue']:,.0f}")
print(f"  Forecasted Revenue (24mo): ${forecast['forecast'].sum():,.0f}")
print()

# Step 8: Run scenarios
print("Step 8: Running scenario analysis...")
scenarios = model.scenario_analysis(
    variables={'revenue': [0.85, 1.0, 1.15]},  # Pessimistic, base, optimistic
    monte_carlo=False  # Skip Monte Carlo for speed
)
print(f"✓ Generated {len(scenarios)} scenarios")
print()

# Step 9: Export report
print("Step 9: Exporting comprehensive report...")
model.export_report('homebuilder_forecast_report.xlsx', include_visuals=True)
print("✓ Report exported: homebuilder_forecast_report.xlsx")
print()

print("="*70)
print("✓ COMPLETE! Check homebuilder_forecast_report.xlsx for full results")
print("="*70)
```

**Run it:**
```bash
python3 my_first_forecast.py
```

---

## Understanding Your Data Format

### Minimum Required Columns for Homebuilders

Your CSV file must have these columns:

```csv
date,closings,asp,net_orders,backlog,starts,active_communities,gross_margin
2024-01-31,150,450000,165,575,165,35,0.22
2024-02-29,155,452000,170,590,170,35,0.21
2024-03-31,162,453500,175,603,175,36,0.21
```

**Column Definitions:**
- `date`: Date in YYYY-MM-DD format
- `closings`: Number of homes closed/delivered
- `asp`: Average Selling Price (in dollars)
- `net_orders`: New orders signed (net of cancellations)
- `backlog`: Homes under contract but not closed
- `starts`: New construction starts
- `active_communities`: Number of active selling communities
- `gross_margin`: Gross profit margin (as decimal, e.g., 0.22 = 22%)

### Optional but Recommended Columns

```csv
incentives,mortgage_rate,cancellation_rate,specs,lots_owned,options_revenue
```

---

## Working with Your Own Data

### Step 1: Prepare Your Data

Create a CSV file with your company's data:

**Example: `my_company_data.csv`**
```csv
date,closings,asp,net_orders,backlog,starts,active_communities,gross_margin,mortgage_rate
2023-01-31,200,485000,215,650,210,42,0.23,6.5
2023-02-28,205,487000,220,665,215,42,0.22,6.6
2023-03-31,210,489000,225,680,220,43,0.22,6.7
...
```

### Step 2: Load and Forecast

```python
from revenue_builder import RevenueModel

# Initialize
model = RevenueModel(business_type='homebuilder')

# Load YOUR data
model.load_data('my_company_data.csv')

# Train
model.train(auto_select=True)

# Forecast
forecast = model.predict(periods=24)

# Export
model.export_report('my_forecast.xlsx')
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "ModuleNotFoundError: No module named 'pandas'"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

#### Issue 2: "Command 'revenue-builder' not found"

**Cause**: Package not installed or virtual environment not activated

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Reinstall package
pip install -e .
```

#### Issue 3: TensorFlow installation fails

**Cause**: TensorFlow has specific system requirements

**Solution (Skip TensorFlow for now)**:

Edit `requirements.txt` and comment out the TensorFlow line:
```
# tensorflow>=2.13.0
```

Then reinstall:
```bash
pip install -r requirements.txt
pip install -e .
```

You can still use Prophet, XGBoost, and other models without TensorFlow.

#### Issue 4: "ImportError: cannot import name 'RevenueModel'"

**Cause**: Package not installed properly

**Solution**:
```bash
# From the New-rev-build directory
pip uninstall revenue-builder
pip install -e .
```

#### Issue 5: Prophet installation fails on Mac M1/M2

**Solution**:
```bash
# Install Prophet with conda instead
conda install -c conda-forge prophet
# Then continue with other dependencies
pip install -r requirements.txt
```

#### Issue 6: Memory error during training

**Cause**: Large dataset or insufficient RAM

**Solution**: Use fewer models at once
```python
# Instead of training all models
model.train(auto_select=True)

# Train just Prophet (lightweight)
model.train(methods=['prophet'])
```

#### Issue 7: "RuntimeError: module compiled against API version ... but this version of numpy is ..."

**Cause**: Numpy version mismatch

**Solution**:
```bash
pip install --upgrade numpy
pip install --force-reinstall --no-cache-dir -r requirements.txt
```

---

## Minimal Installation (If Full Install Fails)

If you're having trouble with all dependencies, install just the essentials:

### Create `requirements_minimal.txt`:

```txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
openpyxl>=3.1.0
pyyaml>=6.0
click>=8.1.0
flask>=2.3.0
flask-cors>=4.0.0
```

### Install minimal version:

```bash
pip install -r requirements_minimal.txt
pip install -e .
```

This gives you basic functionality without advanced ML models.

---

## Next Steps

### 1. Try the Jupyter Notebook

```bash
# Install Jupyter
pip install jupyter ipywidgets

# Start Jupyter
jupyter notebook notebooks/homebuilder_forecast_example.ipynb
```

### 2. Explore CLI Commands

```bash
# List available models
revenue-builder list-models

# View homebuilder template
revenue-builder show-template -b homebuilder

# Generate sample data
revenue-builder generate-sample -b homebuilder -o test.csv

# Validate your data
revenue-builder validate your_data.csv
```

### 3. Read the Documentation

- **Homebuilder Guide**: `docs/HOMEBUILDER_GUIDE.md`
- **API Reference**: `docs/API.md`
- **Quick Start**: `docs/QUICKSTART.md`

### 4. Customize for Your Needs

```python
# Custom configuration
from revenue_builder import RevenueModel

config = {
    'forecasting': {
        'default_periods': 36,
        'confidence_level': 0.90,
    },
    'models': {
        'validation_split': 0.2,
    }
}

model = RevenueModel(business_type='homebuilder', config=config)
```

---

## Getting Help

### Check Logs

If something goes wrong, check the log file:
```bash
cat revenue_builder.log
```

### Debug Mode

Run Python with verbose output:
```bash
python -v my_script.py
```

### Test Installation

Run our test script:
```bash
python3 << 'EOF'
print("Testing Revenue Builder installation...")
print()

# Test 1: Import
try:
    from revenue_builder import RevenueModel
    print("✓ RevenueModel imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")

# Test 2: Create instance
try:
    model = RevenueModel(business_type='homebuilder')
    print("✓ Model created successfully")
except Exception as e:
    print(f"✗ Model creation failed: {e}")

# Test 3: Check dependencies
import sys
required = ['pandas', 'numpy', 'sklearn', 'matplotlib']
for pkg in required:
    try:
        __import__(pkg)
        print(f"✓ {pkg} available")
    except:
        print(f"✗ {pkg} missing")

print()
print("Installation test complete!")
EOF
```

---

## Quick Reference

### Installation Commands (Summary)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Install Revenue Builder
pip install -e .

# 4. Verify
python3 -c "from revenue_builder import RevenueModel; print('✓ Success!')"
```

### First Forecast (Summary)

```python
from revenue_builder import RevenueModel
from revenue_builder.business_models import BusinessModelTemplates

# Generate sample data
data = BusinessModelTemplates.generate_sample_data('homebuilder', 36)
data.to_csv('sample.csv', index=False)

# Forecast
model = RevenueModel(business_type='homebuilder')
model.load_data('sample.csv')
model.train(methods=['prophet'])
forecast = model.predict(periods=24)
model.export_report('forecast.xlsx')
```

---

## Still Having Issues?

1. **Check Python version**: Must be 3.8 or higher
2. **Use virtual environment**: Isolates dependencies
3. **Try minimal install**: Install only essential packages
4. **Check logs**: Look at `revenue_builder.log` for errors
5. **Start simple**: Use just Prophet model first, add others later

---

**You should now be able to install and run Revenue Builder successfully!** 🚀

If you encounter any issues not covered here, please check the logs and error messages carefully.
