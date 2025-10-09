#!/usr/bin/env python3
"""
VAPI Voice Client - Session-based Authentication
Uses sid parameter for secure session management
"""

import json
import os
import time
import httpx
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class CleanVoiceAssistant:
    """
    VAPI voice client with session-based authentication.

    Creates a session on the server, gets sid, and passes it to tools.
    """

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client."""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.assistant_id = self.config.get('vapi_assistant_id')
        self.customer_id = self.config.get('customer_id')
        self.password = self.config.get('password')
        self.api_base = self.config.get('server_url', 'https://securevoice-production.up.railway.app')

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found")

        if not self.assistant_id:
            raise ValueError("vapi_assistant_id not found")

        self.vapi = Vapi(api_key=self.api_key)
        self.sid = None

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _create_session(self) -> str:
        """Create a session on the server and get sid."""
        print(f"\n📡 Creating session at: {self.api_base}/sessions")
        response = httpx.post(
            f"{self.api_base}/sessions",
            json={
                "customer_id": self.customer_id,
                "password": self.password
            },
            timeout=30  # Increased timeout for reliability
        )
        response.raise_for_status()
        data = response.json()
        print(f"✅ Session created successfully")
        print(f"   Session ID: {data['sid']}")
        print(f"   Authenticated: {data.get('authenticated', False)}")
        return data["sid"]

    def start_session(self):
        """Start authenticated voice session with session-based auth."""
        print("=" * 60)
        print("🎤 VAPI Voice Assistant - Session Authentication")
        print("=" * 60)
        print(f"👤 Customer: {self.customer_id}")
        print(f"🔐 Password: {'*' * len(self.password)}")
        print(f"🌐 API Base: {self.api_base}")
        print("=" * 60)

        try:
            # Step 1: Create session on server
            print("\n🔑 Creating session...")
            self.sid = self._create_session()
            print(f"✅ Session created: {self.sid[:8]}...")

            # Step 2: Start VAPI with serverUrl override (includes sid in URL)
            # This routes ALL server messages (including tool calls) to /webhook?sid=xxx
            print("\n📞 Starting VAPI call with sid-based serverUrl...")
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides={
                    # Override server URL to include sid parameter
                    # All tool calls will go to this URL
                    "serverUrl": f"{self.api_base}/webhook?sid={self.sid}",
                    # No firstMessage - let Luna call home_auth() first
                }
            )

            print("✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print(f"🔑 Full Session ID: {self.sid}")
            print(f"🔗 Server URL: {self.api_base}/webhook?sid={self.sid}")
            print(f"⏰ Session TTL: 7 days (604800 seconds)")
            print("\n" + "=" * 60)
            print("🔊 Luna MUST call home_auth() FIRST")
            print("=" * 60)
            print("\n⚠️  IMPORTANT:")
            print("   1. Luna should call home_auth() immediately")
            print("   2. You'll hear the authentication success message")
            print("   3. Then you can control the fan")
            print("\n💡 Example commands:")
            print("   - 'Turn on the fan'")
            print("   - 'Set to medium'")
            print("   - 'Turn off the fan'")
            print("\n🔴 Session is LIVE. Press Ctrl+C to stop.")
            print("⏳ Waiting for Luna to call home_auth()...\n")

            # Keep session alive with status updates
            start_time = time.time()
            while True:
                elapsed = int(time.time() - start_time)
                if elapsed > 0 and elapsed % 30 == 0:
                    print(f"⏱️  Session active for {elapsed}s - waiting for authentication...")
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
        assistant = CleanVoiceAssistant()
        assistant.start_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        exit(1)


if __name__ == "__main__":
    main()
