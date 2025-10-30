"""
Data Logger Module
Handles CSV logging and historical data management for temperature readings
"""

import os
import csv
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from config_manager import ConfigManager

class DataLogger:
    """Manages logging of temperature data to CSV files"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the data logger
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.csv_file = self.config.get('data_logging', 'csv_file_path')
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        # Ensure directory exists
        csv_dir = os.path.dirname(self.csv_file)
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir, exist_ok=True)
        
        # Create file with headers if it doesn't exist
        if not os.path.exists(self.csv_file):
            headers = [
                'timestamp',
                'evaporator_temp',
                'condenser_temp',
                'ambient_temp',
                'evaporator_status',
                'condenser_status',
                'ambient_status',
                'overall_status',
                'failure_mode'
            ]
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def log_reading(self, reading: Dict, status: Dict) -> bool:
        """
        Log a temperature reading to CSV file
        
        Args:
            reading: Temperature reading dictionary
            status: Status dictionary for all zones
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.config.get('data_logging', 'enable_csv_logging'):
            return False
        
        try:
            row = [
                reading['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                reading['evaporator_temp'],
                reading['condenser_temp'],
                reading['ambient_temp'],
                status['evaporator'],
                status['condenser'],
                status['ambient'],
                status['overall'],
                reading.get('failure_mode', False)
            ]
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error logging data: {e}")
            return False
    
    def get_historical_data(self, hours: int = 24) -> pd.DataFrame:
        """
        Get historical data from CSV file
        
        Args:
            hours: Number of hours of historical data to retrieve
            
        Returns:
            DataFrame with historical data
        """
        try:
            if not os.path.exists(self.csv_file):
                return pd.DataFrame()
            
            df = pd.read_csv(self.csv_file)
            
            if df.empty:
                return df
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("America/Sao_Paulo", nonexistent="shift_forward", ambiguous="NaT")
            
            # Filter by time range
            cutoff_time = datetime.now(ZoneInfo("America/Sao_Paulo")) - timedelta(hours=2)
            df = df[df['timestamp'] >= cutoff_time]
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            return df
            
        except Exception as e:
            print(f"Error reading historical data: {e}")
            return pd.DataFrame()
    
    def get_recent_readings(self, count: int = 30) -> pd.DataFrame:
        """
        Get most recent temperature readings
        
        Args:
            count: Number of recent readings to retrieve
            
        Returns:
            DataFrame with recent readings
        """
        try:
            if not os.path.exists(self.csv_file):
                return pd.DataFrame()
            
            df = pd.read_csv(self.csv_file)
            
            if df.empty:
                return df
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("America/Sao_Paulo", nonexistent="shift_forward", ambiguous="NaT")
            
            # Get last N rows
            df = df.tail(count)
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            return df
            
        except Exception as e:
            print(f"Error reading recent data: {e}")
            return pd.DataFrame()
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """
        Calculate statistics for historical data
        
        Args:
            hours: Number of hours to calculate statistics for
            
        Returns:
            Dictionary with statistics
        """
        df = self.get_historical_data(hours)
        
        if df.empty:
            return {}
        
        stats = {
            'evaporator': {
                'min': df['evaporator_temp'].min(),
                'max': df['evaporator_temp'].max(),
                'mean': df['evaporator_temp'].mean(),
                'std': df['evaporator_temp'].std()
            },
            'condenser': {
                'min': df['condenser_temp'].min(),
                'max': df['condenser_temp'].max(),
                'mean': df['condenser_temp'].mean(),
                'std': df['condenser_temp'].std()
            },
            'ambient': {
                'min': df['ambient_temp'].min(),
                'max': df['ambient_temp'].max(),
                'mean': df['ambient_temp'].mean(),
                'std': df['ambient_temp'].std()
            },
            'total_readings': len(df),
            'critical_events': len(df[df['overall_status'] == 'CRITICAL']),
            'warning_events': len(df[df['overall_status'] == 'WARNING'])
        }
        
        return stats
    
    def cleanup_old_data(self) -> int:
        """
        Remove data older than retention period
        
        Returns:
            Number of records removed
        """
        try:
            retention_days = self.config.get('data_logging', 'retention_days')
            
            if not os.path.exists(self.csv_file):
                return 0
            
            df = pd.read_csv(self.csv_file)
            
            if df.empty:
                return 0
            
            original_count = len(df)
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("America/Sao_Paulo", nonexistent="shift_forward", ambiguous="NaT")
            
            # Filter data within retention period
            cutoff_date = datetime.now(ZoneInfo("America/Sao_Paulo")) - timedelta(days=retention_days)
            df = df[df['timestamp'] >= cutoff_date]
            
            # Save cleaned data
            df.to_csv(self.csv_file, index=False)
            
            records_removed = original_count - len(df)
            
            if records_removed > 0:
                print(f"Cleaned up {records_removed} old records from log file")
            
            return records_removed
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return 0
    
    def export_data(self, export_path: str, hours: int = 24) -> bool:
        """
        Export historical data to a new CSV file
        
        Args:
            export_path: Path for exported CSV file
            hours: Number of hours of data to export
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            df = self.get_historical_data(hours)
            
            if df.empty:
                print("No data to export")
                return False
            
            # Ensure export directory exists
            export_dir = os.path.dirname(export_path)
            if export_dir and not os.path.exists(export_dir):
                os.makedirs(export_dir, exist_ok=True)
            
            # Export to CSV
            df.to_csv(export_path, index=False)
            
            print(f"Exported {len(df)} records to {export_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """
        Clear all logged data (reset CSV file)
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            # Recreate CSV with just headers
            headers = [
                'timestamp',
                'evaporator_temp',
                'condenser_temp',
                'ambient_temp',
                'evaporator_status',
                'condenser_status',
                'ambient_status',
                'overall_status',
                'failure_mode'
            ]
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            print("All logged data cleared")
            return True
            
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def get_alert_history(self, hours: int = 24) -> List[Dict]:
        """
        Get history of critical and warning events
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of alert events
        """
        df = self.get_historical_data(hours)
        
        if df.empty:
            return []
        
        # Filter for non-OK statuses
        alerts = df[df['overall_status'].isin(['CRITICAL', 'WARNING'])]
        
        alert_list = []
        for _, row in alerts.iterrows():
            alert_list.append({
                'timestamp': row['timestamp'],
                'status': row['overall_status'],
                'evaporator_temp': row['evaporator_temp'],
                'condenser_temp': row['condenser_temp'],
                'ambient_temp': row['ambient_temp']
            })
        
        return alert_list
