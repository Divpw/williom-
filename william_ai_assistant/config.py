# Configuration for William AI Assistant
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "google/gemini-2.0-flash-exp:free" # Updated to Gemini 2.0 Flash
OPENROUTER_FALLBACK_MODEL = "deepseek/deepseek-r1-0528:free" # Fallback model

# Optional headers for OpenRouter - can be left empty if not needed
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "") # e.g., "http://localhost" or your actual site
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "") # e.g., "William AI Assistant"

# Wake Word
WAKE_WORD = "hey william"

# Other configurations can be added here
# For example, paths to specific applications, default web browser, etc.
# Default microphone index (None for default)
MICROPHONE_INDEX = None # Or an integer like 1, 2, etc. if you know the specific mic index

# Speech recognition settings
PHRASE_TIME_LIMIT = 10 # seconds for listening to a command
BASE_ENERGY_THRESHOLD = 300 # Base energy threshold for voice activity detection
DYNAMIC_ENERGY_THRESHOLD = True # Adjust energy threshold dynamically based on ambient noise
DYNAMIC_ENERGY_ADJUSTMENT_DAMPING = 0.15
PAUSE_THRESHOLD = 0.8 # seconds of non-speaking audio before a phrase is considered complete
NON_SPEAKING_DURATION = 0.5 # seconds of non-speaking audio to keep on the end of the recording

# TTS settings
TTS_RATE = 150 # words per minute for text-to-speech output

# Visual Canvas
ENABLE_VISUAL_CANVAS = True # Set to False to disable the UI dashboard
CANVAS_DATA_FILE = "william_canvas_data.json" # File for passing data to the canvas

# Operational Mode
ALWAYS_LISTEN = False  # Set to True to enable 'always listen' mode, False to require wake word after each command.
ENABLE_PERSONALITY = True # Set to True to enable more personality in responses, False for more direct answers.
