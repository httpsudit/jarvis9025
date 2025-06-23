#!/usr/bin/env python3
"""
Advanced JARVIS AI Assistant - Main Application
Ultra-Advanced AI System with Full Computer Control
Bilingual Support: English & Hindi
"""

import sys
import os
import threading
import time
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.jarvis_brain import JARVISBrain
from core.system_controller import SystemController
from core.voice_engine import VoiceEngine
from core.gui_interface import JARVISInterface
from core.security_manager import SecurityManager
from core.learning_engine import LearningEngine
from core.hardware_controller import HardwareController
from core.network_manager import NetworkManager
from utils.logger import setup_advanced_logger
from utils.config_manager import ConfigManager
from utils.language_manager import LanguageManager

class AdvancedJARVIS:
    """
    Advanced JARVIS AI Assistant
    The most sophisticated AI assistant with complete system control
    """
    
    def __init__(self):
        self.logger = setup_advanced_logger()
        self.config = ConfigManager()
        self.language_manager = LanguageManager()
        
        # Initialize core components
        self.brain = JARVISBrain()
        self.system_controller = SystemController()
        self.voice_engine = VoiceEngine()
        self.security_manager = SecurityManager()
        self.learning_engine = LearningEngine()
        self.hardware_controller = HardwareController()
        self.network_manager = NetworkManager()
        
        # GUI Interface
        self.gui = None
        
        # System state
        self.is_running = False
        self.current_language = 'english'
        self.voice_mode = True
        self.learning_mode = True
        self.gui_mode = True
        
        # Performance metrics
        self.start_time = time.time()
        self.commands_processed = 0
        self.successful_operations = 0
        
        # Advanced features
        self.autonomous_mode = False
        self.predictive_mode = True
        self.context_awareness = True
        
        self.logger.info("🤖 Advanced JARVIS AI System Initialized")
        
    def initialize_system(self):
        """Initialize all JARVIS subsystems"""
        try:
            self.logger.info("🚀 Initializing JARVIS Advanced Systems...")
            
            # Display startup sequence
            self._display_startup_sequence()
            
            # Security check
            if not self.security_manager.verify_system_integrity():
                self.logger.error("❌ System integrity check failed")
                return False
            
            # Initialize AI brain with advanced capabilities
            if not self.brain.initialize():
                self.logger.error("❌ AI Brain initialization failed")
                return False
            
            # Initialize system controller with full access
            if not self.system_controller.initialize():
                self.logger.error("❌ System Controller initialization failed")
                return False
            
            # Initialize hardware controller
            if not self.hardware_controller.initialize():
                self.logger.warning("⚠️ Hardware Controller initialization failed")
            
            # Initialize network manager
            if not self.network_manager.initialize():
                self.logger.warning("⚠️ Network Manager initialization failed")
            
            # Initialize voice engine with bilingual support
            if not self.voice_engine.initialize():
                self.logger.warning("⚠️ Voice Engine initialization failed - continuing without voice")
                self.voice_mode = False
            
            # Initialize learning engine
            self.learning_engine.initialize()
            
            # Initialize GUI
            if self.gui_mode:
                self.gui = JARVISInterface(self)
                
            self.logger.info("✅ All JARVIS systems initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False
    
    def _display_startup_sequence(self):
        """Display advanced startup sequence"""
        startup_messages = [
            "🔋 Power systems online",
            "🧠 AI neural networks activating",
            "🔒 Security protocols engaged",
            "🎤 Voice recognition systems ready",
            "👁️ Computer vision systems online",
            "🌐 Network interfaces connected",
            "⚡ Hardware controllers initialized",
            "🎯 Targeting systems calibrated",
            "📊 System diagnostics complete",
            "✨ JARVIS fully operational"
        ]
        
        for message in startup_messages:
            print(f"\033[94m{message}\033[0m")
            time.sleep(0.3)
    
    def start_gui_mode(self):
        """Start JARVIS with advanced GUI"""
        try:
            if not self.initialize_system():
                return False
            
            self.is_running = True
            
            # Start background services
            self._start_background_services()
            
            # Launch GUI
            if self.gui:
                self.gui.run()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ GUI mode failed: {e}")
            return False
    
    def start_console_mode(self):
        """Start JARVIS in console mode"""
        try:
            if not self.initialize_system():
                return False
            
            self.is_running = True
            
            # Start background services
            self._start_background_services()
            
            # Console interaction loop
            self._console_interaction_loop()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Console mode failed: {e}")
            return False
    
    def _start_background_services(self):
        """Start all background services"""
        services = [
            ('System Monitor', self.system_controller.start_monitoring),
            ('Hardware Monitor', self.hardware_controller.start_monitoring),
            ('Network Monitor', self.network_manager.start_monitoring),
            ('Learning Engine', self.learning_engine.start_learning),
            ('Security Monitor', self.security_manager.start_monitoring)
        ]
        
        for service_name, service_func in services:
            try:
                thread = threading.Thread(target=service_func, daemon=True)
                thread.start()
                self.logger.info(f"✅ {service_name} started")
            except Exception as e:
                self.logger.error(f"❌ Failed to start {service_name}: {e}")
    
    def _console_interaction_loop(self):
        """Main console interaction loop"""
        self._display_welcome_message()
        
        while self.is_running:
            try:
                if self.voice_mode and self.voice_engine.is_available():
                    # Voice input
                    print(f"\033[93m🎤 Listening... (Say 'JARVIS' to activate)\033[0m")
                    user_input = self.voice_engine.listen_for_wake_word()
                else:
                    # Text input
                    user_input = input(f"\033[92m{self.language_manager.get_text('user_prompt')}: \033[0m").strip()
                
                if not user_input:
                    continue
                
                # Process command
                response = self.process_command(user_input)
                
                # Output response
                self._output_response(response)
                
            except KeyboardInterrupt:
                self.shutdown()
                break
            except Exception as e:
                self.logger.error(f"❌ Error in interaction loop: {e}")
    
    def _display_welcome_message(self):
        """Display welcome message in current language"""
        welcome_art = """
\033[94m
╔══════════════════════════════════════════════════════════════╗
║                    🤖 JARVIS AI ASSISTANT 🤖                 ║
║                                                              ║
║  ◉ Advanced AI-Powered Personal Assistant                   ║
║  ◉ Full System Control & Hardware Access                    ║
║  ◉ Bilingual Support (English/Hindi)                        ║
║  ◉ Machine Learning & Predictive Analysis                   ║
║  ◉ Voice Recognition & Natural Language Processing          ║
║  ◉ Computer Vision & Image Recognition                       ║
║  ◉ Network Management & Security                            ║
║                                                              ║
║  Status: 🟢 ONLINE  │  AI Model: 🧠 Gemini 2.5 Flash       ║
╚══════════════════════════════════════════════════════════════╝
\033[0m"""
        
        print(welcome_art)
        
        welcome_msg = self.language_manager.get_text('welcome_message')
        print(f"\033[96m{welcome_msg}\033[0m")
        
        if self.voice_mode:
            self.voice_engine.speak(welcome_msg)
    
    def process_command(self, command):
        """Process user command with advanced AI"""
        try:
            self.commands_processed += 1
            
            # Log command
            self.logger.info(f"Processing command: {command}")
            
            # Detect language
            detected_lang = self.language_manager.detect_language(command)
            if detected_lang != self.current_language:
                self.current_language = detected_lang
                self.language_manager.set_language(detected_lang)
            
            # Context analysis
            context = self._analyze_context(command)
            
            # Process through AI brain
            response = self.brain.process_command(command, context)
            
            # Execute system commands if needed
            if response.get('requires_system_action'):
                system_result = self.system_controller.execute_command(
                    response['system_command'],
                    response.get('parameters', {})
                )
                response['system_result'] = system_result
            
            # Execute hardware commands if needed
            if response.get('requires_hardware_action'):
                hardware_result = self.hardware_controller.execute_command(
                    response['hardware_command'],
                    response.get('parameters', {})
                )
                response['hardware_result'] = hardware_result
            
            # Learn from interaction
            if self.learning_mode:
                self.learning_engine.learn_from_interaction(command, response)
            
            self.successful_operations += 1
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error processing command: {e}")
            return {
                'text': self.language_manager.get_text('error_processing'),
                'success': False,
                'error': str(e)
            }
    
    def _analyze_context(self, command):
        """Analyze command context for better understanding"""
        return {
            'timestamp': datetime.now(),
            'language': self.current_language,
            'system_state': self.system_controller.get_system_state(),
            'user_history': self.learning_engine.get_user_context(),
            'environment': self._get_environment_context()
        }
    
    def _get_environment_context(self):
        """Get current environment context"""
        return {
            'time_of_day': datetime.now().strftime('%H:%M'),
            'day_of_week': datetime.now().strftime('%A'),
            'system_load': self.system_controller.get_system_load(),
            'network_status': self.network_manager.get_status(),
            'active_applications': self.system_controller.get_active_applications()
        }
    
    def _output_response(self, response):
        """Output response in appropriate format"""
        if response.get('success', True):
            print(f"\033[94mJARVIS: {response['text']}\033[0m")
            
            if self.voice_mode and self.voice_engine.is_available():
                self.voice_engine.speak(response['text'])
                
            # Display additional info if available
            if response.get('system_result'):
                print(f"\033[93mSystem: {response['system_result']}\033[0m")
                
            if response.get('hardware_result'):
                print(f"\033[95mHardware: {response['hardware_result']}\033[0m")
        else:
            print(f"\033[91mERROR: {response['text']}\033[0m")
            if response.get('error'):
                print(f"\033[91mDetails: {response['error']}\033[0m")
    
    def switch_language(self, language):
        """Switch system language"""
        if language.lower() in ['english', 'hindi', 'en', 'hi']:
            old_lang = self.current_language
            self.current_language = language.lower()
            self.language_manager.set_language(self.current_language)
            
            msg = self.language_manager.get_text('language_switched')
            print(f"\033[96m{msg}\033[0m")
            
            if self.voice_mode:
                self.voice_engine.speak(msg)
                
            self.logger.info(f"Language switched from {old_lang} to {self.current_language}")
        else:
            error_msg = self.language_manager.get_text('invalid_language')
            print(f"\033[91m{error_msg}\033[0m")
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        uptime = time.time() - self.start_time
        
        return {
            'uptime': uptime,
            'commands_processed': self.commands_processed,
            'successful_operations': self.successful_operations,
            'success_rate': (self.successful_operations / max(self.commands_processed, 1)) * 100,
            'current_language': self.current_language,
            'voice_mode': self.voice_mode,
            'learning_mode': self.learning_mode,
            'system_state': self.system_controller.get_detailed_stats(),
            'hardware_state': self.hardware_controller.get_stats(),
            'network_state': self.network_manager.get_detailed_stats()
        }
    
    def shutdown(self):
        """Shutdown JARVIS system gracefully"""
        self.logger.info("🔄 Initiating JARVIS shutdown sequence...")
        
        shutdown_msg = self.language_manager.get_text('shutdown_message')
        print(f"\033[93m{shutdown_msg}\033[0m")
        
        if self.voice_mode and self.voice_engine.is_available():
            self.voice_engine.speak(shutdown_msg)
        
        self.is_running = False
        
        # Stop all services
        services = [
            self.system_controller,
            self.hardware_controller,
            self.network_manager,
            self.learning_engine,
            self.security_manager,
            self.voice_engine
        ]
        
        for service in services:
            try:
                if hasattr(service, 'shutdown'):
                    service.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down service: {e}")
        
        # Save learning data
        self.learning_engine.save_learning_data()
        
        self.logger.info("✅ JARVIS shutdown complete")
        sys.exit(0)

def main():
    """Main entry point"""
    try:
        jarvis = AdvancedJARVIS()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == '--gui':
                jarvis.start_gui_mode()
            elif sys.argv[1] == '--console':
                jarvis.start_console_mode()
            elif sys.argv[1] == '--help':
                print("""
Advanced JARVIS AI Assistant

Usage:
    python jarvis_main.py [--gui|--console|--help]

Options:
    --gui       Start with graphical interface (default)
    --console   Start in console mode
    --help      Show this help message

Features:
    • Advanced AI with full system control
    • Bilingual support (English/Hindi)
    • Voice recognition and synthesis
    • Machine learning and adaptation
    • Hardware monitoring and control
    • Network management
    • Security monitoring
    • Predictive analysis
                """)
                return
        else:
            # Default to GUI mode
            jarvis.start_gui_mode()
            
    except Exception as e:
        print(f"❌ Critical error starting JARVIS: {e}")
        logging.error(f"Critical startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()