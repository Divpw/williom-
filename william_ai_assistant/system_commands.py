# Handles system-level commands
import os
import datetime
import webbrowser
import subprocess
import platform
import random
import playsound
from typing import Optional
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

def play_random_music_from_library(music_query: Optional[str] = None) -> str:
    """
    Plays a random .mp3 or .wav file from the user's Music folder.
    If a query is provided, it will try to find a matching song. (Basic implementation)
    """
    try:
        music_dir = os.path.expanduser("~/Music")
        if not os.path.isdir(music_dir):
            return "I couldn't find your Music folder."

        music_files = []
        for root, _, files in os.walk(music_dir):
            for file in files:
                if file.lower().endswith((".mp3", ".wav")):
                    music_files.append(os.path.join(root, file))

        if not music_files:
            return "I didn't find any .mp3 or .wav files in your Music folder."

        selected_file = None
        if music_query:
            # Basic search: check if query is in filename (case-insensitive)
            # More advanced search would involve metadata or fuzzy matching
            matching_files = [f for f in music_files if music_query.lower() in os.path.basename(f).lower()]
            if matching_files:
                selected_file = random.choice(matching_files)
                song_name = os.path.basename(selected_file)
                # playsound is blocking, so we might want to run it in a thread if the assistant needs to be responsive
                # For now, let's keep it simple.
                playsound.playsound(selected_file)
                return f"Playing '{song_name}'."
            else:
                return f"Sorry, I couldn't find a song matching '{music_query}'. Playing a random song instead."
                # Fall through to play random if specific query not found, or handle differently

        if not selected_file: # Play random if no query or query not found (and decided to play random)
            selected_file = random.choice(music_files)
            song_name = os.path.basename(selected_file)
            playsound.playsound(selected_file) # This is blocking
            return f"Playing a random song: '{song_name}'."

    except ImportError:
        return "The 'playsound' library is not installed. Please install it to play music."
    except Exception as e:
        # Catch specific playsound errors if known, e.g., PlaysoundException
        print(f"Error playing music: {e}")
        return f"Sorry, I encountered an error trying to play music: {e}"

# --- Volume Control Functions (Windows specific with pycaw) ---
_volume_interface = None

def _get_windows_volume_interface():
    """Initializes and returns the pycaw volume interface."""
    global _volume_interface
    if _volume_interface:
        return _volume_interface
    try:
        from comtypes import CLSCTX_ALL, cast, POINTER
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        _volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        return _volume_interface
    except ImportError:
        print("pycaw library not found. Please install it for volume control on Windows.")
        return None
    except Exception as e:
        print(f"Failed to initialize pycaw: {e}")
        return None

def set_volume_percentage_windows(level_percent: int) -> str:
    """Sets the system master volume to a specified percentage (0-100) on Windows."""
    if platform.system() != "Windows":
        return "Volume control via pycaw is only for Windows."

    volume_control = _get_windows_volume_interface()
    if not volume_control:
        return "Volume control interface not available."

    try:
        level = max(0, min(100, level_percent)) # Clamp between 0 and 100
        volume_control.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except Exception as e:
        print(f"Error setting volume: {e}")
        return f"Sorry, I couldn't set the volume: {e}"

def increase_volume_windows(step_percent: int = 10) -> str:
    """Increases the system master volume by a step percentage on Windows."""
    if platform.system() != "Windows":
        return "Volume control via pycaw is only for Windows."

    volume_control = _get_windows_volume_interface()
    if not volume_control:
        return "Volume control interface not available."

    try:
        current_volume_scalar = volume_control.GetMasterVolumeLevelScalar()
        current_volume_percent = int(current_volume_scalar * 100)
        new_volume_percent = min(100, current_volume_percent + step_percent)
        volume_control.SetMasterVolumeLevelScalar(new_volume_percent / 100.0, None)
        return f"Volume increased to {new_volume_percent}%."
    except Exception as e:
        print(f"Error increasing volume: {e}")
        return f"Sorry, I couldn't increase the volume: {e}"

def decrease_volume_windows(step_percent: int = 10) -> str:
    """Decreases the system master volume by a step percentage on Windows."""
    if platform.system() != "Windows":
        return "Volume control via pycaw is only for Windows."

    volume_control = _get_windows_volume_interface()
    if not volume_control:
        return "Volume control interface not available."

    try:
        current_volume_scalar = volume_control.GetMasterVolumeLevelScalar()
        current_volume_percent = int(current_volume_scalar * 100)
        new_volume_percent = max(0, current_volume_percent - step_percent)
        volume_control.SetMasterVolumeLevelScalar(new_volume_percent / 100.0, None)
        return f"Volume decreased to {new_volume_percent}%."
    except Exception as e:
        print(f"Error decreasing volume: {e}")
        return f"Sorry, I couldn't decrease the volume: {e}"

