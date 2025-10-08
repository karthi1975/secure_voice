#!/usr/bin/env python3
"""
VAPI Voice Client with Webhook Authentication
Uses Railway webhook for server-side credential validation
"""

import json
import os
import time
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class VAPIWebhookVoiceClient:
    """
    VAPI voice client with webhook-based authentication.

    Flow:
    1. Start VAPI call with assistant
    2. Client sends firstMessage with credentials: "customer_id:password Hello..."
    3. VAPI forwards to webhook (https://healthy-alley-production.up.railway.app/auth)
    4. Webhook validates credentials server-side
    5. Webhook returns welcome message or "Authentication failed"
    6. Luna speaks the webhook response
    7. User interacts with voice commands
    """

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client with webhook authentication."""
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

        print(f"✅ Initialized for customer: {self.customer_id}")
        print(f"🔐 Webhook: https://healthy-alley-production.up.railway.app/auth")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def start_voice_session(self, duration: int = 60):
        """
        Start a voice call session with VAPI and webhook authentication.

        Args:
            duration: How long to keep the call active (seconds)

        Flow:
        1. Client prepares firstMessage with credentials
        2. VAPI starts call
        3. VAPI sends firstMessage to webhook
        4. Webhook validates and responds
        5. User can speak voice commands
        """
        print(f"\n🎤 Starting voice session...")
        print(f"👤 Customer ID: {self.customer_id}")
        print(f"🔑 Password: {'*' * len(self.password)}")
        print("=" * 60)

        # Prepare firstMessage with credentials for webhook validation
        first_message = f"{self.customer_id}:{self.password} Hello! I'm ready to help you."

        try:
            # Configure assistant with credentials in firstMessage
            # The webhook will validate these credentials
            assistant_overrides = {
                'firstMessage': first_message
            }

            print("📞 Connecting to VAPI...")

            # Start VAPI call
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides=assistant_overrides
            )

            print(f"✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print(f"⏱️  Session duration: {duration} seconds")
            print("\n" + "=" * 60)
            print("🔊 WEBHOOK AUTHENTICATION IN PROGRESS...")
            print("=" * 60)
            print("\nExpected webhook behavior:")
            print(f"  • If credentials valid ({self.customer_id}:{self.password})")
            print("    → Luna says: 'Welcome! Authentication successful...'")
            print(f"  • If credentials invalid")
            print("    → Luna says: 'Authentication failed'")
            print("\n" + "=" * 60)
            print("🗣️  You can start speaking commands after authentication...")
            print("\n💡 Example commands:")
            print("   - 'Hey Luna, turn on the fan'")
            print("   - 'Luna, set to medium speed'")
            print("   - 'Turn on oscillation'")
            print("=" * 60)

            # Keep session alive
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
        Start a continuous voice session (until Ctrl+C).

        Flow same as start_voice_session but runs indefinitely.
        """
        print(f"\n🎤 Starting continuous voice session...")
        print(f"👤 Customer ID: {self.customer_id}")
        print(f"🔑 Password: {'*' * len(self.password)}")
        print("=" * 60)
        print("Press Ctrl+C to end the session")
        print("=" * 60)

        # Prepare firstMessage with credentials
        first_message = f"{self.customer_id}:{self.password} Hello! I'm ready to help you."

        try:
            # Configure assistant
            assistant_overrides = {
                'firstMessage': first_message
            }

            print("📞 Connecting to VAPI...")

            # Start VAPI call
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides=assistant_overrides
            )

            print(f"✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print("\n" + "=" * 60)
            print("🔊 WEBHOOK AUTHENTICATION IN PROGRESS...")
            print("=" * 60)
            print("\n🗣️  Listening for voice commands...")
            print("💡 Say: 'Hey Luna, turn on the fan'")
            print("\n🔴 Session is LIVE. Press Ctrl+C to stop.\n")

            # Keep session running
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


def main():
    """Main entry point for webhook-authenticated voice client."""
    print("=" * 60)
    print("🎤 VAPI Voice Client with Webhook Authentication")
    print("=" * 60)
    print("\n🔐 Authentication Method: Railway Webhook")
    print("🌐 Webhook URL: https://healthy-alley-production.up.railway.app/auth")
    print("\n📋 Valid Credentials:")
    print("   Customer ID: urbanjungle")
    print("   Password: alpha-bravo-123")
    print("=" * 60)

    try:
        client = VAPIWebhookVoiceClient()

        print("\n📱 Session Options:")
        print("1. Start 60-second voice session")
        print("2. Start continuous session (Ctrl+C to stop)")
        print("3. Exit")

        choice = input("\n👉 Choose option (1-3): ").strip()

        if choice == "1":
            client.start_voice_session(duration=60)
        elif choice == "2":
            client.start_continuous_session()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid option")

    except Exception as e:
        print(f"❌ Failed to start client: {e}")
        exit(1)


if __name__ == "__main__":
    main()
