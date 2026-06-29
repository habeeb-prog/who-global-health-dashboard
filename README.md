# WHO Global Health Analytics Dashboard
### Python · Dash · Plotly · Pandas · SciPy · Docker · Hugging Face

## Live Dashboard
[View Live Dashboard](https://pro580-who-global-health-dashboard.hf.space)

## GitHub Repository
[View Source Code](https://github.com/prolynk/who-global-health-dashboard)

---

## Overview
An interactive web application analysing WHO health data across 193 countries and 16 years. The project covers data engineering, statistical analysis, exploratory data analysis and a deployed multi-page dashboard.

---

## Key Findings
- Global life expectancy improved by **4.9 years** between 2000 and 2015
- A **11-year gap** persists between developed and developing countries
- **Schooling** is the strongest positive predictor of life expectancy (r=0.728)
- **Sierra Leone (51 years)** vs **Slovenia (88 years)** — a 37-year gap
- Countries with high health expenditure live **6.2 years longer** on average
- **2,046 anomalous health changes** detected across 193 countries

---

## Dashboard Pages

### Page 1 — Global Overview
World choropleth map with year slider, 4 KPI cards and top/bottom 15 countries bar chart.

![Global Overview](screenshots/page1_global_overview.png)

### Page 2 — Country Deep Dive
Select any of 193 countries to explore 12 health indicators as trend lines across 16 years with a regression trend table showing slope, R² and direction per indicator.

![Country Deep Dive](screenshots/page2_country_deepdive.png)

### Page 3 — Regional Comparison
Developed vs Developing mean trend lines over time and a latest year comparison bar chart.

![Regional Comparison](screenshots/page3_regional_comparison.png)

### Page 4 — Anomaly Alerts
Z-score threshold slider filtering countries where year-over-year health changes exceeded 2 to 5 standard deviations from the regional mean.

![Anomaly Alerts](screenshots/page4_anomaly_alerts.png)

### Page 5 — Correlation Explorer
12x12 correlation heatmap across all indicators with an interactive scatter plot and OLS trendline.

![Correlation Explorer](screenshots/page5_correlation_explorer.png)

---

## Technical Architecture

### Data Pipeline — src/cleaning.py
- Loads raw WHO CSV and standardises column names to snake_case
- Fills missing values using 3-pass median imputation: country level, status group, then global median
- Validates value ranges using domain knowledge
- Engineers GDP per capita and decade features
- Outputs clean dataset to data/processed/health_clean.csv

### Statistical Analysis — src/analysis.py
- Linear regression per country per indicator using SciPy producing 2,509 trend pairs with slope and R²
- Z-score anomaly detection comparing year-over-year changes against regional mean and standard deviation flagging 2,046 significant health shocks
- Pearson correlation matrix across all 12 indicators
- Regional benchmarks by developed and developing status

### EDA Notebook — notebooks/01_eda_who_global_health.ipynb
- Distribution analysis across all 12 indicators split by status
- Life expectancy trend visualisation 2000 to 2015
- Full correlation heatmap with Seaborn
- Top and bottom 10 country rankings for 2015
- GDP per capita vs life expectancy scatter with outlier labels
- Statistical summary of key findings

### Web Application — app.py
- Multi-page Dash application with Bootstrap styling
- 5 interactive pages with dropdowns, sliders and filters
- Plotly choropleth maps, scatter plots, heatmaps and line charts
- Callback architecture for real-time interactivity

### Deployment
- Dockerised with gunicorn WSGI server on port 7860
- Deployed on Hugging Face Spaces using Docker SDK
- GitHub Actions keep-alive workflow pings the Space every 24 hours to prevent the free tier 48-hour sleep

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.12 |
| Dashboard | Dash, Dash Bootstrap Components |
| Visualisation | Plotly |
| Data | Pandas, NumPy |
| Statistics | SciPy |
| EDA | Jupyter, Matplotlib, Seaborn |
| Deployment | Docker, Hugging Face Spaces, Gunicorn |
| Automation | GitHub Actions |

---

## Project Structure

```
who-global-health-dashboard/
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
├── .github/
│   └── workflows/
│       └── keep_alive.yml
├── data/
│   ├── raw/
│   └── processed/
│       ├── health_clean.csv
│       ├── trends.csv
│       ├── anomalies.csv
│       ├── correlations.csv
│       └── benchmarks.csv
├── src/
│   ├── cleaning.py
│   └── analysis.py
├── notebooks/
│   └── 01_eda_who_global_health.ipynb
└── screenshots/
    ├── page1_global_overview.png
    ├── page2_country_deepdive.png
    ├── page3_regional_comparison.png
    ├── page4_anomaly_alerts.png
    └── page5_correlation_explorer.png
```

---

## How to Run Locally

```bash
git clone https://github.com/prolynk/who-global-health-dashboard.git
cd who-global-health-dashboard
pip install -r requirements.txt
python src/cleaning.py
python src/analysis.py
python app.py
```

Open `http://127.0.0.1:8050` in your browser.

---

## Data Source
WHO Global Health Observatory — Life Expectancy Dataset
193 countries · 2000-2015 · 22 health indicators
[Download Dataset](https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who)
