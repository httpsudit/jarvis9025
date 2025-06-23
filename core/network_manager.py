"""
Network Manager for JARVIS
Handles network operations, monitoring, and connectivity
"""

import os
import time
import threading
import socket
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

try:
    import psutil
    import requests
    NETWORK_LIBS_AVAILABLE = True
except ImportError:
    NETWORK_LIBS_AVAILABLE = False

from utils.logger import get_logger
from utils.config_manager import ConfigManager

class NetworkManager:
    """
    Advanced Network Manager
    Provides comprehensive network monitoring and management
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        
        # Network monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Network state
        self.network_state = {
            'connected': False,
            'interface': 'Unknown',
            'ip_address': 'Unknown',
            'gateway': 'Unknown',
            'dns_servers': [],
            'upload_speed': 0.0,
            'download_speed': 0.0,
            'latency': 0.0,
            'packet_loss': 0.0,
            'bytes_sent': 0,
            'bytes_recv': 0,
            'connections': 0
        }
        
        # Network history
        self.network_history = []
        self.max_history_size = 1000
        
        # Network tests
        self.test_servers = [
            'google.com',
            'cloudflare.com',
            '8.8.8.8'
        ]
        
        # Connection monitoring
        self.active_connections = []
        self.blocked_connections = []
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize network manager"""
        try:
            if not NETWORK_LIBS_AVAILABLE:
                self.logger.warning("⚠️ Network monitoring libraries not available")
                return False
            
            self.logger.info("🌐 Initializing Network Manager...")
            
            # Get initial network state
            self._update_network_state()
            
            # Test connectivity
            self._test_connectivity()
            
            # Get network interfaces
            self._get_network_interfaces()
            
            self.initialized = True
            self.logger.info("✅ Network Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Network Manager initialization failed: {e}")
            return False
    
    def start_monitoring(self):
        """Start network monitoring"""
        try:
            if not self.monitoring_active and NETWORK_LIBS_AVAILABLE:
                self.monitoring_active = True
                self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
                self.monitor_thread.start()
                self.logger.info("Network monitoring started")
        except Exception as e:
            self.logger.error(f"Error starting network monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main network monitoring loop"""
        last_network = psutil.net_io_counters()
        last_time = time.time()
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # Update network state
                self._update_network_speeds(last_network, time_delta)
                self._update_network_connections()
                self._update_network_stats()
                
                # Store network history
                self._store_network_data()
                
                # Test connectivity periodically
                if int(current_time) % 60 == 0:  # Every minute
                    self._test_connectivity()
                
                # Update last values
                last_network = psutil.net_io_counters()
                last_time = current_time
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in network monitoring loop: {e}")
                time.sleep(10)
    
    def _update_network_state(self):
        """Update basic network state"""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            # Find active interface
            for interface_name, addresses in interfaces.items():
                if interface_name.startswith(('eth', 'wlan', 'en', 'wl')):
                    for addr in addresses:
                        if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                            self.network_state['interface'] = interface_name
                            self.network_state['ip_address'] = addr.address
                            
                            # Check if interface is up
                            if interface_name in stats:
                                self.network_state['connected'] = stats[interface_name].isup
                            break
            
            # Get gateway
            self._get_gateway()
            
            # Get DNS servers
            self._get_dns_servers()
            
        except Exception as e:
            self.logger.error(f"Error updating network state: {e}")
    
    def _update_network_speeds(self, last_network, time_delta):
        """Update network speeds"""
        try:
            if last_network and time_delta > 0:
                current_network = psutil.net_io_counters()
                
                sent_bytes = current_network.bytes_sent - last_network.bytes_sent
                recv_bytes = current_network.bytes_recv - last_network.bytes_recv
                
                # Convert to MB/s
                self.network_state['upload_speed'] = sent_bytes / time_delta / 1024 / 1024
                self.network_state['download_speed'] = recv_bytes / time_delta / 1024 / 1024
                
                # Update total bytes
                self.network_state['bytes_sent'] = current_network.bytes_sent
                self.network_state['bytes_recv'] = current_network.bytes_recv
            
        except Exception as e:
            self.logger.error(f"Error updating network speeds: {e}")
    
    def _update_network_connections(self):
        """Update active network connections"""
        try:
            connections = psutil.net_connections()
            self.network_state['connections'] = len(connections)
            
            # Store active connections
            self.active_connections = [
                {
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "Unknown",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "Unknown",
                    'status': conn.status,
                    'pid': conn.pid
                }
                for conn in connections[:50]  # Limit to first 50
            ]
            
        except Exception as e:
            self.logger.error(f"Error updating network connections: {e}")
    
    def _update_network_stats(self):
        """Update network statistics"""
        try:
            # This would update additional network statistics
            pass
        except Exception as e:
            self.logger.error(f"Error updating network stats: {e}")
    
    def _get_gateway(self):
        """Get default gateway"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                # Parse Windows ipconfig output
                for line in result.stdout.split('\n'):
                    if 'Default Gateway' in line:
                        gateway = line.split(':')[-1].strip()
                        if gateway and gateway != '':
                            self.network_state['gateway'] = gateway
                            break
            else:
                result = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        parts = lines[0].split()
                        if len(parts) >= 3:
                            self.network_state['gateway'] = parts[2]
        except Exception as e:
            self.logger.error(f"Error getting gateway: {e}")
    
    def _get_dns_servers(self):
        """Get DNS servers"""
        try:
            dns_servers = []
            
            if platform.system() == "Windows":
                result = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True)
                # Parse nslookup output for DNS server
                for line in result.stdout.split('\n'):
                    if 'Server:' in line:
                        dns_server = line.split(':')[-1].strip()
                        if dns_server:
                            dns_servers.append(dns_server)
            else:
                # Read /etc/resolv.conf on Unix systems
                try:
                    with open('/etc/resolv.conf', 'r') as f:
                        for line in f:
                            if line.startswith('nameserver'):
                                dns_server = line.split()[1]
                                dns_servers.append(dns_server)
                except:
                    pass
            
            self.network_state['dns_servers'] = dns_servers[:3]  # Limit to 3
            
        except Exception as e:
            self.logger.error(f"Error getting DNS servers: {e}")
    
    def _get_network_interfaces(self):
        """Get network interfaces information"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            interface_info = {}
            for interface_name, addresses in interfaces.items():
                interface_info[interface_name] = {
                    'addresses': [
                        {
                            'family': addr.family.name if hasattr(addr.family, 'name') else str(addr.family),
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        }
                        for addr in addresses
                    ],
                    'stats': {
                        'isup': stats[interface_name].isup if interface_name in stats else False,
                        'duplex': stats[interface_name].duplex.name if interface_name in stats and hasattr(stats[interface_name].duplex, 'name') else 'Unknown',
                        'speed': stats[interface_name].speed if interface_name in stats else 0,
                        'mtu': stats[interface_name].mtu if interface_name in stats else 0
                    }
                }
            
            self.network_interfaces = interface_info
            
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
    
    def _test_connectivity(self):
        """Test network connectivity"""
        try:
            # Test ping to multiple servers
            latencies = []
            
            for server in self.test_servers:
                latency = self._ping_server(server)
                if latency > 0:
                    latencies.append(latency)
            
            if latencies:
                self.network_state['latency'] = sum(latencies) / len(latencies)
                self.network_state['connected'] = True
            else:
                self.network_state['connected'] = False
                self.network_state['latency'] = 0.0
            
        except Exception as e:
            self.logger.error(f"Error testing connectivity: {e}")
    
    def _ping_server(self, server: str) -> float:
        """Ping a server and return latency"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ping', '-n', '1', server], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse Windows ping output
                    for line in result.stdout.split('\n'):
                        if 'time=' in line:
                            time_part = line.split('time=')[1].split('ms')[0]
                            return float(time_part)
            else:
                result = subprocess.run(['ping', '-c', '1', server], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse Unix ping output
                    for line in result.stdout.split('\n'):
                        if 'time=' in line:
                            time_part = line.split('time=')[1].split(' ')[0]
                            return float(time_part)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error pinging {server}: {e}")
            return 0.0
    
    def _store_network_data(self):
        """Store network data in history"""
        try:
            network_data = {
                'timestamp': datetime.now().isoformat(),
                'connected': self.network_state['connected'],
                'upload_speed': self.network_state['upload_speed'],
                'download_speed': self.network_state['download_speed'],
                'latency': self.network_state['latency'],
                'connections': self.network_state['connections']
            }
            
            self.network_history.append(network_data)
            
            # Limit history size
            if len(self.network_history) > self.max_history_size:
                self.network_history = self.network_history[-self.max_history_size:]
            
        except Exception as e:
            self.logger.error(f"Error storing network data: {e}")
    
    def execute_command(self, command: str, parameters: Dict = None) -> str:
        """Execute network command"""
        try:
            if parameters is None:
                parameters = {}
            
            self.logger.info(f"Executing network command: {command}")
            
            if command == 'get_status':
                return self._get_network_status()
            elif command == 'test_connectivity':
                return self._test_connectivity_command()
            elif command == 'get_interfaces':
                return self._get_interfaces_info()
            elif command == 'ping':
                host = parameters.get('host', 'google.com')
                return self._ping_command(host)
            elif command == 'speed_test':
                return self._speed_test_command()
            else:
                return f"Unknown network command: {command}"
                
        except Exception as e:
            self.logger.error(f"Error executing network command: {e}")
            return f"Error executing command: {str(e)}"
    
    def _get_network_status(self) -> str:
        """Get network status summary"""
        try:
            status = f"""Network Status Report:
• Connection: {'Connected' if self.network_state['connected'] else 'Disconnected'}
• Interface: {self.network_state['interface']}
• IP Address: {self.network_state['ip_address']}
• Gateway: {self.network_state['gateway']}
• Upload Speed: {self.network_state['upload_speed']:.2f} MB/s
• Download Speed: {self.network_state['download_speed']:.2f} MB/s
• Latency: {self.network_state['latency']:.1f} ms
• Active Connections: {self.network_state['connections']}"""
            
            if self.network_state['dns_servers']:
                status += f"\n• DNS Servers: {', '.join(self.network_state['dns_servers'])}"
            
            return status
            
        except Exception as e:
            return f"Error getting network status: {str(e)}"
    
    def _test_connectivity_command(self) -> str:
        """Test connectivity command"""
        try:
            self._test_connectivity()
            
            if self.network_state['connected']:
                return f"Connectivity test successful. Average latency: {self.network_state['latency']:.1f} ms"
            else:
                return "Connectivity test failed. No internet connection detected."
                
        except Exception as e:
            return f"Error testing connectivity: {str(e)}"
    
    def _get_interfaces_info(self) -> str:
        """Get network interfaces information"""
        try:
            if not hasattr(self, 'network_interfaces'):
                self._get_network_interfaces()
            
            info = "Network Interfaces:\n"
            
            for interface_name, interface_data in self.network_interfaces.items():
                info += f"\n• {interface_name}:\n"
                info += f"  Status: {'Up' if interface_data['stats']['isup'] else 'Down'}\n"
                info += f"  Speed: {interface_data['stats']['speed']} Mbps\n"
                info += f"  MTU: {interface_data['stats']['mtu']}\n"
                
                for addr in interface_data['addresses']:
                    if addr['family'] == 'AddressFamily.AF_INET':
                        info += f"  IPv4: {addr['address']}\n"
                    elif addr['family'] == 'AddressFamily.AF_INET6':
                        info += f"  IPv6: {addr['address']}\n"
            
            return info.strip()
            
        except Exception as e:
            return f"Error getting interfaces info: {str(e)}"
    
    def _ping_command(self, host: str) -> str:
        """Ping command"""
        try:
            latency = self._ping_server(host)
            
            if latency > 0:
                return f"Ping to {host}: {latency:.1f} ms"
            else:
                return f"Ping to {host} failed"
                
        except Exception as e:
            return f"Error pinging {host}: {str(e)}"
    
    def _speed_test_command(self) -> str:
        """Speed test command (simplified)"""
        try:
            # This is a simplified speed test
            # In a real implementation, you might use speedtest-cli or similar
            
            test_url = "http://httpbin.org/bytes/1048576"  # 1MB test file
            
            start_time = time.time()
            response = requests.get(test_url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                speed = len(response.content) / duration / 1024 / 1024  # MB/s
                return f"Download speed test: {speed:.2f} MB/s"
            else:
                return "Speed test failed"
                
        except Exception as e:
            return f"Error running speed test: {str(e)}"
    
    def get_status(self) -> Dict:
        """Get network manager status"""
        return {
            'network_state': self.network_state,
            'monitoring_active': self.monitoring_active,
            'history_size': len(self.network_history),
            'active_connections_count': len(self.active_connections),
            'initialized': self.initialized
        }
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed network statistics"""
        try:
            return {
                'network_state': self.network_state,
                'network_history': self.network_history[-100:],  # Last 100 entries
                'active_connections': self.active_connections[:20],  # First 20 connections
                'network_interfaces': getattr(self, 'network_interfaces', {}),
                'monitoring_active': self.monitoring_active,
                'initialized': self.initialized,
                'libraries_available': NETWORK_LIBS_AVAILABLE
            }
        except Exception as e:
            self.logger.error(f"Error getting detailed network stats: {e}")
            return {'error': str(e)}
    
    def shutdown(self):
        """Shutdown network manager"""
        self.logger.info("🌐 Shutting down Network Manager...")
        self.stop_monitoring()
        
        # Save network history
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/network_history.json", 'w') as f:
                json.dump(self.network_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving network history: {e}")
        
        self.logger.info("✅ Network Manager shutdown complete")