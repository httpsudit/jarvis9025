"""
Security Manager for JARVIS
Handles system security, authentication, and monitoring
"""

import os
import hashlib
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
import platform

from utils.logger import get_logger
from utils.config_manager import ConfigManager

class SecurityManager:
    """
    Advanced Security Manager
    Provides comprehensive security monitoring and protection
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        
        # Security settings
        self.security_enabled = True
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Authentication
        self.authenticated = False
        self.auth_attempts = 0
        self.max_auth_attempts = 3
        self.lockout_time = 300  # 5 minutes
        self.last_auth_attempt = 0
        
        # Security logs
        self.security_events = []
        self.threat_level = "LOW"
        
        # File integrity
        self.file_hashes = {}
        self.monitored_files = [
            "jarvis_main.py",
            "core/jarvis_brain.py",
            "core/system_controller.py",
            "utils/config_manager.py"
        ]
        
        # Network security
        self.allowed_connections = []
        self.blocked_ips = []
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize security manager"""
        try:
            self.logger.info("🔒 Initializing Security Manager...")
            
            # Load security configuration
            self._load_security_config()
            
            # Initialize file integrity monitoring
            self._initialize_file_integrity()
            
            # Check system security
            self._check_system_security()
            
            # Start security monitoring
            if self.security_enabled:
                self._start_monitoring()
            
            self.initialized = True
            self.logger.info("✅ Security Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Security Manager initialization failed: {e}")
            return False
    
    def _load_security_config(self):
        """Load security configuration"""
        try:
            self.security_enabled = self.config.get('security.enabled', True)
            self.max_auth_attempts = self.config.get('security.max_auth_attempts', 3)
            self.lockout_time = self.config.get('security.lockout_time', 300)
            
            self.logger.info("Security configuration loaded")
            
        except Exception as e:
            self.logger.error(f"Error loading security config: {e}")
    
    def _initialize_file_integrity(self):
        """Initialize file integrity monitoring"""
        try:
            for file_path in self.monitored_files:
                if os.path.exists(file_path):
                    file_hash = self._calculate_file_hash(file_path)
                    self.file_hashes[file_path] = file_hash
            
            self.logger.info(f"File integrity monitoring initialized for {len(self.file_hashes)} files")
            
        except Exception as e:
            self.logger.error(f"Error initializing file integrity: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _check_system_security(self):
        """Check overall system security"""
        try:
            security_issues = []
            
            # Check file permissions
            if platform.system() != "Windows":
                for file_path in self.monitored_files:
                    if os.path.exists(file_path):
                        file_stat = os.stat(file_path)
                        if file_stat.st_mode & 0o002:  # World writable
                            security_issues.append(f"File {file_path} is world-writable")
            
            # Check for suspicious processes (basic check)
            self._check_suspicious_processes()
            
            if security_issues:
                self.threat_level = "MEDIUM"
                for issue in security_issues:
                    self._log_security_event("WARNING", issue)
            
        except Exception as e:
            self.logger.error(f"Error checking system security: {e}")
    
    def _check_suspicious_processes(self):
        """Check for suspicious processes"""
        try:
            # This is a basic implementation
            # In production, you would have more sophisticated detection
            suspicious_names = ['keylogger', 'backdoor', 'trojan', 'malware']
            
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                processes = result.stdout.lower()
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                processes = result.stdout.lower()
            
            for suspicious in suspicious_names:
                if suspicious in processes:
                    self._log_security_event("CRITICAL", f"Suspicious process detected: {suspicious}")
                    self.threat_level = "HIGH"
            
        except Exception as e:
            self.logger.error(f"Error checking processes: {e}")
    
    def _start_monitoring(self):
        """Start security monitoring"""
        try:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("Security monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting security monitoring: {e}")
    
    def _monitoring_loop(self):
        """Main security monitoring loop"""
        while self.monitoring_active:
            try:
                # Check file integrity
                self._check_file_integrity()
                
                # Monitor system resources
                self._monitor_system_resources()
                
                # Check network connections
                self._monitor_network_activity()
                
                # Clean old security events
                self._cleanup_old_events()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in security monitoring loop: {e}")
                time.sleep(30)
    
    def _check_file_integrity(self):
        """Check integrity of monitored files"""
        try:
            for file_path, original_hash in self.file_hashes.items():
                if os.path.exists(file_path):
                    current_hash = self._calculate_file_hash(file_path)
                    if current_hash != original_hash:
                        self._log_security_event("CRITICAL", f"File integrity violation: {file_path}")
                        self.threat_level = "HIGH"
                        # Update hash
                        self.file_hashes[file_path] = current_hash
                else:
                    self._log_security_event("WARNING", f"Monitored file missing: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error checking file integrity: {e}")
    
    def _monitor_system_resources(self):
        """Monitor system resources for anomalies"""
        try:
            # This would implement resource monitoring
            # For now, just a placeholder
            pass
            
        except Exception as e:
            self.logger.error(f"Error monitoring system resources: {e}")
    
    def _monitor_network_activity(self):
        """Monitor network activity"""
        try:
            # This would implement network monitoring
            # For now, just a placeholder
            pass
            
        except Exception as e:
            self.logger.error(f"Error monitoring network activity: {e}")
    
    def _log_security_event(self, level: str, message: str):
        """Log security event"""
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'threat_level': self.threat_level
            }
            
            self.security_events.append(event)
            
            # Log to main logger
            if level == "CRITICAL":
                self.logger.critical(f"🚨 SECURITY: {message}")
            elif level == "WARNING":
                self.logger.warning(f"⚠️ SECURITY: {message}")
            else:
                self.logger.info(f"🔒 SECURITY: {message}")
            
            # Limit event history
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
    
    def _cleanup_old_events(self):
        """Clean up old security events"""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)
            
            self.security_events = [
                event for event in self.security_events
                if datetime.fromisoformat(event['timestamp']) > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old events: {e}")
    
    def authenticate(self, password: str = None) -> bool:
        """Authenticate user"""
        try:
            current_time = time.time()
            
            # Check lockout
            if self.auth_attempts >= self.max_auth_attempts:
                if current_time - self.last_auth_attempt < self.lockout_time:
                    remaining = self.lockout_time - (current_time - self.last_auth_attempt)
                    self.logger.warning(f"Authentication locked out for {remaining:.0f} seconds")
                    return False
                else:
                    # Reset attempts after lockout period
                    self.auth_attempts = 0
            
            # For demo purposes, accept any password or no password
            # In production, implement proper authentication
            if not self.config.get('security.require_authentication', False):
                self.authenticated = True
                self._log_security_event("INFO", "User authenticated (no auth required)")
                return True
            
            # Simple password check (in production, use proper hashing)
            stored_password = self.config.get('security.password', '')
            if password and password == stored_password:
                self.authenticated = True
                self.auth_attempts = 0
                self._log_security_event("INFO", "User authenticated successfully")
                return True
            else:
                self.auth_attempts += 1
                self.last_auth_attempt = current_time
                self._log_security_event("WARNING", f"Authentication failed (attempt {self.auth_attempts})")
                return False
            
        except Exception as e:
            self.logger.error(f"Error in authentication: {e}")
            return False
    
    def verify_system_integrity(self) -> bool:
        """Verify overall system integrity"""
        try:
            # Check critical files exist
            critical_files = [
                "jarvis_main.py",
                "core/jarvis_brain.py",
                "utils/config_manager.py"
            ]
            
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    self.logger.error(f"Critical file missing: {file_path}")
                    return False
            
            # Check permissions
            if platform.system() != "Windows":
                for file_path in critical_files:
                    if os.path.exists(file_path):
                        file_stat = os.stat(file_path)
                        if not (file_stat.st_mode & 0o400):  # Not readable by owner
                            self.logger.error(f"File not readable: {file_path}")
                            return False
            
            self.logger.info("System integrity verification passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying system integrity: {e}")
            return False
    
    def get_security_status(self) -> Dict:
        """Get current security status"""
        return {
            'security_enabled': self.security_enabled,
            'monitoring_active': self.monitoring_active,
            'authenticated': self.authenticated,
            'threat_level': self.threat_level,
            'recent_events': self.security_events[-10:],  # Last 10 events
            'auth_attempts': self.auth_attempts,
            'files_monitored': len(self.file_hashes)
        }
    
    def get_security_report(self) -> Dict:
        """Get comprehensive security report"""
        try:
            # Count events by level
            event_counts = {'INFO': 0, 'WARNING': 0, 'CRITICAL': 0}
            for event in self.security_events:
                level = event.get('level', 'INFO')
                event_counts[level] = event_counts.get(level, 0) + 1
            
            return {
                'status': self.get_security_status(),
                'event_summary': event_counts,
                'total_events': len(self.security_events),
                'system_integrity': self.verify_system_integrity(),
                'uptime': time.time() - (self.last_auth_attempt or time.time()),
                'recommendations': self._get_security_recommendations()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating security report: {e}")
            return {'error': str(e)}
    
    def _get_security_recommendations(self) -> List[str]:
        """Get security recommendations"""
        recommendations = []
        
        if not self.config.get('security.require_authentication', False):
            recommendations.append("Enable authentication for better security")
        
        if self.threat_level != "LOW":
            recommendations.append("Review recent security events")
        
        if len(self.security_events) > 100:
            recommendations.append("High number of security events - investigate")
        
        return recommendations
    
    def start_monitoring(self):
        """Start security monitoring"""
        if not self.monitoring_active:
            self._start_monitoring()
    
    def stop_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def shutdown(self):
        """Shutdown security manager"""
        self.logger.info("🔒 Shutting down Security Manager...")
        self.stop_monitoring()
        
        # Save security events
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/security_events.json", 'w') as f:
                json.dump(self.security_events, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving security events: {e}")
        
        self.logger.info("✅ Security Manager shutdown complete")