# Handles interaction with the LLM (OpenRouter)
import requests
import json
from william_ai_assistant import config as app_config # Specific app config
from william_ai_assistant import tts_engine

# PERSONALITY_PROMPT is now enabled/disabled via app_config.ENABLE_PERSONALITY
PERSONALITY_PROMPT = """You are William, a witty, intelligent assistant. Respond helpfully and in a natural human tone."""

# Import canvas_utils if canvas is enabled
if app_config.ENABLE_VISUAL_CANVAS:
    from . import canvas_utils
else:
    # Create a dummy canvas_utils if not enabled, to avoid NameError
    class DummyCanvasUtils:
        def update_canvas(self, *args, **kwargs): pass # No-op
    canvas_utils = DummyCanvasUtils()


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

    # Add personality prompt (system message) if enabled
    if app_config.ENABLE_PERSONALITY:
        messages.append({
            "role": "system",
            "content": [{"type": "text", "text": PERSONALITY_PROMPT}]
        })

    # Add command history if provided
    if command_history:
        for entry in command_history:
            # Ensure history entries also follow the new content structure
            # Assuming history entries are like {"role": "user/assistant", "content": "text string"}
            messages.append({
                "role": entry["role"],
                "content": [{"type": "text", "text": entry["content"]}]
            })

    # Add current user input
    messages.append({
        "role": "user",
        "content": [{"type": "text", "text": text_input}]
    })

    payload = {
        "model": app_config.OPENROUTER_MODEL,
        "messages": messages
        # Add other parameters like max_tokens, temperature if needed for Gemini
        # "max_tokens": 1024, # Example
        # "temperature": 0.7   # Example
    }

    try:
        thought = f"Sending request to LLM ({app_config.OPENROUTER_MODEL}) for input: '{text_input[:70]}...'"
        print(thought) # Keep console log for dev
        canvas_utils.update_canvas(thought_process=thought) # Update canvas

        response = requests.post(app_config.OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()

        canvas_utils.update_canvas(thought_process="Received response from LLM. Parsing...")
        response_data = response.json()

        if response_data.get("choices") and len(response_data["choices"]) > 0:
            assistant_reply = response_data["choices"][0].get("message", {}).get("content")
            if assistant_reply:
                print(f"LLM Response: {assistant_reply}")
                canvas_utils.update_canvas(thought_process="Successfully extracted LLM reply.")
                return assistant_reply.strip()
            else:
                err_msg = "LLM response format error: 'content' not found."
                print(err_msg)
                canvas_utils.update_canvas(thought_process=err_msg, ai_response="Error: Malformed AI response.")
                return "I received a response, but couldn't understand it."
        else:
            err_msg = f"LLM response format error: 'choices' not found or empty. Response: {response_data}"
            print(err_msg)
            canvas_utils.update_canvas(thought_process=err_msg, ai_response="Error: No choices in AI response.")
            return "Sorry, I couldn't get a proper response from the AI."

    except requests.exceptions.RequestException as e:
        err_msg = f"Error connecting to OpenRouter API: {e}"
        print(err_msg)
        canvas_utils.update_canvas(thought_process=err_msg, ai_response="Error: Could not connect to AI service.")
        # tts_engine.speak("I'm having trouble connecting to my brain. Please check the internet connection and API settings.")
        return "Error: Could not connect to the AI service."
    except json.JSONDecodeError as e_json: # Capture the exception instance
        resp_text = response.text if 'response' in locals() and hasattr(response, 'text') else "Response object or text not available"
        err_msg = f"Error decoding JSON response from OpenRouter API. Error: {e_json}. Response text: {resp_text[:200]}..."
        print(err_msg)
        canvas_utils.update_canvas(thought_process=err_msg, ai_response="Error: Could not understand AI's response (JSON decode).")
        # tts_engine.speak("I received an unreadable response from my brain.")
        return "Error: Could not understand the AI's response."
    except Exception as e:
        err_msg = f"An unexpected error occurred in get_llm_response: {e}"
        print(err_msg)
        canvas_utils.update_canvas(thought_process=err_msg, ai_response="An unexpected error occurred while thinking.")
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
