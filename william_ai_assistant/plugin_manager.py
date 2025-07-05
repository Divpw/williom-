# William AI Plugin Manager
import os
import importlib.util
import inspect

# Get the directory containing plugin_manager.py (e.g., william_ai_assistant/)
# This makes the plugin path robust regardless of where the script is called from.
_PLUGIN_MANAGER_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR_PATH = os.path.join(_PLUGIN_MANAGER_DIR, "plugins")


class PluginManager:
    def __init__(self): # base_path argument removed
        self.plugins = {}
        self.plugin_dir = PLUGIN_DIR_PATH # Use the calculated absolute path
        self._discover_plugins()

    def _discover_plugins(self):
        """
        Discovers and loads plugins from the plugin directory.
        A plugin is a Python file containing a class that has a `can_handle_command` method
        and a `execute_command` method.
        """
        if not os.path.isdir(self.plugin_dir):
            print(f"Plugin directory '{self.plugin_dir}' not found. No plugins will be loaded.")
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                filepath = os.path.join(self.plugin_dir, filename)

                try:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, "can_handle_command") and hasattr(obj, "execute_command"):
                            # Instantiate the plugin class
                            plugin_instance = obj()
                            # Store the instance, perhaps keyed by a plugin name or command it handles
                            # For simplicity, let's use module_name, but this could be more sophisticated
                            if module_name not in self.plugins:
                                self.plugins[module_name] = plugin_instance
                                print(f"Loaded plugin: {module_name} from {filename}")
                            else:
                                print(f"Warning: Duplicate plugin name '{module_name}'. Check your plugin files.")
                except Exception as e:
                    print(f"Error loading plugin {module_name} from {filename}: {e}")

    def route_command(self, command_text, context=None):
        """
        Routes a command to the first plugin that can handle it.

        Args:
            command_text (str): The user's command.
            context (dict, optional): Additional context for the command.

        Returns:
            The result from the plugin's execute_command method, or None if no plugin handles it.
        """
        for plugin_name, plugin_instance in self.plugins.items():
            try:
                if plugin_instance.can_handle_command(command_text.lower()): # Pass lowercased command
                    print(f"Routing command to plugin: {plugin_name}")
                    return plugin_instance.execute_command(command_text, context)
            except Exception as e:
                print(f"Error executing plugin {plugin_name}: {e}")
                return "Sorry, there was an error with that plugin."
        return None

if __name__ == '__main__':
    # Example Usage

    print(f"Plugin directory path configured to: {PLUGIN_DIR_PATH}")

    manager = PluginManager() # Constructor no longer takes base_path

    # Create a dummy plugin for testing if weather_reporter.py isn't there yet
    # Ensure paths used for dummy plugin creation are relative to PLUGIN_DIR_PATH
    dummy_plugin_path = os.path.join(PLUGIN_DIR_PATH, "dummy_plugin.py")
    weather_reporter_path = os.path.join(PLUGIN_DIR_PATH, "weather_reporter.py")

    if not os.path.exists(weather_reporter_path):
        if not os.path.isdir(PLUGIN_DIR_PATH): # Ensure plugin directory exists
            os.makedirs(PLUGIN_DIR_PATH)
        with open(dummy_plugin_path, "w") as f:
            f.write("""
class DummyPlugin:
    def can_handle_command(self, command_text):
        return "dummy test" in command_text
    def execute_command(self, command_text, context=None):
        return "Dummy plugin executed successfully for: " + command_text
""")
        print(f"Created dummy plugin for testing at: {dummy_plugin_path}")
        # Need to re-initialize or make _discover_plugins public to re-scan
        # For simplicity in this test block, let's reinstantiate, or add a public rescan
        manager = PluginManager() # Re-instantiate to pick up new dummy plugin

    print("\nTesting plugin routing:")

    response = manager.route_command("What's the weather in Delhi?")
    if response:
        print(f"Response from plugin: {response}")
    else:
        print("No plugin handled 'What's the weather in Delhi?'")

    response = manager.route_command("Run dummy test command")
    if response:
        print(f"Response from plugin: {response}")
    else:
        print("No plugin handled 'Run dummy test command'")

    if os.path.exists(dummy_plugin_path): # Use the defined path
        os.remove(dummy_plugin_path)
        print(f"Removed dummy plugin from: {dummy_plugin_path}")
