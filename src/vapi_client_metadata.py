#!/usr/bin/env python3
"""
VAPI Voice Client - Session via Metadata
Passes sid through VAPI metadata instead of URL override
"""

import json
import os
import time
import httpx
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class MetadataVoiceAssistant:
    """
    VAPI voice client that passes session ID via call metadata.

    This works when tools have static server URLs configured.
    """

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client."""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.assistant_id = self.config.get('vapi_assistant_id')
        self.customer_id = self.config.get('customer_id')
        self.password = self.config.get('password')
        self.api_base = self.config.get('server_url', 'https://securevoice-production-eb77.up.railway.app')

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
        response = httpx.post(
            f"{self.api_base}/sessions",
            json={
                "customer_id": self.customer_id,
                "password": self.password
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data["sid"]

    def start_session(self):
        """Start authenticated voice session."""
        print("=" * 60)
        print("🎤 VAPI Voice Assistant - Metadata-based Auth")
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

            # Step 2: Start VAPI with metadata containing sid
            print("\n📞 Starting VAPI call...")
            print(f"   NOTE: Tools must have server URL with query parameter support")
            print(f"   OR webhook must extract sid from metadata")

            # Option: Pass via firstMessage with sid embedded
            first_message = f"Session authenticated with ID: {self.sid[:8]}"

            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides={
                    # Pass sid in firstMessage for now
                    # Webhook can extract it or use static URL with sid
                    "firstMessage": first_message,
                    # Override serverUrl to include sid
                    "serverUrl": f"{self.api_base}/webhook?sid={self.sid}"
                }
            )

            print("✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")
            print(f"🔑 Full Session ID: {self.sid}")
            print("\n" + "=" * 60)
            print("⚠️  IMPORTANT: Make sure VAPI tools have NO server URL")
            print("   Or server URL without sid parameter")
            print("=" * 60)
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
        assistant = MetadataVoiceAssistant()
        assistant.start_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
