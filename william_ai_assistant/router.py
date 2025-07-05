import re
import webbrowser
from typing import Callable, Dict, Optional, Tuple, Pattern

# Import actual handlers using relative imports as router.py is inside the package
from .system_commands import (
    play_random_music_from_library,
    set_volume,
    increase_volume,
    decrease_volume,
    mute_system,
    unmute_system
)
from .william_brain import get_llm_response
from .plugin_manager import PluginManager # Import PluginManager


# Placeholder for actual functions - these would be in other modules
# Note: The try-except block for imports with placeholders might be less necessary
# if the package structure is consistently used. For robustness during development,
# or if parts can be run standalone, they can be kept.
# For now, assuming direct imports will work due to correct structure.


# Placeholder for actual functions - these would be in other modules
# For example, system_commands.py, william_brain.py, etc.
# TODO: Review if handle_system_command is still needed or if all system commands will have specific routes.
# For now, it's used by "open" and "close" routes.
def handle_system_command(command: str) -> str:
    """Placeholder for actual system command handler."""
    # This could potentially call a more generic system command processor from system_commands.py
    # if we don't want "open/close" to be directly in the router.
    # For now, direct simulation is fine.
    return f"Executing generic system command: {command}"

def handle_web_search(query: str) -> str:
    """Web search handler, already implemented here."""
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    try:
        webbrowser.open(url)
        return f"Searching for '{query}' on Google."
    except Exception as e:
        return f"Sorry, I couldn't open the browser: {e}"

# Use the imported or placeholder function for music
def handle_play_music(query: Optional[str] = None) -> str:
    return play_random_music_from_library(query)

# Volume control handlers now directly call the imported functions
# The router's job is to parse the intent (e.g. "increase volume", "set volume to 50")
# and call the correct function from system_commands.
# The handle_volume_control function in router.py might not be needed if routes directly call specific functions.
# For simplicity with the current router structure, we can keep it and make it a dispatcher.

def handle_volume_control(action: str, value: Optional[int] = None) -> str:
    """Dispatches to specific volume control functions based on action."""
    if action == "increase":
        return increase_volume() # Assumes default step, or pass step from regex if captured
    elif action == "decrease":
        return decrease_volume() # Assumes default step
    elif action == "mute":
        return mute_system()
    elif action == "unmute":
        return unmute_system()
    elif action == "set" and value is not None:
        return set_volume(value)
    else:
        return "Sorry, I didn't understand that volume command."


# Updated fallback_chat_handler to use the imported get_llm_response and accept history
def fallback_chat_handler(text: str, history: Optional[list] = None) -> str:
    """
    Handles commands that don't match any specific route by sending them to the LLM.
    """
    print(f"Fallback: Sending to LLM: '{text}' with history count: {len(history) if history else 0}")

    # Prevent duplicating the current user message if it's already the last item in history.
    # get_llm_response in william_brain.py will add the `text` as the current user prompt.
    history_to_pass = history
    if history and history[-1].get("role") == "user" and history[-1].get("content") == text:
        history_to_pass = history[:-1]
        print("Adjusted history for LLM call to prevent duplication of current user input.")

    return get_llm_response(text, command_history=history_to_pass)


