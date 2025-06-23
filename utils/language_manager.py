"""
Language Manager - Bilingual Support for JARVIS
Handles English and Hindi language processing and translation
"""

import json
import os
from typing import Dict, Optional, List
import re

from utils.logger import get_logger

class LanguageManager:
    """
    Advanced Language Manager
    Provides bilingual support for English and Hindi
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.current_language = 'english'
        self.supported_languages = ['english', 'hindi']
        
        # Language data
        self.translations = {}
        self.language_patterns = {}
        
        # Load language data
        self._load_translations()
        self._load_language_patterns()
        
        self.logger.info("🌐 Language Manager initialized")
    
    def _load_translations(self):
        """Load translation data"""
        try:
            # Default translations
            self.translations = {
                'english': {
                    'welcome_message': "Good evening, Sir. JARVIS is online and ready to assist you.",
                    'user_prompt': "You",
                    'error_processing': "I apologize, Sir. There seems to be an issue processing your request.",
                    'api_error': "I'm experiencing connectivity issues with my AI systems, Sir.",
                    'ai_error': "My AI processing systems are temporarily unavailable, Sir.",
                    'language_switched': "Language switched successfully, Sir.",
                    'invalid_language': "I'm sorry, Sir. That language is not supported.",
                    'shutdown_message': "Goodbye, Sir. JARVIS going offline.",
                    'system_status': "System Status",
                    'cpu_usage': "CPU Usage",
                    'memory_usage': "Memory Usage",
                    'disk_usage': "Disk Usage",
                    'network_activity': "Network Activity",
                    'temperature': "Temperature",
                    'uptime': "Uptime",
                    'processes': "Active Processes",
                    'listening': "Listening...",
                    'processing': "Processing your request, Sir...",
                    'command_executed': "Command executed successfully, Sir.",
                    'command_failed': "I'm sorry, Sir. The command could not be executed.",
                    'file_created': "File created successfully, Sir.",
                    'file_deleted': "File deleted successfully, Sir.",
                    'application_launched': "Application launched, Sir.",
                    'system_locked': "System locked, Sir.",
                    'system_shutdown': "System shutdown initiated, Sir.",
                    'voice_mode_on': "Voice mode activated, Sir.",
                    'voice_mode_off': "Voice mode deactivated, Sir.",
                    'learning_mode_on': "Learning mode activated, Sir.",
                    'learning_mode_off': "Learning mode deactivated, Sir."
                },
                'hindi': {
                    'welcome_message': "नमस्कार साहब। जार्विस ऑनलाइन है और आपकी सेवा के लिए तैयार है।",
                    'user_prompt': "आप",
                    'error_processing': "मुझे खेद है साहब। आपके अनुरोध को संसाधित करने में कोई समस्या है।",
                    'api_error': "साहब, मेरे AI सिस्टम में कनेक्टिविटी की समस्या है।",
                    'ai_error': "साहब, मेरे AI प्रोसेसिंग सिस्टम अस्थायी रूप से अनुपलब्ध हैं।",
                    'language_switched': "भाषा सफलतापूर्वक बदल दी गई, साहब।",
                    'invalid_language': "मुझे खेद है साहब। वह भाषा समर्थित नहीं है।",
                    'shutdown_message': "अलविदा साहब। जार्विस ऑफलाइन हो रहा है।",
                    'system_status': "सिस्टम स्थिति",
                    'cpu_usage': "CPU उपयोग",
                    'memory_usage': "मेमोरी उपयोग",
                    'disk_usage': "डिस्क उपयोग",
                    'network_activity': "नेटवर्क गतिविधि",
                    'temperature': "तापमान",
                    'uptime': "अपटाइम",
                    'processes': "सक्रिय प्रक्रियाएं",
                    'listening': "सुन रहा हूं...",
                    'processing': "आपके अनुरोध को संसाधित कर रहा हूं, साहब...",
                    'command_executed': "कमांड सफलतापूर्वक निष्पादित, साहब।",
                    'command_failed': "मुझे खेद है साहब। कमांड निष्पादित नहीं हो सका।",
                    'file_created': "फाइल सफलतापूर्वक बनाई गई, साहब।",
                    'file_deleted': "फाइल सफलतापूर्वक हटाई गई, साहब।",
                    'application_launched': "एप्लिकेशन लॉन्च किया गया, साहब।",
                    'system_locked': "सिस्टम लॉक किया गया, साहब।",
                    'system_shutdown': "सिस्टम शटडाउन शुरू किया गया, साहब।",
                    'voice_mode_on': "वॉयस मोड सक्रिय किया गया, साहब।",
                    'voice_mode_off': "वॉयस मोड निष्क्रिय किया गया, साहब।",
                    'learning_mode_on': "लर्निंग मोड सक्रिय किया गया, साहब।",
                    'learning_mode_off': "लर्निंग मोड निष्क्रिय किया गया, साहब।"
                }
            }
            
            # Try to load from file if exists
            translations_file = "data/translations.json"
            if os.path.exists(translations_file):
                with open(translations_file, 'r', encoding='utf-8') as f:
                    file_translations = json.load(f)
                    # Merge with defaults
                    for lang in file_translations:
                        if lang in self.translations:
                            self.translations[lang].update(file_translations[lang])
                        else:
                            self.translations[lang] = file_translations[lang]
            
            self.logger.info("✅ Translations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading translations: {e}")
    
    def _load_language_patterns(self):
        """Load language detection patterns"""
        self.language_patterns = {
            'hindi': [
                # Devanagari script characters
                r'[\u0900-\u097F]',
                # Common Hindi words
                r'\b(क्या|कैसे|कहाँ|कब|क्यों|जार्विस|सिस्टम|फाइल|खोलो|बंद|करो|दिखाओ|बताओ)\b',
                # Hindi question words
                r'\b(आप|मैं|हम|यह|वह|कौन|किसका|किसको)\b'
            ],
            'english': [
                # English alphabet
                r'[a-zA-Z]',
                # Common English words
                r'\b(what|how|where|when|why|jarvis|system|file|open|close|show|tell|the|and|or|but)\b',
                # English question words
                r'\b(you|i|we|this|that|who|whose|whom)\b'
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            if not text:
                return self.current_language
            
            text_lower = text.lower()
            scores = {'hindi': 0, 'english': 0}
            
            # Check for language patterns
            for language, patterns in self.language_patterns.items():
                for pattern in patterns:
                    matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                    scores[language] += matches
            
            # Determine language based on scores
            if scores['hindi'] > scores['english']:
                return 'hindi'
            elif scores['english'] > scores['hindi']:
                return 'english'
            else:
                # Default to current language if unclear
                return self.current_language
                
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return self.current_language
    
    def set_language(self, language: str):
        """Set current language"""
        if language.lower() in self.supported_languages:
            self.current_language = language.lower()
            self.logger.info(f"Language set to: {self.current_language}")
        else:
            self.logger.warning(f"Unsupported language: {language}")
    
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """Get translated text for key"""
        try:
            lang = language or self.current_language
            
            if lang in self.translations and key in self.translations[lang]:
                return self.translations[lang][key]
            
            # Fallback to English if translation not found
            if 'english' in self.translations and key in self.translations['english']:
                return self.translations['english'][key]
            
            # Return key if no translation found
            return key
            
        except Exception as e:
            self.logger.error(f"Error getting text for key '{key}': {e}")
            return key
    
    def translate_text(self, text: str, from_lang: str, to_lang: str) -> str:
        """Translate text between languages (basic implementation)"""
        try:
            # This is a basic implementation
            # In a production system, you would use a proper translation API
            
            if from_lang == to_lang:
                return text
            
            # Simple word-by-word translation for common terms
            translation_dict = self._get_translation_dictionary(from_lang, to_lang)
            
            words = text.split()
            translated_words = []
            
            for word in words:
                word_lower = word.lower()
                if word_lower in translation_dict:
                    translated_words.append(translation_dict[word_lower])
                else:
                    translated_words.append(word)
            
            return ' '.join(translated_words)
            
        except Exception as e:
            self.logger.error(f"Error translating text: {e}")
            return text
    
    def _get_translation_dictionary(self, from_lang: str, to_lang: str) -> Dict[str, str]:
        """Get translation dictionary between languages"""
        # Basic translation dictionary
        if from_lang == 'english' and to_lang == 'hindi':
            return {
                'hello': 'नमस्कार',
                'goodbye': 'अलविदा',
                'yes': 'हाँ',
                'no': 'नहीं',
                'please': 'कृपया',
                'thank you': 'धन्यवाद',
                'system': 'सिस्टम',
                'file': 'फाइल',
                'open': 'खोलो',
                'close': 'बंद करो',
                'show': 'दिखाओ',
                'tell': 'बताओ',
                'what': 'क्या',
                'how': 'कैसे',
                'where': 'कहाँ',
                'when': 'कब',
                'why': 'क्यों'
            }
        elif from_lang == 'hindi' and to_lang == 'english':
            return {
                'नमस्कार': 'hello',
                'अलविदा': 'goodbye',
                'हाँ': 'yes',
                'नहीं': 'no',
                'कृपया': 'please',
                'धन्यवाद': 'thank you',
                'सिस्टम': 'system',
                'फाइल': 'file',
                'खोलो': 'open',
                'बंद': 'close',
                'दिखाओ': 'show',
                'बताओ': 'tell',
                'क्या': 'what',
                'कैसे': 'how',
                'कहाँ': 'where',
                'कब': 'when',
                'क्यों': 'why'
            }
        
        return {}
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def add_translation(self, language: str, key: str, value: str):
        """Add new translation"""
        try:
            if language not in self.translations:
                self.translations[language] = {}
            
            self.translations[language][key] = value
            self.logger.info(f"Added translation: {language}.{key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error adding translation: {e}")
    
    def save_translations(self):
        """Save translations to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/translations.json", 'w', encoding='utf-8') as f:
                json.dump(self.translations, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Translations saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving translations: {e}")
    
    def get_language_info(self) -> Dict:
        """Get current language information"""
        return {
            'current_language': self.current_language,
            'supported_languages': self.supported_languages,
            'available_translations': list(self.translations.keys()),
            'translation_count': {
                lang: len(translations) 
                for lang, translations in self.translations.items()
            }
        }