# Ferry Capacity Utilization & Operational Efficiency Analytics System

## 1. Project Overview

The Ferry Capacity Utilization & Operational Efficiency Analytics System is a data analytics project developed using Python, Pandas, NumPy, Plotly, and Streamlit.

The main purpose of this project is to analyze historical Toronto Island Ferry ticket sales and redemption data from 2015 to 2025.

The system helps identify high-activity and low-activity periods, seasonal patterns, daily trends, and operational pressure using historical ticket activity.

It provides an interactive dashboard that helps understand ferry service activity and supports better operational planning.

## 2. Project Objectives

- Analyze historical ferry ticket activity.
- Identify high-activity and low-activity periods.
- Understand weekday and weekend activity patterns.
- Analyze seasonal and yearly trends.
- Calculate Total Activity Load.
- Calculate Redemption Pressure Ratio.
- Develop an Operational Load Index (OLI).
- Identify periods of unusually high or low ticket activity.
- Provide an interactive dashboard for data visualization.

## 3. Dataset Information

**Dataset Name:** Toronto Island Ferry Tickets

**Data Period:** 2015–2025

The dataset contains the following columns:

| Column Name | Description |
|---|---|
| _id | Unique record identifier |
| Timestamp | End time of the 15-minute interval |
| Sales Count | Number of tickets sold |
| Redemption Count | Number of tickets redeemed |

## 4. Key Features

### Interactive Dashboard
- Interactive Streamlit dashboard.
- KPI cards for important metrics.
- Date and season filters.
- Activity granularity selection.

### Activity Analysis
- 15-minute activity analysis.
- Hourly activity analysis.
- Daily activity analysis.
- Sales and redemption comparison.

### Time-Based Analysis
- Weekday and weekend comparison.
- Seasonal activity analysis.
- Yearly activity trends.
- Time-of-day analysis.

### Operational Indicators
- Total Activity Load.
- Redemption Pressure Ratio.
- Operational Load Index.
- High-activity alerts.
- Low-activity indicators.

### Data Visualization
- Interactive line charts.
- Bar charts.
- Heatmaps.
- Seasonal comparisons.
- Trend analysis.

### Data Quality
- Missing value analysis.
- Duplicate timestamp detection.
- Invalid timestamp checking.
- Dataset summary.

## 5. Project Structure

```text
Ferry_Operational_Efficiency/
│
├── app.py
│
├── dataset/
│   └── Toronto Island Ferry Tickets.csv
│
└── README.md
```

## 6. Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- Plotly

## 7. Installation and Setup

### Step 1: Install Python

Install Python on your computer if it is not already installed.

### Step 2: Install Required Libraries

Open the terminal and execute:

```bash
pip install streamlit pandas numpy plotly
```

### Step 3: Run the Application

Open the project folder in the terminal and execute:

```bash
streamlit run app.py
```

### Step 4: Open the Dashboard

Streamlit will provide a local URL, usually:

```text
http://localhost:8501
```

Open this URL in your web browser.

## 8. Key Performance Indicators (KPIs)

### Total Activity Load

Total Activity Load represents the combined number of tickets sold and redeemed.

Formula:

Total Activity Load = Sales Count + Redemption Count

### Redemption Pressure Ratio

This indicator compares ticket redemptions with ticket sales.

Formula:

Redemption Pressure Ratio = Redemption Count / (Sales Count + 1)

### Operational Load Index (OLI)

The Operational Load Index is a normalized activity-based indicator used to understand relative operational pressure.

A higher value indicates relatively higher ticket activity.

### High-Activity Periods

Periods with activity above the configured threshold are highlighted for further operational analysis.

### Low-Activity Periods

Periods with sustained low ticket activity are identified to help understand quieter operating periods.

## 9. Dashboard Sections

The dashboard includes:

1. Overview and KPI Summary
2. Activity Timeline Analysis
3. Sales vs Redemption Analysis
4. Operational Load Index
5. High and Low Activity Analysis
6. Seasonal Analysis
7. Yearly Trends
8. Weekday vs Weekend Analysis
9. Time-of-Day Analysis
10. Data Quality Report

## 10. Important Project Limitation

This project uses ticket sales and redemption records as indicators of ferry service activity.

The dataset does not contain:
- Actual passenger counts for each ferry trip.
- Ferry vessel capacity.
- Trip-level passenger information.
- Number of ferries operating.
- Staffing information.
- Operational costs.

Therefore, the dashboard measures ticket activity and estimated operational pressure, not actual vessel capacity utilization or financial efficiency.

Actual capacity utilization would require passenger counts for each trip and the certified capacity of each ferry.

## 11. Future Enhancements

- Integrate real-time ferry activity data.
- Include actual passenger counts.
- Add ferry-wise capacity information.
- Develop passenger demand forecasting.
- Apply machine learning for activity prediction.
- Build an operational planning recommendation system.
- Add automated alerts for unusual activity.

## 12. Expected Outcome

The project provides an interactive analytics platform for understanding historical Toronto Island Ferry ticket activity.

It helps identify activity patterns, seasonal variations, peak periods, and low-activity periods through visual analytics.

The insights can support data-driven operational planning and further research into ferry service efficiency.

## 13. Author

**Project:** Ferry Capacity Utilization & Operational Efficiency Analytics System

**Developed By:** Prasad Satkar

**Purpose:** Data Analytics Project