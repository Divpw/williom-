# William AI Assistant v2.0

William is an enhanced voice-controlled personal desktop assistant, primarily for Windows, with considerations for macOS and Linux for some functionalities. It uses a wake word ("Hey William"), converts speech to text, processes commands through a sophisticated routing engine or an LLM (OpenRouter: `deepseek/deepseek-r1-0528:free`), and responds via text-to-speech.

## Key Features (v2.0)

1.  **Wake Word Detection**: Listens for "Hey William" (configurable).
2.  **Speech-to-Text**: Uses `speech_recognition` for converting voice to text.
3.  **Command Routing Engine (`router.py`)**:
    *   Intelligently routes user commands based on intent (regex/keywords).
    *   Directs to specific handlers: system commands, web search, music, volume, or fallback to LLM.
4.  **LLM Brain (`william_brain.py`)**:
    *   Interacts with OpenRouter for complex queries and conversational fallback.
    *   **Personality Mode**: If enabled in `config.py` (root), William responds with a witty, helpful tone.
    *   **Command Memory**: Remembers the last 6 interactions (user input & assistant replies) to provide context to the LLM.
5.  **Text-to-Speech (`tts_engine.py`)**: Uses `pyttsx3` for spoken replies.
6.  **Advanced System Commands (`system_commands.py`)**:
    *   **Web Search**: Opens Google searches (e.g., "Search for AI news on Google").
    *   **Play Music**: Plays random `.mp3` or `.wav` files from the user's `~/Music` folder (uses `playsound`). Can also attempt to play specific queried songs.
    *   **Volume Control (Windows)**: Increase/decrease volume, mute/unmute, and set specific volume levels using `pycaw`. (Other OSes have basic support).
    *   Standard commands like opening apps, getting time.
7.  **Context Management (`context_manager.py`)**:
    *   Maintains a short-term history of commands and responses.
8.  **User Experience Enhancements**:
    *   **Auto Wake Mode**: If enabled in `config.py` (root), William automatically listens for the next command after replying, no need to repeat the wake word.
    *   Improved feedback and error handling (ongoing).

## Project Structure

The project is organized into a main package `william_ai_assistant` and some root-level control/config files:

```
.
├── william_ai_assistant/       # Core assistant package
│   ├── main.py                 # Main application script (integrates components)
│   ├── config.py               # Package-specific config (API keys, wake word, TTS rate, etc.)
│   ├── audio_listener.py       # Wake word detection and speech-to-text
│   ├── william_brain.py        # LLM interaction, personality, context injection
│   ├── system_commands.py      # System command implementations (music, volume, etc.)
│   ├── tts_engine.py           # Text-to-speech engine
│   ├── utils.py                # Utility functions (if any)
│   └── requirements.txt        # Python package dependencies for the assistant
│   └── README.md               # This detailed README
├── router.py                   # 🔹 NEW: Command routing logic
├── context_manager.py          # 🔹 NEW: Memory/history management
├── config.py                   # 🔹 NEW: Root config for global toggles (personality, auto-wake)
└── README.md                   # Root README (brief, points here or project overview)
```

## Setup

1.  **Clone the repository (or create files as per the structure).**

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Navigate to the `william_ai_assistant` sub-directory (if not already there) and install dependencies:
    ```bash
    cd william_ai_assistant
    pip install -r requirements.txt
    cd .. # Go back to the root directory if needed for running main.py
    ```
    *   **`PyAudio` Notes**: Installation can be tricky.
        *   Windows: May require pre-compiled `.whl` from sources like Christoph Gohlke's site, or Microsoft Visual C++ Build Tools.
        *   Linux: `sudo apt-get install portaudio19-dev python3-pyaudio` or similar.
        *   macOS: `brew install portaudio` then `pip install pyaudio`.
    *   **`pycaw` Notes**: This is for Windows volume control. It should install smoothly via pip on Windows.
    *   **`playsound` Notes**: On Linux, you might need to install `python3-gst-1.0` or `gstreamer-1.0` packages (`sudo apt-get install gir1.2-gstreamer-1.0`).

4.  **Configuration:**
    *   **API Key**: Open `william_ai_assistant/config.py`. Set your `OPENROUTER_API_KEY`.
        ```python
        OPENROUTER_API_KEY = "YOUR_ACTUAL_OPENROUTER_API_KEY"
        ```
    *   **Feature Toggles**: Open the root `config.py` file. Here you can enable/disable:
        *   `enable_personality = True`  (Set to `False` for default LLM tone)
        *   `always_listen = True` (Set to `False` to require wake word for every command)
    *   **Microphone**: Ensure microphone access. You might need to set `MICROPHONE_INDEX` in `william_ai_assistant/config.py` if the default mic is not desired. Use `speech_recognition.Microphone.list_microphone_names()` to list available mics.

## Usage

Run the main application script from the **root directory** of the project:
```bash
python william_ai_assistant/main.py
```
The assistant will initialize, adjust for ambient noise, and then either listen for the wake word "Hey William" or directly for a command if `always_listen` is `True`.

**Example Commands (v2.0):**
*   "Hey William" ... "What time is it?"
*   "Hey William" ... "Open Notepad"
*   "Hey William" ... "Search Google for the latest AI news"
*   "Hey William" ... "Google how to make pasta"
*   "Hey William" ... "Tell me a joke" (processed by LLM)
*   "Hey William" ... "Play music" (plays random song from `~/Music`)
*   "Hey William" ... "Play yesterday from my music" (attempts to find and play 'yesterday')
*   "Hey William" ... "Increase volume"
*   "Hey William" ... "Decrease volume by 20" (Note: "by 20" part might need specific regex in router if not default step)
*   "Hey William" ... "Set volume to 65 percent"
*   "Hey William" ... "Mute my system" / "Unmute system"

## Key Dependencies
(Refer to `william_ai_assistant/requirements.txt` for the full list)
*   `SpeechRecognition` & `PyAudio`: For voice input.
*   `pyttsx3`: For text-to-speech output.
*   `requests`: For OpenRouter API calls.
*   `playsound`: For playing music files.
*   `pycaw`: For Windows-specific volume control.

## Future Enhancements / TODO
*   **Full Router Integration**: Ensure `main.py` uses `CommandRouter` for all command processing, passing necessary context.
*   **Plugin System**: Develop a more modular plugin architecture for adding new commands/skills.
*   **GUI**: Optional graphical user interface.
*   **Advanced Wake Word**: Consider `pvporcupine` for more reliable wake word detection.
*   **Offline STT/TTS**: Options for VOSK (STT) or local TTS alternatives.
*   **Refined Error Handling**: More granular error feedback to the user.
*   **Configuration Management**: Consolidate or streamline the dual `config.py` files.
*   **Testing**: Add comprehensive unit and integration tests.
```
