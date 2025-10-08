#!/usr/bin/env python3
"""
VAPI Voice Client - Real-time voice interaction with smart home control
Uses vapi_python SDK to start voice calls directly from the terminal
"""

import json
import os
import time
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class SecureVoiceAssistant:
    """
    Voice assistant that uses VAPI SDK to enable real-time voice control.

    Flow:
    1. Start VAPI call with configured assistant
    2. VAPI captures microphone audio
    3. VAPI converts speech to text
    4. Assistant processes with password validation
    5. Assistant calls control_device function
    6. VAPI responds with voice
    """

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice assistant with configuration."""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.assistant_id = self.config.get('vapi_assistant_id')
        self.customer_id = self.config.get('customer_id', 'unknown')
        self.password = self.config.get('password')

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found in environment or config")

        if not self.assistant_id:
            raise ValueError("vapi_assistant_id not found in config")

        # Initialize VAPI client
        self.vapi = Vapi(api_key=self.api_key)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def start_voice_session(self, duration: int = 30):
        """
        Start a voice call session with VAPI.

        Args:
            duration: How long to keep the call active (seconds)

        This will:
        1. Start VAPI call (activates microphone in browser/system)
        2. Listen for your voice commands
        3. Process through your assistant
        4. Respond with voice
        """
        print(f"🎤 Starting voice session for {self.customer_id}...")
        print(f"🔐 Using assistant: {self.assistant_id}")
        print("\n" + "="*60)
        print("IMPORTANT: VAPI will use your system microphone")
        print("Speak your commands naturally!")
        print("Example: 'Turn on the fan'")
        print("="*60 + "\n")

        try:
            # Configure assistant with customer_id:password in first message (invisible authentication)
            assistant_overrides = {
                'firstMessage': f"{self.customer_id}:{self.password} Hello! I'm Luna, your smart home assistant. How can I help you?"
            }

            # Start VAPI call with assistant and credentials override
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides=assistant_overrides
            )

            print(f"✅ Voice session started!")
            print(f"📞 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print(f"⏱️  Session will run for {duration} seconds")
            print("\n🗣️  You can start speaking now...")
            print("💡 Say things like:")
            print("   - 'Turn on the fan'")
            print("   - 'Set living room lights to 50%'")
            print("   - 'Lock the front door'\n")

            # Keep session alive for specified duration
            time.sleep(duration)

            # Stop the call
            print("\n⏹️  Stopping voice session...")
            self.vapi.stop()
            print("✅ Session ended")

        except Exception as e:
            print(f"❌ Error during voice session: {e}")
            try:
                self.vapi.stop()
            except:
                pass

    def start_continuous_session(self):
        """
        Start a voice session that runs until manually stopped.
        Press Ctrl+C to end the session.
        """
        print(f"🎤 Starting continuous voice session for {self.customer_id}...")
        print(f"🔐 Using assistant: {self.assistant_id}")
        print("\n" + "="*60)
        print("IMPORTANT: VAPI will use your system microphone")
        print("Press Ctrl+C to end the session")
        print("="*60 + "\n")

        try:
            # Configure assistant with customer_id:password in first message (invisible authentication)
            assistant_overrides = {
                'firstMessage': f"{self.customer_id}:{self.password} Hello! I'm Luna, your smart home assistant. How can I help you?"
            }

            # Start VAPI call with credentials override
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides=assistant_overrides
            )

            print(f"✅ Voice session started!")
            print(f"📞 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print("\n🗣️  You can start speaking now...")
            print("💡 Say things like:")
            print("   - 'Turn on the fan'")
            print("   - 'Set living room lights to 50%'")
            print("   - 'Lock the front door'\n")

            # Keep session running
            print("🔴 Session is LIVE. Press Ctrl+C to stop.\n")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping voice session...")
            self.vapi.stop()
            print("✅ Session ended")
        except Exception as e:
            print(f"❌ Error during voice session: {e}")
            try:
                self.vapi.stop()
            except:
                pass

    def start_custom_assistant(self, first_message: str = None):
        """
        Start a call with custom assistant configuration.

        Args:
            first_message: Custom greeting message
        """
        print(f"🎤 Starting custom voice session...")

        assistant_config = {
            'firstMessage': first_message or f"Hello! I'm Luna, your smart home assistant for {self.customer_id}. How can I help you?",
            'context': f"You are Luna, a smart home voice assistant. The password for authentication is '{self.password}'. Always validate this password before executing commands.",
            'recordingEnabled': True,
            'interruptionsEnabled': True
        }

        try:
            call = self.vapi.start(assistant=assistant_config)

            print(f"✅ Custom voice session started!")
            print(f"📞 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print("\n🗣️  Speaking to start...")

            time.sleep(30)

            self.vapi.stop()
            print("✅ Session ended")

        except Exception as e:
            print(f"❌ Error: {e}")
            try:
                self.vapi.stop()
            except:
                pass


def main():
    """Main entry point for voice assistant."""
    print("🎤 Secure Voice Assistant - VAPI Integration")
    print("=" * 60)

    try:
        assistant = SecureVoiceAssistant()

        print("\nOptions:")
        print("1. Start 30-second voice session")
        print("2. Start continuous session (Ctrl+C to stop)")
        print("3. Start custom session")

        choice = input("\nChoose option (1-3): ").strip()

        if choice == "1":
            assistant.start_voice_session(duration=30)
        elif choice == "2":
            assistant.start_continuous_session()
        elif choice == "3":
            message = input("Enter custom greeting (or press Enter for default): ").strip()
            assistant.start_custom_assistant(first_message=message or None)
        else:
            print("❌ Invalid option")

    except Exception as e:
        print(f"❌ Failed to start assistant: {e}")


if __name__ == "__main__":
    main()
