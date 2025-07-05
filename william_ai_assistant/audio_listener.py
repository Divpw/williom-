# Handles wake word detection and speech-to-text conversion
import speech_recognition as sr
from william_ai_assistant import tts_engine, config

# Initialize recognizer
recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=config.MICROPHONE_INDEX)

def adjust_for_ambient_noise():
    """Adjusts the recognizer sensitivity to ambient noise."""
    print("Adjusting for ambient noise, please be quiet for a moment...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    recognizer.energy_threshold = config.BASE_ENERGY_THRESHOLD
    recognizer.dynamic_energy_threshold = config.DYNAMIC_ENERGY_THRESHOLD
    recognizer.dynamic_energy_adjustment_damping = config.DYNAMIC_ENERGY_ADJUSTMENT_DAMPING
    recognizer.pause_threshold = config.PAUSE_THRESHOLD
    recognizer.non_speaking_duration = config.NON_SPEAKING_DURATION
    print(f"Ambient noise adjustment complete. Energy threshold set to: {recognizer.energy_threshold}")

def listen_for_wake_word(wake_word=config.WAKE_WORD):
    """
    Continuously listens for the wake word.
    Returns True if the wake word is detected.
    """
    global recognizer, microphone

    with microphone as source:
        print(f"Listening for wake word: '{wake_word}'...")
        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=config.PHRASE_TIME_LIMIT)
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                if wake_word in text:
                    print("Wake word detected!")
                    tts_engine.speak("Yes?")
                    return True
            except sr.WaitTimeoutError:
                # No speech detected within the time limit, continue listening
                # print("No speech detected, still listening for wake word...")
                pass
            except sr.UnknownValueError:
                # Could not understand audio
                # print("Could not understand audio, still listening for wake word...")
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                tts_engine.speak("Speech service error. Please check your internet connection.")
                return False # Potentially exit or wait longer if critical service is down

def listen_for_command():
    """
    Listens for a command after the wake word is detected.
    Returns the transcribed text of the command or None if an error occurs.
    """
    global recognizer, microphone

    with microphone as source:
        print("Listening for command...")
        try:
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
            print(f"Could not request results from Google Speech Recognition service; {e}")
            tts_engine.speak("There was an error with the speech service.")
            return None

if __name__ == '__main__':
    # This is for testing the audio_listener.py module independently
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
