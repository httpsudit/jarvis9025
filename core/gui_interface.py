"""
GUI Interface for JARVIS - Modern Tkinter Interface
Advanced graphical user interface with modern design
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json

from utils.logger import get_logger
from utils.config_manager import ConfigManager
from utils.language_manager import LanguageManager

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False

class JARVISInterface:
    """
    Advanced GUI Interface for JARVIS
    Modern, responsive interface with dark theme
    """
    
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        self.language_manager = LanguageManager()
        
        # GUI components
        self.root = None
        self.chat_display = None
        self.input_entry = None
        self.status_label = None
        self.system_stats_frame = None
        
        # State
        self.is_running = False
        self.chat_history = []
        
        # Theme settings
        self.theme = {
            'bg_primary': '#1a1a1a',
            'bg_secondary': '#2d2d2d',
            'bg_accent': '#3d3d3d',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'accent_color': '#00d4ff',
            'success_color': '#00ff88',
            'warning_color': '#ffaa00',
            'error_color': '#ff4444'
        }
        
        self.logger.info("🖥️ GUI Interface initialized")
    
    def create_interface(self):
        """Create the main GUI interface"""
        try:
            if CTK_AVAILABLE:
                self._create_modern_interface()
            else:
                self._create_classic_interface()
                
            self.logger.info("✅ GUI interface created successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating GUI interface: {e}")
            raise
    
    def _create_modern_interface(self):
        """Create modern interface using CustomTkinter"""
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("JARVIS AI Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self._create_sidebar()
        
        # Create main content area
        self._create_main_content()
        
        # Create status bar
        self._create_status_bar()
        
        # Bind events
        self._bind_events()
    
    def _create_classic_interface(self):
        """Create classic interface using standard Tkinter"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("JARVIS AI Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.root.configure(bg=self.theme['bg_primary'])
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.theme['bg_primary'])
        style.configure('TLabel', background=self.theme['bg_primary'], foreground=self.theme['text_primary'])
        style.configure('TButton', background=self.theme['bg_secondary'], foreground=self.theme['text_primary'])
        
        # Create main layout
        self._create_classic_layout()
        
        # Bind events
        self._bind_events()
    
    def _create_sidebar(self):
        """Create sidebar with controls"""
        if not CTK_AVAILABLE:
            return
            
        # Sidebar frame
        sidebar_frame = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # JARVIS logo/title
        logo_label = ctk.CTkLabel(sidebar_frame, text="🤖 JARVIS", font=ctk.CTkFont(size=24, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(sidebar_frame, text="🟢 ONLINE", font=ctk.CTkFont(size=14))
        self.status_indicator.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Control buttons
        self.voice_button = ctk.CTkButton(sidebar_frame, text="🎤 Voice Mode", command=self._toggle_voice_mode)
        self.voice_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.learning_button = ctk.CTkButton(sidebar_frame, text="🧠 Learning Mode", command=self._toggle_learning_mode)
        self.learning_button.grid(row=3, column=0, padx=20, pady=10)
        
        # System stats frame
        stats_frame = ctk.CTkFrame(sidebar_frame)
        stats_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        stats_label = ctk.CTkLabel(stats_frame, text="System Stats", font=ctk.CTkFont(size=16, weight="bold"))
        stats_label.pack(pady=10)
        
        self.cpu_label = ctk.CTkLabel(stats_frame, text="CPU: 0%")
        self.cpu_label.pack(pady=2)
        
        self.memory_label = ctk.CTkLabel(stats_frame, text="Memory: 0%")
        self.memory_label.pack(pady=2)
        
        self.disk_label = ctk.CTkLabel(stats_frame, text="Disk: 0%")
        self.disk_label.pack(pady=2)
        
        # Language selector
        lang_frame = ctk.CTkFrame(sidebar_frame)
        lang_frame.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        
        lang_label = ctk.CTkLabel(lang_frame, text="Language", font=ctk.CTkFont(size=14, weight="bold"))
        lang_label.pack(pady=5)
        
        self.language_var = tk.StringVar(value="English")
        self.language_menu = ctk.CTkOptionMenu(lang_frame, values=["English", "Hindi"], 
                                             variable=self.language_var, command=self._change_language)
        self.language_menu.pack(pady=5)
    
    def _create_main_content(self):
        """Create main content area"""
        if not CTK_AVAILABLE:
            return
            
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = ctk.CTkTextbox(main_frame, height=400, font=ctk.CTkFont(size=12))
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Input frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input entry
        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Type your command here...", 
                                       font=ctk.CTkFont(size=14), height=40)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Send button
        self.send_button = ctk.CTkButton(input_frame, text="Send", command=self._send_command, 
                                        width=80, height=40)
        self.send_button.grid(row=0, column=1)
        
        # Voice button
        self.voice_input_button = ctk.CTkButton(input_frame, text="🎤", command=self._voice_input, 
                                               width=50, height=40)
        self.voice_input_button.grid(row=0, column=2, padx=(10, 0))
    
    def _create_classic_layout(self):
        """Create classic Tkinter layout"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.theme['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🤖 JARVIS AI Assistant", 
                              font=('Arial', 20, 'bold'), 
                              bg=self.theme['bg_primary'], 
                              fg=self.theme['text_primary'])
        title_label.pack(pady=10)
        
        # Chat display
        chat_frame = tk.Frame(main_frame, bg=self.theme['bg_secondary'])
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, 
                                                     bg=self.theme['bg_secondary'], 
                                                     fg=self.theme['text_primary'],
                                                     font=('Consolas', 11),
                                                     wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=self.theme['bg_primary'])
        input_frame.pack(fill=tk.X, pady=10)
        
        self.input_entry = tk.Entry(input_frame, 
                                   bg=self.theme['bg_secondary'], 
                                   fg=self.theme['text_primary'],
                                   font=('Arial', 12),
                                   insertbackground=self.theme['text_primary'])
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.send_button = tk.Button(input_frame, text="Send", 
                                    command=self._send_command,
                                    bg=self.theme['accent_color'], 
                                    fg=self.theme['text_primary'],
                                    font=('Arial', 10, 'bold'))
        self.send_button.pack(side=tk.RIGHT)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=self.theme['bg_secondary'])
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Ready", 
                                    bg=self.theme['bg_secondary'], 
                                    fg=self.theme['success_color'],
                                    font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def _create_status_bar(self):
        """Create status bar"""
        if not CTK_AVAILABLE:
            return
            
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=20, pady=5)
        
        # Time label
        self.time_label = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=12))
        self.time_label.pack(side="right", padx=20, pady=5)
    
    def _bind_events(self):
        """Bind keyboard and window events"""
        if self.input_entry:
            self.input_entry.bind('<Return>', lambda e: self._send_command())
        
        if self.root:
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _send_command(self):
        """Send command to JARVIS"""
        try:
            if not self.input_entry:
                return
                
            command = self.input_entry.get().strip()
            if not command:
                return
            
            # Clear input
            self.input_entry.delete(0, tk.END)
            
            # Display user input
            self._add_message(f"You: {command}", "user")
            
            # Update status
            self._update_status("Processing...", "processing")
            
            # Process command in separate thread
            thread = threading.Thread(target=self._process_command_thread, args=(command,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error sending command: {e}")
            self._add_message(f"Error: {str(e)}", "error")
    
    def _process_command_thread(self, command):
        """Process command in separate thread"""
        try:
            # Process through JARVIS
            response = self.jarvis.process_command(command)
            
            # Update GUI in main thread
            self.root.after(0, self._handle_response, response)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self.root.after(0, self._add_message, f"Error: {str(e)}", "error")
    
    def _handle_response(self, response):
        """Handle JARVIS response"""
        try:
            if isinstance(response, dict):
                message = response.get('text', 'No response')
                success = response.get('success', True)
                
                if success:
                    self._add_message(f"JARVIS: {message}", "assistant")
                else:
                    self._add_message(f"JARVIS: {message}", "error")
            else:
                self._add_message(f"JARVIS: {str(response)}", "assistant")
            
            # Update status
            self._update_status("Ready", "ready")
            
        except Exception as e:
            self.logger.error(f"Error handling response: {e}")
            self._add_message(f"Error handling response: {str(e)}", "error")
    
    def _add_message(self, message, message_type="info"):
        """Add message to chat display"""
        try:
            if not self.chat_display:
                return
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            
            if CTK_AVAILABLE:
                self.chat_display.insert("end", formatted_message)
                self.chat_display.see("end")
            else:
                # Color coding for classic interface
                self.chat_display.insert(tk.END, formatted_message)
                self.chat_display.see(tk.END)
            
            # Store in history
            self.chat_history.append({
                'timestamp': timestamp,
                'message': message,
                'type': message_type
            })
            
        except Exception as e:
            self.logger.error(f"Error adding message: {e}")
    
    def _update_status(self, status, status_type="info"):
        """Update status display"""
        try:
            if self.status_label:
                self.status_label.configure(text=f"Status: {status}")
            
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def _voice_input(self):
        """Handle voice input"""
        try:
            if not self.jarvis.voice_engine.is_available():
                self._add_message("Voice engine not available", "error")
                return
            
            self._update_status("Listening...", "listening")
            
            # Start voice input in separate thread
            thread = threading.Thread(target=self._voice_input_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error with voice input: {e}")
            self._add_message(f"Voice input error: {str(e)}", "error")
    
    def _voice_input_thread(self):
        """Voice input thread"""
        try:
            # Listen for voice input
            voice_text = self.jarvis.voice_engine.listen(timeout=10)
            
            if voice_text:
                # Update GUI in main thread
                self.root.after(0, self._handle_voice_input, voice_text)
            else:
                self.root.after(0, self._update_status, "No voice input detected", "warning")
                
        except Exception as e:
            self.logger.error(f"Voice input thread error: {e}")
            self.root.after(0, self._add_message, f"Voice input error: {str(e)}", "error")
    
    def _handle_voice_input(self, voice_text):
        """Handle voice input result"""
        try:
            # Set input text
            if self.input_entry:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, voice_text)
            
            # Process command
            self._send_command()
            
        except Exception as e:
            self.logger.error(f"Error handling voice input: {e}")
    
    def _toggle_voice_mode(self):
        """Toggle voice mode"""
        try:
            self.jarvis.voice_mode = not self.jarvis.voice_mode
            status = "enabled" if self.jarvis.voice_mode else "disabled"
            self._add_message(f"Voice mode {status}", "info")
            
        except Exception as e:
            self.logger.error(f"Error toggling voice mode: {e}")
    
    def _toggle_learning_mode(self):
        """Toggle learning mode"""
        try:
            self.jarvis.learning_mode = not self.jarvis.learning_mode
            status = "enabled" if self.jarvis.learning_mode else "disabled"
            self._add_message(f"Learning mode {status}", "info")
            
        except Exception as e:
            self.logger.error(f"Error toggling learning mode: {e}")
    
    def _change_language(self, language):
        """Change system language"""
        try:
            lang_map = {"English": "english", "Hindi": "hindi"}
            if language in lang_map:
                self.jarvis.switch_language(lang_map[language])
                
        except Exception as e:
            self.logger.error(f"Error changing language: {e}")
    
    def _update_system_stats(self):
        """Update system statistics display"""
        try:
            if not hasattr(self, 'cpu_label'):
                return
                
            stats = self.jarvis.system_controller.get_system_state()
            
            if self.cpu_label:
                self.cpu_label.configure(text=f"CPU: {stats.get('cpu_percent', 0):.1f}%")
            
            if self.memory_label:
                self.memory_label.configure(text=f"Memory: {stats.get('memory_percent', 0):.1f}%")
            
            if self.disk_label:
                self.disk_label.configure(text=f"Disk: {stats.get('disk_percent', 0):.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error updating system stats: {e}")
    
    def _update_time(self):
        """Update time display"""
        try:
            if hasattr(self, 'time_label') and self.time_label:
                current_time = datetime.now().strftime("%H:%M:%S")
                self.time_label.configure(text=current_time)
                
        except Exception as e:
            self.logger.error(f"Error updating time: {e}")
    
    def _start_update_loop(self):
        """Start GUI update loop"""
        try:
            # Update system stats every 5 seconds
            self._update_system_stats()
            self.root.after(5000, self._start_update_loop)
            
            # Update time every second
            self._update_time()
            self.root.after(1000, self._update_time)
            
        except Exception as e:
            self.logger.error(f"Error in update loop: {e}")
    
    def _on_closing(self):
        """Handle window closing"""
        try:
            if messagebox.askokcancel("Quit", "Do you want to quit JARVIS?"):
                self.is_running = False
                self.jarvis.shutdown()
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Error closing application: {e}")
            self.root.destroy()
    
    def run(self):
        """Run the GUI interface"""
        try:
            self.create_interface()
            self.is_running = True
            
            # Add welcome message
            self._add_message("JARVIS AI Assistant initialized and ready!", "info")
            
            # Start update loops
            self._start_update_loop()
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"❌ Error running GUI: {e}")
            raise
    
    def get_status(self):
        """Get GUI status"""
        return {
            'running': self.is_running,
            'chat_history_length': len(self.chat_history),
            'ctk_available': CTK_AVAILABLE
        }