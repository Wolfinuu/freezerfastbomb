# FAST BOMBAS - Freezer Thermal Control System

A comprehensive Python-based monitoring system for industrial freezers featuring real-time temperature monitoring, automated alerts, and historical data logging.

## Features

- **Real-Time Monitoring**: Live temperature tracking across three zones (Evaporator, Condenser, Ambient)
- **Interactive Dashboard**: Professional web interface built with Streamlit
- **Visual Indicators**: Temperature gauges with color-coded status indicators
- **Trend Charts**: Historical temperature visualization with configurable time ranges
- **Automated Alerts**: Email notifications for critical temperature events
- **Data Logging**: CSV export and historical data management
- **Fully Configurable**: All thresholds, intervals, and settings customizable through the UI
- **Simulation Mode**: Built-in temperature simulator for testing without hardware

## System Requirements

- Python 3.11+
- Streamlit
- Plotly
- Pandas

## Installation

1. All required packages are already installed in this Replit environment

2. The system is configured to run automatically with the Server workflow

## Configuration

### Setting Up Email Alerts

For security, the SMTP password must be set as an environment variable:

1. Go to the Replit Secrets panel (Tools > Secrets)
2. Add a new secret:
   - Key: `SMTP_PASSWORD`
   - Value: Your SMTP email password or app-specific password

**Important Security Notes:**
- Never store passwords in configuration files
- Use app-specific passwords when possible (Gmail, Outlook, etc.)
- The system will only send alerts if the SMTP_PASSWORD environment variable is set

### Configuring Temperature Thresholds

1. Open the Dashboard
2. Navigate to **Configuration** page
3. Go to **Temperature Thresholds** tab
4. Set the following for each zone:
   - **Normal Min/Max**: Operating range for normal conditions
   - **Critical Low/High**: Thresholds that trigger alerts

### Setting Up Email Recipients

1. Go to **Configuration** > **Email Alerts**
2. Enter recipient email addresses (one per line)
3. Configure SMTP settings:
   - SMTP Server (e.g., smtp.gmail.com)
   - SMTP Port (usually 587)
   - Sender Email Address
4. Save configuration

## Usage

### Dashboard Overview

The main dashboard displays:
- **System Status**: Overall health and operational mode
- **Temperature Gauges**: Real-time readings for all three zones
- **Status Indicators**: Color-coded status (Green=OK, Yellow=Warning, Red=Critical)
- **Temperature Trends**: Historical chart showing last 30 readings
- **Alert History**: Recent warning and critical events

### Navigation

- **Dashboard**: Main monitoring interface
- **Configuration**: All system settings and customization
- **Data Export**: Export historical data to CSV
- **System Info**: System diagnostics and information

### Customizing Settings

All settings can be customized through the Configuration page:

1. **Freezer Info**: Model name, location, operator details
2. **Temperature Thresholds**: Min/max/critical limits for each zone
3. **Data Collection**: Reading intervals, chart refresh rates
4. **Email Alerts**: SMTP settings, cooldown periods, trigger thresholds
5. **Data Logging**: CSV file paths, retention periods
6. **Simulation**: Testing parameters for data generator

### Exporting Data

1. Navigate to **Data Export** page
2. Select time range (hours of historical data)
3. Click **Export to CSV**
4. Download the generated file

### Understanding Status Indicators

- **🟢 OK**: Temperature within normal range
- **🟡 WARNING**: Temperature outside normal range but not critical
- **🔴 CRITICAL**: Temperature beyond critical thresholds - Alert triggered!

## Alert System

The system sends email alerts when:
1. Temperature exceeds critical thresholds
2. Multiple consecutive critical readings occur (configurable)
3. Cooldown period has elapsed since last alert (prevents spam)

Alert emails include:
- Timestamp and freezer information
- Current readings for all zones
- Status indicators
- Configured temperature thresholds
- Actionable information for operators

## Data Logging

All temperature readings are automatically logged to CSV files:
- Default location: `data/temperature_logs.csv`
- Includes: timestamp, all temperatures, status flags
- Automatic cleanup based on retention period
- Export capability for custom time ranges

## Simulation Mode

The built-in simulator generates realistic temperature data:
- Normal operation: Temperature oscillates within configured range
- Failure mode: Random critical events to test alert system
- Configurable failure probability and duration
- Smooth temperature transitions

## File Structure

```
├── app.py                      # Main Streamlit application
├── config_manager.py           # Configuration management
├── data_simulator.py           # Temperature data simulator
├── email_notifier.py           # Email alert system
├── data_logger.py              # CSV logging and data management
├── config_panel.py             # Configuration UI
├── data_export_panel.py        # Data export UI
├── system_info_panel.py        # System information UI
├── freezer_config.json         # System configuration (auto-generated)
├── data/                       # CSV log files
└── exports/                    # Exported data files
```

## Security Best Practices

1. **Never commit credentials**: SMTP passwords are stored in environment variables only
2. **Use app-specific passwords**: Create dedicated passwords for email alerts
3. **Restrict file access**: Ensure configuration files have appropriate permissions
4. **Regular updates**: Keep dependencies updated for security patches

## Troubleshooting

### Email Alerts Not Working

1. Check that `SMTP_PASSWORD` environment variable is set
2. Verify SMTP server and port settings
3. Ensure sender email is correct
4. Check recipient email addresses
5. Use "Test Email Connection" button in Configuration

### Dashboard Not Updating

1. Check that the Server workflow is running
2. Verify browser is not blocking auto-refresh
3. Check browser console for errors
4. Refresh the page manually

### No Historical Data

1. Verify CSV logging is enabled in Configuration
2. Check that `data/` directory exists
3. Ensure sufficient disk space
4. Check file permissions

## Support

For issues, questions, or feature requests:
- Contact: operator@fastbombas.com
- System Version: 1.0.0

## License

Proprietary - FAST BOMBAS Industrial Systems

---

**Developed for FAST BOMBAS industrial freezer monitoring**
