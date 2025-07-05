# William AI Assistant

William is a voice-controlled personal desktop assistant for Windows (with some cross-platform considerations for macOS and Linux where feasible for system commands). It activates using the wake word “Hey William”, converts spoken commands into text, processes them using the OpenRouter LLM (`deepseek/deepseek-r1-0528:free`), and replies using text-to-speech. It can also execute basic system-level commands.

## Features

1.  **Wake Word Detection**: Listens for "Hey William" to activate.
2.  **Speech-to-Text**: Converts voice commands to text using `speech_recognition`.
3.  **LLM Brain**: Sends transcribed text to OpenRouter for intelligent responses.
4.  **Text-to-Speech**: Uses `pyttsx3` to speak replies aloud.
5.  **System Commands**: Handles commands like:
    *   Opening applications (e.g., "Open Notepad")
    *   Checking time (e.g., "What time is it?")
    *   Searching the web (e.g., "Search Google for AI news")
    *   Playing music (basic placeholder - e.g., "Play music")
    *   Volume control (basic placeholders - e.g., "Increase volume")

## Project Structure

```
william_ai_assistant/
├── main.py                 # Main application script
├── config.py               # Configuration (API keys, wake word, etc.)
├── audio_listener.py       # Wake word detection and speech-to-text
├── william_brain.py        # LLM interaction (OpenRouter)
├── system_commands.py      # Logic for executing system-level commands
├── tts_engine.py           # Text-to-speech functionality
├── utils.py                # Utility functions (currently a placeholder)
├── README.md               # This file
└── requirements.txt        # Python package dependencies
```

## Setup

1.  **Clone the repository (or create files as per the structure).**

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note on `PyAudio`*: If you encounter issues installing `PyAudio` on Windows, you might need to install it using a pre-compiled wheel (`.whl`) file from a source like Christoph Gohlke's Unofficial Windows Binaries for Python Extension Packages, or install Microsoft Visual C++ Build Tools. On Linux, you might need `portaudio19-dev` (`sudo apt-get install portaudio19-dev python3-pyaudio`). On macOS, `brew install portaudio` followed by `pip install pyaudio` usually works.

4.  **Configure API Key:**
    Open `william_ai_assistant/config.py` and replace `"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"` with your actual OpenRouter API key in the `OPENROUTER_API_KEY` variable.
    ```python
    OPENROUTER_API_KEY = "YOUR_ACTUAL_OPENROUTER_API_KEY"
    ```

5.  **Microphone Access:** Ensure the application has permission to access your microphone. You might also need to specify a `MICROPHONE_INDEX` in `config.py` if you have multiple microphones and the default is not the one you want to use. You can list microphones using `speech_recognition.Microphone.list_microphone_names()`.

## Usage

Run the main application script:
```bash
python main.py
```
Or, if you are in the `william_ai_assistant` directory:
```bash
python main.py
```

The assistant will start by adjusting for ambient noise and then listen for the wake word "Hey William". Once detected, it will prompt you for a command.

**Example Commands:**
*   "Hey William" ... "What time is it?"
*   "Hey William" ... "Open Notepad"
*   "Hey William" ... "Search Google for the latest AI news"
*   "Hey William" ... "Tell me a joke"
*   "Hey William" ... "Play music"

## Dependencies
Key dependencies are listed in `requirements.txt` and include:
*   `SpeechRecognition`: For speech-to-text.
*   `PyAudio`: Microphone access for SpeechRecognition (platform-dependent installation).
*   `pyttsx3`: For text-to-speech.
*   `requests`: For making API calls to OpenRouter.
*   *(Potentially `pycaw` for Windows volume control, or other OS-specific libraries if full volume control is implemented beyond placeholders)*

## Future Enhancements (TODO)
*   More robust wake word detection (e.g., using `pvporcupine`).
*   GUI interface.
*   More sophisticated system command parsing and execution.
*   Persistent memory / context for conversations.
*   Customizable commands and skills.
*   Full implementation of volume controls using OS-specific libraries (`pycaw` for Windows, `osascript` for macOS, `amixer` for Linux).
*   Option for VOSK for offline speech recognition.
*   Better error handling and user feedback.
```
