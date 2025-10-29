"""
System Information Panel Module
Displays system status, diagnostics, and information
"""

import streamlit as st
from datetime import datetime
import os
from config_manager import ConfigManager
from data_simulator import TemperatureSimulator
from email_notifier import EmailNotifier
from data_logger import DataLogger

def show_system_info_panel(config: ConfigManager, simulator: TemperatureSimulator, 
                           notifier: EmailNotifier, logger: DataLogger):
    """
    Display system information and diagnostics
    
    Args:
        config: Configuration manager instance
        simulator: Temperature simulator instance
        notifier: Email notifier instance
        logger: Data logger instance
    """
    st.title("ℹ️ System Information")
    st.markdown("System status, diagnostics, and technical information")
    
    # System Status
    st.subheader("🔌 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Configuration", "✓ Loaded")
        config_file_exists = os.path.exists('freezer_config.json')
        st.metric("Config File", "✓ Found" if config_file_exists else "✗ Not Found")
    
    with col2:
        csv_path = config.get('data_logging', 'csv_file_path')
        csv_exists = os.path.exists(csv_path)
        st.metric("Data Logger", "✓ Active" if csv_exists else "⚠ No Data Yet")
        
        if csv_exists:
            file_size = os.path.getsize(csv_path)
            st.metric("Log File Size", f"{file_size / 1024:.2f} KB")
    
    with col3:
        email_configured = (
            config.get('email_config', 'sender_email') and
            config.get('email_config', 'sender_password') and
            len(config.get('email_config', 'recipient_emails')) > 0
        )
        st.metric("Email Alerts", "✓ Configured" if email_configured else "⚠ Not Configured")
        st.metric("Simulator", "✓ Running")
    
    st.markdown("---")
    
    # Freezer Information
    st.subheader("🏭 Freezer Information")
    
    info_data = {
        "Model": config.get('freezer_info', 'model_name'),
        "Location": config.get('freezer_info', 'location'),
        "Operator": config.get('freezer_info', 'operator_name'),
        "Contact": config.get('freezer_info', 'operator_contact'),
    }
    
    for label, value in info_data.items():
        st.text(f"{label}: {value}")
    
    st.markdown("---")
    
    # Configuration Summary
    st.subheader("⚙️ Configuration Summary")
    
    config_tabs = st.tabs(["Temperature Limits", "Data Collection", "Alerts", "Logging"])
    
    with config_tabs[0]:
        st.markdown("**Evaporator Zone**")
        evap = config.get('temperature_thresholds', 'evaporator')
        st.text(f"Normal Range: {evap['min']}°C to {evap['max']}°C")
        st.text(f"Critical Limits: {evap['critical_low']}°C to {evap['critical_high']}°C")
        
        st.markdown("**Condenser Zone**")
        cond = config.get('temperature_thresholds', 'condenser')
        st.text(f"Normal Range: {cond['min']}°C to {cond['max']}°C")
        st.text(f"Critical Limits: {cond['critical_low']}°C to {cond['critical_high']}°C")
        
        st.markdown("**Ambient Zone**")
        amb = config.get('temperature_thresholds', 'ambient')
        st.text(f"Normal Range: {amb['min']}°C to {amb['max']}°C")
        st.text(f"Critical Limits: {amb['critical_low']}°C to {amb['critical_high']}°C")
    
    with config_tabs[1]:
        st.text(f"Reading Interval: {config.get('data_collection', 'reading_interval_seconds')} seconds")
        st.text(f"Refresh Interval: {config.get('data_collection', 'chart_refresh_interval_seconds')} seconds")
        st.text(f"Chart Data Points: {config.get('data_collection', 'max_data_points_display')}")
        st.text(f"Max Historical Records: {config.get('data_collection', 'max_historical_records')}")
    
    with config_tabs[2]:
        alerts_enabled = "Enabled" if config.get('alert_settings', 'enable_email_alerts') else "Disabled"
        st.text(f"Email Alerts: {alerts_enabled}")
        st.text(f"Alert Cooldown: {config.get('alert_settings', 'alert_cooldown_seconds')} seconds")
        st.text(f"Trigger Threshold: {config.get('alert_settings', 'consecutive_readings_trigger')} readings")
        
        if email_configured:
            st.text(f"SMTP Server: {config.get('email_config', 'smtp_server')}:{config.get('email_config', 'smtp_port')}")
            st.text(f"Sender: {config.get('email_config', 'sender_email')}")
            st.text(f"Recipients: {len(config.get('email_config', 'recipient_emails'))}")
    
    with config_tabs[3]:
        logging_enabled = "Enabled" if config.get('data_logging', 'enable_csv_logging') else "Disabled"
        st.text(f"CSV Logging: {logging_enabled}")
        st.text(f"Log File: {config.get('data_logging', 'csv_file_path')}")
        st.text(f"Retention: {config.get('data_logging', 'retention_days')} days")
    
    st.markdown("---")
    
    # Simulator Status
    st.subheader("🔬 Simulator Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text(f"Failure Mode: {'Active' if simulator.failure_mode else 'Inactive'}")
        st.text(f"Failure Probability: {config.get('simulation', 'failure_probability') * 100}%")
        st.text(f"Failure Duration: {config.get('simulation', 'failure_duration_seconds')}s")
    
    with col2:
        st.text(f"Normal Range: {config.get('simulation', 'normal_temp_evaporator_min')}°C to {config.get('simulation', 'normal_temp_evaporator_max')}°C")
        st.text(f"Temperature Variation: ±{config.get('simulation', 'temp_variation_range')}°C")
    
    st.markdown("**Last Recorded Temperatures:**")
    for zone, temp in simulator.last_temperatures.items():
        st.text(f"{zone.capitalize()}: {temp:.2f}°C")
    
    if st.button("Reset Simulator", key="reset_simulator"):
        simulator.reset_simulator()
        st.success("✓ Simulator reset to initial state")
    
    st.markdown("---")
    
    # System Diagnostics
    st.subheader("🔍 System Diagnostics")
    
    diagnostics = {
        "Config File": "✓ OK" if os.path.exists('freezer_config.json') else "✗ Missing",
        "Data Directory": "✓ OK" if os.path.exists('data') else "⚠ Not Created",
        "Export Directory": "✓ OK" if os.path.exists('exports') else "⚠ Not Created",
        "CSV Log File": "✓ OK" if csv_exists else "⚠ Not Created",
    }
    
    for check, status in diagnostics.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(check)
        with col2:
            if "✓" in status:
                st.success(status)
            elif "⚠" in status:
                st.warning(status)
            else:
                st.error(status)
    
    st.markdown("---")
    
    # About Section
    st.subheader("📖 About")
    
    st.markdown("""
    **FAST BOMBAS - Freezer Thermal Control System**
    
    Version: 1.0.0
    
    A comprehensive Python-based monitoring system for industrial freezers featuring:
    - Real-time temperature monitoring across multiple zones
    - Automated email alerts for critical conditions
    - Historical data logging and export capabilities
    - Fully configurable thresholds and settings
    - Professional dashboard interface built with Streamlit
    
    **Components:**
    - Configuration Manager: Handles all system settings with JSON persistence
    - Data Simulator: Generates realistic temperature data for testing
    - Email Notifier: Sends automated alerts via SMTP
    - Data Logger: Manages CSV logging and historical data
    - Dashboard: Interactive web interface for monitoring and control
    
    **System Requirements:**
    - Python 3.11+
    - Streamlit
    - Plotly
    - Pandas
    
    ---
    
    *Developed for FAST BOMBAS industrial freezer monitoring*
    """)
    
    st.markdown("---")
    
    # System Metadata
    with st.expander("📋 System Metadata"):
        metadata = config.get('system_metadata')
        st.json(metadata)
