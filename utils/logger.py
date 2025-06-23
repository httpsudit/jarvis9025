"""
Advanced Logging System for JARVIS
Provides comprehensive logging with multiple outputs and formatting
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

# Color codes for console output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support and advanced formatting"""
    
    LEVEL_COLORS = {
        'DEBUG': Colors.BRIGHT_BLACK,
        'INFO': Colors.BRIGHT_GREEN,
        'WARNING': Colors.BRIGHT_YELLOW,
        'ERROR': Colors.BRIGHT_RED,
        'CRITICAL': Colors.BRIGHT_MAGENTA + Colors.BOLD
    }
    
    COMPONENT_COLORS = {
        'jarvis_main': Colors.BRIGHT_CYAN,
        'jarvis_brain': Colors.BRIGHT_BLUE,
        'system_controller': Colors.BRIGHT_GREEN,
        'voice_engine': Colors.BRIGHT_YELLOW,
        'gui_interface': Colors.BRIGHT_MAGENTA,
        'security_manager': Colors.BRIGHT_RED,
        'learning_engine': Colors.CYAN,
        'hardware_controller': Colors.GREEN,
        'network_manager': Colors.BLUE
    }
    
    def __init__(self, use_colors=True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record):
        if not self.use_colors:
            return self._format_plain(record)
        
        # Get colors
        level_color = self.LEVEL_COLORS.get(record.levelname, Colors.WHITE)
        component_color = self.COMPONENT_COLORS.get(record.name.split('.')[-1], Colors.WHITE)
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        timestamp_colored = f"{Colors.DIM}{timestamp}{Colors.RESET}"
        
        # Format level
        level_colored = f"{level_color}{record.levelname:8}{Colors.RESET}"
        
        # Format component name
        component_name = record.name.split('.')[-1] if '.' in record.name else record.name
        component_colored = f"{component_color}{component_name:15}{Colors.RESET}"
        
        # Format message
        message = record.getMessage()
        
        # Add file and line info for debug level
        if record.levelno == logging.DEBUG:
            file_info = f"{Colors.DIM}({record.filename}:{record.lineno}){Colors.RESET}"
            message = f"{message} {file_info}"
        
        # Combine all parts
        formatted = f"{timestamp_colored} │ {level_colored} │ {component_colored} │ {message}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{Colors.RED}{self.formatException(record.exc_info)}{Colors.RESET}"
        
        return formatted
    
    def _format_plain(self, record):
        """Format without colors for file output"""
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        component_name = record.name.split('.')[-1] if '.' in record.name else record.name
        
        formatted = f"{timestamp} | {record.levelname:8} | {component_name:15} | {record.getMessage()}"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'component': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class AdvancedLogger:
    """Advanced logging system for JARVIS"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Log files
        self.main_log_file = self.log_dir / "jarvis.log"
        self.error_log_file = self.log_dir / "jarvis_errors.log"
        self.debug_log_file = self.log_dir / "jarvis_debug.log"
        self.json_log_file = self.log_dir / "jarvis.json"
        
        # Performance tracking
        self.performance_log_file = self.log_dir / "performance.log"
        
        self.loggers = {}
    
    def setup_logger(self, name: str = 'JARVIS', level: int = logging.INFO) -> logging.Logger:
        """Setup and configure logger"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(ColoredFormatter(use_colors=True))
        logger.addHandler(console_handler)
        
        # Main log file handler
        file_handler = logging.FileHandler(self.main_log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(ColoredFormatter(use_colors=False))
        logger.addHandler(file_handler)
        
        # Error log file handler
        error_handler = logging.FileHandler(self.error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(ColoredFormatter(use_colors=False))
        logger.addHandler(error_handler)
        
        # Debug log file handler
        debug_handler = logging.FileHandler(self.debug_log_file, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(ColoredFormatter(use_colors=False))
        logger.addHandler(debug_handler)
        
        # JSON log file handler for structured logging
        json_handler = logging.FileHandler(self.json_log_file, encoding='utf-8')
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSONFormatter())
        logger.addHandler(json_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        self.loggers[name] = logger
        return logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get existing logger or create new one"""
        if name not in self.loggers:
            return self.setup_logger(name)
        return self.loggers[name]
    
    def log_performance(self, component: str, operation: str, duration: float, details: dict = None):
        """Log performance metrics"""
        try:
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'component': component,
                'operation': operation,
                'duration_ms': round(duration * 1000, 2),
                'details': details or {}
            }
            
            with open(self.performance_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(performance_data, ensure_ascii=False) + '\n')
                
        except Exception as e:
            print(f"Error logging performance: {e}")
    
    def cleanup_old_logs(self, days: int = 7):
        """Clean up old log files"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    print(f"Deleted old log file: {log_file}")
                    
        except Exception as e:
            print(f"Error cleaning up logs: {e}")
    
    def get_log_stats(self) -> dict:
        """Get logging statistics"""
        try:
            stats = {
                'log_directory': str(self.log_dir),
                'log_files': [],
                'total_size_mb': 0
            }
            
            for log_file in self.log_dir.glob("*.log*"):
                file_size = log_file.stat().st_size
                stats['log_files'].append({
                    'name': log_file.name,
                    'size_mb': round(file_size / 1024 / 1024, 2),
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                })
                stats['total_size_mb'] += file_size / 1024 / 1024
            
            stats['total_size_mb'] = round(stats['total_size_mb'], 2)
            return stats
            
        except Exception as e:
            return {'error': str(e)}

# Global logger instance
_logger_instance = None

def setup_advanced_logger(name: str = 'JARVIS', level: int = logging.INFO) -> logging.Logger:
    """Setup advanced logger (main entry point)"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = AdvancedLogger()
    
    return _logger_instance.setup_logger(name, level)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = AdvancedLogger()
    
    return _logger_instance.get_logger(name)

def log_performance(component: str, operation: str, duration: float, details: dict = None):
    """Log performance metrics"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = AdvancedLogger()
    
    _logger_instance.log_performance(component, operation, duration, details)

def cleanup_logs(days: int = 7):
    """Clean up old log files"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = AdvancedLogger()
    
    _logger_instance.cleanup_old_logs(days)

def get_log_stats() -> dict:
    """Get logging statistics"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = AdvancedLogger()
    
    return _logger_instance.get_log_stats()