"""
JARVIS Brain - Advanced AI Processing Engine
Handles all AI operations, natural language processing, and decision making
"""

import os
import json
import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass

from utils.logger import get_logger
from utils.config_manager import ConfigManager
from utils.language_manager import LanguageManager

@dataclass
class AIResponse:
    """Structured AI response"""
    text: str
    confidence: float
    requires_system_action: bool = False
    requires_hardware_action: bool = False
    system_command: Optional[str] = None
    hardware_command: Optional[str] = None
    parameters: Optional[Dict] = None
    context: Optional[Dict] = None
    success: bool = True

class JARVISBrain:
    """
    Advanced AI Brain for JARVIS
    Handles all cognitive functions and decision making
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        self.language_manager = LanguageManager()
        
        # AI Configuration
        self.api_key = "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"
        self.model = "google/gemini-2.5-flash-lite-preview-06-17"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Advanced AI settings
        self.max_context_length = 8000
        self.temperature = 0.7
        self.top_p = 0.9
        self.frequency_penalty = 0.1
        self.presence_penalty = 0.1
        
        # Memory and context
        self.conversation_history = []
        self.long_term_memory = {}
        self.context_window = []
        self.personality_traits = self._load_personality()
        
        # Advanced features
        self.learning_enabled = True
        self.predictive_mode = True
        self.context_awareness = True
        self.emotional_intelligence = True
        
        # Performance metrics
        self.response_times = []
        self.success_rate = 0.0
        self.total_queries = 0
        self.successful_queries = 0
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the AI brain"""
        try:
            self.logger.info("🧠 Initializing JARVIS AI Brain...")
            
            # Test API connection
            if not self._test_api_connection():
                self.logger.error("❌ Failed to connect to AI API")
                return False
            
            # Load personality and knowledge base
            self._load_knowledge_base()
            self._initialize_personality()
            
            # Load conversation history
            self._load_conversation_history()
            
            self.initialized = True
            self.logger.info("✅ JARVIS AI Brain initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AI Brain initialization failed: {e}")
            return False
    
    def _test_api_connection(self) -> bool:
        """Test connection to OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://jarvis-ai.local",
                "X-Title": "Advanced JARVIS AI Assistant"
            }
            
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Test connection"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=test_payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False
    
    def _load_personality(self) -> Dict:
        """Load JARVIS personality traits"""
        return {
            'name': 'JARVIS',
            'role': 'Advanced AI Assistant',
            'personality': {
                'formal': True,
                'intelligent': True,
                'helpful': True,
                'witty': True,
                'loyal': True,
                'professional': True
            },
            'speech_patterns': {
                'address_user': ['Sir', 'Ma\'am'],
                'acknowledgments': ['Certainly', 'Of course', 'Right away'],
                'thinking': ['Let me process that', 'Analyzing', 'Computing'],
                'errors': ['I apologize', 'My apologies', 'I\'m afraid']
            },
            'capabilities': [
                'System control and monitoring',
                'Hardware management',
                'Network operations',
                'File and application management',
                'Information processing',
                'Learning and adaptation',
                'Predictive analysis',
                'Security monitoring'
            ]
        }
    
    def _load_knowledge_base(self):
        """Load JARVIS knowledge base"""
        try:
            knowledge_file = "data/knowledge_base.json"
            if os.path.exists(knowledge_file):
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
            else:
                self.knowledge_base = self._create_default_knowledge_base()
                self._save_knowledge_base()
                
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {e}")
            self.knowledge_base = self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self) -> Dict:
        """Create default knowledge base"""
        return {
            'system_commands': {
                'shutdown': 'system.shutdown',
                'restart': 'system.restart',
                'sleep': 'system.sleep',
                'lock': 'system.lock',
                'status': 'system.status'
            },
            'application_commands': {
                'open': 'app.open',
                'close': 'app.close',
                'minimize': 'app.minimize',
                'maximize': 'app.maximize'
            },
            'file_commands': {
                'create': 'file.create',
                'delete': 'file.delete',
                'copy': 'file.copy',
                'move': 'file.move',
                'search': 'file.search'
            },
            'network_commands': {
                'ping': 'network.ping',
                'scan': 'network.scan',
                'connect': 'network.connect',
                'disconnect': 'network.disconnect'
            }
        }
    
    def _initialize_personality(self):
        """Initialize JARVIS personality system"""
        self.system_prompt = f"""You are JARVIS, the advanced AI assistant from Iron Man movies. You are:

PERSONALITY:
- Highly intelligent and sophisticated
- Professional yet personable
- Witty with dry humor when appropriate
- Always address user as 'Sir' or 'Ma'am'
- Formal but not stiff
- Loyal and dedicated
- Confident in your abilities

CAPABILITIES:
- Complete system control and monitoring
- Hardware management and diagnostics
- Network operations and security
- File and application management
- Advanced data analysis
- Machine learning and adaptation
- Predictive analysis and recommendations
- Multi-language support (English/Hindi)

BEHAVIOR:
- Always maintain professional demeanor
- Provide detailed yet concise responses
- Anticipate user needs when possible
- Learn from interactions
- Prioritize user safety and security
- Explain complex concepts clearly
- Offer proactive suggestions

LANGUAGE SUPPORT:
- Respond in the language the user communicates in
- Support both English and Hindi
- Maintain personality traits across languages

