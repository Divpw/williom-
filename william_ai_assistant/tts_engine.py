# Text-to-Speech engine
import pyttsx3
from william_ai_assistant import config # To get TTS_RATE

engine = None
# This flag helps prevent re-initialization issues or use before init.
engine_initialized = False

def initialize_engine():
    """Initializes the pyttsx3 engine."""
    global engine, engine_initialized
    if not engine_initialized:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', config.TTS_RATE)
            # You can also list and set voices here if needed
            # voices = engine.getProperty('voices')
            # engine.setProperty('voice', voices[0].id) # Example: Set to the first available voice
            engine_initialized = True
            print("TTS Engine Initialized.")
        except Exception as e:
            print(f"Error initializing pyttsx3 engine: {e}")
            print("Text-to-speech will not be available.")
            engine = None # Ensure engine is None if initialization fails
            engine_initialized = False # Explicitly mark as not initialized

def speak(text):
    """
    Converts the given text to speech.
    """
    global engine, engine_initialized
    if not engine_initialized:
        print("TTS engine not initialized. Attempting to initialize now.")
        initialize_engine() # Attempt to initialize if not already

    if engine:
        try:
            print(f"Speaking: {text}")
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error during speech: {e}")
    else:
        # Fallback if engine couldn't be initialized or is None
        print(f"TTS Engine not available. Would have said: {text}")

if __name__ == '__main__':
    # This is for testing the tts_engine.py module independently
    print("Testing TTS Engine...")
    initialize_engine() # Explicitly initialize for test

    if engine_initialized:
        speak("Hello, this is William's text to speech engine.")
        speak(f"My current speech rate is {config.TTS_RATE} words per minute.")

        engine.setProperty('rate', 200) # Test changing rate
        speak("I can also speak faster.")

        engine.setProperty('rate', 100) # Test changing rate
        speak("Or slower.")

        # Reset to config rate for consistency if other tests import this
        engine.setProperty('rate', config.TTS_RATE)
        speak("Testing complete. Resetting rate.")
    else:
        print("TTS Engine could not be initialized for testing.")
