# William AI Assistant

William AI is a voice-activated personal desktop assistant.

## Features (v2.1)

*   Voice-activated commands.
*   Wake word detection ("Hey William").
*   Integration with OpenRouter for LLM capabilities.
*   Text-to-speech responses.
*   Basic system commands (extensible via `router.py` and `system_commands.py`).
*   Context management for conversation history.

## Setup and Configuration

### Prerequisites

*   Python 3.8+
*   Pip (Python package installer)
*   PortAudio (for PyAudio, required by SpeechRecognition). Installation varies by OS:
    *   **Windows**: PyAudio usually bundles this. If not, you might need to install it separately or use a pre-compiled wheel.
    *   **macOS**: `brew install portaudio`
    *   **Linux (Debian/Ubuntu)**: `sudo apt-get install portaudio19-dev`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd william-ai-assistant
    ```
    (Replace `<repository-url>` with the actual URL of your Git repository)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate it:
    *   Windows: `.\venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    Navigate to the `william_ai_assistant` sub-directory where `requirements.txt` is located:
    ```bash
    cd william_ai_assistant
    pip install -r requirements.txt
    ```
    If you are in the project root, you can also run:
    ```bash
    pip install -r william_ai_assistant/requirements.txt
    ```


### API Key Configuration

William AI Assistant uses the OpenRouter API for its advanced language model capabilities. You need to provide your own OpenRouter API key.

1.  **Create a `.env` file:**
    In the **project root directory** (alongside this `README.md` and the `william_ai_assistant` folder), create a file named `.env`.

2.  **Add your API key to the `.env` file:**
    Open the `.env` file and add the following line, replacing `YOUR_OPENROUTER_API_KEY_HERE` with your actual key:
    ```
    OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY_HERE
    ```
    For example:
    ```
    OPENROUTER_API_KEY=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
    ```

    **Important:** Keep your API key secret. Do not commit the `.env` file to public repositories if it contains your actual key. The `.gitignore` file should ideally include `.env`.

### Microphone Configuration (Optional)

By default, the assistant tries to use the default system microphone. If you need to use a specific microphone, you can set the `MICROPHONE_INDEX` in `william_ai_assistant/config.py`.

To find the correct index:
1. Run the following Python script:
   ```python
   import speech_recognition as sr
   print(sr.Microphone.list_microphone_names())
   ```
2. This will print a list of microphone names with their indices.
3. Update `MICROPHONE_INDEX = None` to `MICROPHONE_INDEX = X` in `config.py`, where `X` is the desired index.

## Running the Assistant

1.  Ensure your virtual environment is activated and you are in the project root directory.
2.  Run the main script:
    ```bash
    python -m william_ai_assistant.main
    ```
    (Note: Running as a module `python -m ...` from the project root helps ensure Python can find all packages correctly, especially `config.py` at the root level if it's imported by sub-modules directly, though current setup tries to handle this).
    Alternatively, if your Python path is set up or you are in the `william_ai_assistant` directory:
    ```bash
    python william_ai_assistant/main.py
    ```

Upon startup, you should see:
"🚫 William AI is a private desktop assistant. Not intended for distribution."
"William AI Assistant is now active. Listening for wake word..." (or "Always listen mode is active.")

Say "Hey William" to activate the assistant, followed by your command.

## Development Notes

*   **Configuration:** Most settings are in `william_ai_assistant/config.py`. Root-level configurations (like `always_listen`) can be placed in a `config.py` in the project root, which `main.py` attempts to load.
*   **Commands:** New voice commands and their actions can be added by modifying `router.py` and potentially adding new functions to `system_commands.py` or other specialized modules.
*   **TTS Engine:** Uses `pyttsx3` for text-to-speech.
*   **Speech Recognition:** Uses `SpeechRecognition` library with Google Web Speech API by default.

## Troubleshooting

*   **Microphone Issues:**
    *   Ensure your microphone is connected and working.
    *   Check if `PyAudio` is installed correctly.
    *   Try specifying `MICROPHONE_INDEX` in `config.py`.
    *   "Could not adjust for ambient noise": Ensure the microphone is picking up sound.
*   **API Key Errors:**
    *   "OpenRouter API key is not found": Make sure your `.env` file is in the project root and correctly formatted.
*   **Speech Service Errors:**
    *   "Could not request results from Google Speech Recognition service": Check your internet connection.

## Disclaimer
"🚫 William AI is a private desktop assistant. Not intended for distribution." This project is for personal and educational purposes.