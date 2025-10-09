#!/usr/bin/env python3
"""
Simple VAPI Voice Client - No Authentication
Just tests fan control directly
"""

import json
import os
import time
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class SimpleVoiceAssistant:
    """Simple VAPI voice client without authentication."""

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client."""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.assistant_id = self.config.get('vapi_assistant_id')

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found")

        if not self.assistant_id:
            raise ValueError("vapi_assistant_id not found")

        self.vapi = Vapi(api_key=self.api_key)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def start_session(self):
        """Start simple voice session - no authentication."""
        print("=" * 60)
        print("🎤 VAPI Voice Assistant - Simple Test Mode")
        print("=" * 60)
        print("⚠️  NO AUTHENTICATION - Direct to Home Assistant")
        print("=" * 60)

        try:
            print("\n📞 Starting VAPI call...")
            call = self.vapi.start(
                assistant_id=self.assistant_id
                # No overrides - uses tool's server.url directly
            )

            print("✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print("\n" + "=" * 60)
            print("🎤 Start speaking to test fan control")
            print("=" * 60)
            print("\n💡 Try saying:")
            print("   - 'Turn on the fan'")
            print("   - 'Turn off the fan'")
            print("   - 'Set to medium'")
            print("\n🔴 Session is LIVE. Press Ctrl+C to stop.\n")

            # Keep session alive
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping session...")
            self.vapi.stop()
            print("✅ Session ended")
        except Exception as e:
            print(f"❌ Error: {e}")
            try:
                self.vapi.stop()
            except:
                pass


def main():
    """Main entry point."""
    try:
        assistant = SimpleVoiceAssistant()
        assistant.start_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        exit(1)


if __name__ == "__main__":
    main()