class CommandRouter:
    def __init__(self):
        self.routes: Dict[Pattern[str], Callable[..., str]] = {}
        self.plugin_manager = PluginManager() # Instantiate PluginManager
        # The fallback handler now needs history, so it cannot be pre-registered
        # in _register_default_routes in the same way if we want 'route' to pass history to it.
        # Instead, fallback_chat_handler will be called explicitly by the route method.
        self._register_default_routes()

    def _register_default_routes(self):
        """
        Registers predefined command patterns and their handlers.
        Note: Fallback is handled directly in the `route` method.
        """
        # Web Search
        self.add_route(r"search for (.+) (on google|on the web|online)", handle_web_search, pass_query_group=1)
        self.add_route(r"google (.+)", handle_web_search, pass_query_group=1)

        # Music
        self.add_route(r"play music", handle_play_music)
        self.add_route(r"play some music", handle_play_music)
        self.add_route(r"play (.+) from my music", handle_play_music, pass_query_group=1) # e.g. play song_name from my music

        # Volume Control (examples, assuming specific keywords)
        self.add_route(r"increase volume", lambda: handle_volume_control("increase"))
        self.add_route(r"decrease volume", lambda: handle_volume_control("decrease"))
        self.add_route(r"lower volume", lambda: handle_volume_control("decrease"))
        self.add_route(r"turn up the volume", lambda: handle_volume_control("increase"))
        self.add_route(r"turn down the volume", lambda: handle_volume_control("decrease"))
        self.add_route(r"mute (?:my )?system", lambda: handle_volume_control("mute"))
        self.add_route(r"unmute (?:my )?system", lambda: handle_volume_control("unmute"))
        self.add_route(r"set volume to (\d+) percent", lambda level: handle_volume_control("set", int(level)), pass_query_group=1)


        # System Commands (generic example, more specific ones would be better)
        # These are very basic, real system commands would need more robust parsing.
        self.add_route(r"open (.+)", lambda app: handle_system_command(f"open {app}"), pass_query_group=1) # e.g. open calculator
        self.add_route(r"close (.+)", lambda app: handle_system_command(f"close {app}"), pass_query_group=1) # e.g. close notepad
        # Add more specific system commands as needed, e.g., shutdown, restart, check disk space

    def add_route(self, pattern: str, handler: Callable[..., str], pass_query_group: Optional[int] = None):
        """
        Adds a new command route.

        Args:
            pattern (str): A regex pattern to match against user input.
            handler (Callable[..., str]): The function to call if the pattern matches.
            pass_query_group (Optional[int]): If set, the content of this regex group
                                               will be passed as an argument to the handler.
                                               If None, the handler is called without arguments.
        """
        compiled_pattern = re.compile(pattern, re.IGNORECASE)

        if pass_query_group is not None:
            # Wrapper to extract group and pass to handler
            # The wrapper now also needs to accept `history` but only passes it to fallback_chat_handler
            def wrapped_handler(text_input: str, history: Optional[list] = None) -> str:
                match = compiled_pattern.search(text_input)
                if match and len(match.groups()) >= pass_query_group:
                    query = match.group(pass_query_group)
                    return handler(query) # Specific handlers currently don't take history

                # This case should ideally not be reached if routing logic is correct
                # If it is, it means a pattern was matched but group extraction failed.
                # Fallback with an error message, passing history.
                error_message = f"Error extracting query for pattern {pattern.pattern} from input: {text_input}"
                print(f"ERROR: {error_message}")
                return fallback_chat_handler(error_message, history=history)
            self.routes[compiled_pattern] = wrapped_handler
        else:
            # Wrapper to ensure consistent signature for handlers that take no query
            # Also needs to accept history for consistency, but doesn't use it for the specific handler
            def no_arg_handler_wrapper(text_input: str, history: Optional[list] = None) -> str:
                return handler() # Specific handlers currently don't take history
            self.routes[compiled_pattern] = no_arg_handler_wrapper


    def route(self, text: str, history: Optional[list] = None) -> str:
        """
        Routes the user's text input to the appropriate handler.

        Args:
            text (str): The user's spoken or typed command.
            history (Optional[list]): The conversation history.

        Returns:
            str: The response from the handler or fallback.
        """
        for pattern, handler_wrapper in self.routes.items():
            match = pattern.search(text)
            if match:
                # The handler_wrapper will correctly call the underlying handler
                # It now also accepts history, mainly for the fallback scenario within wrapped_handler
                return handler_wrapper(text, history=history) # Pass history here

        # If no specific command pattern matched, try the plugin manager
        # PluginManager's route_command expects (command_text, context=None)
        # We can pass 'history' as part of the context if plugins might need it.
        # For now, let's keep it simple and not pass history as context to plugins by default.
        # If a plugin needs history, its 'execute_command' could be designed to accept it.
        plugin_response = self.plugin_manager.route_command(text) # context could be {'history': history}
        if plugin_response is not None:
            print(f"Command handled by plugin: {plugin_response}")
            return plugin_response

        # If no plugin handled it either, use the fallback chat handler
        return fallback_chat_handler(text, history=history)

if __name__ == '__main__':
    # Example Usage:
    # Note: For standalone testing of router.py, william_brain.get_llm_response might be a placeholder.
    # Ensure app_config and root_config are handled if get_llm_response directly uses them.
    # For simplicity, the get_llm_response placeholder defined above is self-contained.

    router = CommandRouter()

    # Mock history for testing fallback
    mock_history = [
        {"role": "user", "content": "What was my last question?"},
        {"role": "assistant", "content": "You asked about the capital of France."}
    ]

    commands_to_test = [
        ("search for cute kittens on google", None),
        ("google how to learn python", None),
        ("play music", None),
        ("play some funky tunes from my music", None), # "funky tunes" would be the query
        ("increase volume", None),
        ("mute my system", None),
        ("set volume to 75 percent", None),
        ("open calculator", None),
        ("tell me a joke", mock_history), # Should go to fallback, pass history
        ("what's the weather like?", mock_history) # Should go to fallback, pass history
    ]

    for cmd, hist in commands_to_test:
        response = router.route(cmd, history=hist)
        print(f"User: '{cmd}' (History: {'Yes' if hist else 'No'})\nWilliam: '{response}'\n")

    # Example of adding a new route dynamically (if needed)
    # The handler for this new route would also need to conform to (text_input, history) if it could fallback
    # or if the wrapper itself calls fallback. Simpler handlers that don't error out don't strictly need history.
    def handle_custom_greeting(name: str) -> str:
        return f"Hello, {name}! Nice to meet you."

    router.add_route(r"my name is (.+)", handle_custom_greeting, pass_query_group=1)

    greet_command = "my name is Alex"
    response = router.route(greet_command)
    print(f"User: '{greet_command}'\nWilliam: '{response}'\n")

    no_match_command = "can you sing a song"
    response = router.route(no_match_command) # Should use fallback
    print(f"User: '{no_match_command}'\nWilliam: '{response}'\n")
