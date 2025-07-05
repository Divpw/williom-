# Handles interaction with the LLM (OpenRouter)
import requests
import json
from william_ai_assistant import config as app_config # Specific app config
from william_ai_assistant import tts_engine

# Attempt to import root config for personality settings
try:
    import config as root_config
except ImportError:
    # Fallback if running william_brain.py directly and root is not in path
    class RootConfigMock:
        enable_personality = False # Default to False if root config not found
    root_config = RootConfigMock()
    print("Warning: Root config.py not found, personality disabled by default.")


PERSONALITY_PROMPT = """You are William, a witty, intelligent assistant. Respond helpfully and in a natural human tone."""

def get_llm_response(text_input, command_history: list = None):
    """
    Sends the user's text input to OpenRouter and returns the LLM's response.
    Optionally includes command history.
    """
    headers = {
        "Authorization": f"Bearer {app_config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []

    if hasattr(root_config, 'enable_personality') and root_config.enable_personality:
        messages.append({"role": "system", "content": PERSONALITY_PROMPT})

    # Add command history if provided (to be implemented in context_manager)
    if command_history:
        for entry in command_history: # Assuming history is list of {"role": "user/assistant", "content": "..."}
            messages.append(entry)

    messages.append({"role": "user", "content": text_input})

    payload = {
        "model": app_config.OPENROUTER_MODEL,
        "messages": messages
    }

    try:
        print(f"Sending to LLM ({app_config.OPENROUTER_MODEL}): Input: '{text_input}', Full payload messages: {messages}")
        response = requests.post(app_config.OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        response_data = response.json()

        if response_data.get("choices") and len(response_data["choices"]) > 0:
            assistant_reply = response_data["choices"][0].get("message", {}).get("content")
            if assistant_reply:
                print(f"LLM Response: {assistant_reply}")
                return assistant_reply.strip()
            else:
                print("LLM response format error: 'content' not found.")
                return "I received a response, but couldn't understand it."
        else:
            print(f"LLM response format error: 'choices' not found or empty. Response: {response_data}")
            return "Sorry, I couldn't get a proper response from the AI."

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to OpenRouter API: {e}")
        tts_engine.speak("I'm having trouble connecting to my brain. Please check the internet connection and API settings.")
        return "Error: Could not connect to the AI service."
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from OpenRouter API. Response text: {response.text}")
        tts_engine.speak("I received an unreadable response from my brain.")
        return "Error: Could not understand the AI's response."
    except Exception as e:
        print(f"An unexpected error occurred in get_llm_response: {e}")
        return "An unexpected error occurred while thinking."

if __name__ == '__main__':
    # This is for testing the william_brain.py module independently
    # Ensure tts_engine is minimally available for error speech, if needed.
    if not hasattr(tts_engine, 'pyttsx3'): # Check if tts_engine was already initialized
        import pyttsx3 as tts_engine_pyttsx3
        tts_engine.pyttsx3_module = tts_engine_pyttsx3 # Store module in tts_engine
        tts_engine.engine = tts_engine.pyttsx3_module.init()
        if hasattr(app_config, 'TTS_RATE'):
             tts_engine.engine.setProperty('rate', app_config.TTS_RATE)
        else: # Fallback if TTS_RATE is not in app_config for some reason
            tts_engine.engine.setProperty('rate', 150)

        def speak_test(text):
            print(f"TTS (test): {text}")
            if hasattr(tts_engine, 'engine') and tts_engine.engine:
                tts_engine.engine.say(text)
                tts_engine.engine.runAndWait()
            else:
                print("TTS engine not initialized for testing.")
        tts_engine.speak = speak_test


    if not app_config.OPENROUTER_API_KEY or app_config.OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE":
        print("ERROR: OpenRouter API key is not set in william_ai_assistant/config.py. Please set it to test this module.")
        if hasattr(tts_engine, 'speak'): tts_engine.speak("OpenRouter API key is not configured.")
    else:
        test_prompt = "Hello, who are you?"
        print(f"Testing LLM with prompt: '{test_prompt}'")
        response = get_llm_response(test_prompt)
        print(f"LLM said: {response}")
        if response and not response.startswith("Error:"):
            tts_engine.speak(response)

        test_prompt_2 = "What is the capital of France?"
        print(f"Testing LLM with prompt: '{test_prompt_2}'")
        response_2 = get_llm_response(test_prompt_2)
        print(f"LLM said: {response_2}")
        if response_2 and not response_2.startswith("Error:"):
            tts_engine.speak(response_2)
