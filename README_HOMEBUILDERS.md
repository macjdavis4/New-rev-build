# Revenue Builder for Homebuilders

## ML-Powered Revenue Forecasting for Residential Construction Companies

**Built specifically for homebuilding companies like Lennar, DR Horton, Toll Brothers, KB Home, and PulteGroup**

Revenue Builder is a production-ready forecasting system that models all critical factors affecting homebuilder revenue, from lots and interest rates to absorption rates and incentives.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🏗️ Why Revenue Builder for Homebuilders?

Homebuilding is unique. Revenue forecasting must account for:

- **Lot inventory and land pipeline**
- **Interest rate volatility** (mortgage rates)
- **Seasonal patterns** (spring/summer strength)
- **Backlog dynamics** (4-6 month conversion)
- **Buyer incentives** (rate buy-downs, concessions)
- **Community lifecycle** (openings and closeouts)  
- **Absorption rates** (sales pace per community)
- **Price appreciation** vs. **market resistance**
- **Construction cycle times**
- **Gross margin compression**

Revenue Builder handles all of these factors automatically.

---

## 🚀 Key Features for Homebuilders

### Critical Metrics Tracked

**Volume Metrics:**
- Closings (home deliveries)
- Net Orders (new contracts)
- Backlog (contracted homes)
- Starts (new construction)
- Cancellation rates

**Pricing Metrics:**
- Average Selling Price (ASP)
- Incentives ($ and % of ASP)
- Net ASP (after incentives)
- Options/upgrade revenue

**Operational Metrics:**
- Active communities
- Absorption rate (sales/community/month)
- Closings per community
- Cycle time (start to close)
- Spec home strategy

**Land/Inventory:**
- Lots owned and controlled
- Years of supply
- Land cost per lot
- Backlog coverage (months)

**Profitability:**
- Gross margin %
- Revenue per community
- Cost per home (land + construction)

**External Factors:**
- Mortgage rates (30-year fixed)
- Interest rate sensitivity
- Market conditions

### Multiple Forecasting Approaches

1. **Bottom-Up**: Communities × Absorption Rate × ASP
2. **Backlog-Based**: Existing Pipeline + New Orders - Cancellations
3. **Time Series** (Prophet): Captures strong seasonality
4. **ML Models** (XGBoost): Factor-based with rates, communities, pricing
5. **Ensemble**: Combines all methods for robust forecasts

### Scenario Planning

- **Interest rate scenarios**: Model 5%, 7%, 8.5% mortgage rates
- **Incentive optimization**: Test different concession levels
- **Community expansion**: Model growth plans
- **Price sensitivity**: ASP appreciation scenarios
- **Monte Carlo simulation**: 10,000+ probabilistic forecasts

---

## 📦 Installation

```bash
pip install revenue-builder
```

---

## 🎯 Quick Start for Homebuilders

### Generate Forecast in 5 Lines

```python
from revenue_builder import RevenueModel

model = RevenueModel(business_type='homebuilder')
model.load_data('historical_closings.csv')
model.train(auto_select=True)
forecast = model.predict(periods=24)  # 24-month forecast
model.export_report('forecast_2025.xlsx')
```

### Required Data Format

Your CSV/Excel should include these columns:

```csv
date,closings,asp,net_orders,backlog,starts,active_communities,gross_margin
2024-01-31,150,450000,165,575,165,35,0.22
2024-02-29,155,452000,170,590,170,35,0.21
2024-03-31,162,453500,175,603,175,36,0.21
```

**Optional but recommended:**
- `incentives` or `incentive_pct`
- `mortgage_rate`
- `cancellation_rate`
- `specs`
- `lots_owned`
- `options_revenue`

### CLI Usage

```bash
# Generate forecast
revenue-builder forecast closings_data.csv -b homebuilder -p 24 -o forecast.xlsx

# Generate sample data for testing
revenue-builder generate-sample -b homebuilder -p 36 -o sample.csv

# View homebuilder template
revenue-builder show-template -b homebuilder
```

---

## 📊 Critical Factors Included

### 1. **Lots (Land Inventory)** 🏞️

Land is the foundation. Revenue Builder factors in:
- Years of lot supply
- Land cost per lot
- Constraints on growth

