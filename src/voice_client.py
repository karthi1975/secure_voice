#!/usr/bin/env python3
"""
Secure Voice Client for Smart Home Control via VAPI
Raspberry Pi compatible voice assistant with password-based authentication
"""

import json
import os
import requests
from typing import Dict, Any, Optional


class SecureVoiceClient:
    """
    Voice client that prepends password to commands before sending to VAPI.

    Flow:
    1. Load config (customer_id, password, vapi_assistant_id)
    2. User speaks command
    3. Prepend password invisibly
    4. Send to VAPI via HTTP POST
    5. VAPI validates password in system prompt
    6. VAPI calls control_device function
    7. Return response to user
    """

    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize client with configuration file.

        Args:
            config_path: Path to JSON config file with credentials
        """
        self.config = self._load_config(config_path)
        self.customer_id = self.config['customer_id']
        self.password = self.config['password']
        self.assistant_id = self.config['vapi_assistant_id']
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found in environment or config")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Config file not found at {config_path}. "
                "Create config.json with customer_id, password, and vapi_assistant_id"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def send_command(self, user_text: str, include_wake_word: bool = False) -> Dict[str, Any]:
        """
        Send command to VAPI with password prepended invisibly.

        Args:
            user_text: User's voice command (e.g., "Turn on the fan" or "Hey Luna, turn on the fan")
            include_wake_word: If True, prepend "Hey Luna" to command for wake word testing

        Returns:
            VAPI response as dictionary

        Example:
            >>> client.send_command("Turn on the fan")
            {"status": "success", "message": "Fan on."}

            >>> client.send_command("Turn on the fan", include_wake_word=True)
            {"status": "success", "message": "Yes? Fan on."}
        """
        # Optionally prepend wake word for testing
        if include_wake_word and not any(wake in user_text.lower() for wake in ['hey luna', 'hello luna', 'luna']):
            user_text = f"Hey Luna, {user_text}"

        # Prepend password invisibly to user command
        authenticated_text = f"{self.password} {user_text}"

        url = "https://api.vapi.ai/v1/conversation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "assistant_id": self.assistant_id,
            "text": authenticated_text
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def run_interactive(self):
        """
        Run interactive command loop for testing.
        Simulates voice input via text.
        """
        print(f"🎤 Luna Voice Assistant - {self.customer_id}")
        print("Commands:")
        print("  - Type commands naturally (e.g., 'turn on the fan')")
        print("  - Add 'wake:' prefix to test wake word (e.g., 'wake: turn on the fan')")
        print("  - Type 'quit' to exit")
        print("-" * 60)
        print("\nExamples:")
        print("  turn on the fan")
        print("  wake: turn on the fan")
        print("  Hey Luna, set to medium")
        print("  Luna, turn on oscillation")
        print("-" * 60)

        while True:
            try:
                command = input("\nYou: ").strip()

                if command.lower() in ['quit', 'exit', 'stop']:
                    print("Goodbye!")
                    break

                if not command:
                    continue

                # Check for wake word prefix
                include_wake = False
                if command.lower().startswith('wake:'):
                    include_wake = True
                    command = command[5:].strip()

                print("⏳ Processing...")
                result = self.send_command(command, include_wake_word=include_wake)

                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    # Try to extract message from response
                    if isinstance(result, dict):
                        message = result.get('message', result.get('text', str(result)))
                        print(f"🔊 Luna: {message}")
                    else:
                        print(f"✅ Response: {result}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


def main():
    """Main entry point for the voice client."""
    try:
        client = SecureVoiceClient()
        client.run_interactive()
    except Exception as e:
        print(f"Failed to start client: {e}")
        exit(1)


if __name__ == "__main__":
    main()