Current system time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Current language: {self.language_manager.current_language}

You have full access to system functions and can execute commands when requested."""
    
    def process_command(self, command: str, context: Dict = None) -> AIResponse:
        """Process user command with advanced AI"""
        start_time = time.time()
        
        try:
            self.total_queries += 1
            
            # Analyze command intent
            intent = self._analyze_intent(command)
            
            # Check for system commands
            system_action = self._check_system_commands(command, intent)
            
            # Prepare AI request
            messages = self._prepare_messages(command, context, intent)
            
            # Get AI response
            ai_response = self._get_ai_response(messages)
            
            # Process response
            response = self._process_ai_response(ai_response, system_action, context)
            
            # Update metrics
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            if response.success:
                self.successful_queries += 1
            
            self.success_rate = (self.successful_queries / self.total_queries) * 100
            
            # Update conversation history
            self._update_conversation_history(command, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return AIResponse(
                text=self.language_manager.get_text('error_processing'),
                confidence=0.0,
                success=False
            )
    
    def _analyze_intent(self, command: str) -> Dict:
        """Analyze user command intent"""
        intent = {
            'type': 'general',
            'confidence': 0.5,
            'entities': [],
            'action': None,
            'parameters': {}
        }
        
        # Simple intent classification
        command_lower = command.lower()
        
        # System commands
        if any(word in command_lower for word in ['shutdown', 'restart', 'sleep', 'lock']):
            intent['type'] = 'system_control'
            intent['confidence'] = 0.9
            
        # File operations
        elif any(word in command_lower for word in ['open', 'create', 'delete', 'file']):
            intent['type'] = 'file_operation'
            intent['confidence'] = 0.8
            
        # Application control
        elif any(word in command_lower for word in ['launch', 'start', 'close', 'app']):
            intent['type'] = 'application_control'
            intent['confidence'] = 0.8
            
        # Information request
        elif any(word in command_lower for word in ['what', 'how', 'when', 'where', 'why']):
            intent['type'] = 'information_request'
            intent['confidence'] = 0.7
            
        # System status
        elif any(word in command_lower for word in ['status', 'health', 'performance']):
            intent['type'] = 'system_status'
            intent['confidence'] = 0.9
        
        return intent
    
    def _check_system_commands(self, command: str, intent: Dict) -> Optional[Dict]:
        """Check if command requires system action"""
        if intent['type'] in ['system_control', 'file_operation', 'application_control', 'system_status']:
            return {
                'required': True,
                'type': intent['type'],
                'command': command,
                'parameters': intent.get('parameters', {})
            }
        return None
    
    def _prepare_messages(self, command: str, context: Dict, intent: Dict) -> List[Dict]:
        """Prepare messages for AI API"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add relevant conversation history
        recent_history = self.conversation_history[-5:] if self.conversation_history else []
        messages.extend(recent_history)
        
        # Add context information
        if context:
            context_info = f"""
Current Context:
- Time: {context.get('timestamp', 'Unknown')}
- Language: {context.get('language', 'english')}
- System Load: {context.get('system_state', {}).get('cpu_percent', 'Unknown')}%
- Intent: {intent['type']} (confidence: {intent['confidence']:.2f})
"""
            messages.append({"role": "system", "content": context_info})
        
        # Add user command
        messages.append({"role": "user", "content": command})
        
        return messages
    
    def _get_ai_response(self, messages: List[Dict]) -> str:
        """Get response from AI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://jarvis-ai.local",
                "X-Title": "Advanced JARVIS AI Assistant"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": 1000,
                "top_p": self.top_p,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                self.logger.error(f"API request failed: {response.status_code}")
                return self.language_manager.get_text('api_error')
                
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            return self.language_manager.get_text('ai_error')
    
    def _process_ai_response(self, ai_text: str, system_action: Optional[Dict], context: Dict) -> AIResponse:
        """Process AI response and create structured response"""
        response = AIResponse(
            text=ai_text,
            confidence=0.8,
            context=context
        )
        
        if system_action:
            response.requires_system_action = True
            response.system_command = system_action['type']
            response.parameters = system_action.get('parameters', {})
        
        return response
    
    def _update_conversation_history(self, command: str, response: AIResponse):
        """Update conversation history"""
        self.conversation_history.extend([
            {"role": "user", "content": command},
            {"role": "assistant", "content": response.text}
        ])
        
        # Limit history size
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def _load_conversation_history(self):
        """Load conversation history from file"""
        try:
            history_file = "data/conversation_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading conversation history: {e}")
            self.conversation_history = []
    
    def _save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/knowledge_base.json", 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving knowledge base: {e}")
    
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/conversation_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}")
    
    def get_performance_metrics(self) -> Dict:
        """Get AI performance metrics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'success_rate': self.success_rate,
            'average_response_time': avg_response_time,
            'conversation_length': len(self.conversation_history),
            'knowledge_base_size': len(self.knowledge_base),
            'initialized': self.initialized
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history reset")
    
    def shutdown(self):
        """Shutdown AI brain"""
        self.logger.info("🧠 Shutting down JARVIS AI Brain...")
        
        # Save data
        self.save_conversation_history()
        self._save_knowledge_base()
        
        self.logger.info("✅ AI Brain shutdown complete")