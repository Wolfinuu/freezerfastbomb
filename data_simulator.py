"""
Data Simulator Module
Simulates temperature sensor data for freezer monitoring system
Mimics Arduino serial output behavior in pure Python
"""

import random
import time
from datetime import datetime
from typing import Dict, Tuple
from config_manager import ConfigManager

class TemperatureSimulator:
    """Simulates realistic temperature sensor readings for freezer zones"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the temperature simulator
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.failure_mode = False
        self.failure_start_time = None
        self.last_temperatures = {
            'evaporator': -18.0,
            'condenser': 30.0,
            'ambient': 24.0
        }
    
    def _add_variation(self, base_temp: float, variation_range: float) -> float:
        """
        Add random variation to temperature reading
        
        Args:
            base_temp: Base temperature value
            variation_range: Range of variation (+/-)
            
        Returns:
            Temperature with added variation
        """
        return base_temp + random.uniform(-variation_range, variation_range)
    
    def _check_failure_trigger(self) -> bool:
        """
        Check if a failure should be triggered based on probability
        
        Returns:
            True if failure should start, False otherwise
        """
        failure_prob = self.config.get('simulation', 'failure_probability')
        return random.random() < failure_prob
    
    def _check_failure_end(self) -> bool:
        """
        Check if current failure should end
        
        Returns:
            True if failure should end, False otherwise
        """
        if self.failure_start_time is None:
            return False
        
        failure_duration = self.config.get('simulation', 'failure_duration_seconds')
        elapsed = time.time() - self.failure_start_time
        return elapsed >= failure_duration
    
    def _generate_evaporator_temp(self) -> float:
        """
        Generate evaporator temperature reading
        
        Returns:
            Temperature in Celsius
        """
        variation_range = self.config.get('simulation', 'temp_variation_range')
        
        if self.failure_mode:
            # During failure, temperature rises above critical threshold
            critical_high = self.config.get('temperature_thresholds', 'evaporator', 'critical_high')
            # Temperature rises gradually during failure
            target_temp = critical_high + random.uniform(0, 5.0)
            # Smooth transition
            current_temp = self.last_temperatures['evaporator']
            new_temp = current_temp + (target_temp - current_temp) * 0.3
            return self._add_variation(new_temp, variation_range * 0.5)
        else:
            # Normal operation
            min_temp = self.config.get('simulation', 'normal_temp_evaporator_min')
            max_temp = self.config.get('simulation', 'normal_temp_evaporator_max')
            target_temp = random.uniform(min_temp, max_temp)
            # Smooth transition
            current_temp = self.last_temperatures['evaporator']
            new_temp = current_temp + (target_temp - current_temp) * 0.2
            return self._add_variation(new_temp, variation_range)
    
    def _generate_condenser_temp(self) -> float:
        """
        Generate condenser temperature reading
        
        Returns:
            Temperature in Celsius
        """
        variation_range = self.config.get('simulation', 'temp_variation_range')
        min_temp = self.config.get('temperature_thresholds', 'condenser', 'min')
        max_temp = self.config.get('temperature_thresholds', 'condenser', 'max')
        
        # Condenser temperature varies normally
        target_temp = random.uniform(min_temp, max_temp)
        current_temp = self.last_temperatures['condenser']
        new_temp = current_temp + (target_temp - current_temp) * 0.2
        return self._add_variation(new_temp, variation_range)
    
    def _generate_ambient_temp(self) -> float:
        """
        Generate ambient temperature reading
        
        Returns:
            Temperature in Celsius
        """
        variation_range = self.config.get('simulation', 'temp_variation_range')
        min_temp = self.config.get('temperature_thresholds', 'ambient', 'min')
        max_temp = self.config.get('temperature_thresholds', 'ambient', 'max')
        
        # Ambient temperature varies slowly
        target_temp = random.uniform(min_temp, max_temp)
        current_temp = self.last_temperatures['ambient']
        new_temp = current_temp + (target_temp - current_temp) * 0.1
        return self._add_variation(new_temp, variation_range * 0.3)
    
    def get_reading(self) -> Dict[str, any]:
        """
        Get a complete sensor reading with all temperature zones
        
        Returns:
            Dictionary containing temperature readings and metadata
        """
        # Check failure state transitions
        if not self.failure_mode and self._check_failure_trigger():
            self.failure_mode = True
            self.failure_start_time = time.time()
        elif self.failure_mode and self._check_failure_end():
            self.failure_mode = False
            self.failure_start_time = None
        
        # Generate temperature readings
        evaporator_temp = self._generate_evaporator_temp()
        condenser_temp = self._generate_condenser_temp()
        ambient_temp = self._generate_ambient_temp()
        
        # Update last temperatures
        self.last_temperatures = {
            'evaporator': evaporator_temp,
            'condenser': condenser_temp,
            'ambient': ambient_temp
        }
        
        # Create reading data structure
        reading = {
            'timestamp': datetime.now(),
            'evaporator_temp': round(evaporator_temp, 2),
            'condenser_temp': round(condenser_temp, 2),
            'ambient_temp': round(ambient_temp, 2),
            'failure_mode': self.failure_mode
        }
        
        return reading
    
    def get_status(self, reading: Dict[str, any]) -> Dict[str, str]:
        """
        Determine status for each temperature zone
        
        Args:
            reading: Temperature reading dictionary
            
        Returns:
            Dictionary with status for each zone
        """
        status = {}
        
        # Check evaporator
        evap_temp = reading['evaporator_temp']
        evap_thresholds = self.config.get('temperature_thresholds', 'evaporator')
        if evap_temp > evap_thresholds['critical_high'] or evap_temp < evap_thresholds['critical_low']:
            status['evaporator'] = 'CRITICAL'
        elif evap_temp > evap_thresholds['max'] or evap_temp < evap_thresholds['min']:
            status['evaporator'] = 'WARNING'
        else:
            status['evaporator'] = 'OK'
        
        # Check condenser
        cond_temp = reading['condenser_temp']
        cond_thresholds = self.config.get('temperature_thresholds', 'condenser')
        if cond_temp > cond_thresholds['critical_high'] or cond_temp < cond_thresholds['critical_low']:
            status['condenser'] = 'CRITICAL'
        elif cond_temp > cond_thresholds['max'] or cond_temp < cond_thresholds['min']:
            status['condenser'] = 'WARNING'
        else:
            status['condenser'] = 'OK'
        
        # Check ambient
        amb_temp = reading['ambient_temp']
        amb_thresholds = self.config.get('temperature_thresholds', 'ambient')
        if amb_temp > amb_thresholds['critical_high'] or amb_temp < amb_thresholds['critical_low']:
            status['ambient'] = 'CRITICAL'
        elif amb_temp > amb_thresholds['max'] or amb_temp < amb_thresholds['min']:
            status['ambient'] = 'WARNING'
        else:
            status['ambient'] = 'OK'
        
        # Overall status (worst case)
        all_statuses = list(status.values())
        if 'CRITICAL' in all_statuses:
            status['overall'] = 'CRITICAL'
        elif 'WARNING' in all_statuses:
            status['overall'] = 'WARNING'
        else:
            status['overall'] = 'OK'
        
        return status
    
    def format_serial_output(self, reading: Dict[str, any]) -> str:
        """
        Format reading as simulated serial output (Arduino-style)
        
        Args:
            reading: Temperature reading dictionary
            
        Returns:
            Formatted string mimicking Arduino serial output
        """
        output = f"[{reading['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] "
        output += f"Evaporator: {reading['evaporator_temp']:.2f}°C | "
        output += f"Condenser: {reading['condenser_temp']:.2f}°C | "
        output += f"Ambient: {reading['ambient_temp']:.2f}°C"
        
        if reading['failure_mode']:
            output += " | STATUS: FAILURE MODE ACTIVE"
        
        return output
    
    def reset_simulator(self):
        """Reset simulator to initial state"""
        self.failure_mode = False
        self.failure_start_time = None
        self.last_temperatures = {
            'evaporator': -18.0,
            'condenser': 30.0,
            'ambient': 24.0
        }
