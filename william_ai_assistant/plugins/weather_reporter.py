# William AI Weather Reporter Plugin
import json
import urllib.request
import urllib.parse

# A simple weather API that doesn't require a key for basic city queries
# Format: curl wttr.in/London?format=j1
WEATHER_API_URL_FORMAT = "https://wttr.in/{location}?format=j1"
# For OpenWeatherMap, you'd need an API key and different URL structure.
# Example: api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}&units=metric

class WeatherReporterPlugin:
    def __init__(self):
        self.keywords = ["weather", "forecast", "temperature"]
        self.location_prepositions = ["in", "for", "at"] # "weather in London", "temperature for Berlin"

    def can_handle_command(self, command_text):
        """
        Checks if the command is related to weather.
        e.g., "What's the weather in London?", "Tell me the temperature in Berlin"
        """
        command_lower = command_text.lower()
        return any(keyword in command_lower for keyword in self.keywords)

    def _extract_location(self, command_text):
        """
        Tries to extract the location from the command text.
        This is a simple implementation and can be improved with NLP.
        """
        command_lower = command_text.lower()
        words = command_lower.split()

        for keyword in self.keywords:
            if keyword in words:
                try:
                    idx = words.index(keyword)
                    # Look for a preposition after the keyword
                    for i in range(idx + 1, len(words)):
                        if words[i] in self.location_prepositions:
                            # Assume location is the rest of the string after preposition
                            location_parts = words[i+1:]
                            if location_parts:
                                return " ".join(location_parts).strip().rstrip('?')
                    # If no preposition, maybe the location is directly after, or before?
                    # This part can get complex. For wttr.in, often just the city name is enough.
                    # A simpler fallback: if "weather in X", X is location.
                    # Or, if "X weather", X might be location.
                    # For now, focus on "weather in/for/at LOCATION"
                except ValueError:
                    continue

        # Fallback: if no preposition found, and command is short, assume last part is location
        # e.g. "weather paris"
        if len(words) > 1 and words[0] in self.keywords:
            return " ".join(words[1:]).strip().rstrip('?')

        return None

    def execute_command(self, command_text, context=None):
        """
        Fetches and returns the weather for the extracted location.
        """
        location = self._extract_location(command_text)
        if not location:
            return "I can fetch the weather, but I need a location. For example, 'What's the weather in London?'"

        try:
            encoded_location = urllib.parse.quote(location)
            url = WEATHER_API_URL_FORMAT.format(location=encoded_location)

            # print(f"Fetching weather from: {url}") # For debugging

            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())

                    # wttr.in j1 format provides a lot of data. Let's extract some.
                    current_condition = data.get("current_condition", [{}])[0]
                    weather_desc = current_condition.get("weatherDesc", [{}])[0].get("value", "N/A")
                    temp_c = current_condition.get("temp_C", "N/A")
                    feels_like_c = current_condition.get("FeelsLikeC", "N/A")
                    humidity = current_condition.get("humidity", "N/A")
                    nearest_area = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", location)

                    # More detailed forecast (e.g., today's summary)
                    today_weather = data.get("weather", [{}])[0]
                    avg_temp_c = today_weather.get("avgtempC", "N/A")
                    max_temp_c = today_weather.get("maxtempC", "N/A")
                    min_temp_c = today_weather.get("mintempC", "N/A")
                    # sun_rise = today_weather.get("astronomy", [{}])[0].get("sunrise", "N/A")
                    # sun_set = today_weather.get("astronomy", [{}])[0].get("sunset", "N/A")

                    report = (
                        f"Weather in {nearest_area.title()}:\n"
                        f"- Currently: {weather_desc}, Temperature: {temp_c}°C (Feels like {feels_like_c}°C)\n"
                        f"- Humidity: {humidity}%\n"
                        f"- Today's forecast: Min {min_temp_c}°C, Avg {avg_temp_c}°C, Max {max_temp_c}°C."
                    )
                    return report
                else:
                    return f"Sorry, I couldn't fetch the weather for {location}. API status: {response.status}"

        except urllib.error.URLError as e:
            # print(f"URL Error fetching weather: {e}") # For debugging
            return f"Sorry, I couldn't connect to the weather service for {location}. Please check your internet connection."
        except json.JSONDecodeError:
            # print(f"JSON Decode Error fetching weather.") # For debugging
            return f"Sorry, I received an unexpected response from the weather service for {location}."
        except Exception as e:
            # print(f"Unexpected error in weather plugin: {e}") # For debugging
            return f"An unexpected error occurred while fetching weather for {location}."

if __name__ == '__main__':
    # Test the plugin directly
    reporter = WeatherReporterPlugin()

    commands_to_test = [
        "what's the weather in London",
        "weather for paris",
        "temperature at new york city",
        "forecast tokyo", # This might not work well with current simple location extraction
        "gibberish command",
        "weather", # Should ask for location
        "what is the current weather in Berlin?"
    ]

    for cmd in commands_to_test:
        print(f"\nTesting command: '{cmd}'")
        if reporter.can_handle_command(cmd):
            print("Plugin can handle this.")
            location = reporter._extract_location(cmd)
            print(f"Extracted location: {location}")
            response = reporter.execute_command(cmd)
            print(f"Response: {response}")
        else:
            print("Plugin cannot handle this.")
