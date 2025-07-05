from collections import deque

MAX_HISTORY_MESSAGES = 6 # Stores 3 user commands and 3 assistant replies

class ContextManager:
    def __init__(self, max_history_size: int = MAX_HISTORY_MESSAGES):
        """
        Manages a short-term memory of the conversation history.

        Args:
            max_history_size (int): The maximum number of messages (user + assistant) to store.
                                    Should be an even number to keep pairs.
        """
        if max_history_size % 2 != 0:
            # Technically not required, but good for keeping user/assistant pairs balanced
            print(f"Warning: max_history_size ({max_history_size}) is odd. Consider using an even number.")

        self.history = deque(maxlen=max_history_size)

    def add_message(self, role: str, content: str):
        """
        Adds a message to the history.

        Args:
            role (str): Typically "user" or "assistant".
            content (str): The text of the message.
        """
        if role not in ["user", "assistant", "system"]: # System messages could also be part of history
            print(f"Warning: Adding message with unconventional role: {role}")

        self.history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        """
        Retrieves the current conversation history.

        Returns:
            list[dict[str, str]]: A list of message dictionaries,
                                  e.g., [{"role": "user", "content": "Hello"}, ...].
        """
        return list(self.history)

    def clear_history(self):
        """Clears the conversation history."""
        self.history.clear()
        print("Conversation history cleared.")

if __name__ == '__main__':
    # Example Usage
    context = ContextManager(max_history_size=4) # Keep last 2 pairs

    context.add_message("user", "Hello William.")
    context.add_message("assistant", "Hello! How can I help you today?")
    print("History after 1st exchange:", context.get_history())

    context.add_message("user", "What's the weather like?")
    context.add_message("assistant", "I can't check the weather yet, but I hope it's nice!")
    print("History after 2nd exchange (full):", context.get_history())
    # Expected: user:Hello, assistant:Hello, user:Weather, assistant:Can't check

    context.add_message("user", "Play some music.")
    context.add_message("assistant", "Sure, playing some music for you.")
    print("History after 3rd exchange (older messages should be dropped):", context.get_history())
    # Expected: user:Weather, assistant:Can't check, user:Music, assistant:Playing

    assert len(context.get_history()) <= 4

    context.clear_history()
    print("History after clear:", context.get_history())
    assert len(context.get_history()) == 0

    context.add_message("user", "Test with odd size limit (internally handled by deque).")
    context_odd = ContextManager(max_history_size=3)
    context_odd.add_message("user", "u1")
    context_odd.add_message("assistant", "a1")
    context_odd.add_message("user", "u2")
    print("History with odd size (3):", context_odd.get_history()) # a1, u2
    assert len(context_odd.get_history()) == 3 # Deque stores up to maxlen
    context_odd.add_message("assistant", "a2")
    print("History with odd size (3) after one more:", context_odd.get_history()) # u2, a2
    assert len(context_odd.get_history()) == 3 # a1, u2, a2 -> u2, a2 is wrong. deque keeps last N items.
    # Correct history for max_size=3: [a1, u2, a2] if u1,a1,u2,a2 were added.
    # If u1, a1, u2 added -> result is [u1, a1, u2]
    # If then a2 added -> result is [a1, u2, a2]

    # Re-test logic for odd size:
    context_odd_test = ContextManager(max_history_size=3)
    context_odd_test.add_message("user", "Message 1")
    context_odd_test.add_message("assistant", "Message 2")
    context_odd_test.add_message("user", "Message 3")
    # History: [M1, M2, M3]
    print("History (size 3, 3 added):", context_odd_test.get_history())
    assert len(context_odd_test.get_history()) == 3
    context_odd_test.add_message("assistant", "Message 4")
    # History should be [M2, M3, M4]
    print("History (size 3, 4 added):", context_odd_test.get_history())
    assert len(context_odd_test.get_history()) == 3
    assert context_odd_test.get_history()[0]['content'] == "Message 2"
    assert context_odd_test.get_history()[1]['content'] == "Message 3"
    assert context_odd_test.get_history()[2]['content'] == "Message 4"

    print("ContextManager tests passed.")
