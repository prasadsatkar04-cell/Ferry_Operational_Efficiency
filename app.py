import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# FERRY CAPACITY UTILIZATION & OPERATIONAL EFFICIENCY ANALYTICS
# Single-file Streamlit application
# ============================================================

st.set_page_config(
    page_title="Ferry Operational Efficiency Analytics",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {background-color: #f7f9fc;}
    [data-testid="stMetric"] {
        background: white; padding: 16px; border-radius: 12px;
        border: 1px solid #e8edf5; box-shadow: 0 2px 8px rgba(0,0,0,.035);
    }
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    h1, h2, h3 {color: #16324f;}
    .note {background:#eef6ff; padding:12px 16px; border-left:4px solid #2780d8; border-radius:7px;}
    .warning {background:#fff7e6; padding:12px 16px; border-left:4px solid #f0ad4e; border-radius:7px;}
</style>
""", unsafe_allow_html=True)

st.title("⛴️ Ferry Capacity Utilization & Operational Efficiency Analytics")
st.caption("Jack Layton Ferry Terminal | Toronto Islands | Historical ticket activity analysis")

# --------------------------- DATA ----------------------------

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        candidates = [
            Path(__file__).resolve().parent / "dataset" / "Toronto Island Ferry Tickets.csv",
            Path(__file__).resolve().parent / "Toronto Island Ferry Tickets.csv",
            Path.cwd() / "dataset" / "Toronto Island Ferry Tickets.csv",
            Path.cwd() / "Toronto Island Ferry Tickets.csv"
        ]
        file_path = next((p for p in candidates if p.exists()), None)
        if file_path is None:
            return None
        df = pd.read_csv(file_path)

    df.columns = df.columns.astype(str).str.strip()
    required = ["Timestamp", "Sales Count", "Redemption Count"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    invalid_timestamp_count = int(df["Timestamp"].isna().sum())

    for col in ["Sales Count", "Redemption Count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    missing_count_values = int(df[["Sales Count", "Redemption Count"]].isna().sum().sum())

    df = df.dropna(subset=["Timestamp"]).copy()
    df[["Sales Count", "Redemption Count"]] = df[
        ["Sales Count", "Redemption Count"]
    ].fillna(0)

    # Retain original counts for audit; negative values are flagged and excluded from load.
    df["Negative Count Flag"] = (
        (df["Sales Count"] < 0) | (df["Redemption Count"] < 0)
    )
    df["Sales Count"] = df["Sales Count"].clip(lower=0)
    df["Redemption Count"] = df["Redemption Count"].clip(lower=0)

    df = df.sort_values("Timestamp")
    duplicate_timestamp_count = int(df["Timestamp"].duplicated().sum())
    df = df.drop_duplicates(subset=["Timestamp"], keep="last")
    df["Total Activity"] = df["Sales Count"] + df["Redemption Count"]
    df["Redemption Pressure Ratio"] = (
        df["Redemption Count"] / (df["Sales Count"] + 1)
    )
    df["Year"] = df["Timestamp"].dt.year
    df["Month"] = df["Timestamp"].dt.month
    df["Month Name"] = df["Timestamp"].dt.strftime("%b")
    df["Day"] = df["Timestamp"].dt.day
    df["Date"] = df["Timestamp"].dt.date
    df["Day Name"] = df["Timestamp"].dt.day_name()
    df["Day Type"] = np.where(df["Timestamp"].dt.dayofweek >= 5, "Weekend", "Weekday")
    df["Hour"] = df["Timestamp"].dt.hour
    df["Season"] = np.select(
        [df["Month"].isin([6, 7, 8]), df["Month"].isin([5, 9, 10])],
        ["Summer", "Shoulder Season"],
        default="Off-season"
    )
    df["Time Band"] = pd.cut(
        df["Hour"], bins=[-1, 10, 15, 23],
        labels=["Morning", "Afternoon", "Evening"]
    ).astype(str)

    df = df.reset_index(drop=True)
    df.attrs["invalid_timestamp_count"] = invalid_timestamp_count
    df.attrs["duplicate_timestamp_count"] = duplicate_timestamp_count
    df.attrs["missing_count_values"] = missing_count_values
    return df


with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    uploaded = st.file_uploader("Upload ferry ticket CSV", type=["csv"])
    st.caption("Or place the CSV in a `dataset` folder beside app.py.")
    granularity = st.radio(
        "Analysis granularity",
        ["15-minute", "Hourly", "Daily"],
        horizontal=False
    )
    st.divider()
    st.subheader("Efficiency thresholds")
    low_threshold = st.number_input("Low activity threshold", min_value=0.0, value=5.0, step=1.0)
    high_threshold = st.number_input("High activity threshold", min_value=0.0, value=100.0, step=5.0)
    rolling_window = st.slider("Smoothing window (intervals)", 1, 24, 4)
    st.caption("Thresholds are activity-count proxies, not certified vessel capacity limits.")

try:
    raw = load_data(uploaded)
except Exception as e:
    st.error(f"Could not read the dataset: {e}")
    st.stop()

if raw is None or raw.empty:
    st.warning("Dataset not found. Upload `Toronto Island Ferry Tickets.csv` using the sidebar, or place it in a `dataset` folder beside app.py.")
    st.info("Required columns: Timestamp, Sales Count, Redemption Count. Optional `_id` is not required.")
    st.stop()

# ---------------------- FILTERS & AGGREGATION -----------------

st.sidebar.subheader("Date and season filters")
min_date = raw["Timestamp"].min().date()
max_date = raw["Timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Select date range", value=(min_date, max_date),
    min_value=min_date, max_value=max_date
)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = raw[
    (raw["Timestamp"].dt.date >= start_date) &
    (raw["Timestamp"].dt.date <= end_date)
].copy()

season_options = ["Summer", "Shoulder Season", "Off-season"]
selected_seasons = st.sidebar.multiselect("Season", season_options, default=season_options)
day_options = ["Weekday", "Weekend"]
selected_days = st.sidebar.multiselect("Day type", day_options, default=day_options)
filtered = filtered[
    filtered["Season"].isin(selected_seasons) &
    filtered["Day Type"].isin(selected_days)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters. Please change the date, season, or day-type filters.")
    st.stop()

def aggregate_data(data, level):
    x = data.set_index("Timestamp")
    rule = {"15-minute": "15min", "Hourly": "h", "Daily": "D"}[level]
    agg = x.resample(rule).agg({
        "Sales Count": "sum",
        "Redemption Count": "sum",
        "Total Activity": "sum"
    }).reset_index()
    agg["Redemption Pressure Ratio"] = (
        agg["Redemption Count"] / (agg["Sales Count"] + 1)
    )
    agg["Rolling Activity"] = agg["Total Activity"].rolling(
        rolling_window, min_periods=1
    ).mean()
    agg["Year"] = agg["Timestamp"].dt.year
    agg["Month"] = agg["Timestamp"].dt.month
    agg["Month Name"] = agg["Timestamp"].dt.strftime("%b")
    agg["Date"] = agg["Timestamp"].dt.date
    agg["Hour"] = agg["Timestamp"].dt.hour
    agg["Day Name"] = agg["Timestamp"].dt.day_name()
    agg["Day Type"] = np.where(agg["Timestamp"].dt.dayofweek >= 5, "Weekend", "Weekday")
    agg["Season"] = np.select(
        [agg["Month"].isin([6, 7, 8]), agg["Month"].isin([5, 9, 10])],
        ["Summer", "Shoulder Season"], default="Off-season"
    )
    agg["Time Band"] = pd.cut(
        agg["Hour"], bins=[-1, 10, 15, 23],
        labels=["Morning", "Afternoon", "Evening"]
    ).astype(str)
    return agg

data = aggregate_data(filtered, granularity)

# Activity-based thresholds. These do NOT represent actual ferry capacity.
data["Activity Status"] = np.select(
    [data["Total Activity"] >= high_threshold,
     data["Total Activity"] <= low_threshold],
    ["High activity alert", "Low activity / possible idle"],
    default="Within selected range"
)
data["High Alert"] = data["Total Activity"] >= high_threshold
data["Low Activity"] = data["Total Activity"] <= low_threshold

# Normalize activity to 0-100 for a relative operational load index.
max_activity = data["Total Activity"].max()
data["Operational Load Index"] = (
    data["Total Activity"] / max_activity * 100 if max_activity > 0 else 0
)

# A sustained low-activity flag: at least three consecutive aggregated intervals.
low_group = (~data["Low Activity"]).cumsum()
data["Sustained Low Activity"] = (
    data["Low Activity"].groupby(low_group).transform("sum") >= 3
) & data["Low Activity"]

# --------------------------- KPI -----------------------------

total_sales = filtered["Sales Count"].sum()
total_redemptions = filtered["Redemption Count"].sum()
total_activity = filtered["Total Activity"].sum()
high_count = int(data["High Alert"].sum())
idle_count = int(data["Sustained Low Activity"].sum())
idle_pct = idle_count / len(data) * 100 if len(data) else 0
avg_activity = data["Total Activity"].mean()
variability = (
    data["Total Activity"].std(ddof=0) / avg_activity * 100
    if avg_activity and not np.isnan(avg_activity) else 0
)
peak_strain = 0
current_run = 0
for flag in data["High Alert"]:
    current_run = current_run + 1 if flag else 0
    peak_strain = max(peak_strain, current_run)

st.markdown(
    '<div class="note"><b>Interpretation note:</b> The source data contains ticket sales and redemptions, '
    'not vessel capacity, trip-level passenger loads, operating costs, or staffing. This dashboard therefore '
    'reports activity-based operational pressure and potential idle windows. It does not claim actual '
    'capacity utilization, congestion, or cost savings.</div>',
    unsafe_allow_html=True
)

st.subheader("📌 Operational KPI Summary")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Ticket Sales", f"{total_sales:,.0f}")
c2.metric("Total Redemptions", f"{total_redemptions:,.0f}")
c3.metric("Total Activity Load", f"{total_activity:,.0f}")
c4.metric("High-Activity Intervals", f"{high_count:,}")
c5.metric("Potential Idle Intervals", f"{idle_count:,}", f"{idle_pct:.1f}% of intervals")

c6, c7, c8 = st.columns(3)
c6.metric("Average Activity / Interval", f"{avg_activity:,.2f}")
c7.metric("Operational Variability Score", f"{variability:.1f}%")
c8.metric("Peak Strain Duration", f"{peak_strain} consecutive intervals")

st.caption(
    "The activity-based Operational Load Index is normalized to the maximum activity in the selected data "
    "(0–100). It is a relative indicator, not a passenger-to-capacity ratio."
)

# -------------------------- TABS -----------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Activity Timeline", "🔥 Congestion & Idle", "🌤️ Seasonal Analysis",
    "🗓️ Time Patterns", "🧹 Data Quality", "💡 Insights & Export"
])

with tab1:
    st.subheader(f"Capacity Activity Timeline — {granularity}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["Timestamp"], y=data["Total Activity"],
        mode="lines", name="Total Activity", line=dict(width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=data["Timestamp"], y=data["Rolling Activity"],
        mode="lines", name=f"Rolling mean ({rolling_window})", line=dict(width=3)
    ))
    fig.add_hline(y=high_threshold, line_dash="dash", annotation_text="High activity threshold")
    fig.add_hline(y=low_threshold, line_dash="dot", annotation_text="Low activity threshold")
    fig.update_layout(
        xaxis_title="Timestamp", yaxis_title="Ticket activity count",
        hovermode="x unified", height=470, legend_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales vs Redemptions")
    compare = data.melt(
        id_vars="Timestamp",
        value_vars=["Sales Count", "Redemption Count"],
        var_name="Activity Type", value_name="Count"
    )
    fig2 = px.area(
        compare, x="Timestamp", y="Count", color="Activity Type",
        title="Ticket sales and redemptions over time"
    )
    fig2.update_layout(height=390)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Operational Load Index")
    fig3 = px.line(
        data, x="Timestamp", y="Operational Load Index",
        title="Relative Operational Load Index (0–100)"
    )
    fig3.update_yaxes(range=[0, 105], title="Normalized index")
    fig3.update_layout(height=320)
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("High-Activity and Potential Idle Periods")
    left, right = st.columns(2)
    with left:
        st.metric("High activity intervals", f"{high_count:,}")
        st.write("Intervals at or above the selected high-activity threshold.")
    with right:
        st.metric("Sustained low-activity intervals", f"{idle_count:,}")
        st.write("Low-activity intervals that are part of a run of at least three intervals.")

    heat = data.pivot_table(
        index="Day Name", columns="Hour", values="Total Activity",
        aggfunc="mean", observed=False
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat = heat.reindex(day_order)
    fig4 = px.imshow(
        heat, aspect="auto", color_continuous_scale="Blues",
        labels=dict(x="Hour of day", y="Day of week", color="Avg activity"),
        title="Average Activity Heatmap: Day of Week × Hour"
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

    status_counts = data["Activity Status"].value_counts().rename_axis("Status").reset_index(name="Intervals")
    fig5 = px.bar(
        status_counts, x="Status", y="Intervals", color="Status",
        title="Activity Alert Distribution", text="Intervals"
    )
    fig5.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Alert Intervals")
    alerts = data[data["High Alert"] | data["Sustained Low Activity"]][
        ["Timestamp", "Total Activity", "Operational Load Index", "Activity Status", "Sustained Low Activity"]
    ].copy()
    st.dataframe(alerts, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download alert intervals",
        alerts.to_csv(index=False).encode("utf-8"),
        "ferry_activity_alerts.csv", "text/csv"
    )

with tab3:
    st.subheader("Seasonal Efficiency Comparison")
    seasonal = filtered.groupby("Season", observed=False).agg(
        Total_Sales=("Sales Count", "sum"),
        Total_Redemptions=("Redemption Count", "sum"),
        Total_Activity=("Total Activity", "sum"),
        Average_Interval_Activity=("Total Activity", "mean"),
        Active_Intervals=("Total Activity", "size")
    ).reset_index()
    seasonal["Activity per Interval"] = (
        seasonal["Total_Activity"] / seasonal["Active_Intervals"].replace(0, np.nan)
    )
    season_order = ["Off-season", "Shoulder Season", "Summer"]
    seasonal["Season"] = pd.Categorical(seasonal["Season"], season_order, ordered=True)
    seasonal = seasonal.sort_values("Season")

    fig6 = px.bar(
        seasonal, x="Season", y="Total_Activity", color="Season",
        title="Total Ticket Activity by Season", text_auto=".3s"
    )
    fig6.update_layout(showlegend=False, height=370, yaxis_title="Total activity")
    st.plotly_chart(fig6, use_container_width=True)

    fig7 = px.bar(
        seasonal, x="Season", y="Activity per Interval",
        title="Average Activity per Original 15-minute Record"
    )
    fig7.update_layout(height=350)
    st.plotly_chart(fig7, use_container_width=True)
    st.dataframe(seasonal, use_container_width=True, hide_index=True)

    st.subheader("Year-over-Year Activity Trend")
    yearly = filtered.groupby("Year").agg(
        Sales=("Sales Count", "sum"),
        Redemptions=("Redemption Count", "sum"),
        Activity=("Total Activity", "sum")
    ).reset_index()
    fig8 = px.line(
        yearly, x="Year", y="Activity", markers=True,
        title="Annual Ticket Activity Trend (selected period)"
    )
    fig8.update_layout(height=380)
    st.plotly_chart(fig8, use_container_width=True)

with tab4:
    st.subheader("Weekday vs Weekend")
    day_summary = filtered.groupby("Day Type").agg(
        Total_Activity=("Total Activity", "sum"),
        Average_Activity=("Total Activity", "mean"),
        Records=("Total Activity", "size")
    ).reset_index()
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(
            px.bar(day_summary, x="Day Type", y="Average_Activity",
                   title="Average Activity per 15-minute Record", text_auto=".2f"),
            use_container_width=True
        )
    with col_b:
        st.plotly_chart(
            px.bar(day_summary, x="Day Type", y="Total_Activity",
                   title="Total Activity by Day Type", text_auto=".3s"),
            use_container_width=True
        )
    st.dataframe(day_summary, use_container_width=True, hide_index=True)

    st.subheader("Morning, Afternoon and Evening")
    time_summary = filtered.groupby("Time Band", observed=False).agg(
        Total_Activity=("Total Activity", "sum"),
        Average_Activity=("Total Activity", "mean"),
        Records=("Total Activity", "size")
    ).reset_index()
    fig9 = px.bar(
        time_summary, x="Time Band", y="Average_Activity",
        title="Average Activity by Time Band", color="Time Band", text_auto=".2f"
    )
    fig9.update_layout(showlegend=False, height=360)
    st.plotly_chart(fig9, use_container_width=True)
    st.dataframe(time_summary, use_container_width=True, hide_index=True)

    st.subheader("Monthly Activity Pattern")
    monthly = filtered.groupby("Month").agg(
        Activity=("Total Activity", "sum")
    ).reset_index()
    monthly["Month Name"] = pd.to_datetime(monthly["Month"], format="%m").dt.strftime("%b")
    fig10 = px.bar(monthly, x="Month Name", y="Activity", title="Total Activity by Month")
    fig10.update_layout(height=350)
    st.plotly_chart(fig10, use_container_width=True)

with tab5:
    st.subheader("Data Quality and Consistency Checks")
    original = raw.copy()
    # Read quality counts saved during the original load. Do not read the
    # Streamlit UploadedFile again: its file pointer may already be at EOF.
    missing_timestamp = int(original.attrs.get("invalid_timestamp_count", 0))
    duplicate_timestamps = int(original.attrs.get("duplicate_timestamp_count", 0))
    negative_rows = int(original["Negative Count Flag"].sum())
    missing_counts = int(original.attrs.get("missing_count_values", 0))

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows after timestamp validation", f"{len(original):,}")
    q2.metric("Duplicate timestamps removed", f"{duplicate_timestamps:,}")
    q3.metric("Negative-count rows", f"{negative_rows:,}")
    q4.metric("Missing count values after cleaning", f"{missing_counts:,}")

    st.write("**Time interval consistency**")
    intervals = original["Timestamp"].sort_values().diff().dropna()
    if not intervals.empty:
        interval_table = intervals.value_counts().head(10).rename_axis("Time Gap").reset_index(name="Frequency")
        st.dataframe(interval_table, use_container_width=True, hide_index=True)
        expected = pd.Timedelta(minutes=15)
        irregular = int((intervals != expected).sum())
        st.metric("Gaps not equal to 15 minutes", f"{irregular:,}")
        st.caption("A non-15-minute gap can indicate a missing record, a data collection gap, or a different recording pattern.")
    else:
        st.info("Not enough records to inspect interval consistency.")

    st.write("**Extreme activity observations**")
    q_low = original["Total Activity"].quantile(0.25)
    q_high = original["Total Activity"].quantile(0.75)
    iqr = q_high - q_low
    upper_bound = q_high + 1.5 * iqr
    outliers = original[original["Total Activity"] > upper_bound][
        ["Timestamp", "Sales Count", "Redemption Count", "Total Activity"]
    ]
    st.metric("Potential high outlier records (IQR method)", f"{len(outliers):,}")
    st.dataframe(outliers.head(500), use_container_width=True, hide_index=True)
    st.caption("Outliers are flagged for investigation, not automatically deleted or replaced.")

with tab6:
    st.subheader("Key Findings and Operational Recommendations")
    peak_row = data.loc[data["Total Activity"].idxmax()]
    quiet_row = data.loc[data["Total Activity"].idxmin()]
    st.markdown(f"""
    **Observed in the selected filters:**
    - Highest activity interval: **{peak_row['Timestamp']}** with **{peak_row['Total Activity']:,.0f}** activity count.
    - Lowest activity interval: **{quiet_row['Timestamp']}** with **{quiet_row['Total Activity']:,.0f}** activity count.
    - High-activity alerts: **{high_count:,}** intervals using the selected threshold.
    - Sustained low-activity intervals: **{idle_count:,}** intervals using the selected low threshold.
    - Operational variability score: **{variability:.1f}%** (coefficient of variation of aggregated activity).
    """)

    st.markdown("### Recommendations")
    st.markdown("""
    1. **Review peak windows:** Compare high-activity timestamps with vessel schedules and actual passenger counts before changing deployment.
    2. **Review low-activity windows:** Consider whether schedules, staffing, or vessel assignments can be adjusted, while preserving required service frequency.
    3. **Plan seasonally:** Use summer, shoulder-season, and off-season patterns as an initial planning signal.
    4. **Improve data collection:** Join ticket records with trip IDs, vessel capacity, actual passenger counts, cancellations, staffing, and operating costs.
    5. **Monitor safety:** Never use ticket activity alone to determine whether a vessel is at or above its certified passenger capacity.
    """)

    st.subheader("Executive Summary")
    st.write(
        f"Across the selected period, the dataset records {total_sales:,.0f} ticket sales and "
        f"{total_redemptions:,.0f} redemptions, producing {total_activity:,.0f} combined ticket activity. "
        f"The selected activity thresholds identify {high_count:,} high-activity intervals and "
        f"{idle_count:,} sustained low-activity intervals. These findings can help prioritize operational "
        "reviews. Actual ferry capacity utilization and cost efficiency require vessel capacity, trip-level "
        "passenger, staffing, and cost data."
    )

    export = data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download aggregated analysis CSV",
        export, "ferry_operational_efficiency_analysis.csv", "text/csv"
    )

    st.download_button(
        "⬇️ Download filtered cleaned source data",
        filtered.to_csv(index=False).encode("utf-8"),
        "ferry_cleaned_filtered_data.csv", "text/csv"
    )

st.divider()
st.caption("Ferry Operational Efficiency Analytics | Ticket activity is a proxy measure; actual capacity utilization requires vessel and trip-level capacity data.")
