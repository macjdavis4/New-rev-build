# Homebuilder Revenue Forecasting Guide

## Revenue Forecasting for Residential Construction Companies

This guide is specifically designed for homebuilding companies like **Lennar**, **DR Horton**, **Toll Brothers**, **KB Home**, and **PulteGroup**.

## Key Homebuilder Metrics

Revenue Builder tracks and forecasts all critical metrics for homebuilders:

### Volume Metrics
- **Closings**: Home deliveries (revenue recognition point)
- **Net Orders**: New contracts signed (gross orders - cancellations)
- **Backlog**: Homes under contract but not yet closed
- **Starts**: New home construction beginnings
- **Spec Homes**: Homes started before being sold

### Pricing Metrics
- **ASP (Average Selling Price)**: Average home price
- **Incentives**: Buyer concessions (% of ASP)
- **Net ASP**: Price after incentives
- **Options Revenue**: Upgrades and customizations

### Operational Metrics
- **Active Communities**: Number of selling locations
- **Absorption Rate**: Sales pace per community per month
- **Cancellation Rate**: % of contracts cancelled
- **Cycle Time**: Days from start to closing
- **Closings per Community**: Delivery rate per location

### Profitability Metrics
- **Gross Margin**: Gross profit as % of revenue
- **Land Cost per Lot**: Average land acquisition cost
- **Construction Cost**: Direct build costs per home
- **Revenue per Community**: Monthly revenue per location

### Land/Inventory Metrics
- **Lots Owned**: Controlled land inventory
- **Years of Supply**: Lot inventory / annual closings
- **Backlog Coverage**: Backlog / monthly closings (in months)

### External Factors
- **Mortgage Rates**: 30-year fixed rate impact on demand
- **Interest Rate Sensitivity**: Demand elasticity
- **Market Conditions**: Local housing market trends

## Critical Factors for Homebuilder Forecasting

### 1. Lots (Land Inventory)
**Why it matters**: Land is the foundation of homebuilder business. Without lots, you can't build homes.

**Key considerations**:
- Owned lots vs. optioned lots
- Years of supply (target: 3-5 years)
- Lot acquisition costs relative to ASP
- Market-specific land availability

**In the model**:
```python
model = RevenueModel(business_type='homebuilder')
model.load_data('homebuilder_data.csv')  # Must include 'lots_owned' column

# Forecast considers lot constraints
forecast = model.predict(
    periods=24,
    # Model automatically factors in lot availability
)
```

### 2. Home Prices (ASP)
**Why it matters**: ASP is 50% of the revenue equation (Closings × ASP = Revenue).

**Key considerations**:
- Historical ASP trends
- Price appreciation rates
- Market segment mix (entry-level vs. move-up vs. luxury)
- Price elasticity with interest rates

**In the model**:
```python
# ASP is automatically tracked and forecasted
# Scenario analysis for different price assumptions
scenarios = model.scenario_analysis(
    variables={
        'asp': [400000, 450000, 500000],  # Low, base, high scenarios
    }
)
```

### 3. Interest Rates
**Why it matters**: Mortgage rates are the #1 external factor affecting homebuilder demand.

**Impact**:
- **Higher rates** → Lower affordability → Fewer orders → Higher cancellations → More incentives
- **Lower rates** → Higher affordability → More orders → Lower cancellations → Fewer incentives

**In the model**:
```python
# Include mortgage_rate in your data
# Model automatically factors rate impact into:
# - Order pace
# - Cancellation rates
# - Incentive levels
# - ASP growth

# Stress test different rate scenarios
stress_scenarios = model.scenario_analysis(
    variables={
        'mortgage_rate': [5.0, 6.5, 8.0],  # Low, base, high
    }
)
```

### 4. Incentives
**Why it matters**: Incentives directly reduce net ASP and compress margins.

**Types of incentives**:
- Rate buy-downs
- Closing cost assistance
- Free upgrades
- Price reductions

**In the model**:
```python
# Track incentive % of ASP
# Model shows impact on:
# - Net ASP
# - Gross margin
# - Revenue per closing

# Optimize incentive strategy
model.scenario_analysis(
    variables={
        'incentive_pct': [0.02, 0.03, 0.05],  # 2%, 3%, 5% of ASP
    }
)
```

### 5. Absorption Rate (Sales Pace)
**Why it matters**: Determines how fast you sell homes = revenue velocity.

**Key considerations**:
- Seasonality (stronger spring/summer)
- Interest rate sensitivity
- Community maturity (new communities start slow)
- Competitive dynamics

**In the model**:
```python
# Calculated automatically as: closings / active_communities
# Prophet model captures seasonal patterns
# Forecast accounts for community count growth
```

### 6. Backlog Dynamics
**Why it matters**: Backlog is your revenue pipeline. It converts to closings over 4-6 months.

**Key metrics**:
- Backlog units
- Backlog value
- Backlog coverage (months)
- Conversion rate

**In the model**:
```python
# Backlog-based forecasting:
# Future Closings = Current Backlog × Conversion Rate + New Orders
# Model tracks backlog build/burn
```

### 7. Active Communities
**Why it matters**: More communities = more sales locations = more closings.

**Key considerations**:
- Community opening schedule
- Closeout timing
- Mature vs. new community mix
- Geographic diversification

**In the model**:
```python
# Revenue = Active Communities × Absorption Rate × ASP
# Model forecasts community count growth
# Scenario analysis for different expansion plans
```

### 8. Gross Margin
**Why it matters**: Profitability driver. Typical range: 18-25%.

**Pressure points**:
- Rising land costs
- Construction cost inflation
- Higher incentives
- Product mix shifts

