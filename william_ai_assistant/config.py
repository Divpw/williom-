# Configuration for William AI Assistant

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"  # Replace with your actual OpenRouter API key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "deepseek/deepseek-r1-0528:free" # Corrected model name

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