**Example:**
```python
# Model automatically constrains forecast to available lots
# Alerts if projected closings exceed lot inventory
```

### 2. **Home Prices (ASP)** 💰

ASP drives 50% of revenue equation (Closings × ASP).

**Model handles:**
- Historical price trends
- Price appreciation rates
- Market segment mix
- Rate sensitivity on pricing power

**Scenario analysis:**
```python
scenarios = model.scenario_analysis(
    variables={
        'asp': [400000, 450000, 500000]  # Test different price points
    }
)
```

### 3. **Interest Rates** 📈

Mortgage rates are the #1 external factor.

**Impact modeled:**
- Higher rates → Fewer orders, more cancellations, higher incentives
- Lower rates → More orders, fewer cancellations, lower incentives

**Rate scenarios:**
```python
model.scenario_analysis(
    variables={
        'mortgage_rate': [5.0, 6.5, 8.0]  # Low, base, high
    }
)
```

### 4. **Incentives** 🎁

Directly affects net ASP and margins.

**Types tracked:**
- Rate buy-downs
- Closing cost assistance
- Free upgrades
- Price concessions

**Model shows:**
- Impact on net ASP
- Margin compression
- Optimal incentive strategy

### 5. **Absorption Rate** 🏘️

Sales pace per community determines revenue velocity.

**Model accounts for:**
- Seasonal patterns (spring/summer peaks)
- Interest rate sensitivity
- Community maturity curves
- Competitive dynamics

### 6. **Backlog** 📋

Your revenue pipeline.

**Model tracks:**
- Backlog units and value
- Conversion to closings (4-6 months)
- Backlog coverage (months of supply)
- Build/burn dynamics

### 7. **Active Communities** 🗺️

More communities = more sales capacity.

**Formula:**
Revenue = Communities × Absorption × ASP

**Model handles:**
- Community opening schedules
- Closeout timing
- Geographic expansion

### 8. **Gross Margin** 💵

Profitability driver (typical range: 18-25%).

**Pressure points modeled:**
- Rising land costs
- Construction inflation
- Incentive levels
- Product mix

### 9. **Seasonality** 🌞

Strong seasonal patterns in homebuilding.

**Typical cycle:**
- Q2 (Spring): Peak selling
- Q3 (Summer): Strong
- Q4 (Fall): Slowing
- Q1 (Winter): Recovering

**Prophet model** automatically captures and forecasts seasonality.

### 10. **Cycle Time** ⏱️

Time from start to closing affects revenue timing.

**Factors:**
- Spec vs. pre-sold strategy
- Product type (townhomes vs. single-family)
- Labor and supply chain
- Build efficiency

---

## 💡 Complete Example

```python
from revenue_builder import RevenueModel

# 1. Initialize for homebuilder
model = RevenueModel(business_type='homebuilder')

# 2. Load historical data (24+ months recommended)
model.load_data('lennar_historical.csv', validate=True)

# 3. Train models (auto-selects Prophet + XGBoost for homebuilders)
model.train(auto_select=True)

# 4. Generate 24-month forecast with confidence intervals
forecast = model.predict(periods=24, confidence_level=0.95)

# 5. Calculate all homebuilder metrics
metrics = model.calculate_metrics()

print(f"Current Backlog: {metrics['backlog']:.0f} homes")
print(f"Absorption Rate: {metrics['absorption_rate']:.1f} sales/community/month")
print(f"Gross Margin: {metrics['gross_margin']:.1%}")

# 6. Scenario analysis: Interest rate sensitivity
scenarios = model.scenario_analysis(
    variables={
        'mortgage_rate': [5.5, 7.0, 8.5],  # Optimistic, base, pessimistic
        'incentive_pct': [0.02, 0.03, 0.05],  # 2%, 3%, 5% of ASP
        'absorption_rate': [3.5, 3.0, 2.5],  # Sales pace scenarios
    },
    monte_carlo=True,
    n_simulations=10000
)

# 7. Export comprehensive Excel report
model.export_report(
    'lennar_forecast_2025.xlsx',
    include_visuals=True,
    include_commentary=True
)
```

---

## 📈 What You Get

### Forecasts
- Monthly closings projections
- Revenue by month (24-36 months)
- ASP trends with price appreciation
- Backlog build/burn dynamics

