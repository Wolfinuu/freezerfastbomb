"""
Configuration Panel Module
Provides UI for adjusting all system settings
"""

import streamlit as st
from config_manager import ConfigManager

def show_configuration_panel(config: ConfigManager):
    """
    Display configuration panel for all system settings
    
    Args:
        config: Configuration manager instance
    """
    st.title("⚙️ System Configuration")
    st.markdown("Customize all freezer monitoring settings to match your specific requirements.")
    
    # Create tabs for different configuration sections
    tabs = st.tabs([
        "Freezer Info",
        "Temperature Thresholds",
        "Data Collection",
        "Email Alerts",
        "Data Logging",
        "Simulation",
        "Advanced"
    ])
    
    # Tab 1: Freezer Information
    with tabs[0]:
        st.subheader("🏭 Freezer Information")
        st.markdown("Basic information about your freezer installation")
        
        model_name = st.text_input(
            "Freezer Model Name",
            value=config.get('freezer_info', 'model_name'),
            help="Enter the model name or identifier for this freezer"
        )
        
        location = st.text_input(
            "Installation Location",
            value=config.get('freezer_info', 'location'),
            help="Physical location where the freezer is installed"
        )
        
        operator_name = st.text_input(
            "Operator Name",
            value=config.get('freezer_info', 'operator_name'),
            help="Name of the person or team responsible"
        )
        
        operator_contact = st.text_input(
            "Operator Contact Email",
            value=config.get('freezer_info', 'operator_contact'),
            help="Email address for the responsible operator"
        )
        
        if st.button("Save Freezer Info", key="save_freezer_info"):
            config.set('freezer_info', 'model_name', model_name)
            config.set('freezer_info', 'location', location)
            config.set('freezer_info', 'operator_name', operator_name)
            config.set('freezer_info', 'operator_contact', operator_contact)
            st.success("✓ Freezer information saved successfully!")
    
    # Tab 2: Temperature Thresholds
    with tabs[1]:
        st.subheader("🌡️ Temperature Thresholds")
        st.markdown("Configure temperature limits for each zone. Critical thresholds trigger alerts.")
        
        # Evaporator Zone
        st.markdown("**Evaporator Zone**")
        col1, col2 = st.columns(2)
        with col1:
            evap_min = st.number_input(
                "Normal Min (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'min')),
                step=0.5,
                key="evap_min"
            )
            evap_critical_low = st.number_input(
                "Critical Low (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'critical_low')),
                step=0.5,
                key="evap_crit_low"
            )
        with col2:
            evap_max = st.number_input(
                "Normal Max (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'max')),
                step=0.5,
                key="evap_max"
            )
            evap_critical_high = st.number_input(
                "Critical High (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'critical_high')),
                step=0.5,
                key="evap_crit_high"
            )
        
        st.markdown("---")
        
        # Condenser Zone
        st.markdown("**Condenser Zone**")
        col1, col2 = st.columns(2)
        with col1:
            cond_min = st.number_input(
                "Normal Min (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'min')),
                step=0.5,
                key="cond_min"
            )
            cond_critical_low = st.number_input(
                "Critical Low (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'critical_low')),
                step=0.5,
                key="cond_crit_low"
            )
        with col2:
            cond_max = st.number_input(
                "Normal Max (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'max')),
                step=0.5,
                key="cond_max"
            )
            cond_critical_high = st.number_input(
                "Critical High (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'critical_high')),
                step=0.5,
                key="cond_crit_high"
            )
        
        st.markdown("---")
        
        # Ambient Zone
        st.markdown("**Ambient Zone**")
        col1, col2 = st.columns(2)
        with col1:
            amb_min = st.number_input(
                "Normal Min (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'min')),
                step=0.5,
                key="amb_min"
            )
            amb_critical_low = st.number_input(
                "Critical Low (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'critical_low')),
                step=0.5,
                key="amb_crit_low"
            )
        with col2:
            amb_max = st.number_input(
                "Normal Max (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'max')),
                step=0.5,
                key="amb_max"
            )
            amb_critical_high = st.number_input(
                "Critical High (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'critical_high')),
                step=0.5,
                key="amb_crit_high"
            )
        
        if st.button("Save Temperature Thresholds", key="save_temp_thresholds"):
            # Save evaporator thresholds
            config.set('temperature_thresholds', 'evaporator', 'min', evap_min)
            config.set('temperature_thresholds', 'evaporator', 'max', evap_max)
            config.set('temperature_thresholds', 'evaporator', 'critical_low', evap_critical_low)
            config.set('temperature_thresholds', 'evaporator', 'critical_high', evap_critical_high)
            
            # Save condenser thresholds
            config.set('temperature_thresholds', 'condenser', 'min', cond_min)
            config.set('temperature_thresholds', 'condenser', 'max', cond_max)
            config.set('temperature_thresholds', 'condenser', 'critical_low', cond_critical_low)
            config.set('temperature_thresholds', 'condenser', 'critical_high', cond_critical_high)
            
            # Save ambient thresholds
            config.set('temperature_thresholds', 'ambient', 'min', amb_min)
            config.set('temperature_thresholds', 'ambient', 'max', amb_max)
            config.set('temperature_thresholds', 'ambient', 'critical_low', amb_critical_low)
            config.set('temperature_thresholds', 'ambient', 'critical_high', amb_critical_high)
            
            st.success("✓ Temperature thresholds saved successfully!")
    
    # Tab 3: Data Collection
    with tabs[2]:
        st.subheader("📡 Data Collection Settings")
        st.markdown("Configure how often data is collected and displayed")
        
        reading_interval = st.number_input(
            "Reading Interval (seconds)",
            min_value=1,
            max_value=60,
            value=config.get('data_collection', 'reading_interval_seconds'),
            help="How often to collect temperature readings"
        )
        
        refresh_interval = st.number_input(
            "Dashboard Refresh Interval (seconds)",
            min_value=1,
            max_value=60,
            value=config.get('data_collection', 'chart_refresh_interval_seconds'),
            help="How often to update the dashboard display"
        )
        
        max_points = st.number_input(
            "Maximum Chart Data Points",
            min_value=10,
            max_value=100,
            value=config.get('data_collection', 'max_data_points_display'),
            help="Number of recent readings to show in trend charts"
        )
        
        max_records = st.number_input(
            "Maximum Historical Records",
            min_value=1000,
            max_value=100000,
            value=config.get('data_collection', 'max_historical_records'),
            step=1000,
            help="Maximum number of records to keep in memory"
        )
        
        if st.button("Save Data Collection Settings", key="save_data_collection"):
            config.set('data_collection', 'reading_interval_seconds', reading_interval)
            config.set('data_collection', 'chart_refresh_interval_seconds', refresh_interval)
            config.set('data_collection', 'max_data_points_display', max_points)
            config.set('data_collection', 'max_historical_records', max_records)
            st.success("✓ Data collection settings saved successfully!")
    
    # Tab 4: Email Alerts
    with tabs[3]:
        st.subheader("📧 Email Alert Configuration")
        st.markdown("Configure automated email notifications for critical events")
        
        enable_email = st.checkbox(
            "Enable Email Alerts",
            value=config.get('alert_settings', 'enable_email_alerts'),
            help="Turn email notifications on or off"
        )
        
        alert_cooldown = st.number_input(
            "Alert Cooldown Period (seconds)",
            min_value=60,
            max_value=3600,
            value=config.get('alert_settings', 'alert_cooldown_seconds'),
            step=60,
            help="Minimum time between repeated alerts"
        )
        
        consecutive_readings = st.number_input(
            "Consecutive Critical Readings to Trigger Alert",
            min_value=1,
            max_value=10,
            value=config.get('alert_settings', 'consecutive_readings_trigger'),
            help="Number of consecutive critical readings before sending alert"
        )
        
        st.markdown("---")
        st.markdown("**SMTP Configuration**")
        
        smtp_server = st.text_input(
            "SMTP Server",
            value=config.get('email_config', 'smtp_server'),
            help="SMTP server address (e.g., smtp.gmail.com)"
        )
        
        smtp_port = st.number_input(
            "SMTP Port",
            min_value=1,
            max_value=65535,
            value=config.get('email_config', 'smtp_port'),
            help="SMTP port (usually 587 for TLS)"
        )
        
        sender_email = st.text_input(
            "Sender Email Address",
            value=config.get('email_config', 'sender_email'),
            help="Email address to send alerts from"
        )
        
        st.info("🔒 SMTP password must be set as an environment variable 'SMTP_PASSWORD' for security. Never store passwords in configuration files!")
        
        import os
        password_status = "✓ Password is set in environment" if os.environ.get('SMTP_PASSWORD') else "⚠ Password not found in environment"
        st.text(password_status)
        
        use_tls = st.checkbox(
            "Use TLS Encryption",
            value=config.get('email_config', 'use_tls'),
            help="Enable TLS for secure email transmission"
        )
        
        recipient_emails_text = st.text_area(
            "Recipient Email Addresses (one per line)",
            value='\n'.join(config.get('email_config', 'recipient_emails')),
            help="Enter email addresses to receive alerts, one per line"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Email Configuration", key="save_email_config"):
                config.set('alert_settings', 'enable_email_alerts', enable_email)
                config.set('alert_settings', 'alert_cooldown_seconds', alert_cooldown)
                config.set('alert_settings', 'consecutive_readings_trigger', consecutive_readings)
                config.set('email_config', 'smtp_server', smtp_server)
                config.set('email_config', 'smtp_port', smtp_port)
                config.set('email_config', 'sender_email', sender_email)
                config.set('email_config', 'use_tls', use_tls)
                
                # Parse recipient emails
                recipients = [email.strip() for email in recipient_emails_text.split('\n') if email.strip()]
                config.set('email_config', 'recipient_emails', recipients)
                
                st.success("✓ Email configuration saved successfully!")
                st.info("Remember: Set SMTP_PASSWORD environment variable to enable email alerts")
        
        with col2:
            if st.button("Test Email Connection", key="test_email"):
                from email_notifier import EmailNotifier
                test_notifier = EmailNotifier(config)
                success, message = test_notifier.test_email_connection()
                if success:
                    st.success(f"✓ {message}")
                else:
                    st.error(f"✗ {message}")
    
    # Tab 5: Data Logging
    with tabs[4]:
        st.subheader("💾 Data Logging Settings")
        st.markdown("Configure how temperature data is logged to files")
        
        enable_logging = st.checkbox(
            "Enable CSV Logging",
            value=config.get('data_logging', 'enable_csv_logging'),
            help="Save all readings to CSV file"
        )
        
        csv_path = st.text_input(
            "CSV File Path",
            value=config.get('data_logging', 'csv_file_path'),
            help="Path where CSV log file will be saved"
        )
        
        retention_days = st.number_input(
            "Data Retention Period (days)",
            min_value=1,
            max_value=365,
            value=config.get('data_logging', 'retention_days'),
            help="Number of days to keep historical data"
        )
        
        if st.button("Save Logging Settings", key="save_logging"):
            config.set('data_logging', 'enable_csv_logging', enable_logging)
            config.set('data_logging', 'csv_file_path', csv_path)
            config.set('data_logging', 'retention_days', retention_days)
            st.success("✓ Logging settings saved successfully!")
    
    # Tab 6: Simulation Settings
    with tabs[5]:
        st.subheader("🔬 Simulation Settings")
        st.markdown("Configure the temperature simulator behavior (for testing)")
        
        st.info("These settings control the simulated temperature data generator used for testing the system.")
        
        sim_min = st.number_input(
            "Normal Temperature Min (°C)",
            value=float(config.get('simulation', 'normal_temp_evaporator_min')),
            step=0.5,
            help="Minimum normal operating temperature for evaporator"
        )
        
        sim_max = st.number_input(
            "Normal Temperature Max (°C)",
            value=float(config.get('simulation', 'normal_temp_evaporator_max')),
            step=0.5,
            help="Maximum normal operating temperature for evaporator"
        )
        
        failure_prob = st.slider(
            "Failure Probability (%)",
            min_value=0.0,
            max_value=20.0,
            value=config.get('simulation', 'failure_probability') * 100,
            step=0.5,
            help="Probability of simulating a failure event per reading"
        )
        
        failure_duration = st.number_input(
            "Failure Duration (seconds)",
            min_value=10,
            max_value=600,
            value=config.get('simulation', 'failure_duration_seconds'),
            step=10,
            help="How long a simulated failure lasts"
        )
        
        temp_variation = st.number_input(
            "Temperature Variation Range (±°C)",
            min_value=0.1,
            max_value=2.0,
            value=float(config.get('simulation', 'temp_variation_range')),
            step=0.1,
            help="Random variation added to readings"
        )
        
        if st.button("Save Simulation Settings", key="save_simulation"):
            config.set('simulation', 'normal_temp_evaporator_min', sim_min)
            config.set('simulation', 'normal_temp_evaporator_max', sim_max)
            config.set('simulation', 'failure_probability', failure_prob / 100)
            config.set('simulation', 'failure_duration_seconds', failure_duration)
            config.set('simulation', 'temp_variation_range', temp_variation)
            st.success("✓ Simulation settings saved successfully!")
    
    # Tab 7: Advanced Settings
    with tabs[6]:
        st.subheader("🔧 Advanced Settings")
        
        dashboard_title = st.text_input(
            "Dashboard Title",
            value=config.get('ui_settings', 'dashboard_title'),
            help="Custom title for the dashboard"
        )
        
        show_advanced = st.checkbox(
            "Show Advanced Metrics",
            value=config.get('ui_settings', 'show_advanced_metrics'),
            help="Display additional metrics and statistics"
        )
        
        if st.button("Save Advanced Settings", key="save_advanced"):
            config.set('ui_settings', 'dashboard_title', dashboard_title)
            config.set('ui_settings', 'show_advanced_metrics', show_advanced)
            st.success("✓ Advanced settings saved successfully!")
        
        st.markdown("---")
        st.markdown("**Configuration Management**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Reset to Defaults", key="reset_config"):
                if st.checkbox("Confirm reset to default configuration", key="confirm_reset"):
                    config.reset_to_default()
                    st.success("✓ Configuration reset to defaults!")
                    st.rerun()
        
        with col2:
            if st.button("Export Configuration", key="export_config"):
                export_path = f"freezer_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                if config.export_config(export_path):
                    st.success(f"✓ Configuration exported to {export_path}")
        
        with col3:
            st.download_button(
                "Download Config File",
                data=open('freezer_config.json', 'r').read() if os.path.exists('freezer_config.json') else "",
                file_name=f"freezer_config_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                disabled=not os.path.exists('freezer_config.json')
            )

import os
from datetime import datetime
