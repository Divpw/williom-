# Main application file for William AI Assistant
import time
import sys # For sys.exit()
import os # For path manipulation
import webbrowser # For opening the canvas
from william_ai_assistant import audio_listener
from . import canvas_utils # Import canvas utilities
# william_brain and system_commands will be used by the router, not directly by main's process_command
# from william_ai_assistant import william_brain
# from william_ai_assistant import system_commands
from william_ai_assistant import tts_engine
from william_ai_assistant import config as app_config # This is the single source of truth for config

# Imports for context_manager and router, assuming main.py is part of william_ai_assistant package
from william_ai_assistant.context_manager import ContextManager
from william_ai_assistant.router import CommandRouter
# Potentially, if plugin_manager is used directly in main later:
# from william_ai_assistant.plugin_manager import PluginManager


# Global command_router_instance, initialized in main()
command_router_instance: CommandRouter = None

def process_command(command_text: str, context_mgr: ContextManager) -> str:
    """
    Processes the command using the CommandRouter.
    Updates context and returns assistant's response.
    """
    global command_router_instance
    if not command_router_instance:
        error_msg = "CommandRouter not initialized!"
        print(f"CRITICAL ERROR: {error_msg}")
        if app_config.ENABLE_VISUAL_CANVAS:
            canvas_utils.update_canvas(ai_response=error_msg, thought_process="Critical error in processing.")
        return error_msg

    print(f"Processing command via Router: '{command_text}'")
    if app_config.ENABLE_VISUAL_CANVAS:
        # Clear previous response/thoughts for a new cycle, update current command
        canvas_utils.update_canvas(
            current_command=command_text,
            clear_ai_response=True,
            clear_thought_process=True,
            # web_actions and system_events might persist or be cleared depending on desired UX
            # For now, let's clear web_actions for a new command, system_events can accumulate or be managed
            clear_web_actions=True,
            thought_process="Processing new command..."
        )

    context_mgr.add_message("user", command_text)
    history_for_llm = context_mgr.get_history()

    assistant_response = command_router_instance.route(command_text, history=history_for_llm)

    context_mgr.add_message("assistant", assistant_response)

    if app_config.ENABLE_VISUAL_CANVAS:
        canvas_utils.update_canvas(ai_response=assistant_response, thought_process="Command processed. Displaying response.")
        # Specific thoughts from LLM or system actions would be updated by those modules directly.

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
    declaration_message = "🚫 William AI is a private desktop assistant. Not for public distribution." # Updated message
    print(declaration_message)
    # tts_engine.speak(declaration_message) # Decided to make this print-only to avoid long startup speech

    # Initialize and Open Visual Canvas if enabled
    if app_config.ENABLE_VISUAL_CANVAS:
        canvas_utils.initialize_canvas_data_file() # Initialize the data file
        try:
            # Construct path to canvas.html relative to main.py's location
            base_dir = os.path.dirname(os.path.abspath(__file__))
            canvas_path = os.path.join(base_dir, 'canvas', 'canvas.html')
            # Check if file exists before attempting to open
            if os.path.exists(canvas_path):
                # Prepend 'file://' for local files
                canvas_url = f"file://{os.path.abspath(canvas_path)}"
                print(f"Opening Visual Canvas: {canvas_url}")
                webbrowser.open(canvas_url) # Opens in default browser, Chrome preferred by prompt.
                                            # To specifically use Chrome: webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
                                            # then webbrowser.get('chrome').open(canvas_url)
                                            # This path might vary, so default browser is safer for now.
            else:
                print(f"Error: Canvas HTML file not found at {canvas_path}")
        except Exception as e:
            print(f"Could not open visual canvas: {e}")

    tts_engine.speak("William AI Assistant is now active.")

    # Determine initial listening mode based on app_config
    currently_listening_for_command = app_config.ALWAYS_LISTEN
    if not currently_listening_for_command:
        print("William AI Assistant is now active. Listening for wake word...")
    else:
        print("William AI Assistant is now active and in always listen mode.")
        tts_engine.speak("Always listen mode is active.") # Notify user

    try:
        while True:
            command_text = None
            if currently_listening_for_command:
                listening_status_msg = "Listening for next command..."
                print(listening_status_msg)
                if app_config.ENABLE_VISUAL_CANVAS:
                    canvas_utils.update_canvas(current_command="", thought_process=listening_status_msg, clear_ai_response=True) # Clear previous command/response

                command_text = audio_listener.listen_for_command()
                if command_text is None: # Timeout or silence
                    if app_config.ENABLE_VISUAL_CANVAS:
                        canvas_utils.update_canvas(thought_process="No command heard, still listening (if in always listen mode)...")
                    if app_config.ALWAYS_LISTEN:
                        time.sleep(0.1) # Brief pause
                        continue
                    else:
                        # This case implies not in ALWAYS_LISTEN mode and timed out.
                        # This specific 'else' might be redundant if currently_listening_for_command is already false
                        # when not in ALWAYS_LISTEN mode after a timeout.
                        # However, explicit handling is safer.
                        currently_listening_for_command = False # Should already be false if not ALWAYS_LISTEN
                        print("No command heard. Reverting to wake word.")
                        # tts_engine.speak("No command. Waiting for wake word.") # Can be verbose
                        continue
            else: # Not currently_listening_for_command, so wait for wake word
                listening_status_msg = "Listening for wake word..."
                print(listening_status_msg)
                if app_config.ENABLE_VISUAL_CANVAS:
                    canvas_utils.update_canvas(current_command="", thought_process=listening_status_msg, clear_ai_response=True)

                if audio_listener.listen_for_wake_word():
                    currently_listening_for_command = True # Heard wake word, now listen for command
                    wake_word_detected_msg = "Wake word detected. Listening for command..."
                    print(wake_word_detected_msg)
                    if app_config.ENABLE_VISUAL_CANVAS:
                         canvas_utils.update_canvas(thought_process=wake_word_detected_msg)
                    command_text = audio_listener.listen_for_command()
                    if command_text is None and app_config.ENABLE_VISUAL_CANVAS: # No command after wake word
                        canvas_utils.update_canvas(thought_process="No command heard after wake word. Reverting to wake word listening.")
                else:
                    # Error with wake word listener (e.g., speech service error)
                    error_msg = "Error with wake word listener or speech service. Retrying after delay..."
                    print(error_msg)
                    if app_config.ENABLE_VISUAL_CANVAS:
                        canvas_utils.update_canvas(thought_process=error_msg, ai_response="Speech service issue.")
                    tts_engine.speak("There was an issue with the speech service. I will try again.")
                    time.sleep(3)
                    continue # Retry listening for wake word

            if command_text:
                assistant_response = process_command(command_text, context_manager)
                tts_engine.speak(assistant_response)

                # Decide if we should continue listening for a command or go back to wake word
                if app_config.ALWAYS_LISTEN:
                    currently_listening_for_command = True
                    # No need to print "listening for next command" here, it's at the start of the loop
                else:
                    currently_listening_for_command = False
                    print("Command processed. Listening for wake word...")
                    # tts_engine.speak("Waiting for wake word.") # Can be too verbose
            else:
                # No command heard after wake word, or timeout in always_listen mode.
                # If ALWAYS_LISTEN is false, and we were listening for a command (e.g. after wake word),
                # but got no command, we should revert to wake word listening.
                if currently_listening_for_command and not app_config.ALWAYS_LISTEN:
                    # This means wake word was heard (or it was the first command attempt in non-always-listen mode)
                    # but no command followed. Revert to wake word.
                    currently_listening_for_command = False
                    print("No command heard. Listening for wake word again...")
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
