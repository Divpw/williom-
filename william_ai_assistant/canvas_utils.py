import json
import os
import datetime
from typing import Dict, List, Optional, Any
from . import config as app_config # To get CANVAS_DATA_FILE path

# Ensure the canvas data file path is absolute, typically within the project directory
# If main.py is in william_ai_assistant/, and canvas_data.json should also be there.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory of canvas_utils.py (william_ai_assistant)
CANVAS_DATA_FILE_PATH = os.path.join(_BASE_DIR, app_config.CANVAS_DATA_FILE)

# Initialize a lock if threading becomes an issue, for now, keep it simple
# import threading
# _canvas_lock = threading.Lock()

_current_canvas_data: Dict[str, Any] = {
    "currentCommand": "",
    "thoughtProcess": "Initializing...",
    "webActions": [],
    "aiResponse": "",
    "systemEvents": [],
    "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat()
}

def _write_canvas_data():
    """Internal function to write the current state to the JSON file."""
    global _current_canvas_data
    _current_canvas_data["lastUpdated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        # with _canvas_lock: # If using threading
        with open(CANVAS_DATA_FILE_PATH, 'w') as f:
            json.dump(_current_canvas_data, f, indent=4)
        # print(f"Canvas data updated: {CANVAS_DATA_FILE_PATH}") # For debugging
    except Exception as e:
        print(f"Error writing to canvas data file ({CANVAS_DATA_FILE_PATH}): {e}")

def update_canvas(
    current_command: Optional[str] = None,
    thought_process: Optional[str] = None,
    web_actions: Optional[List[str]] = None, # Use this to append or replace
    append_web_action: Optional[str] = None,
    ai_response: Optional[str] = None,
    system_events: Optional[List[str]] = None, # Use this to append or replace
    append_system_event: Optional[str] = None,
    clear_web_actions: bool = False,
    clear_system_events: bool = False,
    clear_thought_process: bool = False,
    clear_ai_response: bool = False
):
    """
    Updates specified parts of the canvas data and writes to the JSON file.
    None for a field means no change to that field.
    Use append_web_action or append_system_event to add to lists.
    Use clear flags to reset specific fields before update (e.g., for a new command cycle).
    """
    global _current_canvas_data
    # with _canvas_lock: # If using threading
    if current_command is not None:
        _current_canvas_data["currentCommand"] = current_command

    if clear_thought_process:
        _current_canvas_data["thoughtProcess"] = ""
    if thought_process is not None:
        # Option to append to thought process or replace
        if _current_canvas_data["thoughtProcess"] and not clear_thought_process:
            _current_canvas_data["thoughtProcess"] += f"\n{thought_process}"
        else:
            _current_canvas_data["thoughtProcess"] = thought_process

    if clear_web_actions:
        _current_canvas_data["webActions"] = []
    if web_actions is not None: # Overwrites existing web_actions
        _current_canvas_data["webActions"] = web_actions
    if append_web_action:
        _current_canvas_data["webActions"].append(append_web_action)

    if clear_ai_response:
        _current_canvas_data["aiResponse"] = ""
    if ai_response is not None:
        _current_canvas_data["aiResponse"] = ai_response

    if clear_system_events:
        _current_canvas_data["systemEvents"] = []
    if system_events is not None: # Overwrites existing system_events
        _current_canvas_data["systemEvents"] = system_events
    if append_system_event:
        _current_canvas_data["systemEvents"].append(append_system_event)
        # Optional: limit the number of system events shown
        max_events = 10
        if len(_current_canvas_data["systemEvents"]) > max_events:
            _current_canvas_data["systemEvents"] = _current_canvas_data["systemEvents"][-max_events:]

    _write_canvas_data()

def initialize_canvas_data_file():
    """Writes the initial empty state to the canvas data file if it doesn't exist or to clear it."""
    global _current_canvas_data
    _current_canvas_data = {
        "currentCommand": "Waiting for command...",
        "thoughtProcess": "William AI Initialized. System Ready.",
        "webActions": [],
        "aiResponse": "",
        "systemEvents": [f"Canvas Initialized at {datetime.datetime.now(datetime.timezone.utc).isoformat()}"],
        "lastUpdated": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    _write_canvas_data()
    print(f"Canvas data file initialized/cleared: {CANVAS_DATA_FILE_PATH}")

if __name__ == "__main__":
    # Test function
    initialize_canvas_data_file()
    update_canvas(current_command="Test command: Hello William", thought_process="Thinking about how to respond...")
    update_canvas(append_system_event="System check complete.", append_web_action="Visited google.com")
    update_canvas(ai_response="Hello there! This is a test response.", thought_process="Responded to user.")
    update_canvas(append_system_event="Another system event.")

    # Test clearing before new command cycle
    update_canvas(
        current_command="New research task",
        clear_thought_process=True,
        clear_web_actions=True,
        clear_ai_response=True,
        # system_events are often kept or managed with a max length
    )
    update_canvas(thought_process="Starting research...", append_system_event="Research module activated.")

    print(f"Test complete. Check the content of: {CANVAS_DATA_FILE_PATH}")
