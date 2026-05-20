import streamlit as st
import pandas as pd
import numpy as np
import random
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# =========================
# Page Config - Enhanced for larger display
# =========================
st.set_page_config(
    page_title="PowerGuard Enterprise | AI Anomaly Detection & Real-Time Monitoring",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look and larger elements
st.markdown("""
<style>
    /* Main container padding */
    .main > div {
        padding: 0rem 1rem;
    }
    
    /* Headers */
    h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }
    
    /* Subheader styling */
    .stSubheader {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
    }
    
    /* Dataframe font size */
    .stDataFrame {
        font-size: 1rem !important;
    }
    
    /* Metric text size */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    
    /* Animation for alerts */
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .alert-animation {
        animation: slideIn 0.5s ease-out;
    }
    
    .live-indicator {
        animation: pulse 2s infinite;
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #ff4444;
        margin-right: 8px;
    }
    
    /* Card hover effect */
    .stMetric {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Session State Initialization
# =========================
if "running" not in st.session_state:
    st.session_state.running = False

if "realtime_data" not in st.session_state:
    st.session_state.realtime_data = []

if "alert_history" not in st.session_state:
    st.session_state.alert_history = []

if "user_feedback" not in st.session_state:
    st.session_state.user_feedback = {}

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# =========================
# REAL TIME SIMULATION FUNCTIONS
# =========================
def generate_realtime_sample():
    """Generate real-time sensor data with anomaly injection"""
    consumption = random.uniform(2, 4)

    # anomaly injection (12% chance)
    if random.random() < 0.12:
        consumption = random.uniform(6, 10)

    temperature = random.uniform(20, 35)
    humidity = random.uniform(30, 70)
    wind_speed = random.uniform(0, 10)
    voltage = random.uniform(210, 240)
    current = random.uniform(10, 20)

    if consumption >= 7:
        status = "CRITICAL ANOMALY"
        risk = "High"
        alert_level = "Critical"
    elif consumption >= 5:
        status = "SUSPICIOUS"
        risk = "Medium"
        alert_level = "Warning"
    else:
        status = "NORMAL"
        risk = "Low"
        alert_level = "Info"

    return {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "FullDateTime": datetime.now(),
        "Consumption (kW)": round(consumption, 2),
        "Temperature (°C)": round(temperature, 2),
        "Humidity (%)": round(humidity, 2),
        "Wind Speed (m/s)": round(wind_speed, 2),
        "Voltage (V)": round(voltage, 2),
        "Current (A)": round(current, 2),
        "Status": status,
        "Risk Level": risk,
        "Alert Level": alert_level,
        "Model": "Real-time AI v3.0",
        "Confidence Score": round(random.uniform(0.85, 0.99), 3)
    }

# =========================
# Load Historical Data with caching
# =========================
@st.cache_data
def load_historical_data():
    try:
        df = pd.read_csv("powerguard_results_v1_20260419_1007.csv")
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.warning("⚠️ Historical data file 'powerguard_results_v1_20260419_1007.csv' not found. Running in real-time only mode.")
        return None

@st.cache_data
def get_data_summary(df):
    """Generate comprehensive data summary"""
    if df is None:
        return {}
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "memory_usage": df.memory_usage(deep=True).sum() / 1024**2,
        "duplicate_rows": df.duplicated().sum(),
        "missing_values": df.isnull().sum().sum(),
        "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
        "categorical_columns": len(df.select_dtypes(include=['object']).columns)
    }
    return summary

@st.cache_data
def generate_statistics(df, status_col):
    """Generate advanced statistics"""
    stats = {}
    if df is not None and status_col and status_col in df.columns and len(df) > 0:
        status_counts = df[status_col].value_counts()
        stats["status_distribution"] = status_counts.to_dict()
        anomaly_keywords = ["Anomaly", "CRITICAL ANOMALY", "Anomaly Detected"]
        anomaly_count = 0
        for keyword in anomaly_keywords:
            anomaly_count += status_counts.get(keyword, 0)
        stats["anomaly_rate"] = (anomaly_count / len(df)) * 100 if len(df) > 0 else 0
    return stats

# Load historical data
historical_df = load_historical_data()

# =========================
# Helper Functions
# =========================
def find_col(possible_names, df):
    """Find column by possible names"""
    if df is None:
        return None
    for col in df.columns:
        for name in possible_names:
            if name.lower() in col.lower():
                return col
    return None

def find_numeric_cols(df):
    """Get numeric columns"""
    if df is None:
        return []
    return df.select_dtypes(include=[np.number]).columns.tolist()

# =========================
# Title Section
# =========================
col_logo, col_title, col_settings = st.columns([1, 8, 1])
with col_title:
    st.title("⚡ PowerGuard Enterprise")
    st.markdown("### AI-Powered Electricity Anomaly Detection & Predictive Intelligence Platform")
    if st.session_state.running:
        st.markdown('<span class="live-indicator"></span> **LIVE MONITORING ACTIVE**', unsafe_allow_html=True)
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_settings:
    if st.button("⚙️ Settings", use_container_width=True):
        with st.expander("Settings"):
            st.session_state.dark_mode = st.toggle("Dark Mode", st.session_state.dark_mode)
            if st.session_state.dark_mode:
                st.markdown("""
                <style>
                    .stApp {
                        background-color: #1e1e1e;
                        color: #ffffff;
                    }
                </style>
                """, unsafe_allow_html=True)

st.divider()

# =========================
# MODE SELECTION
# =========================
mode = st.radio(
    "Select Operating Mode",
    ["🔴 Real-Time Monitoring", "📊 Historical Analytics", "📈 Hybrid View (Live + Historical)"],
    horizontal=True
)

st.divider()

# =========================
# REAL-TIME MONITORING SECTION
# =========================
if mode in ["🔴 Real-Time Monitoring", "📈 Hybrid View (Live + Historical)"]:
    st.header("🔴 Live Real-Time Data Stream")
    
    # Control buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("▶ START SYSTEM", use_container_width=True):
            st.session_state.running = True
    with col2:
        if st.button("⛔ STOP SYSTEM", use_container_width=True):
            st.session_state.running = False
    with col3:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.realtime_data = []
            st.rerun()
    with col4:
        if st.button("📥 Export Live Data", use_container_width=True):
            if len(st.session_state.realtime_data) > 0:
                rt_df_export = pd.DataFrame(st.session_state.realtime_data)
                csv = rt_df_export.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "live_data_export.csv", "text/csv")
    
    # Real-time display placeholder
    realtime_placeholder = st.empty()
    
    # Run real-time simulation
    if st.session_state.running:
        status_text = st.empty()
        
        for i in range(500):
            if not st.session_state.running:
                break
            
            new_row = generate_realtime_sample()
            st.session_state.realtime_data.append(new_row)
            
            if len(st.session_state.realtime_data) > 200:
                st.session_state.realtime_data = st.session_state.realtime_data[-200:]
            
            rt_df = pd.DataFrame(st.session_state.realtime_data)
            status_text.info(f"🟢 Live streaming active... {len(rt_df)} readings collected")
            
            with realtime_placeholder.container():
                total_rt = len(rt_df)
                normal_rt = len(rt_df[rt_df["Status"] == "NORMAL"])
                suspicious_rt = len(rt_df[rt_df["Status"] == "SUSPICIOUS"])
                anomaly_rt = len(rt_df[rt_df["Status"] == "CRITICAL ANOMALY"])
                
                if anomaly_rt > 0 and (len(st.session_state.alert_history) == 0 or 
                   st.session_state.alert_history[-1].get('anomaly_count', 0) != anomaly_rt):
                    st.session_state.alert_history.append({
                        'timestamp': datetime.now(),
                        'message': f"🚨 New anomaly detected! Total: {anomaly_rt}",
                        'type': 'anomaly',
                        'anomaly_count': anomaly_rt
                    })
                
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("📊 Live Readings", total_rt)
                c2.metric("✅ Normal", normal_rt)
                c3.metric("⚠️ Suspicious", suspicious_rt)
                c4.metric("🚨 Anomalies", anomaly_rt, delta="⚠️" if anomaly_rt>0 else None, delta_color="inverse")
                c5.metric("🎯 Confidence", f"{rt_df['Confidence Score'].mean():.1%}" if total_rt>0 else "N/A")
                
                if anomaly_rt > 0:
                    st.error(f"🚨 CRITICAL ALERT: {anomaly_rt} anomalies detected!", icon="🚨")
                elif suspicious_rt > 3:
                    st.warning(f"⚠️ Suspicious activity: {suspicious_rt} cases", icon="⚠️")
                else:
                    st.success("✅ System Stable", icon="✅")
                
                colA, colB = st.columns(2)
                with colA:
                    fig_pie = px.pie(rt_df, names="Status", title="Live Status Distribution", hole=0.3)
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with colB:
                    fig_line = px.line(rt_df, x="Timestamp", y="Consumption (kW)", title="Live Energy Consumption", markers=True)
                    fig_line.add_hline(y=5, line_dash="dash", line_color="orange", annotation_text="Warning")
                    fig_line.add_hline(y=7, line_dash="dash", line_color="red", annotation_text="Critical")
                    fig_line.update_layout(height=400)
                    st.plotly_chart(fig_line, use_container_width=True)
                
                colC, colD = st.columns(2)
                with colC:
                    fig_env = px.line(rt_df, x="Timestamp", y=["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"],
                                     title="Environmental Factors")
                    fig_env.update_layout(height=400)
                    st.plotly_chart(fig_env, use_container_width=True)
                with colD:
                    fig_elec = px.line(rt_df, x="Timestamp", y=["Voltage (V)", "Current (A)"],
                                      title="Electrical Metrics")
                    fig_elec.update_layout(height=400)
                    st.plotly_chart(fig_elec, use_container_width=True)
                
                st.subheader("📡 Live Data Stream")
                st.dataframe(rt_df.tail(15), use_container_width=True, height=400)
            
            time.sleep(1)
        
        status_text.info("✅ Live monitoring session completed")
    
    elif mode == "🔴 Real-Time Monitoring":
        st.info("Press **START SYSTEM** to activate real-time monitoring ⚡")
        if len(st.session_state.realtime_data) > 0:
            st.subheader("📊 Last Session Data")
            rt_df_last = pd.DataFrame(st.session_state.realtime_data)
            st.dataframe(rt_df_last.tail(20), use_container_width=True)

# =========================
# HISTORICAL ANALYTICS SECTION
# =========================
if mode in ["📊 Historical Analytics", "📈 Hybrid View (Live + Historical)"] and historical_df is not None:
    st.header("📊 Historical Data Analytics")
    
    df = historical_df.copy()
    
    # Auto-detect columns
    status_col = find_col(["status", "final", "classification", "result"], df)
    risk_col = find_col(["risk", "risk_level", "severity"], df)
    model_col = find_col(["model", "algorithm", "predictor"], df)
    confidence_col = find_col(["confidence", "score", "probability"], df)
    timestamp_col = find_col(["timestamp", "datetime", "date", "time"], df)
    
    if status_col is None:
        st.error("❌ No Status/Classification column found in historical dataset")
        st.write("📌 Available columns:", df.columns.tolist())
    else:
        # Sidebar filters
        with st.sidebar:
            st.image("https://img.icons8.com/fluency/96/lightning-bolt.png", width=80)
            st.markdown("## 🔍 Historical Data Filters")
            st.markdown("---")
            
            st.markdown("### 📊 Filter by Status")
            status_options = ["All"] + df[status_col].dropna().unique().tolist()
            selected_status = st.selectbox("Select Status", status_options, key="hist_status", index=0)
            
            if risk_col:
                st.markdown("### ⚠️ Risk Level")
                risk_options = ["All"] + sorted(df[risk_col].dropna().unique().tolist())
                selected_risk = st.selectbox("Select Risk Level", risk_options, key="hist_risk", index=0)
            else:
                selected_risk = "All"
            
            if model_col:
                st.markdown("### 🤖 Model Type")
                model_options = ["All"] + df[model_col].dropna().unique().tolist()
                selected_model = st.selectbox("Select Model", model_options, key="hist_model", index=0)
            else:
                selected_model = "All"
            
            if confidence_col:
                st.markdown("### 🎯 Confidence Threshold")
                confidence_threshold = st.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.05, key="conf_thresh")
            else:
                confidence_threshold = 0.0
            
            st.markdown("---")
            
            # Date filter
            if timestamp_col:
                st.markdown("### 📅 Time Range")
                try:
                    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
                    min_date = df[timestamp_col].min()
                    max_date = df[timestamp_col].max()
                    date_range = st.date_input("Select Date Range", [min_date, max_date], 
                                               min_value=min_date, max_value=max_date, key="date_range")
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        df = df[(df[timestamp_col].dt.date >= start_date) & (df[timestamp_col].dt.date <= end_date)]
                except:
                    pass
            
            st.markdown("---")
            st.caption("PowerGuard v3.0 | Enterprise Edition")
        
        # Apply filters
        filtered_df = df.copy()
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df[status_col] == selected_status]
        if selected_risk != "All" and risk_col:
            filtered_df = filtered_df[filtered_df[risk_col] == selected_risk]
        if selected_model != "All" and model_col:
            filtered_df = filtered_df[filtered_df[model_col] == selected_model]
        if confidence_col and confidence_threshold > 0:
            filtered_df = filtered_df[filtered_df[confidence_col] >= confidence_threshold]
        
        # Data summary
        data_summary = get_data_summary(filtered_df)
        stats = generate_statistics(filtered_df, status_col)
        
        # KPIs
        total_hist = len(filtered_df)
        normal_hist = len(filtered_df[filtered_df[status_col].str.contains("Normal", case=False, na=False)])
        suspicious_hist = len(filtered_df[filtered_df[status_col].str.contains("Suspicious", case=False, na=False)])
        anomaly_hist = len(filtered_df[filtered_df[status_col].str.contains("Anomaly", case=False, na=False)])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", f"{total_hist:,}")
        with col2:
            st.metric("✅ Normal", f"{normal_hist:,}")
        with col3:
            st.metric("⚠️ Suspicious", f"{suspicious_hist:,}")
        with col4:
            st.metric("🚨 Anomalies", f"{anomaly_hist:,}")
        
        if risk_col:
            col5, col6, col7, col8 = st.columns(4)
            risk_counts = filtered_df[risk_col].value_counts()
            with col5:
                st.metric("🔴 High Risk", risk_counts.get("High", 0) + risk_counts.get("Very High", 0))
            with col6:
                st.metric("🟡 Medium Risk", risk_counts.get("Medium", 0))
            with col7:
                st.metric("🟢 Low Risk", risk_counts.get("Low", 0))
            with col8:
                st.metric("💀 Critical", risk_counts.get("Critical", 0))
        
        st.divider()
        
        # Tabs for historical analysis
        hist_tab1, hist_tab2, hist_tab3, hist_tab4, hist_tab5 = st.tabs(
            ["📈 Analytics", "📋 Data Explorer", "🚨 Risk Analysis", "🤖 Model Performance", "📊 Trends"]
        )
        
        with hist_tab1:
            col_left, col_right = st.columns([2, 1])
            with col_left:
                status_counts = filtered_df[status_col].value_counts()
                fig_pie = px.pie(values=status_counts.values, names=status_counts.index, 
                               title="Status Distribution", hole=0.4)
                fig_pie.update_layout(height=500)
                st.plotly_chart(fig_pie, use_container_width=True)
                
                fig_bar = px.bar(x=status_counts.index, y=status_counts.values, 
                               title="Status Counts", color=status_counts.index)
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_right:
                if confidence_col:
                    avg_conf = filtered_df[confidence_col].mean()
                    st.metric("Average Confidence", f"{avg_conf:.1%}")
                    st.progress(avg_conf)
                
                health_score = 100 - (anomaly_hist/total_hist*2 if total_hist>0 else 0)
                health_score = max(0, min(100, health_score))
                st.metric("System Health", f"{health_score:.0f}/100")
                
                if anomaly_hist > total_hist * 0.1:
                    st.error("🚨 High anomaly rate detected!")
                elif suspicious_hist > total_hist * 0.2:
                    st.warning("⚠️ Elevated suspicious activities")
                else:
                    st.success("✅ System operating normally")
        
        with hist_tab2:
            st.subheader("Historical Data Explorer")
            
            # Data quality report
            with st.expander("📊 Data Quality Report", expanded=False):
                col_q1, col_q2, col_q3, col_q4 = st.columns(4)
                with col_q1:
                    st.metric("Missing Values", data_summary.get('missing_values', 0))
                with col_q2:
                    st.metric("Duplicate Rows", data_summary.get('duplicate_rows', 0))
                with col_q3:
                    st.metric("Memory Usage", f"{data_summary.get('memory_usage', 0):.2f} MB")
                with col_q4:
                    completeness = (1 - data_summary.get('missing_values', 0)/(data_summary.get('total_rows', 1)*data_summary.get('total_columns', 1)))*100 if data_summary.get('total_rows', 0) > 0 else 100
                    st.metric("Data Completeness", f"{completeness:.1f}%")
            
            all_cols = filtered_df.columns.tolist()
            selected_cols = st.multiselect("Select Columns to Display", all_cols, default=all_cols[:min(6, len(all_cols))])
            display_df = filtered_df[selected_cols] if selected_cols else filtered_df
            
            search_term = st.text_input("🔍 Search", placeholder="Enter search term...")
            if search_term:
                mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                display_df = display_df[mask]
                st.info(f"Found {len(display_df)} records")
            
            page_size = st.selectbox("Rows per page", [10, 25, 50, 100], key="hist_page")
            page_number = st.number_input("Page", min_value=1, value=1, key="hist_page_num")
            start_idx = (page_number - 1) * page_size
            st.dataframe(display_df.iloc[start_idx:start_idx + page_size], use_container_width=True, height=400)
            
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Historical Data", csv, "historical_export.csv", "text/csv")
        
        with hist_tab3:
            if risk_col:
                st.subheader("Risk Analysis Dashboard")
                high_risk_df = filtered_df[filtered_df[risk_col].isin(["High", "Very High", "Critical"])]
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    risk_dist = filtered_df[risk_col].value_counts()
                    fig_risk = px.bar(x=risk_dist.index, y=risk_dist.values, title="Risk Distribution")
                    st.plotly_chart(fig_risk, use_container_width=True)
                with col_r2:
                    st.metric("Total High Risk Cases", len(high_risk_df))
                    if len(high_risk_df) > 0:
                        st.dataframe(high_risk_df.head(20), use_container_width=True)
            else:
                st.info("Risk column not available")
        
        with hist_tab4:
            if model_col:
                model_counts = filtered_df[model_col].value_counts()
                fig_model = px.bar(x=model_counts.index, y=model_counts.values, title="Model Distribution")
                st.plotly_chart(fig_model, use_container_width=True)
                
                if confidence_col:
                    fig_box = px.box(filtered_df, x=model_col, y=confidence_col, title="Confidence by Model")
                    st.plotly_chart(fig_box, use_container_width=True)
                
                model_status = pd.crosstab(filtered_df[model_col], filtered_df[status_col])
                fig_heat = px.imshow(model_status, text_auto=True, aspect="auto", title="Model vs Status Matrix")
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("Model information not available")
        
        with hist_tab5:
            if timestamp_col:
                try:
                    filtered_df[timestamp_col] = pd.to_datetime(filtered_df[timestamp_col])
                    time_series = filtered_df.set_index(timestamp_col).resample('D').size()
                    
                    fig_trend = px.line(x=time_series.index, y=time_series.values, title="Activity Trend")
                    fig_trend.add_scatter(x=time_series.index, y=time_series.rolling(window=7).mean(),
                                         name='7-Day MA', line=dict(color='red', dash='dash'))
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # Simple forecast
                    last_7_days = time_series.tail(7).mean()
                    forecast_dates = pd.date_range(start=time_series.index[-1] + pd.Timedelta(days=1), periods=7)
                    fig_forecast = go.Figure()
                    fig_forecast.add_trace(go.Scatter(x=time_series.index[-30:], y=time_series.values[-30:],
                                                     mode='lines+markers', name='Historical'))
                    fig_forecast.add_trace(go.Scatter(x=forecast_dates, y=[last_7_days]*7,
                                                     mode='lines+markers', name='Forecast',
                                                     line=dict(color='red', dash='dash')))
                    fig_forecast.update_layout(title="7-Day Forecast", height=400)
                    st.plotly_chart(fig_forecast, use_container_width=True)
                except Exception as e:
                    st.info("Trend analysis not available")
            else:
                st.info("Timestamp column not available for trend analysis")

# =========================
# HYBRID VIEW COMPARISON
# =========================
if mode == "📈 Hybrid View (Live + Historical)" and len(st.session_state.realtime_data) > 0 and historical_df is not None and status_col:
    st.divider()
    st.header("📊 Live vs Historical Comparison")
    
    rt_df = pd.DataFrame(st.session_state.realtime_data)
    rt_anomaly_rate = (len(rt_df[rt_df["Status"] == "CRITICAL ANOMALY"]) / len(rt_df) * 100) if len(rt_df) > 0 else 0
    hist_anomaly_rate = stats.get('anomaly_rate', 0) if 'stats' in locals() else 0
    
    col_comp1, col_comp2, col_comp3 = st.columns(3)
    with col_comp1:
        st.metric("Real-Time Anomaly Rate", f"{rt_anomaly_rate:.1f}%")
    with col_comp2:
        st.metric("Historical Anomaly Rate", f"{hist_anomaly_rate:.1f}%")
    with col_comp3:
        diff = rt_anomaly_rate - hist_anomaly_rate
        st.metric("Difference", f"{diff:+.1f}%", delta=f"{diff:+.1f}%", delta_color="inverse" if diff > 0 else "normal")
    
    if rt_anomaly_rate > hist_anomaly_rate * 1.5:
        st.warning("⚠️ Real-time anomaly rate is significantly higher than historical average! Investigation recommended.")
        st.session_state.alert_history.append({
            'timestamp': datetime.now(),
            'message': f"⚠️ Real-time anomaly rate ({rt_anomaly_rate:.1f}%) exceeds historical average ({hist_anomaly_rate:.1f}%)",
            'type': 'warning'
        })

# =========================
# ALERT HISTORY
# =========================
if st.session_state.alert_history:
    st.divider()
    with st.expander("📜 Alert History", expanded=False):
        for alert in st.session_state.alert_history[-20:]:
            timestamp = alert['timestamp'].strftime('%H:%M:%S') if isinstance(alert['timestamp'], datetime) else str(alert['timestamp'])
            st.caption(f"{timestamp} - {alert['message']}")

# =========================
# FOOTER
# =========================
st.markdown("---")
footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)
with footer_col1:
    st.caption("⚡ PowerGuard Enterprise Edition v3.0")
with footer_col2:
    st.caption("🔒 AI-Powered Anomaly Detection")
with footer_col3:
    st.caption(f"📊 Real-Time: {len(st.session_state.realtime_data)} records")
with footer_col4:
    st.caption(f"🎯 Last update: {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh button
if st.button("🔄 Refresh All Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()