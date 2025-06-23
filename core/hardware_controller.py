"""
Hardware Controller for JARVIS
Manages hardware monitoring and control
"""

import os
import time
import threading
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import psutil
    import GPUtil
    HARDWARE_LIBS_AVAILABLE = True
except ImportError:
    HARDWARE_LIBS_AVAILABLE = False

from utils.logger import get_logger
from utils.config_manager import ConfigManager

class HardwareController:
    """
    Advanced Hardware Controller
    Provides comprehensive hardware monitoring and control
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        
        # Hardware monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Hardware state
        self.hardware_state = {
            'cpu': {
                'usage': 0.0,
                'temperature': 0.0,
                'frequency': 0.0,
                'cores': 0
            },
            'memory': {
                'usage': 0.0,
                'total': 0,
                'available': 0,
                'used': 0
            },
            'gpu': {
                'usage': 0.0,
                'memory_usage': 0.0,
                'temperature': 0.0,
                'name': 'Unknown'
            },
            'disk': {
                'usage': 0.0,
                'read_speed': 0.0,
                'write_speed': 0.0,
                'total': 0,
                'free': 0
            },
            'network': {
                'upload_speed': 0.0,
                'download_speed': 0.0,
                'bytes_sent': 0,
                'bytes_recv': 0
            },
            'sensors': {
                'temperatures': {},
                'fans': {},
                'battery': {}
            }
        }
        
        # Performance history
        self.performance_history = []
        self.max_history_size = 1000
        
        # Hardware capabilities
        self.capabilities = {
            'gpu_available': False,
            'temperature_sensors': False,
            'fan_control': False,
            'battery_info': False
        }
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize hardware controller"""
        try:
            if not HARDWARE_LIBS_AVAILABLE:
                self.logger.warning("⚠️ Hardware monitoring libraries not available")
                return False
            
            self.logger.info("🔧 Initializing Hardware Controller...")
            
            # Detect hardware capabilities
            self._detect_capabilities()
            
            # Initialize hardware monitoring
            self._initialize_monitoring()
            
            # Get initial hardware state
            self._update_hardware_state()
            
            self.initialized = True
            self.logger.info("✅ Hardware Controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Hardware Controller initialization failed: {e}")
            return False
    
    def _detect_capabilities(self):
        """Detect available hardware capabilities"""
        try:
            # Check GPU availability
            try:
                gpus = GPUtil.getGPUs()
                self.capabilities['gpu_available'] = len(gpus) > 0
            except:
                self.capabilities['gpu_available'] = False
            
            # Check temperature sensors
            try:
                temps = psutil.sensors_temperatures()
                self.capabilities['temperature_sensors'] = len(temps) > 0
            except:
                self.capabilities['temperature_sensors'] = False
            
            # Check fan sensors
            try:
                fans = psutil.sensors_fans()
                self.capabilities['fan_control'] = len(fans) > 0
            except:
                self.capabilities['fan_control'] = False
            
            # Check battery
            try:
                battery = psutil.sensors_battery()
                self.capabilities['battery_info'] = battery is not None
            except:
                self.capabilities['battery_info'] = False
            
            self.logger.info(f"Hardware capabilities detected: {self.capabilities}")
            
        except Exception as e:
            self.logger.error(f"Error detecting capabilities: {e}")
    
    def _initialize_monitoring(self):
        """Initialize hardware monitoring"""
        try:
            # Get CPU info
            self.hardware_state['cpu']['cores'] = psutil.cpu_count(logical=True)
            
            # Get memory info
            memory = psutil.virtual_memory()
            self.hardware_state['memory']['total'] = memory.total
            
            # Get disk info
            disk = psutil.disk_usage('/')
            self.hardware_state['disk']['total'] = disk.total
            
            self.logger.info("Hardware monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring: {e}")
    
    def start_monitoring(self):
        """Start hardware monitoring"""
        try:
            if not self.monitoring_active and HARDWARE_LIBS_AVAILABLE:
                self.monitoring_active = True
                self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
                self.monitor_thread.start()
                self.logger.info("Hardware monitoring started")
        except Exception as e:
            self.logger.error(f"Error starting hardware monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop hardware monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main hardware monitoring loop"""
        last_network = psutil.net_io_counters()
        last_disk = psutil.disk_io_counters()
        last_time = time.time()
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # Update hardware state
                self._update_cpu_state()
                self._update_memory_state()
                self._update_gpu_state()
                self._update_disk_state(last_disk, time_delta)
                self._update_network_state(last_network, time_delta)
                self._update_sensors_state()
                
                # Store performance history
                self._store_performance_data()
                
                # Update last values
                last_network = psutil.net_io_counters()
                if psutil.disk_io_counters():
                    last_disk = psutil.disk_io_counters()
                last_time = current_time
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Error in hardware monitoring loop: {e}")
                time.sleep(5)
    
    def _update_cpu_state(self):
        """Update CPU state"""
        try:
            # CPU usage
            self.hardware_state['cpu']['usage'] = psutil.cpu_percent(interval=None)
            
            # CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                self.hardware_state['cpu']['frequency'] = freq.current
            
            # CPU temperature (if available)
            if self.capabilities['temperature_sensors']:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    cpu_temps = [temp.current for temp in temps['coretemp']]
                    if cpu_temps:
                        self.hardware_state['cpu']['temperature'] = sum(cpu_temps) / len(cpu_temps)
                elif 'cpu_thermal' in temps:
                    self.hardware_state['cpu']['temperature'] = temps['cpu_thermal'][0].current
            
        except Exception as e:
            self.logger.error(f"Error updating CPU state: {e}")
    
    def _update_memory_state(self):
        """Update memory state"""
        try:
            memory = psutil.virtual_memory()
            self.hardware_state['memory'].update({
                'usage': memory.percent,
                'available': memory.available,
                'used': memory.used
            })
        except Exception as e:
            self.logger.error(f"Error updating memory state: {e}")
    
    def _update_gpu_state(self):
        """Update GPU state"""
        try:
            if self.capabilities['gpu_available']:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    self.hardware_state['gpu'].update({
                        'usage': gpu.load * 100,
                        'memory_usage': gpu.memoryUtil * 100,
                        'temperature': gpu.temperature,
                        'name': gpu.name
                    })
        except Exception as e:
            self.logger.error(f"Error updating GPU state: {e}")
    
    def _update_disk_state(self, last_disk, time_delta):
        """Update disk state"""
        try:
            # Disk usage
            disk = psutil.disk_usage('/')
            self.hardware_state['disk'].update({
                'usage': (disk.used / disk.total) * 100,
                'free': disk.free
            })
            
            # Disk I/O speeds
            if last_disk and time_delta > 0:
                current_disk = psutil.disk_io_counters()
                if current_disk:
                    read_bytes = current_disk.read_bytes - last_disk.read_bytes
                    write_bytes = current_disk.write_bytes - last_disk.write_bytes
                    
                    self.hardware_state['disk'].update({
                        'read_speed': read_bytes / time_delta / 1024 / 1024,  # MB/s
                        'write_speed': write_bytes / time_delta / 1024 / 1024  # MB/s
                    })
            
        except Exception as e:
            self.logger.error(f"Error updating disk state: {e}")
    
    def _update_network_state(self, last_network, time_delta):
        """Update network state"""
        try:
            current_network = psutil.net_io_counters()
            
            self.hardware_state['network'].update({
                'bytes_sent': current_network.bytes_sent,
                'bytes_recv': current_network.bytes_recv
            })
            
            # Network speeds
            if last_network and time_delta > 0:
                sent_bytes = current_network.bytes_sent - last_network.bytes_sent
                recv_bytes = current_network.bytes_recv - last_network.bytes_recv
                
                self.hardware_state['network'].update({
                    'upload_speed': sent_bytes / time_delta / 1024 / 1024,  # MB/s
                    'download_speed': recv_bytes / time_delta / 1024 / 1024  # MB/s
                })
            
        except Exception as e:
            self.logger.error(f"Error updating network state: {e}")
    
    def _update_sensors_state(self):
        """Update sensors state"""
        try:
            # Temperature sensors
            if self.capabilities['temperature_sensors']:
                temps = psutil.sensors_temperatures()
                self.hardware_state['sensors']['temperatures'] = {}
                for name, entries in temps.items():
                    self.hardware_state['sensors']['temperatures'][name] = [
                        {'label': entry.label or 'Unknown', 'current': entry.current}
                        for entry in entries
                    ]
            
            # Fan sensors
            if self.capabilities['fan_control']:
                fans = psutil.sensors_fans()
                self.hardware_state['sensors']['fans'] = {}
                for name, entries in fans.items():
                    self.hardware_state['sensors']['fans'][name] = [
                        {'label': entry.label or 'Unknown', 'current': entry.current}
                        for entry in entries
                    ]
            
            # Battery info
            if self.capabilities['battery_info']:
                battery = psutil.sensors_battery()
                if battery:
                    self.hardware_state['sensors']['battery'] = {
                        'percent': battery.percent,
                        'power_plugged': battery.power_plugged,
                        'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                    }
            
        except Exception as e:
            self.logger.error(f"Error updating sensors state: {e}")
    
    def _update_hardware_state(self):
        """Update complete hardware state"""
        try:
            self._update_cpu_state()
            self._update_memory_state()
            self._update_gpu_state()
            self._update_disk_state(None, 0)
            self._update_network_state(None, 0)
            self._update_sensors_state()
        except Exception as e:
            self.logger.error(f"Error updating hardware state: {e}")
    
    def _store_performance_data(self):
        """Store performance data in history"""
        try:
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': self.hardware_state['cpu']['usage'],
                'memory_usage': self.hardware_state['memory']['usage'],
                'gpu_usage': self.hardware_state['gpu']['usage'],
                'disk_usage': self.hardware_state['disk']['usage'],
                'network_upload': self.hardware_state['network']['upload_speed'],
                'network_download': self.hardware_state['network']['download_speed']
            }
            
            self.performance_history.append(performance_data)
            
            # Limit history size
            if len(self.performance_history) > self.max_history_size:
                self.performance_history = self.performance_history[-self.max_history_size:]
            
        except Exception as e:
            self.logger.error(f"Error storing performance data: {e}")
    
    def execute_command(self, command: str, parameters: Dict = None) -> str:
        """Execute hardware command"""
        try:
            if parameters is None:
                parameters = {}
            
            self.logger.info(f"Executing hardware command: {command}")
            
            if command == 'get_status':
                return self._get_hardware_status()
            elif command == 'get_temperatures':
                return self._get_temperature_info()
            elif command == 'get_performance':
                return self._get_performance_info()
            elif command == 'optimize_performance':
                return self._optimize_performance()
            else:
                return f"Unknown hardware command: {command}"
                
        except Exception as e:
            self.logger.error(f"Error executing hardware command: {e}")
            return f"Error executing command: {str(e)}"
    
    def _get_hardware_status(self) -> str:
        """Get hardware status summary"""
        try:
            status = f"""Hardware Status Report:
• CPU Usage: {self.hardware_state['cpu']['usage']:.1f}%
• Memory Usage: {self.hardware_state['memory']['usage']:.1f}%
• Disk Usage: {self.hardware_state['disk']['usage']:.1f}%"""
            
            if self.capabilities['gpu_available']:
                status += f"\n• GPU Usage: {self.hardware_state['gpu']['usage']:.1f}%"
            
            if self.hardware_state['cpu']['temperature'] > 0:
                status += f"\n• CPU Temperature: {self.hardware_state['cpu']['temperature']:.1f}°C"
            
            return status
            
        except Exception as e:
            return f"Error getting hardware status: {str(e)}"
    
    def _get_temperature_info(self) -> str:
        """Get temperature information"""
        try:
            if not self.capabilities['temperature_sensors']:
                return "Temperature sensors not available"
            
            temp_info = "Temperature Information:\n"
            
            if self.hardware_state['cpu']['temperature'] > 0:
                temp_info += f"• CPU: {self.hardware_state['cpu']['temperature']:.1f}°C\n"
            
            if self.hardware_state['gpu']['temperature'] > 0:
                temp_info += f"• GPU: {self.hardware_state['gpu']['temperature']:.1f}°C\n"
            
            # Add other temperature sensors
            for sensor_name, temps in self.hardware_state['sensors']['temperatures'].items():
                for temp in temps:
                    temp_info += f"• {sensor_name} ({temp['label']}): {temp['current']:.1f}°C\n"
            
            return temp_info.strip()
            
        except Exception as e:
            return f"Error getting temperature info: {str(e)}"
    
    def _get_performance_info(self) -> str:
        """Get performance information"""
        try:
            if not self.performance_history:
                return "No performance data available"
            
            recent_data = self.performance_history[-10:]  # Last 10 entries
            
            avg_cpu = sum(d['cpu_usage'] for d in recent_data) / len(recent_data)
            avg_memory = sum(d['memory_usage'] for d in recent_data) / len(recent_data)
            avg_gpu = sum(d['gpu_usage'] for d in recent_data) / len(recent_data)
            
            perf_info = f"""Performance Summary (Last 10 readings):
• Average CPU Usage: {avg_cpu:.1f}%
• Average Memory Usage: {avg_memory:.1f}%
• Average GPU Usage: {avg_gpu:.1f}%
• Network Upload: {self.hardware_state['network']['upload_speed']:.2f} MB/s
• Network Download: {self.hardware_state['network']['download_speed']:.2f} MB/s"""
            
            return perf_info
            
        except Exception as e:
            return f"Error getting performance info: {str(e)}"
    
    def _optimize_performance(self) -> str:
        """Optimize system performance"""
        try:
            optimizations = []
            
            # Check if CPU usage is high
            if self.hardware_state['cpu']['usage'] > 80:
                optimizations.append("High CPU usage detected - consider closing unnecessary applications")
            
            # Check if memory usage is high
            if self.hardware_state['memory']['usage'] > 85:
                optimizations.append("High memory usage detected - clearing system cache")
                # In a real implementation, you might actually clear cache here
            
            # Check if disk usage is high
            if self.hardware_state['disk']['usage'] > 90:
                optimizations.append("High disk usage detected - consider cleaning temporary files")
            
            # Check temperatures
            if self.hardware_state['cpu']['temperature'] > 70:
                optimizations.append("High CPU temperature detected - check cooling system")
            
            if optimizations:
                return "Performance optimizations suggested:\n" + "\n".join(f"• {opt}" for opt in optimizations)
            else:
                return "System performance is optimal"
                
        except Exception as e:
            return f"Error optimizing performance: {str(e)}"
    
    def get_hardware_state(self) -> Dict:
        """Get current hardware state"""
        return self.hardware_state.copy()
    
    def get_stats(self) -> Dict:
        """Get hardware statistics"""
        try:
            return {
                'hardware_state': self.hardware_state,
                'capabilities': self.capabilities,
                'monitoring_active': self.monitoring_active,
                'performance_history_size': len(self.performance_history),
                'initialized': self.initialized,
                'libraries_available': HARDWARE_LIBS_AVAILABLE
            }
        except Exception as e:
            self.logger.error(f"Error getting hardware stats: {e}")
            return {'error': str(e)}
    
    def shutdown(self):
        """Shutdown hardware controller"""
        self.logger.info("🔧 Shutting down Hardware Controller...")
        self.stop_monitoring()
        self.logger.info("✅ Hardware Controller shutdown complete")