**In the model**:
```python
# Automatically calculated and forecasted
# Factors in:
# - Land cost per lot
# - Construction costs
# - Incentives impact
# - Price realization
```

### 9. Seasonality
**Why it matters**: Homebuilding has strong seasonal patterns.

**Typical pattern**:
- **Q1 (Jan-Mar)**: Slow, building momentum
- **Q2 (Apr-Jun)**: Peak selling season
- **Q3 (Jul-Sep)**: Still strong
- **Q4 (Oct-Dec)**: Slowing down

**In the model**:
```python
# Prophet model automatically detects and forecasts seasonality
# Historical patterns applied to future periods
```

### 10. Cycle Time
**Why it matters**: Determines how fast backlog converts to revenue.

**Key considerations**:
- Spec strategy (specs close faster)
- Product type (townhomes faster than single-family)
- Labor availability
- Supply chain issues

**In the model**:
```python
# Used in backlog-to-closings conversion
# Shorter cycle time = faster revenue recognition
```

## Example: Complete Homebuilder Forecast

```python
from revenue_builder import RevenueModel

# 1. Initialize homebuilder model
model = RevenueModel(business_type='homebuilder')

# 2. Load your data with required columns:
# - date, closings, asp, net_orders, backlog, starts, 
# - active_communities, gross_margin
model.load_data('lennar_historical.csv')

# 3. Train models (auto-selects best for homebuilders)
model.train(auto_select=True)

# 4. Generate 24-month forecast
forecast = model.predict(periods=24)

# 5. Scenario analysis: Interest rate sensitivity
scenarios = model.scenario_analysis(
    variables={
        'mortgage_rate': [5.5, 7.0, 8.5],  # Low, base, high
        'incentive_pct': [0.02, 0.03, 0.05],
        'absorption_rate': [3.5, 3.0, 2.5],
    },
    monte_carlo=True,
    n_simulations=10000
)

# 6. Calculate all homebuilder metrics
metrics = model.calculate_metrics()

print(f"Backlog Coverage: {metrics['backlog_months']:.1f} months")
print(f"Absorption Rate: {metrics['absorption_rate']:.1f} sales/community")
print(f"Gross Margin: {metrics['gross_margin']:.1%}")

# 7. Export comprehensive report
model.export_report('lennar_forecast_2025.xlsx', include_visuals=True)
```

## Data Requirements

### Required Columns
```csv
date,closings,asp,net_orders,backlog,starts,active_communities,gross_margin
2024-01-31,150,450000,165,575,165,35,0.22
2024-02-29,155,452000,170,590,170,35,0.21
...
```

### Optional (but recommended) Columns
- `incentives` or `incentive_pct`: Buyer incentives
- `mortgage_rate`: Current 30-year rate
- `cancellation_rate`: % of orders cancelled
- `specs`: Spec home count
- `lots_owned`: Owned lot inventory
- `options_revenue`: Upgrade revenue
- `land_cost_per_lot`: Land costs
- `construction_cost_per_home`: Build costs

## Best Practices

### 1. Data Granularity
- **Monthly data**: Best for forecasting
- **Quarterly data**: Acceptable but less precise
- **At least 24 months** of history for reliable forecasts

### 2. Include External Factors
```python
# Add mortgage rate data
data['mortgage_rate'] = get_freddie_mac_rates()

# Include local market indicators
data['market_home_sales'] = get_local_sales_data()
```

### 3. Segment by Market/Division
```python
# Forecast by geography for better accuracy
east_model = RevenueModel(business_type='homebuilder')
east_model.load_data(data[data['division'] == 'East'])

west_model = RevenueModel(business_type='homebuilder')
west_model.load_data(data[data['division'] == 'West'])

# Aggregate forecasts
total_forecast = east_forecast + west_forecast
```

### 4. Regular Updates
- Update forecasts **monthly** as new data arrives
- Refresh assumptions **quarterly**
- Full model retrain **annually**

### 5. Scenario Planning
Always forecast with 3 scenarios:
1. **Base case**: Current trends continue
2. **Optimistic**: Rates drop, strong demand
3. **Pessimistic**: Rates rise, weak demand

## Common Homebuilder Forecasting Challenges

### Challenge 1: Interest Rate Volatility
**Solution**: Use scenario analysis with multiple rate assumptions

### Challenge 2: Backlog Visibility
**Solution**: Track backlog aging and conversion rates by cohort

### Challenge 3: Community Lifecycle
**Solution**: Model absorption curves by community maturity

### Challenge 4: Land Pipeline
**Solution**: Forecast constrained by lot availability

### Challenge 5: Margin Compression
**Solution**: Model cost inflation and pricing power separately

## Output Examples

Revenue Builder generates:
1. **Revenue forecasts** by month
2. **Key metrics dashboard** (closings, ASP, absorption, margin)
3. **Scenario comparisons** (base vs. optimistic vs. pessimistic)
4. **Sensitivity analysis** (impact of rates, pricing, pace)
5. **Backlog analysis** (conversion trends, coverage)
6. **Community economics** (revenue per community)
7. **Probabilistic forecasts** (Monte Carlo distributions)

## Getting Help

- Example notebook: `notebooks/homebuilder_forecast_example.ipynb`
- Sample data: `sample_data/homebuilder_sample.csv`
- Template: `revenue-builder show-template -b homebuilder`
- Generate sample: `revenue-builder generate-sample -b homebuilder -o test.csv`

## Industry Benchmarks

**Typical Ranges** (varies by segment and market):
- Absorption Rate: 2.5-4.0 sales/community/month
- Gross Margin: 18-25%
- Cancellation Rate: 8-15%
- Backlog Coverage: 4-6 months
- Incentives: 2-5% of ASP
- Cycle Time: 4-6 months

Use these as sanity checks for your forecasts!
