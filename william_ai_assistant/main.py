# Main application file for William AI Assistant

from william_ai_assistant import audio_listener
from william_ai_assistant import william_brain
from william_ai_assistant import system_commands
from william_ai_assistant import tts_engine
from william_ai_assistant import config

def main():
    """
    Main function to run William AI Assistant.
    """
    # Initialize components
    tts_engine.initialize_engine()
    audio_listener.adjust_for_ambient_noise()

    tts_engine.speak("William AI Assistant is now active.")
    print("William AI Assistant is now active. Listening for wake word...")

    try:
        while True:
            if audio_listener.listen_for_wake_word():
                command_text = audio_listener.listen_for_command()

                if command_text:
                    print(f"Processing command: '{command_text}'")

                    # Try to process as a system command first
                    system_response = system_commands.process_system_command(command_text)

                    if system_response:
                        tts_engine.speak(system_response)
                    else:
                        # If not a system command, send to LLM
                        if not config.OPENROUTER_API_KEY or config.OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE" or config.OPENROUTER_API_KEY == "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": # Second part of OR is the example key
                            warning_message = "The OpenRouter API key is not configured. Please set it in config.py to use LLM features."
                            print(f"WARNING: {warning_message}")
                            tts_engine.speak(warning_message)
                            # Check if the user provided key in the prompt should be considered "not configured"
                            # For now, if it's the example key, we'll treat it as unconfigured for LLM specific tasks.
                            if config.OPENROUTER_API_KEY == "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":
                                tts_engine.speak("Using the example API key. LLM features may be limited or not work as expected for personalized tasks without a dedicated key.")
                            # Even if API key is the example one, we can still try, OpenRouter might allow some free tier access.
                            llm_response = william_brain.get_llm_response(command_text)
                            tts_engine.speak(llm_response)

                        else:
                            llm_response = william_brain.get_llm_response(command_text)
                            tts_engine.speak(llm_response)
                else:
                    # listen_for_command already gives feedback like "I didn't hear a command."
                    pass # Or print("No command processed.")
            else:
                # This case (False from listen_for_wake_word) usually means a sr.RequestError
                # audio_listener.py already speaks an error message.
                # We might want to add a delay here before retrying to avoid spamming requests if there's a persistent issue.
                print("Error with wake word listener or speech service. Retrying after a short delay...")
                tts_engine.speak("There was an issue with the speech service. I will try again in a moment.")
                import time
                time.sleep(5) # Wait 5 seconds before trying to listen for wake word again

    except KeyboardInterrupt:
        print("\nExiting William AI Assistant...")
        tts_engine.speak("Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred in main loop: {e}")
        tts_engine.speak("An unexpected error occurred. I have to shut down.")
        # Log the error to a file or more detailed logging mechanism if desired

if __name__ == "__main__":
    # Check for API key before starting, as it's crucial for part of the functionality
    if not config.OPENROUTER_API_KEY or config.OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
        print("CRITICAL ERROR: OpenRouter API key is not set in config.py.")
        print("Please set OPENROUTER_API_KEY to your actual key to use LLM features.")
        # Optionally, initialize TTS just to speak this message if possible
        try:
            tts_engine.initialize_engine()
            if tts_engine.engine_initialized:
                 tts_engine.speak("Critical Error: OpenRouter API key is not configured. Please set it in the config file and restart.")
        except Exception:
            pass # Ignore if TTS itself fails here
    elif config.OPENROUTER_API_KEY == "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":
        print("WARNING: Using the example OpenRouter API key provided in the prompt.")
        print("LLM features may be limited or not work as expected without a dedicated key.")
        print("The application will proceed, but for full functionality, please use your own OpenRouter API key.")
        try:
            tts_engine.initialize_engine() # Ensure tts is up to voice the warning
            if tts_engine.engine_initialized:
                tts_engine.speak("Warning: You are using the example API key. LLM features might be restricted. Please consider using your own OpenRouter API key for full functionality.")
        except Exception:
            pass
        main() # Proceed even with the example key
    else:
        main()
