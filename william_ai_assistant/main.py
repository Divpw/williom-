# Main application file for William AI Assistant
import time
import sys # For sys.exit()
from william_ai_assistant import audio_listener
# william_brain and system_commands will be used by the router, not directly by main's process_command
# from william_ai_assistant import william_brain
# from william_ai_assistant import system_commands
from william_ai_assistant import tts_engine
from william_ai_assistant import config as app_config # Renamed to avoid clash with root config

from context_manager import ContextManager # Import from root
from router import CommandRouter # Import from root

# Attempt to import root config for always_listen and personality settings
try:
    import config as root_config
except ImportError:
    # Fallback if running main.py directly and root is not in python path correctly for some reason
    # (though it should be if context_manager was imported successfully from root)
    class RootConfigMock:
        always_listen = False # Default to False
        enable_personality = False # Default
    root_config = RootConfigMock()
    print("Warning: Root config.py not found by main.py, using default values for always_listen and personality.")

# Global command_router instance, initialized in main()
command_router_instance: CommandRouter = None

def process_command(command_text: str, context_mgr: ContextManager) -> str:
    """
    Processes the command using the CommandRouter.
    Updates context and returns assistant's response.
    """
    global command_router_instance
    if not command_router_instance:
        # This should not happen if main() initializes it properly
        error_msg = "CommandRouter not initialized!"
        print(f"CRITICAL ERROR: {error_msg}")
        return error_msg

    print(f"Processing command via Router: '{command_text}'")
    context_mgr.add_message("user", command_text)

    # Get history BEFORE the current user message for the LLM context
    history_for_llm = context_mgr.get_history()
    # The user's current command_text is the last item if we get history after adding.
    # The LLM in william_brain.py expects the current user prompt separately.
    # So, we can pass history[:-1] or let william_brain handle it if it expects current prompt in history.
    # Given current william_brain.py, it adds the text_input to messages after processing history.
    # So, passing the full history from context_mgr (which includes the latest user prompt) is fine.

    # The API key check for OpenRouter is now implicitly handled by william_brain.get_llm_response
    # if the router's fallback_chat_handler calls it. We don't need the explicit check here anymore.

    assistant_response = command_router_instance.route(command_text, history=history_for_llm)

    context_mgr.add_message("assistant", assistant_response)
    return assistant_response


