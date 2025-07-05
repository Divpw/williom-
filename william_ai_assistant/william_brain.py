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
        "Content-Type": "application/json",
    }
    # Add optional headers if they are set in config
    if app_config.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = app_config.OPENROUTER_SITE_URL
    if app_config.OPENROUTER_SITE_NAME:
        headers["X-Title"] = app_config.OPENROUTER_SITE_NAME

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

    models_to_try = [app_config.OPENROUTER_MODEL]
    if app_config.OPENROUTER_FALLBACK_MODEL:
        models_to_try.append(app_config.OPENROUTER_FALLBACK_MODEL)

    last_error = None

    for model_name in models_to_try:
        payload["model"] = model_name
        try:
            thought = f"Sending request to LLM ({model_name}) for input: '{text_input[:70]}...'"
            print(thought) # Keep console log for dev
            canvas_utils.update_canvas(thought_process=thought)

            response = requests.post(app_config.OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=30)
            response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

            canvas_utils.update_canvas(thought_process=f"Received response from {model_name}. Parsing...")
            response_data = response.json()

            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message_content = response_data["choices"][0].get("message", {}).get("content")
                # The content might be a list of parts or a direct string depending on the model/API version.
                # Handle if content is a list (e.g., with Gemini 2.0 Flash)
                if isinstance(message_content, list):
                    assistant_reply = ""
                    for part in message_content:
                        if part.get("type") == "text":
                            assistant_reply += part.get("text", "")
                elif isinstance(message_content, str): # Direct string content
                    assistant_reply = message_content
                else: # Unexpected format
                    assistant_reply = None

                if assistant_reply is not None: # Check for None explicitly
                    print(f"LLM ({model_name}) Response: {assistant_reply}")
                    canvas_utils.update_canvas(thought_process=f"Successfully extracted LLM reply from {model_name}.")
                    return assistant_reply.strip()
                else:
                    err_msg = f"LLM response format error: 'content' not found or in unexpected format from {model_name}."
                    print(err_msg)
                    canvas_utils.update_canvas(thought_process=err_msg, ai_response="Error: Malformed AI response.")
                    last_error = "I received a response, but couldn't understand it." # Keep this generic for user
            else:
                err_msg = f"LLM response format error: 'choices' not found or empty from {model_name}. Response: {response_data}"
                print(err_msg)
                canvas_utils.update_canvas(thought_process=err_msg, ai_response="Error: No choices in AI response.")
                last_error = "Sorry, I couldn't get a proper response from the AI." # Keep this generic

            if last_error and model_name == models_to_try[-1]: # If it's the last model and there was a parsing error
                return last_error
            elif last_error: # If there was a parsing error but more models to try
                continue # Try next model


        except requests.exceptions.HTTPError as e_http:
            err_msg = f"HTTP error with {model_name}: {e_http}"
            print(err_msg)
            last_error = f"Error: Could not connect to the AI service ({e_http.response.status_code})."
            # If it's a rate limit error (429) or server error (5XX) on the primary, try fallback.
            # For other client errors (4XX) with primary, maybe don't try fallback unless it's auth.
            # For now, let's try fallback for any HTTP error with the primary model.
            if model_name == models_to_try[0] and len(models_to_try) > 1:
                canvas_utils.update_canvas(thought_process=f"{err_msg}. Trying fallback model...")
                continue # Try next model
            else: # Error on fallback or no fallback
                canvas_utils.update_canvas(thought_process=err_msg, ai_response=last_error)
                return last_error # Return the error from the last attempted model

        except requests.exceptions.RequestException as e_req:
            err_msg = f"Request error with {model_name}: {e_req}"
            print(err_msg)
            last_error = "Error: Could not connect to the AI service (network issue)."
            if model_name == models_to_try[0] and len(models_to_try) > 1:
                canvas_utils.update_canvas(thought_process=f"{err_msg}. Trying fallback model...")
                continue # Try next model
            else:
                canvas_utils.update_canvas(thought_process=err_msg, ai_response=last_error)
                return last_error

        except json.JSONDecodeError as e_json:
            resp_text = response.text if 'response' in locals() and hasattr(response, 'text') else "Response object or text not available"
            err_msg = f"Error decoding JSON response from {model_name}. Error: {e_json}. Response text: {resp_text[:200]}..."
            print(err_msg)
            last_error = "Error: Could not understand the AI's response (JSON decode)."
            if model_name == models_to_try[0] and len(models_to_try) > 1:
                canvas_utils.update_canvas(thought_process=f"{err_msg}. Trying fallback model...")
                continue # Try next model
            else:
                canvas_utils.update_canvas(thought_process=err_msg, ai_response=last_error)
                return last_error

        except Exception as e: # Catch-all for unexpected errors
            err_msg = f"An unexpected error occurred with {model_name}: {e}"
            print(err_msg)
            last_error = "An unexpected error occurred while thinking."
            if model_name == models_to_try[0] and len(models_to_try) > 1:
                canvas_utils.update_canvas(thought_process=f"{err_msg}. Trying fallback model...")
                continue
            else:
                canvas_utils.update_canvas(thought_process=err_msg, ai_response=last_error)
                return last_error

    # If loop finishes without returning (e.g., models_to_try was empty or all failed silently before error assignment)
    if last_error:
        return last_error
    return "Error: AI service could not be reached or process the request after multiple attempts."


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