def toggle_mute_windows() -> str:
    """Toggles the system master volume mute state on Windows."""
    if platform.system() != "Windows":
        return "Volume control via pycaw is only for Windows."

    volume_control = _get_windows_volume_interface()
    if not volume_control:
        return "Volume control interface not available."

    try:
        is_muted = volume_control.GetMute()
        volume_control.SetMute(not is_muted, None)
        return "System muted." if not is_muted else "System unmuted."
    except Exception as e:
        print(f"Error toggling mute: {e}")
        return f"Sorry, I couldn't toggle mute: {e}"

# --- Fallback/Cross-platform Stubs for non-Windows or if pycaw fails ---
# These replace the old set_volume, increase_volume, decrease_volume placeholders

def set_volume(level_percent: int) -> str:
    """Sets the system volume (0-100%). Uses Windows specific if available."""
    if platform.system() == "Windows":
        # Check if pycaw is available and successfully imported by _get_windows_volume_interface
        if _get_windows_volume_interface():
             return set_volume_percentage_windows(level_percent)
        else: # pycaw not available or failed to init
            return "Windows volume control requires pycaw, which is not available or failed to initialize."
    elif platform.system() == "Darwin": # macOS
        try:
            subprocess.call(["osascript", "-e", f"set volume output volume {level_percent}"])
            return f"Setting volume to {level_percent}% on macOS."
        except FileNotFoundError:
            return "osascript not found. Cannot control volume on macOS."
        except Exception as e:
            return f"Error setting volume on macOS: {e}"
    elif platform.system() == "Linux": # Linux (using amixer, requires ALSA utils)
        try:
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", f"{level_percent}%"])
            return f"Attempting to set master volume to {level_percent}% on Linux."
        except FileNotFoundError:
            return "amixer not found. Cannot control volume on Linux."
        except Exception as e:
            return f"Error setting volume on Linux: {e}"
    else:
        return "Volume control is not supported on this operating system yet."

def increase_volume(step: int = 10) -> str:
    """Increases system volume by a step (default 10%). Uses Windows specific if available."""
    if platform.system() == "Windows":
        if _get_windows_volume_interface():
            return increase_volume_windows(step)
        else:
            return "Windows volume control requires pycaw, which is not available or failed to initialize."
    # Add macOS/Linux specific implementations if desired, similar to set_volume
    # For now, a generic message for non-Windows or if specific implementation is missing
    current_vol_msg = "(Current volume not read for this OS in generic increase)"
    return f"Volume increase by {step}% requested. {current_vol_msg}"


def decrease_volume(step: int = 10) -> str:
    """Decreases system volume by a step (default 10%). Uses Windows specific if available."""
    if platform.system() == "Windows":
        if _get_windows_volume_interface():
            return decrease_volume_windows(step)
        else:
            return "Windows volume control requires pycaw, which is not available or failed to initialize."
    # Add macOS/Linux specific implementations if desired
    current_vol_msg = "(Current volume not read for this OS in generic decrease)"
    return f"Volume decrease by {step}% requested. {current_vol_msg}"

def mute_system() -> str:
    """Mutes the system. Uses Windows specific if available."""
    if platform.system() == "Windows":
        if _get_windows_volume_interface():
            # Ensure it mutes, not toggles, if current state is unmuted
            vc = _get_windows_volume_interface()
            if vc:
                vc.SetMute(1, None)
                return "System muted."
            return "Volume control interface not available for mute."
        else:
            return "Windows volume control requires pycaw for mute."
    # Add macOS/Linux specific implementations
    return "Mute function not fully implemented for this OS."

def unmute_system() -> str:
    """Unmutes the system. Uses Windows specific if available."""
    if platform.system() == "Windows":
        if _get_windows_volume_interface():
            vc = _get_windows_volume_interface()
            if vc:
                vc.SetMute(0, None)
                return "System unmuted."
            return "Volume control interface not available for unmute."
        else:
            return "Windows volume control requires pycaw for unmute."
    # Add macOS/Linux specific implementations
    return "Unmute function not fully implemented for this OS."


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
