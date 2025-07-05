# Main application file for William AI Assistant
import time
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

    tts_engine.initialize_engine()
    audio_listener.adjust_for_ambient_noise()

    # Initialize ContextManager for conversation history
    context_manager = ContextManager()

    # Initialize CommandRouter
    command_router_instance = CommandRouter()
    print("Command Router initialized.")

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
                command_text = audio_listener.listen_for_command(timeout=10, phrase_time_limit=10) # Use a timeout
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
        print("\nExiting William AI Assistant...")
        tts_engine.speak("Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred in main loop: {e}")
        tts_engine.speak("An unexpected error occurred. I have to shut down.")
        # Log the error to a file or more detailed logging mechanism if desired

if __name__ == "__main__":
    # Check for API key before starting, as it's crucial for part of the functionality
    if not app_config.OPENROUTER_API_KEY or app_config.OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
        print("CRITICAL ERROR: OpenRouter API key is not set in william_ai_assistant/config.py.")
        print("Please set OPENROUTER_API_KEY to your actual key to use LLM features.")
        # Optionally, initialize TTS just to speak this message if possible
        try:
            tts_engine.initialize_engine()
            if tts_engine.engine_initialized:
                 tts_engine.speak("Critical Error: OpenRouter API key is not configured. Please set it in the config file and restart.")
        except Exception:
            pass # Ignore if TTS itself fails here
    elif app_config.OPENROUTER_API_KEY == "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": # Example key
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
