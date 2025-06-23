"""
System Controller - Advanced System Management
Handles all system operations, monitoring, and control
"""

import os
import sys
import psutil
import platform
import subprocess
import threading
import time
import json
import shutil
import winreg
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from utils.logger import get_logger
from utils.config_manager import ConfigManager

class SystemController:
    """
    Advanced System Controller
    Provides complete system control and monitoring capabilities
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        
        # System information
        self.system_info = self._get_system_info()
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Performance metrics
        self.performance_history = []
        self.alert_thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0,
            'temperature': 70.0
        }
        
        # System state
        self.system_state = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0,
            'network_speed': 0.0,
            'temperature': 0.0,
            'processes': 0,
            'uptime': 0,
            'boot_time': psutil.boot_time()
        }
        
        # Advanced features
        self.auto_optimization = True
        self.predictive_maintenance = True
        self.security_monitoring = True
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize system controller"""
        try:
            self.logger.info("⚙️ Initializing System Controller...")
            
            # Check system permissions
            if not self._check_permissions():
                self.logger.warning("⚠️ Limited system permissions detected")
            
            # Initialize system monitoring
            self._initialize_monitoring()
            
            # Load system configuration
            self._load_system_config()
            
            self.initialized = True
            self.logger.info("✅ System Controller initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System Controller initialization failed: {e}")
            return False
    
    def _check_permissions(self) -> bool:
        """Check system permissions"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def _get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        try:
            # Basic system info
            info = {
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
            # CPU information
            info['cpu'] = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'min_frequency': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            }
            
            # Disk information
            info['disks'] = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    info['disks'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'file_system': partition.fstype,
                        'total_size': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percentage': (partition_usage.used / partition_usage.total) * 100
                    })
                except PermissionError:
                    continue
            
            # Network information
            info['network'] = psutil.net_io_counters()._asdict()
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def _initialize_monitoring(self):
        """Initialize system monitoring"""
        try:
            # Start monitoring thread
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("✅ System monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_network = psutil.net_io_counters()
        last_time = time.time()
        
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_state['cpu_percent'] = cpu_percent
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.system_state['memory_percent'] = memory.percent
                
                # Disk usage (primary disk)
                disk = psutil.disk_usage('/')
                self.system_state['disk_percent'] = (disk.used / disk.total) * 100
                
                # Network speed calculation
                current_network = psutil.net_io_counters()
                current_time = time.time()
                
                if last_network:
                    time_delta = current_time - last_time
                    bytes_sent = current_network.bytes_sent - last_network.bytes_sent
                    bytes_recv = current_network.bytes_recv - last_network.bytes_recv
                    
                    # Convert to MB/s
                    network_speed = (bytes_sent + bytes_recv) / time_delta / 1024 / 1024
                    self.system_state['network_speed'] = network_speed
                
                last_network = current_network
                last_time = current_time
                
                # Process count
                self.system_state['processes'] = len(psutil.pids())
                
                # Uptime
                self.system_state['uptime'] = time.time() - self.system_state['boot_time']
                
                # Temperature (if available)
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        avg_temp = sum(temp.current for sensor in temps.values() for temp in sensor) / sum(len(sensor) for sensor in temps.values())
                        self.system_state['temperature'] = avg_temp
                except:
                    pass
                
                # Store performance history
                self.performance_history.append({
                    'timestamp': datetime.now(),
                    'cpu': cpu_percent,
                    'memory': memory.percent,
                    'disk': self.system_state['disk_percent'],
                    'network': self.system_state['network_speed']
                })
                
                # Limit history size
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
                
                # Check for alerts
                self._check_system_alerts()
                
                # Auto-optimization
                if self.auto_optimization:
                    self._auto_optimize_system()
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _check_system_alerts(self):
        """Check for system performance alerts"""
        alerts = []
        
        if self.system_state['cpu_percent'] > self.alert_thresholds['cpu']:
            alerts.append(f"High CPU usage: {self.system_state['cpu_percent']:.1f}%")
        
        if self.system_state['memory_percent'] > self.alert_thresholds['memory']:
            alerts.append(f"High memory usage: {self.system_state['memory_percent']:.1f}%")
        
        if self.system_state['disk_percent'] > self.alert_thresholds['disk']:
            alerts.append(f"High disk usage: {self.system_state['disk_percent']:.1f}%")
        
        if self.system_state['temperature'] > self.alert_thresholds['temperature']:
            alerts.append(f"High temperature: {self.system_state['temperature']:.1f}°C")
        
        if alerts:
            for alert in alerts:
                self.logger.warning(f"⚠️ System Alert: {alert}")
    
    def _auto_optimize_system(self):
        """Automatically optimize system performance"""
        try:
            # Clear temporary files if disk usage is high
            if self.system_state['disk_percent'] > 85:
                self._clear_temp_files()
            
            # Optimize memory if usage is high
            if self.system_state['memory_percent'] > 80:
                self._optimize_memory()
            
        except Exception as e:
            self.logger.error(f"Error in auto-optimization: {e}")
    
    def execute_command(self, command: str, parameters: Dict = None) -> str:
        """Execute system command"""
        try:
            if parameters is None:
                parameters = {}
            
            self.logger.info(f"Executing system command: {command}")
            
            if command == 'system_control':
                return self._handle_system_control(parameters)
            elif command == 'file_operation':
                return self._handle_file_operation(parameters)
            elif command == 'application_control':
                return self._handle_application_control(parameters)
            elif command == 'system_status':
                return self._handle_system_status(parameters)
            else:
                return f"Unknown system command: {command}"
                
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return f"Error executing command: {str(e)}"
    
    def _handle_system_control(self, parameters: Dict) -> str:
        """Handle system control commands"""
        action = parameters.get('action', '').lower()
        
        if action == 'shutdown':
            return self._shutdown_system(parameters.get('delay', 60))
        elif action == 'restart':
            return self._restart_system(parameters.get('delay', 60))
        elif action == 'sleep':
            return self._sleep_system()
        elif action == 'lock':
            return self._lock_system()
        elif action == 'hibernate':
            return self._hibernate_system()
        else:
            return f"Unknown system control action: {action}"
    
    def _handle_file_operation(self, parameters: Dict) -> str:
        """Handle file operations"""
        operation = parameters.get('operation', '').lower()
        path = parameters.get('path', '')
        
        if operation == 'create':
            return self._create_file(path, parameters.get('content', ''))
        elif operation == 'delete':
            return self._delete_file(path)
        elif operation == 'copy':
            return self._copy_file(path, parameters.get('destination', ''))
        elif operation == 'move':
            return self._move_file(path, parameters.get('destination', ''))
        elif operation == 'search':
            return self._search_files(parameters.get('query', ''), path)
        else:
            return f"Unknown file operation: {operation}"
    
    def _handle_application_control(self, parameters: Dict) -> str:
        """Handle application control"""
        action = parameters.get('action', '').lower()
        app_name = parameters.get('app_name', '')
        
        if action == 'launch':
            return self._launch_application(app_name)
        elif action == 'close':
            return self._close_application(app_name)
        elif action == 'list':
            return self._list_applications()
        else:
            return f"Unknown application action: {action}"
    
    def _handle_system_status(self, parameters: Dict) -> str:
        """Handle system status requests"""
        status_type = parameters.get('type', 'general').lower()
        
        if status_type == 'general':
            return self._get_general_status()
        elif status_type == 'detailed':
            return self._get_detailed_status()
        elif status_type == 'performance':
            return self._get_performance_status()
        else:
            return self._get_general_status()
    
    def _shutdown_system(self, delay: int = 60) -> str:
        """Shutdown the system"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['shutdown', '/s', '/t', str(delay)], check=True)
            else:
                subprocess.run(['sudo', 'shutdown', '-h', f'+{delay//60}'], check=True)
            
            return f"System shutdown scheduled in {delay} seconds, Sir."
            
        except Exception as e:
            return f"Failed to shutdown system: {str(e)}"
    
    def _restart_system(self, delay: int = 60) -> str:
        """Restart the system"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['shutdown', '/r', '/t', str(delay)], check=True)
            else:
                subprocess.run(['sudo', 'shutdown', '-r', f'+{delay//60}'], check=True)
            
            return f"System restart scheduled in {delay} seconds, Sir."
            
        except Exception as e:
            return f"Failed to restart system: {str(e)}"
    
    def _sleep_system(self) -> str:
        """Put system to sleep"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            else:
                subprocess.run(['systemctl', 'suspend'], check=True)
            
            return "System entering sleep mode, Sir."
            
        except Exception as e:
            return f"Failed to put system to sleep: {str(e)}"
    
    def _lock_system(self) -> str:
        """Lock the system"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            else:
                subprocess.run(['loginctl', 'lock-session'], check=True)
            
            return "System locked, Sir."
            
        except Exception as e:
            return f"Failed to lock system: {str(e)}"
    
    def _launch_application(self, app_name: str) -> str:
        """Launch an application"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen([app_name], shell=True)
            else:
                subprocess.Popen([app_name])
            
            return f"Launched {app_name}, Sir."
            
        except Exception as e:
            return f"Failed to launch {app_name}: {str(e)}"
    
    def _get_general_status(self) -> str:
        """Get general system status"""
        uptime_str = str(timedelta(seconds=int(self.system_state['uptime'])))
        
        status = f"""System Status Report:
• CPU Usage: {self.system_state['cpu_percent']:.1f}%
• Memory Usage: {self.system_state['memory_percent']:.1f}%
• Disk Usage: {self.system_state['disk_percent']:.1f}%
• Network Activity: {self.system_state['network_speed']:.2f} MB/s
• Active Processes: {self.system_state['processes']}
• System Uptime: {uptime_str}
• Temperature: {self.system_state['temperature']:.1f}°C"""
        
        return status
    
    def get_system_state(self) -> Dict:
        """Get current system state"""
        return self.system_state.copy()
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed system statistics"""
        return {
            'system_info': self.system_info,
            'current_state': self.system_state,
            'performance_history': self.performance_history[-100:],  # Last 100 entries
            'alert_thresholds': self.alert_thresholds,
            'monitoring_active': self.monitoring_active
        }
    
    def start_monitoring(self):
        """Start system monitoring"""
        if not self.monitoring_active:
            self._initialize_monitoring()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _load_system_config(self):
        """Load system configuration"""
        try:
            config_file = "config/system_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.alert_thresholds.update(config.get('alert_thresholds', {}))
                    self.auto_optimization = config.get('auto_optimization', True)
        except Exception as e:
            self.logger.error(f"Error loading system config: {e}")
    
    def shutdown(self):
        """Shutdown system controller"""
        self.logger.info("⚙️ Shutting down System Controller...")
        self.stop_monitoring()
        self.logger.info("✅ System Controller shutdown complete")