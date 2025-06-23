"""
Advanced Voice Engine - Speech Recognition and Synthesis
Supports bilingual operation (English/Hindi) with advanced features
"""

import os
import threading
import time
import queue
import json
from typing import Optional, Dict, List, Callable
import numpy as np

# Voice libraries
try:
    import pyttsx3
    import speech_recognition as sr
    import sounddevice as sd
    import librosa
    import webrtcvad
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

from utils.logger import get_logger
from utils.config_manager import ConfigManager
from utils.language_manager import LanguageManager

class VoiceEngine:
    """
    Advanced Voice Engine for JARVIS
    Handles speech recognition, synthesis, and voice processing
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        self.language_manager = LanguageManager()
        
        # Voice components
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.vad = None
        
        # Voice settings
        self.voice_settings = {
            'rate': 180,
            'volume': 0.9,
            'voice_id': 0,
            'language': 'en-US'
        }
        
        # Recognition settings
        self.recognition_settings = {
            'energy_threshold': 4000,
            'dynamic_energy_threshold': True,
            'pause_threshold': 0.8,
            'phrase_threshold': 0.3,
            'non_speaking_duration': 0.8
        }
        
        # Advanced features
        self.wake_word_detection = True
        self.continuous_listening = False
        self.noise_suppression = True
        self.voice_activity_detection = True
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.wake_words = ['jarvis', 'जार्विस']
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize voice engine"""
        try:
            if not VOICE_AVAILABLE:
                self.logger.warning("⚠️ Voice libraries not available")
                return False
            
            self.logger.info("🎤 Initializing Voice Engine...")
            
            # Initialize TTS
            if not self._initialize_tts():
                self.logger.error("❌ TTS initialization failed")
                return False
            
            # Initialize speech recognition
            if not self._initialize_speech_recognition():
                self.logger.error("❌ Speech recognition initialization failed")
                return False
            
            # Initialize voice activity detection
            if not self._initialize_vad():
                self.logger.warning("⚠️ VAD initialization failed")
            
            # Start audio processing thread
            self._start_audio_processing()
            
            self.initialized = True
            self.logger.info("✅ Voice Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Voice Engine initialization failed: {e}")
            return False
    
    def _initialize_tts(self) -> bool:
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Select appropriate voice based on language
                selected_voice = self._select_voice(voices)
                if selected_voice:
                    self.tts_engine.setProperty('voice', selected_voice.id)
                    self.voice_settings['voice_id'] = selected_voice.id
            
            # Set voice properties
            self.tts_engine.setProperty('rate', self.voice_settings['rate'])
            self.tts_engine.setProperty('volume', self.voice_settings['volume'])
            
            self.logger.info("✅ TTS engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"TTS initialization error: {e}")
            return False
    
    def _select_voice(self, voices):
        """Select appropriate voice based on current language"""
        current_lang = self.language_manager.current_language
        
        # Voice selection preferences
        preferences = {
            'english': ['david', 'mark', 'zira', 'male'],
            'hindi': ['hindi', 'indian', 'female']
        }
        
        preferred = preferences.get(current_lang, ['male', 'english'])
        
        # Find best matching voice
        for voice in voices:
            voice_name = voice.name.lower()
            for pref in preferred:
                if pref in voice_name:
                    return voice
        
        # Default to first available voice
        return voices[0] if voices else None
    
    def _initialize_speech_recognition(self) -> bool:
        """Initialize speech recognition"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configure recognizer
            self.recognizer.energy_threshold = self.recognition_settings['energy_threshold']
            self.recognizer.dynamic_energy_threshold = self.recognition_settings['dynamic_energy_threshold']
            self.recognizer.pause_threshold = self.recognition_settings['pause_threshold']
            self.recognizer.phrase_threshold = self.recognition_settings['phrase_threshold']
            self.recognizer.non_speaking_duration = self.recognition_settings['non_speaking_duration']
            
            # Calibrate for ambient noise
            with self.microphone as source:
                self.logger.info("🎤 Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.logger.info("✅ Speech recognition initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Speech recognition initialization error: {e}")
            return False
    
    def _initialize_vad(self) -> bool:
        """Initialize Voice Activity Detection"""
        try:
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
            self.logger.info("✅ Voice Activity Detection initialized")
            return True
        except Exception as e:
            self.logger.error(f"VAD initialization error: {e}")
            return False
    
    def _start_audio_processing(self):
        """Start audio processing thread"""
        try:
            self.processing_thread = threading.Thread(target=self._audio_processing_loop, daemon=True)
            self.processing_thread.start()
            self.logger.info("✅ Audio processing thread started")
        except Exception as e:
            self.logger.error(f"Error starting audio processing: {e}")
    
    def _audio_processing_loop(self):
        """Main audio processing loop"""
        while self.initialized:
            try:
                if self.continuous_listening and not self.is_speaking:
                    self._process_continuous_audio()
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in audio processing loop: {e}")
                time.sleep(1)
    
    def speak(self, text: str, language: Optional[str] = None):
        """Convert text to speech"""
        if not self.initialized or not self.tts_engine:
            self.logger.warning("TTS not available")
            return
        
        try:
            self.is_speaking = True
            
            # Adjust voice for language if specified
            if language and language != self.voice_settings['language']:
                self._adjust_voice_for_language(language)
            
            # Run TTS in separate thread
            tts_thread = threading.Thread(target=self._speak_thread, args=(text,))
            tts_thread.daemon = True
            tts_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
            self.is_speaking = False
    
    def _speak_thread(self, text: str):
        """TTS thread function"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS thread error: {e}")
        finally:
            self.is_speaking = False
    
    def _adjust_voice_for_language(self, language: str):
        """Adjust voice settings for specific language"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Find voice for specific language
                for voice in voices:
                    if language.lower() in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        self.voice_settings['language'] = language
                        break
        except Exception as e:
            self.logger.error(f"Error adjusting voice for language: {e}")
    
    def listen(self, timeout: int = 10, phrase_timeout: int = 5) -> Optional[str]:
        """Listen for voice input and convert to text"""
        if not self.initialized or not self.recognizer or not self.microphone:
            return None
        
        try:
            self.is_listening = True
            
            with self.microphone as source:
                self.logger.info("🎤 Listening for speech...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_timeout
                )
            
            # Convert speech to text
            return self._recognize_speech(audio)
            
        except sr.WaitTimeoutError:
            self.logger.info("Listening timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return None
        finally:
            self.is_listening = False
    
    def listen_for_wake_word(self, timeout: int = 30) -> Optional[str]:
        """Listen for wake word activation"""
        if not self.initialized:
            return None
        
        try:
            self.logger.info("🎤 Listening for wake word...")
            
            # Listen for wake word
            wake_detected = False
            start_time = time.time()
            
            while not wake_detected and (time.time() - start_time) < timeout:
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    # Quick recognition for wake word
                    text = self._recognize_speech(audio, quick=True)
                    if text and any(wake_word in text.lower() for wake_word in self.wake_words):
                        wake_detected = True
                        self.logger.info("🎯 Wake word detected!")
                        
                        # Listen for actual command
                        return self.listen(timeout=10, phrase_timeout=5)
                        
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    self.logger.debug(f"Wake word detection error: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in wake word detection: {e}")
            return None
    
    def _recognize_speech(self, audio, quick: bool = False) -> Optional[str]:
        """Recognize speech from audio"""
        try:
            # Determine language for recognition
            current_lang = self.language_manager.current_language
            lang_code = 'hi-IN' if current_lang == 'hindi' else 'en-US'
            
            # Use appropriate recognition method
            if quick:
                # Quick recognition for wake words
                text = self.recognizer.recognize_google(audio, language=lang_code)
            else:
                # Full recognition with better accuracy
                text = self.recognizer.recognize_google(
                    audio,
                    language=lang_code,
                    show_all=False
                )
            
            self.logger.info(f"Recognized: {text}")
            return text.strip()
            
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
    
    def start_continuous_listening(self):
        """Start continuous listening mode"""
        self.continuous_listening = True
        self.logger.info("🎤 Continuous listening mode activated")
    
    def stop_continuous_listening(self):
        """Stop continuous listening mode"""
        self.continuous_listening = False
        self.logger.info("🎤 Continuous listening mode deactivated")
    
    def _process_continuous_audio(self):
        """Process audio in continuous listening mode"""
        try:
            # This would implement continuous audio processing
            # with voice activity detection and wake word recognition
            pass
        except Exception as e:
            self.logger.error(f"Error in continuous audio processing: {e}")
    
    def set_voice_settings(self, settings: Dict):
        """Update voice settings"""
        try:
            if 'rate' in settings:
                self.voice_settings['rate'] = settings['rate']
                self.tts_engine.setProperty('rate', settings['rate'])
            
            if 'volume' in settings:
                self.voice_settings['volume'] = settings['volume']
                self.tts_engine.setProperty('volume', settings['volume'])
            
            if 'voice_id' in settings:
                self.voice_settings['voice_id'] = settings['voice_id']
                self.tts_engine.setProperty('voice', settings['voice_id'])
            
            self.logger.info("Voice settings updated")
            
        except Exception as e:
            self.logger.error(f"Error updating voice settings: {e}")
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of available voices"""
        try:
            if not self.tts_engine:
                return []
            
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            self.logger.error(f"Error getting available voices: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if voice engine is available and initialized"""
        return VOICE_AVAILABLE and self.initialized
    
    def get_status(self) -> Dict:
        """Get voice engine status"""
        return {
            'initialized': self.initialized,
            'available': VOICE_AVAILABLE,
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'continuous_listening': self.continuous_listening,
            'voice_settings': self.voice_settings,
            'recognition_settings': self.recognition_settings,
            'wake_words': self.wake_words
        }
    
    def shutdown(self):
        """Shutdown voice engine"""
        self.logger.info("🎤 Shutting down Voice Engine...")
        
        self.initialized = False
        self.continuous_listening = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=2)
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        self.logger.info("✅ Voice Engine shutdown complete")