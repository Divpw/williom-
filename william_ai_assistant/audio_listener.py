# Handles wake word detection and speech-to-text conversion
import speech_recognition as sr
from william_ai_assistant import tts_engine, config
import time

# Initialize recognizer
recognizer = sr.Recognizer()
microphone = None # Will be initialized in initialize_microphone

def initialize_microphone():
    """Initializes the microphone, handling potential errors."""
    global microphone
    if microphone is not None:
        return True # Already initialized

    try:
        microphone = sr.Microphone(device_index=config.MICROPHONE_INDEX)
        print(f"Microphone initialized with device index: {config.MICROPHONE_INDEX if config.MICROPHONE_INDEX is not None else 'default'}.")
        # Perform a brief test listen to catch immediate issues
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5) # Quick adjustment
        print("Microphone test successful.")
        return True
    except sr.RequestError as e: # This can happen if no default mic is found or specific index is bad sometimes
        print(f"Error initializing microphone (sr.RequestError): {e}. This might indicate no microphone is connected or configured.")
        tts_engine.speak("Error initializing microphone. Please check your microphone connection and configuration.")
        microphone = None
        return False
    except AttributeError as e: # Can occur if device_index is invalid leading to issues accessing mic properties
        print(f"Error initializing microphone (AttributeError): {e}. This might be due to an invalid microphone device index.")
        tts_engine.speak("Invalid microphone configuration. Please check the microphone device index.")
        microphone = None
        return False
    except Exception as e: # Catch any other exceptions during microphone initialization
        print(f"An unexpected error occurred while initializing the microphone: {e}")
        tts_engine.speak("An unexpected error occurred with the microphone setup.")
        microphone = None
        return False

def adjust_for_ambient_noise():
    """Adjusts the recognizer sensitivity to ambient noise."""
    global microphone, recognizer
    if not microphone and not initialize_microphone():
        print("Cannot adjust for ambient noise, microphone not available.")
        return

    print("Adjusting for ambient noise, please be quiet for a moment...")
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.energy_threshold = config.BASE_ENERGY_THRESHOLD
        recognizer.dynamic_energy_threshold = config.DYNAMIC_ENERGY_THRESHOLD
        recognizer.dynamic_energy_adjustment_damping = config.DYNAMIC_ENERGY_ADJUSTMENT_DAMPING
        recognizer.pause_threshold = config.PAUSE_THRESHOLD
        recognizer.non_speaking_duration = config.NON_SPEAKING_DURATION
        print(f"Ambient noise adjustment complete. Energy threshold set to: {recognizer.energy_threshold}")
    except sr.WaitTimeoutError:
        print("Timeout during ambient noise adjustment. Using default energy threshold.")
        # Fallback or re-attempt logic could be added here
    except Exception as e:
        print(f"Error during ambient noise adjustment: {e}")
        tts_engine.speak("Could not adjust for ambient noise due to an error.")


def listen_for_wake_word(wake_word=config.WAKE_WORD):
    """
    Continuously listens for the wake word.
    Returns True if the wake word is detected, False otherwise (e.g. error).
    """
    global recognizer, microphone
    if not microphone and not initialize_microphone():
        print("Cannot listen for wake word, microphone not available.")
        # Give some time for TTS to speak if it was triggered in initialize_microphone
        time.sleep(3)
        return False

    # Ensure ambient noise adjustment is done before listening, if not already
    # This might be redundant if main.py calls adjust_for_ambient_noise() at startup,
    # but good for robustness if this function is called independently.
    # Consider if this should always be called or only if a flag indicates it hasn't been.
    # For now, let main.py handle the initial adjustment.

    print(f"Listening for wake word: '{wake_word}'...")
    try:
        with microphone as source:
            while True: # Keep listening until wake word or critical error
                try:
                    audio = recognizer.listen(source, phrase_time_limit=config.PHRASE_TIME_LIMIT)
                    text = recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")
                    if wake_word in text:
                        print("Wake word detected!")
                        tts_engine.speak("Yes?")
                        return True
                except sr.WaitTimeoutError:
                    # print("No speech detected, still listening for wake word...")
                    pass # Normal timeout, continue listening
                except sr.UnknownValueError:
                    # print("Could not understand audio, still listening for wake word...")
                    pass # Normal, speech not recognized, continue listening
                except sr.RequestError as e:
                    print(f"Google Speech Recognition service error: {e}")
                    tts_engine.speak("Speech service error. Please check your internet connection.")
                    # Depending on severity, might want to pause and retry, or return False
                    time.sleep(2) # Brief pause before returning False or retrying listen
                    return False # Indicate an error occurred
    except AttributeError: # This can happen if microphone is None and initialization failed silently prior
        print("Microphone not available for wake word detection (AttributeError).")
        # This case should ideally be caught by the initial check, but as a safeguard.
        return False
    except Exception as e: # Catch-all for other unexpected errors with the microphone
        print(f"An unexpected error occurred with the microphone during wake word listening: {e}")
        tts_engine.speak("A microphone error occurred while listening for the wake word.")
        return False

