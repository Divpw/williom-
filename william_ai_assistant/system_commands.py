# Handles system-level commands
import os
import datetime
import webbrowser
import subprocess
import platform
from william_ai_assistant import tts_engine # Assuming tts_engine.py will have a speak function

# --- Command Implementations ---

def open_notepad():
    """Opens Notepad."""
    try:
        if platform.system() == "Windows":
            os.startfile("notepad.exe")
            return "Opening Notepad."
        elif platform.system() == "Darwin": # macOS
            subprocess.call(["open", "-a", "TextEdit"]) # TextEdit is the macOS equivalent
            return "Opening TextEdit."
        else: # Linux
            try:
                subprocess.call(["gedit"]) # Try Gedit first
                return "Opening Gedit."
            except FileNotFoundError:
                try:
                    subprocess.call(["kate"]) # Try Kate if Gedit not found
                    return "Opening Kate."
                except FileNotFoundError:
                    return "Could not find a default text editor to open."
    except Exception as e:
        print(f"Error opening text editor: {e}")
        return "Sorry, I couldn't open the text editor."

def get_time():
    """Gets the current time."""
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p") # e.g., 03:30 PM
    return f"The current time is {current_time}."

def search_google(query):
    """Searches Google for the given query."""
    if not query:
        return "What would you like me to search for on Google?"
    try:
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for {query}."
    except Exception as e:
        print(f"Error searching Google: {e}")
        return "Sorry, I couldn't perform the Google search."

def play_music():
    """
    Placeholder for playing music.
    On Windows, tries to open the default media player.
    On macOS, tries to open Apple Music.
    On Linux, this is highly dependent on setup; provides a message.
    """
    try:
        if platform.system() == "Windows":
            # This command tries to launch the default application for music files.
            # It might open Groove Music, Windows Media Player, or another associated app.
            # A more robust solution might involve specific app commands if known.
            os.startfile("explorer.exe shell:MyMusic") # Opens the Music folder, user can pick
            return "Opening your music library. You can choose what to play."
        elif platform.system() == "Darwin": # macOS
            subprocess.call(["open", "-a", "Music"])
            return "Opening Apple Music."
        else: # Linux - very DE dependent
            # Could try common players, but it's better to let user configure this.
            # Example: subprocess.call(["rhythmbox"]) or subprocess.call(["spotify"])
            return "Playing music isn't fully set up for this system. You can open your preferred music player."
    except Exception as e:
        print(f"Error trying to play music: {e}")
        return "Sorry, I had trouble trying to play music."

def set_volume(level_percent):
    """
    Sets the system volume (0-100%).
    This is a placeholder as it's OS-dependent and complex.
    Requires external libraries like pycaw for Windows, or osascript for macOS.
    """
    system = platform.system()
    try:
        if system == "Windows":
            # Using pycaw would be:
            # from comtypes import CLSCTX_ALL
            # from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            # devices = AudioUtilities.GetSpeakers()
            # interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            # volume = cast(interface, POINTER(IAudioEndpointVolume))
            # volume.SetMasterVolumeLevelScalar(level_percent / 100.0, None)
            return f"Volume control for Windows needs the 'pycaw' library. Set volume to {level_percent}% (simulated)."
        elif system == "Darwin": # macOS
            subprocess.call(["osascript", "-e", f"set volume output volume {level_percent}"])
            return f"Setting volume to {level_percent}%."
        elif system == "Linux":
            # For systems using ALSA with amixer:
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", f"{level_percent}%"])
            return f"Setting master volume to {level_percent}%."
        else:
            return "Volume control is not supported on this operating system yet."
    except FileNotFoundError:
        return f"Required command for volume control not found on your {system} system."
    except Exception as e:
        print(f"Error setting volume: {e}")
        return f"Sorry, I couldn't change the volume on {system}."

def increase_volume(step=10):
    """Increases system volume by a step (default 10%). Placeholder."""
    # This would ideally get current volume and add, then call set_volume.
    # For now, it's a direct call to simulate.
    # On macOS and Linux, we can often get current volume.
    # For simplicity, we'll just call set_volume with a target or simulate.
    return f"Volume increase by {step}% requested. (This is a placeholder, full implementation is complex)."
    # Example for macOS:
    # current_volume_str = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"]).strip().decode()
    # current_volume = int(current_volume_str)
    # new_volume = min(100, current_volume + step)
    # return set_volume(new_volume)


