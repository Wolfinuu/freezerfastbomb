"""
Data Export Panel Module
Provides UI for exporting and managing historical data
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data_logger import DataLogger
from config_manager import ConfigManager

def show_data_export_panel(logger: DataLogger, config: ConfigManager):
    """
    Display data export and management panel
    
    Args:
        logger: Data logger instance
        config: Configuration manager instance
    """
    st.title("📥 Data Export & Management")
    st.markdown("Export historical temperature data and manage log files")
    
    # Statistics Overview
    st.subheader("📊 Data Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hours_range = st.selectbox(
            "Time Range for Statistics",
            [6, 12, 24, 48, 72, 168],
            index=2,
            format_func=lambda x: f"Last {x} hours" if x < 168 else "Last week"
        )
    
    with col2:
        if st.button("Calculate Statistics", key="calc_stats"):
            stats = logger.get_statistics(hours_range)
            
            if stats:
                st.session_state.current_stats = stats
            else:
                st.warning("No data available for the selected time range")
    
    if hasattr(st.session_state, 'current_stats') and st.session_state.current_stats:
        stats = st.session_state.current_stats
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Readings", stats.get('total_readings', 0))
            st.metric("Critical Events", stats.get('critical_events', 0))
        
        with col2:
            evap_stats = stats.get('evaporator', {})
            st.metric("Evaporator Avg", f"{evap_stats.get('mean', 0):.2f}°C")
            st.metric("Evaporator Range", 
                     f"{evap_stats.get('min', 0):.2f}°C to {evap_stats.get('max', 0):.2f}°C")
        
        with col3:
            cond_stats = stats.get('condenser', {})
            st.metric("Condenser Avg", f"{cond_stats.get('mean', 0):.2f}°C")
            st.metric("Warning Events", stats.get('warning_events', 0))
    
    st.markdown("---")
    
    # Data Export Section
    st.subheader("💾 Export Temperature Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_hours = st.number_input(
            "Hours of Data to Export",
            min_value=1,
            max_value=720,
            value=24,
            step=1,
            help="Number of hours of historical data to export"
        )
    
    with col2:
        export_filename = st.text_input(
            "Export Filename",
            value=f"temperature_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            help="Name for the exported CSV file"
        )
    
    if st.button("Export to CSV", key="export_csv"):
        export_path = f"exports/{export_filename}"
        
        if logger.export_data(export_path, hours=export_hours):
            st.success(f"✓ Data exported successfully to {export_path}")
            
            # Offer download
            try:
                with open(export_path, 'r') as f:
                    csv_data = f.read()
                
                st.download_button(
                    label="Download Exported File",
                    data=csv_data,
                    file_name=export_filename,
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error preparing download: {e}")
        else:
            st.error("Failed to export data")
    
    st.markdown("---")
    
    # View Historical Data
    st.subheader("📋 View Historical Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        view_hours = st.number_input(
            "Hours of Data to View",
            min_value=1,
            max_value=72,
            value=6,
            step=1,
            key="view_hours"
        )
    
    with col2:
        if st.button("Load Historical Data", key="load_historical"):
            df = logger.get_historical_data(hours=view_hours)
            
            if not df.empty:
                st.session_state.historical_df = df
                st.success(f"Loaded {len(df)} records")
            else:
                st.warning("No data available for the selected time range")
    
    if hasattr(st.session_state, 'historical_df') and not st.session_state.historical_df.empty:
        df = st.session_state.historical_df
        
        # Format timestamp for display
        display_df = df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download current view
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download Current View as CSV",
            data=csv,
            file_name=f"historical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    # Data Management
    st.subheader("🗑️ Data Management")
    
    st.warning("⚠️ Data management operations are permanent and cannot be undone!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Cleanup Old Data**")
        st.info(f"Current retention period: {config.get('data_logging', 'retention_days')} days")
        
        if st.button("Cleanup Old Records", key="cleanup_data"):
            if st.checkbox("Confirm cleanup of old records", key="confirm_cleanup"):
                records_removed = logger.cleanup_old_data()
                if records_removed > 0:
                    st.success(f"✓ Removed {records_removed} old records")
                else:
                    st.info("No old records to remove")
    
    with col2:
        st.markdown("**Clear All Data**")
        st.error("This will delete ALL historical data!")
        
        if st.button("Clear All Data", key="clear_all_data"):
            confirm_text = st.text_input(
                "Type 'DELETE ALL' to confirm",
                key="confirm_delete_text"
            )
            
            if confirm_text == "DELETE ALL":
                if logger.clear_all_data():
                    st.success("✓ All data has been cleared")
                    if hasattr(st.session_state, 'historical_df'):
                        del st.session_state.historical_df
                    if hasattr(st.session_state, 'current_stats'):
                        del st.session_state.current_stats
                    st.rerun()
                else:
                    st.error("Failed to clear data")