### Key Metrics
- Absorption rates by community
- Backlog coverage (months)
- Cancellation rate trends
- Gross margin trajectory
- Revenue per community

### Scenario Analysis
- Base/optimistic/pessimistic cases
- Interest rate sensitivity
- Pricing power assessment
- Incentive optimization

### Monte Carlo Results
- Probabilistic revenue distribution
- 10th, 25th, 50th, 75th, 90th percentiles
- Risk-adjusted forecasts

### Visualizations
- Revenue forecast charts
- Backlog-to-closings conversion
- Community economics
- Seasonal patterns
- Scenario comparisons

---

## 📚 Documentation

- **Homebuilder Guide**: `docs/HOMEBUILDER_GUIDE.md`
- **Example Notebook**: `notebooks/homebuilder_forecast_example.ipynb`
- **Sample Data**: `sample_data/homebuilder_sample.csv`
- **API Docs**: `docs/API.md`

---

## 🏢 Industry Benchmarks

**Typical Ranges** (use as sanity checks):

| Metric | Range |
|--------|-------|
| Absorption Rate | 2.5-4.0 sales/community/month |
| Gross Margin | 18-25% |
| Cancellation Rate | 8-15% |
| Backlog Coverage | 4-6 months |
| Incentives (% of ASP) | 2-5% |
| Cycle Time | 4-6 months |
| ASP Growth (annual) | 3-7% |

---

## 🎓 Learn More

### Generate Sample Data

```bash
revenue-builder generate-sample -b homebuilder -p 36 -o sample.csv
```

This creates 36 months of realistic homebuilder data with:
- Seasonal patterns
- Interest rate impacts
- Backlog dynamics
- Margin compression

### Try the Example

```bash
jupyter notebook notebooks/homebuilder_forecast_example.ipynb
```

Walks through complete forecasting workflow for homebuilders.

### View Template

```bash
revenue-builder show-template -b homebuilder
```

Shows all metrics, required columns, and recommended models.

---

## 🛠️ Advanced Features

### Segment Forecasting

```python
# Forecast by division/market
west_model = RevenueModel(business_type='homebuilder')
west_model.load_data(data[data['division'] == 'West'])
west_forecast = west_model.predict(24)

east_model = RevenueModel(business_type='homebuilder')
east_model.load_data(data[data['division'] == 'East'])
east_forecast = east_model.predict(24)

# Aggregate
total_forecast = combine_forecasts([west_forecast, east_forecast])
```

### API Integration

```python
from revenue_builder.api import create_app

app = create_app()
app.run(port=5000)

# Use REST API for automated forecasting
```

### Docker Deployment

```bash
docker build -t revenue-builder .
docker run -p 5000:5000 revenue-builder
```

---

## ✅ Best Practices

1. **Use Monthly Data**: More accurate than quarterly
2. **Include 24+ Months**: Minimum for reliable forecasts
3. **Add Mortgage Rates**: Critical external factor
4. **Segment by Market**: Better accuracy than aggregated
5. **Update Monthly**: Keep forecasts current
6. **Run Scenarios**: Always model multiple cases
7. **Validate Backlog**: Ensure conversion assumptions are realistic
8. **Check Lot Constraints**: Don't forecast beyond land availability

---

## 🚨 Common Mistakes to Avoid

❌ **Ignoring interest rate impact** → Model unrealistic demand  
✅ **Include mortgage rate data** → Accurate demand forecasting

❌ **Forecasting beyond lot inventory** → Impossible to deliver  
✅ **Constrain by land availability** → Realistic capacity planning

❌ **Ignoring seasonality** → Miss spring/summer peaks  
✅ **Use Prophet or similar** → Capture seasonal patterns

❌ **Not modeling backlog** → Miss revenue timing  
✅ **Track backlog conversion** → Accurate revenue recognition

❌ **Single point forecast** → Overconfident  
✅ **Scenario analysis** → Understand range of outcomes

---

## 🤝 Support

- GitHub Issues: [Report bugs](https://github.com/yourusername/revenue-builder/issues)
- Email: support@revenue-builder.com
- Docs: Full documentation in `docs/` directory

---

## 📄 License

MIT License - Free to use for commercial homebuilding applications

---

**Built specifically for the homebuilding industry. Ready to use today.**