def listen_for_command():
    """
    Listens for a command after the wake word is detected.
    Returns the transcribed text of the command or None if an error/timeout occurs.
    """
    global recognizer, microphone
    if not microphone and not initialize_microphone():
        print("Cannot listen for command, microphone not available.")
        # Give some time for TTS to speak if it was triggered in initialize_microphone
        time.sleep(3)
        return None

    print("Listening for command...")
    try:
        with microphone as source:
            # It's good practice to ensure the microphone is "fresh" for the command.
            # While adjust_for_ambient_noise is usually done once,
            # a quick listen can help if the environment changed.
            # However, frequent adjustments might be too slow.
            # For now, assume initial adjustment is sufficient.
            # recognizer.adjust_for_ambient_noise(source, duration=0.2) # Optional quick re-adjust

            audio = recognizer.listen(source, phrase_time_limit=config.PHRASE_TIME_LIMIT)
            command = recognizer.recognize_google(audio).lower()
            print(f"Command heard: {command}")
            return command
    except sr.WaitTimeoutError:
        tts_engine.speak("I didn't hear a command.")
        print("No command heard (timeout).")
        return None
    except sr.UnknownValueError:
        tts_engine.speak("Sorry, I didn't understand that.")
        print("Could not understand command.")
        return None
    except sr.RequestError as e:
        print(f"Google Speech Recognition service error during command listen: {e}")
        tts_engine.speak("There was an error with the speech service while listening for your command.")
        return None
    except AttributeError: # Microphone became None unexpectedly
        print("Microphone not available for command listening (AttributeError).")
        tts_engine.speak("Microphone error. Cannot listen for command.")
        return None
    except Exception as e: # Catch-all for other unexpected errors
        print(f"An unexpected error occurred during command listening: {e}")
        tts_engine.speak("An unexpected error occurred while trying to listen.")
        return None

if __name__ == '__main__':
    # This is for testing the audio_listener.py module independently
    # Initialize tts_engine for testing feedback
    if not tts_engine.engine_initialized: # Check custom flag
        tts_engine.initialize_engine()

    if initialize_microphone(): # Crucial step for testing
        adjust_for_ambient_noise()

        if listen_for_wake_word():
            command = listen_for_command()
            if command:
                tts_engine.speak(f"You said: {command}")
            else:
                tts_engine.speak("No command was processed.")
        else:
            print("Wake word not detected or error occurred.")
    else:
        print("Microphone initialization failed. Cannot run audio listener test.")
    # Initialize tts_engine for testing feedback
    if not hasattr(tts_engine, 'engine'): # Basic check if engine is initialized
        tts_engine.engine = tts_engine.pyttsx3.init()
        tts_engine.engine.setProperty('rate', config.TTS_RATE)

    adjust_for_ambient_noise()

    if listen_for_wake_word():
        command = listen_for_command()
        if command:
            tts_engine.speak(f"You said: {command}")
        else:
            tts_engine.speak("No command was processed.")
    else:
        print("Wake word not detected or error occurred.")