def main():
    """
    Main function to run William AI Assistant.
    """
    global command_router_instance

    # TTS engine is initialized in the `if __name__ == "__main__":` block before `main()` is called.
    audio_listener.adjust_for_ambient_noise() # This will also initialize the microphone if needed.

    # Initialize ContextManager for conversation history
    context_manager = ContextManager()

    # Initialize CommandRouter
    command_router_instance = CommandRouter()
    print("Command Router initialized.")

    # Personal Assistant Declaration
    declaration_message = "🚫 William AI is a private desktop assistant. Not intended for distribution."
    print(declaration_message)
    tts_engine.speak(declaration_message)

    tts_engine.speak("William AI Assistant is now active.")

    # Determine initial listening mode
    currently_listening_for_command = hasattr(root_config, 'always_listen') and root_config.always_listen
    if not currently_listening_for_command:
        print("William AI Assistant is now active. Listening for wake word...")
    else:
        print("William AI Assistant is now active and in always listen mode.")
        tts_engine.speak("Always listen mode is active.") # Notify user

    try:
        while True:
            command_text = None
            if currently_listening_for_command:
                print("Listening for next command...")
                # phrase_time_limit is handled by listen_for_command internally via config
                command_text = audio_listener.listen_for_command()
                if command_text is None: # Timeout or silence
                    if hasattr(root_config, 'always_listen') and root_config.always_listen:
                        # Still in always listen mode, just loop again after a short pause perhaps
                        # print("No command heard, still listening...")
                        time.sleep(0.1) # Brief pause
                        continue
                    else:
                        # This case should not be reached if always_listen is true and command_text is None due to timeout.
                        # If always_listen became false somehow, revert to wake word.
                        currently_listening_for_command = False
                        print("No command heard. Reverting to wake word.")
                        tts_engine.speak("No command. Waiting for wake word.")
                        continue
            else: # Not currently_listening_for_command, so wait for wake word
                print("Listening for wake word...")
                if audio_listener.listen_for_wake_word():
                    currently_listening_for_command = True # Heard wake word, now listen for command
                    # Immediately listen for command after wake word
                    print("Wake word detected. Listening for command...")
                    command_text = audio_listener.listen_for_command()
                else:
                    # Error with wake word listener (e.g., speech service error)
                    print("Error with wake word listener or speech service. Retrying after delay...")
                    tts_engine.speak("There was an issue with the speech service. I will try again.")
                    time.sleep(3)
                    continue # Retry listening for wake word

            if command_text:
                assistant_response = process_command(command_text, context_manager)
                tts_engine.speak(assistant_response)

                # Decide if we should continue listening for a command or go back to wake word
                if hasattr(root_config, 'always_listen') and root_config.always_listen:
                    currently_listening_for_command = True
                    # No need to print "listening for next command" here, it's at the start of the loop
                else:
                    currently_listening_for_command = False
                    print("Command processed. Listening for wake word...")
                    # tts_engine.speak("Waiting for wake word.") # Can be too verbose
            else:
                # No command heard after wake word, or timeout in always_listen mode
                if currently_listening_for_command and not (hasattr(root_config, 'always_listen') and root_config.always_listen):
                    # This means wake word was heard, but no command followed. Revert to wake word.
                    currently_listening_for_command = False
                    print("No command heard after wake word. Listening for wake word again...")
                    # tts_engine.speak("I didn't catch that. Waiting for wake word.")


    except KeyboardInterrupt:
        print("\nExiting William AI Assistant via KeyboardInterrupt...")
        if tts_engine.engine_initialized:
            tts_engine.speak("Goodbye!")
        # Resources like microphone (if held outside 'with' or in global scope)
        # or TTS engine itself might need explicit cleanup if not handled by OS on exit.
        # pyttsx3 engine doesn't usually need explicit stop on normal exit.
        # Microphone is used with context manager, so it should release.
        print("Exited cleanly.")
        sys.exit(0)
    except Exception as e:
        error_message = f"An unexpected error occurred in main loop: {e}"
        print(error_message)
        # Add more detailed logging here if a logging framework is introduced
        # For now, just printing to console.

        if tts_engine.engine_initialized:
            tts_engine.speak("Something went wrong. Shutting down.")
        else:
            # This case might happen if TTS failed to initialize early on
            print("TTS not available to announce shutdown.")

        # Attempt to clean up resources if any were globally acquired and not managed by context managers
        # For example, if tts_engine had a specific close/shutdown method:
        # if hasattr(tts_engine, 'shutdown') and callable(tts_engine.shutdown):
        # tts_engine.shutdown()
        # For speech_recognition's Microphone, it's typically used with a context manager,
        # which handles cleanup. If used globally, it might need explicit closing.
        # However, current audio_listener.py uses 'with microphone as source:'.

        print("Application shutting down due to an error.")
        sys.exit(1) # Exit with a non-zero code to indicate an error

if __name__ == "__main__":
    # API key is now loaded from .env via config.py
    # Initial check to ensure tts_engine can be initialized for critical errors.
    try:
        tts_engine.initialize_engine()
    except Exception as e:
        print(f"FATAL: Could not initialize TTS engine: {e}. The application cannot continue.")
        # No tts_engine.speak here as it might be the source of the problem.
        # Consider logging to a file here if advanced logging is set up.
        exit(1) # Exit if TTS cannot start, as it's critical for feedback.

    if not app_config.OPENROUTER_API_KEY:
        error_message = "CRITICAL ERROR: OpenRouter API key is not found. Please ensure it is set in the .env file."
        print(error_message)
        tts_engine.speak(error_message + " The application will now exit.")
        exit(1) # Exit if API key is missing

    main()
