"""
FAST BOMBAS - Freezer Thermal Control System
Main Streamlit Dashboard Application
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import pandas as pd

from config_manager import ConfigManager
from data_simulator import TemperatureSimulator
from email_notifier import EmailNotifier
from data_logger import DataLogger

# Page configuration
st.set_page_config(
    page_title="FAST BOMBAS - Freezer Control",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-critical {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    if 'simulator' not in st.session_state:
        st.session_state.simulator = TemperatureSimulator(st.session_state.config_manager)
    
    if 'notifier' not in st.session_state:
        st.session_state.notifier = EmailNotifier(st.session_state.config_manager)
    
    if 'logger' not in st.session_state:
        st.session_state.logger = DataLogger(st.session_state.config_manager)
    
    if 'current_reading' not in st.session_state:
        st.session_state.current_reading = None
    
    if 'current_status' not in st.session_state:
        st.session_state.current_status = None
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

initialize_session_state()

# Get references to session objects
config = st.session_state.config_manager
simulator = st.session_state.simulator
notifier = st.session_state.notifier
logger = st.session_state.logger

def create_gauge_chart(value: float, title: str, min_val: float, max_val: float, 
                       critical_low: float, critical_high: float, 
                       normal_min: float, normal_max: float) -> go.Figure:
    """
    Create a gauge chart for temperature display
    
    Args:
        value: Current temperature value
        title: Chart title
        min_val: Minimum scale value
        max_val: Maximum scale value
        critical_low: Critical low threshold
        critical_high: Critical high threshold
        normal_min: Normal range minimum
        normal_max: Normal range maximum
        
    Returns:
        Plotly figure object
    """
    # Determine color based on value
    if value < critical_low or value > critical_high:
        color = "#dc3545"  # Red for critical
    elif value < normal_min or value > normal_max:
        color = "#ffc107"  # Yellow for warning
    else:
        color = "#28a745"  # Green for OK
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        number={'suffix': "°C", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, critical_low], 'color': '#ffebee'},
                {'range': [critical_low, normal_min], 'color': '#fff9c4'},
                {'range': [normal_min, normal_max], 'color': '#e8f5e9'},
                {'range': [normal_max, critical_high], 'color': '#fff9c4'},
                {'range': [critical_high, max_val], 'color': '#ffebee'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': critical_high
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333", 'family': "Arial"}
    )
    
    return fig

def create_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a trend chart for temperature history
    
    Args:
        df: DataFrame with historical temperature data
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    if not df.empty:
        # Evaporator temperature
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['evaporator_temp'],
            mode='lines+markers',
            name='Evaporator',
            line=dict(color='#2196f3', width=2),
            marker=dict(size=6)
        ))
        
        # Condenser temperature
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['condenser_temp'],
            mode='lines+markers',
            name='Condenser',
            line=dict(color='#ff9800', width=2),
            marker=dict(size=6)
        ))
        
        # Ambient temperature
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ambient_temp'],
            mode='lines+markers',
            name='Ambient',
            line=dict(color='#4caf50', width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Temperature Trend (Last 30 Readings)",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        height=400,
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    
    return fig

def get_status_badge(status: str) -> str:
    """
    Get HTML badge for status
    
    Args:
        status: Status string (OK, WARNING, CRITICAL)
        
    Returns:
        HTML string for status badge
    """
    if status == 'OK':
        return '<span class="status-ok">✓ OK</span>'
    elif status == 'WARNING':
        return '<span class="status-warning">⚠ WARNING</span>'
    else:
        return '<span class="status-critical">🚨 CRITICAL</span>'

def update_data():
    """Update temperature reading and process alerts"""
    # Get new reading
    reading = simulator.get_reading()
    status = simulator.get_status(reading)
    
    # Log the reading
    logger.log_reading(reading, status)
    
    # Check for critical status and send alert
    if status['overall'] == 'CRITICAL':
        notifier.send_alert(reading, status)
    
    # Update session state
    st.session_state.current_reading = reading
    st.session_state.current_status = status
    st.session_state.last_update = datetime.now()

# Main Dashboard
def main_dashboard():
    """Main dashboard page"""
    
    # Header
    dashboard_title = config.get('ui_settings', 'dashboard_title')
    st.markdown(f'<div class="main-header">❄️ {dashboard_title}</div>', unsafe_allow_html=True)
    
    # Update data
    update_data()
    
    reading = st.session_state.current_reading
    status = st.session_state.current_status
    
    if reading is None or status is None:
        st.warning("Waiting for data...")
        return
    
    # System Status Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Status", status['overall'], 
                 delta="Active" if status['overall'] == 'OK' else "Alert")
    
    with col2:
        st.metric("Last Update", 
                 st.session_state.last_update.strftime("%H:%M:%S"))
    
    with col3:
        freezer_location = config.get('freezer_info', 'location')
        st.metric("Location", freezer_location)
    
    with col4:
        if reading.get('failure_mode', False):
            st.metric("Mode", "FAILURE SIMULATION", delta="Warning", delta_color="inverse")
        else:
            st.metric("Mode", "Normal Operation", delta="OK")
    
    st.markdown("---")
    
    # Temperature Gauges
    st.subheader("📊 Current Temperature Readings")
    
    col1, col2, col3 = st.columns(3)
    
    # Evaporator gauge
    with col1:
        evap_thresholds = config.get('temperature_thresholds', 'evaporator')
        fig_evap = create_gauge_chart(
            reading['evaporator_temp'],
            "Evaporator Zone",
            evap_thresholds['critical_low'] - 5,
            evap_thresholds['critical_high'] + 5,
            evap_thresholds['critical_low'],
            evap_thresholds['critical_high'],
            evap_thresholds['min'],
            evap_thresholds['max']
        )
        st.plotly_chart(fig_evap, use_container_width=True)
        st.markdown(f"Status: {get_status_badge(status['evaporator'])}", unsafe_allow_html=True)
    
    # Condenser gauge
    with col2:
        cond_thresholds = config.get('temperature_thresholds', 'condenser')
        fig_cond = create_gauge_chart(
            reading['condenser_temp'],
            "Condenser Zone",
            cond_thresholds['critical_low'] - 5,
            cond_thresholds['critical_high'] + 10,
            cond_thresholds['critical_low'],
            cond_thresholds['critical_high'],
            cond_thresholds['min'],
            cond_thresholds['max']
        )
        st.plotly_chart(fig_cond, use_container_width=True)
        st.markdown(f"Status: {get_status_badge(status['condenser'])}", unsafe_allow_html=True)
    
    # Ambient gauge
    with col3:
        amb_thresholds = config.get('temperature_thresholds', 'ambient')
        fig_amb = create_gauge_chart(
            reading['ambient_temp'],
            "Ambient Zone",
            amb_thresholds['critical_low'] - 5,
            amb_thresholds['critical_high'] + 5,
            amb_thresholds['critical_low'],
            amb_thresholds['critical_high'],
            amb_thresholds['min'],
            amb_thresholds['max']
        )
        st.plotly_chart(fig_amb, use_container_width=True)
        st.markdown(f"Status: {get_status_badge(status['ambient'])}", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Temperature Trend Chart
    st.subheader("📈 Temperature History")
    
    max_points = config.get('data_collection', 'max_data_points_display')
    recent_df = logger.get_recent_readings(max_points)
    
    if not recent_df.empty:
        trend_fig = create_trend_chart(recent_df)
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("No historical data available yet. Data will appear as readings are collected.")
    
    # Alert History
    if config.get('ui_settings', 'show_advanced_metrics'):
        st.markdown("---")
        st.subheader("🚨 Recent Alerts")
        
        alerts = logger.get_alert_history(hours=2)
        
        if alerts:
            alert_df = pd.DataFrame(alerts)
            alert_df['timestamp'] = pd.to_datetime(alert_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(alert_df, use_container_width=True)
        else:
            st.success("No alerts in the last 2 hours - System operating normally!")
    
    # Auto-refresh
    refresh_interval = config.get('data_collection', 'chart_refresh_interval_seconds')
    time.sleep(refresh_interval)
    st.rerun()

# Sidebar Navigation
st.sidebar.title("🎛️ Navigation")
page = st.sidebar.radio("Select Page", 
                        ["Dashboard", "Configuration", "Data Export", "System Info"])

if page == "Dashboard":
    main_dashboard()
    
elif page == "Configuration":
    from config_panel import show_configuration_panel
    show_configuration_panel(config)
    
elif page == "Data Export":
    from data_export_panel import show_data_export_panel
    show_data_export_panel(logger, config)
    
elif page == "System Info":
    from system_info_panel import show_system_info_panel
    show_system_info_panel(config, simulator, notifier, logger)
