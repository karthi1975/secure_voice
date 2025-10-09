#!/usr/bin/env python3
"""
VAPI Voice Client with Authentication
Tests session-based authentication before device control
"""

import json
import os
import time
import httpx
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class AuthenticatedVoiceAssistant:
    """VAPI voice client with session-based authentication."""

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client."""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.assistant_id = self.config.get('vapi_assistant_id')
        self.server_url = self.config.get('server_url')
        self.customer_id = self.config.get('customer_id')
        self.password = self.config.get('password')

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found")

        if not self.assistant_id:
            raise ValueError("vapi_assistant_id not found")

        if not self.server_url:
            raise ValueError("server_url not found in config")

        self.vapi = Vapi(api_key=self.api_key)
        self.session_id = None

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def create_session(self) -> str:
        """
        Create a new session with the server.

        Returns:
            Session ID (sid) for authenticated requests
        """
        session_url = f"{self.server_url}/sessions"

        payload = {
            "customer_id": self.customer_id,
            "password": self.password
        }

        print(f"📝 Creating session with credentials...")
        print(f"   Customer ID: {self.customer_id}")

        response = httpx.post(session_url, json=payload, timeout=10.0)

        if response.status_code == 200:
            data = response.json()
            sid = data.get("sid")
            print(f"✅ Session created: {sid}")
            return sid
        else:
            raise Exception(f"Failed to create session: {response.status_code}")

    def start_session(self):
        """Start authenticated voice session."""
        print("=" * 60)
        print("🎤 VAPI Voice Assistant - Authenticated Mode")
        print("=" * 60)
        print("🔐 AUTHENTICATION REQUIRED")
        print("=" * 60)

        try:
            # Create session first
            self.session_id = self.create_session()

            # Build webhook URL with session ID
            webhook_url = f"{self.server_url}/webhook?sid={self.session_id}"

            print(f"\n🔗 Webhook URL: {webhook_url}")
            print("\n📞 Starting VAPI call with authentication...")

            # Override assistant with server URL including session ID
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides={
                    "serverUrl": webhook_url
                }
            )

            print("✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print("\n" + "=" * 60)
            print("🎤 SESSION ACTIVE - Authentication required first")
            print("=" * 60)
            print("\n💡 The assistant will:")
            print("   1. Ask you to authenticate")
            print("   2. Verify your credentials automatically")
            print("   3. Allow fan control after successful auth")
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
            import traceback
            traceback.print_exc()
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
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
