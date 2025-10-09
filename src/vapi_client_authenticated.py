#!/usr/bin/env python3
"""
VAPI Voice Client with Authentication
Uses direct server URLs with customer_id/password in query params
"""

import json
import os
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class AuthenticatedVoiceAssistant:
    """VAPI voice client with authentication via query parameters."""

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client."""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.assistant_id = self.config.get('vapi_assistant_id')
        self.customer_id = self.config.get('customer_id')
        self.password = self.config.get('password')
        self.server_url = self.config.get('server_url', 'https://securevoice-production-eb77.up.railway.app')

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
        """Start authenticated voice session."""
        print("=" * 60)
        print("🎤 VAPI Voice Assistant - Authenticated Mode")
        print("=" * 60)
        print(f"👤 Customer: {self.customer_id}")
        print(f"🔐 Password: {'*' * len(self.password)}")
        print(f"🌐 Server: {self.server_url}")
        print("=" * 60)

        try:
            # Build auth query parameters
            auth_params = urlencode({
                'customer_id': self.customer_id,
                'password': self.password
            })

            # Tools will use these URLs with auth params
            auth_url = f"{self.server_url}/auth?{auth_params}"
            control_url = f"{self.server_url}/control?{auth_params}"

            print(f"\n🔑 Auth URL: {self.server_url}/auth?customer_id=***")
            print(f"🎛️  Control URL: {self.server_url}/control?customer_id=***")

            print("\n📞 Starting VAPI call...")
            print("⚠️  NOTE: Update VAPI tools with these server URLs:")
            print(f"   home_auth: {auth_url}")
            print(f"   control_air_circulator: {control_url}")

            call = self.vapi.start(
                assistant_id=self.assistant_id
                # Tools must have server URLs configured in VAPI dashboard
            )

            print("\n✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print("\n" + "=" * 60)
            print("🎤 Start speaking - Luna will authenticate first")
            print("=" * 60)
            print("\n💡 Say:")
            print("   1. 'Luna' (authentication)")
            print("   2. 'Turn on the fan'")
            print("   3. 'Turn off the fan'")
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
        assistant = AuthenticatedVoiceAssistant()
        assistant.start_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        exit(1)


if __name__ == "__main__":
    main()