def decrease_volume(step=10):
    """Decreases system volume by a step (default 10%). Placeholder."""
    return f"Volume decrease by {step}% requested. (This is a placeholder, full implementation is complex)."
    # Example for macOS:
    # current_volume_str = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"]).strip().decode()
    # current_volume = int(current_volume_str)
    # new_volume = max(0, current_volume - step)
    # return set_volume(new_volume)

# --- Command Mapping and Processing ---

# Maps spoken phrases (keywords) to functions and their arguments
# Keywords should be lowercase
COMMANDS = {
    "open notepad": {"function": open_notepad, "args": []},
    "what time is it": {"function": get_time, "args": []},
    "what's the time": {"function": get_time, "args": []},
    "search google for": {"function": search_google, "args": ["query_placeholder"], "requires_argument": True},
    "google": {"function": search_google, "args": ["query_placeholder"], "requires_argument": True}, # e.g. "google cats"
    "play music": {"function": play_music, "args": []},
    # Volume commands are tricky due to variability in phrasing "increase volume by X" vs "set volume to Y"
    # Simple versions:
    "increase volume": {"function": increase_volume, "args": []}, # Default step
    "decrease volume": {"function": decrease_volume, "args": []}, # Default step
    "turn the volume up": {"function": increase_volume, "args": []},
    "turn the volume down": {"function": decrease_volume, "args": []},
    # More specific volume commands would require parsing numbers from the command string.
    # e.g., "set volume to 50" -> set_volume(50)
}

def process_system_command(command_text):
    """
    Checks if the command_text matches a known system command and executes it.
    Returns the spoken response from the command execution, or None if no command matched.
    """
    command_text = command_text.lower().strip()

    for phrase, details in COMMANDS.items():
        if command_text.startswith(phrase):
            if details.get("requires_argument"):
                # Extract argument after the command phrase
                argument = command_text[len(phrase):].strip()
                if not argument:
                    # tts_engine.speak(f"What would you like me to {phrase}?") # Handled by the function itself
                    # return f"What would you like me to {phrase}?"
                    # Let the function handle missing argument, e.g. search_google will ask.
                    pass # Fall through to call the function, it should handle missing args.

                # Replace placeholder in args with actual argument
                actual_args = [argument if arg == "query_placeholder" else arg for arg in details["args"]]
                response = details["function"](*actual_args)
            else:
                response = details["function"](*details["args"])

            print(f"Executing system command: '{phrase}' with result: {response}")
            return response

    return None # No system command matched

if __name__ == '__main__':
    # This is for testing the system_commands.py module independently
    # Initialize tts_engine for testing feedback
    if not hasattr(tts_engine, 'pyttsx3'):
        import pyttsx3 as tts_engine_pyttsx3 # Alias to avoid conflict
        tts_engine.pyttsx3 = tts_engine_pyttsx3
        tts_engine.engine = tts_engine.pyttsx3.init()
        def speak_test(text):
            print(f"TTS (test): {text}")
            # tts_engine.engine.say(text) # Comment out for faster testing if TTS is not crucial here
            # tts_engine.engine.runAndWait()
        tts_engine.speak = speak_test

    print("Testing system commands...")

    # Test cases
    test_commands = [
        "open notepad",
        "what time is it",
        "search google for cute puppies",
        "google how to learn python",
        "play music",
        "increase volume",
        "decrease volume",
        "search google for", # Test missing argument
        "non existent command"
    ]

    for cmd_text in test_commands:
        print(f"\nInput: '{cmd_text}'")
        response = process_system_command(cmd_text)
        if response:
            print(f"Response: {response}")
            # tts_engine.speak(response) # Optional: speak response during test
        else:
            print("No system command matched or executed.")

    # Test volume with specific values (requires more parsing logic in process_system_command not yet implemented)
    # For now, these would not be directly matched by the simple startswith logic for "set volume to X"
    # print(set_volume(50))
    # print(set_volume(10))
    # print(increase_volume(20))
    # print(decrease_volume(5))
