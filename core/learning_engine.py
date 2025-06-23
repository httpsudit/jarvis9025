"""
Learning Engine for JARVIS
Implements machine learning and adaptive behavior
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import pickle

from utils.logger import get_logger
from utils.config_manager import ConfigManager

class LearningEngine:
    """
    Advanced Learning Engine
    Implements machine learning and user adaptation
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        
        # Learning settings
        self.learning_enabled = True
        self.learning_active = False
        self.learning_thread = None
        
        # User behavior data
        self.user_interactions = []
        self.command_patterns = defaultdict(int)
        self.response_feedback = defaultdict(list)
        self.user_preferences = {}
        
        # Learning models (simplified)
        self.command_frequency = Counter()
        self.time_patterns = defaultdict(list)
        self.context_patterns = defaultdict(list)
        
        # Adaptation parameters
        self.adaptation_threshold = 10  # Minimum interactions before adaptation
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7
        
        # Performance metrics
        self.learning_sessions = 0
        self.adaptations_made = 0
        self.accuracy_improvements = []
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize learning engine"""
        try:
            self.logger.info("🧠 Initializing Learning Engine...")
            
            # Load learning configuration
            self._load_learning_config()
            
            # Load existing learning data
            self._load_learning_data()
            
            # Initialize learning models
            self._initialize_models()
            
            # Start learning process
            if self.learning_enabled:
                self._start_learning()
            
            self.initialized = True
            self.logger.info("✅ Learning Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Learning Engine initialization failed: {e}")
            return False
    
    def _load_learning_config(self):
        """Load learning configuration"""
        try:
            self.learning_enabled = self.config.get('learning.enabled', True)
            self.adaptation_threshold = self.config.get('learning.adaptation_threshold', 10)
            self.learning_rate = self.config.get('learning.learning_rate', 0.1)
            
            self.logger.info("Learning configuration loaded")
            
        except Exception as e:
            self.logger.error(f"Error loading learning config: {e}")
    
    def _load_learning_data(self):
        """Load existing learning data"""
        try:
            # Load user interactions
            interactions_file = "data/user_interactions.json"
            if os.path.exists(interactions_file):
                with open(interactions_file, 'r', encoding='utf-8') as f:
                    self.user_interactions = json.load(f)
            
            # Load user preferences
            preferences_file = "data/user_preferences.json"
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
            
            # Load learning models
            models_file = "data/learning_models.pkl"
            if os.path.exists(models_file):
                with open(models_file, 'rb') as f:
                    models_data = pickle.load(f)
                    self.command_frequency = models_data.get('command_frequency', Counter())
                    self.time_patterns = models_data.get('time_patterns', defaultdict(list))
                    self.context_patterns = models_data.get('context_patterns', defaultdict(list))
            
            self.logger.info(f"Loaded {len(self.user_interactions)} interactions and {len(self.user_preferences)} preferences")
            
        except Exception as e:
            self.logger.error(f"Error loading learning data: {e}")
    
    def _initialize_models(self):
        """Initialize learning models"""
        try:
            # Process existing interactions to build models
            for interaction in self.user_interactions:
                self._update_models(interaction)
            
            self.logger.info("Learning models initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
    
    def _start_learning(self):
        """Start learning process"""
        try:
            self.learning_active = True
            self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
            self.learning_thread.start()
            
            self.logger.info("Learning process started")
            
        except Exception as e:
            self.logger.error(f"Error starting learning process: {e}")
    
    def _learning_loop(self):
        """Main learning loop"""
        while self.learning_active:
            try:
                # Analyze patterns
                self._analyze_patterns()
                
                # Update user preferences
                self._update_preferences()
                
                # Optimize responses
                self._optimize_responses()
                
                # Clean old data
                self._cleanup_old_data()
                
                # Save learning data periodically
                self._save_learning_data()
                
                time.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in learning loop: {e}")
                time.sleep(300)
    
    def learn_from_interaction(self, command: str, response: Dict, feedback: Optional[str] = None):
        """Learn from user interaction"""
        try:
            if not self.learning_enabled:
                return
            
            # Create interaction record
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'command': command,
                'response': response,
                'feedback': feedback,
                'context': self._get_current_context()
            }
            
            # Store interaction
            self.user_interactions.append(interaction)
            
            # Update models
            self._update_models(interaction)
            
            # Limit interaction history
            if len(self.user_interactions) > 10000:
                self.user_interactions = self.user_interactions[-10000:]
            
            self.logger.debug(f"Learned from interaction: {command[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error learning from interaction: {e}")
    
    def _update_models(self, interaction: Dict):
        """Update learning models with new interaction"""
        try:
            command = interaction.get('command', '').lower()
            timestamp = interaction.get('timestamp', '')
            context = interaction.get('context', {})
            
            # Update command frequency
            self.command_frequency[command] += 1
            
            # Update time patterns
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hour = dt.hour
                    day_of_week = dt.weekday()
                    
                    self.time_patterns[hour].append(command)
                    self.time_patterns[f"day_{day_of_week}"].append(command)
                except:
                    pass
            
            # Update context patterns
            if context:
                for key, value in context.items():
                    if isinstance(value, (str, int, float)):
                        self.context_patterns[f"{key}_{value}"].append(command)
            
        except Exception as e:
            self.logger.error(f"Error updating models: {e}")
    
    def _get_current_context(self) -> Dict:
        """Get current context for learning"""
        try:
            return {
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'language': getattr(self, 'current_language', 'english'),
                'session_length': len(self.user_interactions)
            }
        except Exception as e:
            self.logger.error(f"Error getting context: {e}")
            return {}
    
    def _analyze_patterns(self):
        """Analyze user behavior patterns"""
        try:
            if len(self.user_interactions) < self.adaptation_threshold:
                return
            
            # Analyze command patterns
            recent_interactions = self.user_interactions[-100:]  # Last 100 interactions
            
            # Find most common commands
            recent_commands = [i.get('command', '').lower() for i in recent_interactions]
            common_commands = Counter(recent_commands).most_common(10)
            
            # Find time-based patterns
            time_based_commands = defaultdict(list)
            for interaction in recent_interactions:
                try:
                    timestamp = interaction.get('timestamp', '')
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp)
                        hour = dt.hour
                        command = interaction.get('command', '').lower()
                        time_based_commands[hour].append(command)
                except:
                    continue
            
            # Update preferences based on patterns
            self.user_preferences['common_commands'] = [cmd for cmd, count in common_commands]
            self.user_preferences['time_patterns'] = dict(time_based_commands)
            
            self.logger.debug("Pattern analysis completed")
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}")
    
    def _update_preferences(self):
        """Update user preferences based on learning"""
        try:
            if len(self.user_interactions) < self.adaptation_threshold:
                return
            
            # Analyze response preferences
            positive_responses = []
            negative_responses = []
            
            for interaction in self.user_interactions:
                feedback = interaction.get('feedback')
                if feedback == 'positive':
                    positive_responses.append(interaction)
                elif feedback == 'negative':
                    negative_responses.append(interaction)
            
            # Update preferences
            if positive_responses:
                self.user_preferences['preferred_response_style'] = 'detailed'
            
            if len(self.user_interactions) > 50:
                # Determine preferred language based on usage
                languages = [i.get('context', {}).get('language', 'english') for i in self.user_interactions[-50:]]
                most_common_lang = Counter(languages).most_common(1)[0][0]
                self.user_preferences['preferred_language'] = most_common_lang
            
            self.logger.debug("User preferences updated")
            
        except Exception as e:
            self.logger.error(f"Error updating preferences: {e}")
    
    def _optimize_responses(self):
        """Optimize response generation based on learning"""
        try:
            # This would implement response optimization
            # For now, just track that optimization occurred
            self.adaptations_made += 1
            
        except Exception as e:
            self.logger.error(f"Error optimizing responses: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old learning data"""
        try:
            # Remove interactions older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            self.user_interactions = [
                interaction for interaction in self.user_interactions
                if datetime.fromisoformat(interaction.get('timestamp', '')) > cutoff_date
            ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_user_context(self) -> Dict:
        """Get current user context for AI processing"""
        try:
            context = {
                'total_interactions': len(self.user_interactions),
                'common_commands': self.user_preferences.get('common_commands', [])[:5],
                'preferred_language': self.user_preferences.get('preferred_language', 'english'),
                'current_session_length': self._get_current_session_length(),
                'time_of_day_pattern': self._get_time_pattern()
            }
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting user context: {e}")
            return {}
    
    def _get_current_session_length(self) -> int:
        """Get current session length"""
        try:
            # Count interactions in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_interactions = [
                i for i in self.user_interactions
                if datetime.fromisoformat(i.get('timestamp', '')) > one_hour_ago
            ]
            return len(recent_interactions)
        except:
            return 0
    
    def _get_time_pattern(self) -> str:
        """Get time-based usage pattern"""
        try:
            current_hour = datetime.now().hour
            
            if 6 <= current_hour < 12:
                return "morning"
            elif 12 <= current_hour < 18:
                return "afternoon"
            elif 18 <= current_hour < 22:
                return "evening"
            else:
                return "night"
        except:
            return "unknown"
    
    def predict_next_command(self, context: Dict = None) -> Optional[str]:
        """Predict likely next command based on patterns"""
        try:
            if len(self.user_interactions) < 10:
                return None
            
            current_hour = datetime.now().hour
            
            # Get commands commonly used at this time
            time_commands = self.time_patterns.get(current_hour, [])
            
            if time_commands:
                # Return most common command for this time
                return Counter(time_commands).most_common(1)[0][0]
            
            # Fallback to overall most common command
            if self.command_frequency:
                return self.command_frequency.most_common(1)[0][0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error predicting next command: {e}")
            return None
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        try:
            return {
                'learning_enabled': self.learning_enabled,
                'total_interactions': len(self.user_interactions),
                'learning_sessions': self.learning_sessions,
                'adaptations_made': self.adaptations_made,
                'user_preferences_count': len(self.user_preferences),
                'command_patterns_count': len(self.command_frequency),
                'time_patterns_count': len(self.time_patterns),
                'most_common_commands': self.command_frequency.most_common(5),
                'learning_active': self.learning_active
            }
        except Exception as e:
            self.logger.error(f"Error getting learning stats: {e}")
            return {'error': str(e)}
    
    def _save_learning_data(self):
        """Save learning data to files"""
        try:
            os.makedirs("data", exist_ok=True)
            
            # Save user interactions
            with open("data/user_interactions.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_interactions, f, indent=2, ensure_ascii=False)
            
            # Save user preferences
            with open("data/user_preferences.json", 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
            
            # Save learning models
            models_data = {
                'command_frequency': self.command_frequency,
                'time_patterns': dict(self.time_patterns),
                'context_patterns': dict(self.context_patterns)
            }
            
            with open("data/learning_models.pkl", 'wb') as f:
                pickle.dump(models_data, f)
            
        except Exception as e:
            self.logger.error(f"Error saving learning data: {e}")
    
    def save_learning_data(self):
        """Public method to save learning data"""
        self._save_learning_data()
    
    def start_learning(self):
        """Start learning process"""
        if not self.learning_active:
            self._start_learning()
    
    def stop_learning(self):
        """Stop learning process"""
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
    
    def shutdown(self):
        """Shutdown learning engine"""
        self.logger.info("🧠 Shutting down Learning Engine...")
        self.stop_learning()
        self._save_learning_data()
        self.logger.info("✅ Learning Engine shutdown complete")