#!/usr/bin/env python3
"""
VAPI Client with SDK - Process Restart Version
Restarts entire Python process between calls to avoid Daily Core context issues
"""

import json
import os
import sys
import time
import httpx
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()


class SecureVapiClient:
    """VAPI client using SDK with multi-tenant webhook routing."""

    def __init__(self, config_path: str = "config/device_config.json"):
        """Initialize VAPI client."""
        self.config = self._load_config(config_path)

        # Device credentials (only thing stored locally)
        self.device_id = os.getenv('DEVICE_ID', self.config.get('device_id'))
        self.device_secret = os.getenv('DEVICE_SECRET', self.config.get('device_secret'))
        self.proxy_url = self.config.get('proxy_url', 'https://securevoice-production-f5c9.up.railway.app')

        if not self.device_id or not self.device_secret:
            raise ValueError("device_id and device_secret required")

        # VAPI config (fetched from server)
        self.api_key = None
        self.assistant_id = None
        self.vapi = None

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _fetch_vapi_config(self):
        """Fetch VAPI API key and assistant ID from Railway server."""
        print(f"🔑 Authenticating with proxy server...")

        # Authenticate and get JWT token
        response = httpx.post(
            f"{self.proxy_url}/device/auth",
            json={
                "device_id": self.device_id,
                "device_secret": self.device_secret
            },
            timeout=30
        )
        response.raise_for_status()
        auth_data = response.json()

        jwt_token = auth_data["access_token"]
        print(f"✅ Authenticated! Customer: {auth_data.get('customer_id')}")

        # Fetch VAPI config from server
        print(f"📡 Fetching VAPI configuration from server...")
        response = httpx.get(
            f"{self.proxy_url}/device/vapi-config",
            headers={"Authorization": f"Bearer {jwt_token}"},
            timeout=30
        )
        response.raise_for_status()
        vapi_config = response.json()

        self.api_key = vapi_config["api_key"]
        self.assistant_id = vapi_config["assistant_id"]

        print(f"✅ VAPI config received!")
        print(f"   Assistant ID: {self.assistant_id}")

        # Initialize VAPI SDK
        self.vapi = Vapi(api_key=self.api_key)

    def start_single_session(self):
        """Start a single voice session (no restart loop - handled by wrapper script)."""
        print("=" * 80)
        print("🔊 VAPI Voice Assistant - Process Restart Mode")
        print("=" * 80)
        print(f"Device: {self.device_id}")
        print("=" * 80)

        # Fetch VAPI config
        self._fetch_vapi_config()

        # Build webhook URL
        webhook_url = f"{self.proxy_url}/webhook?device_id={self.device_id}"

        print(f"\n📞 Starting VAPI call with webhook routing...")
        print(f"🔗 Webhook: {webhook_url}")

        try:
            # Start call with serverUrl override
            call = self.vapi.start(
                assistant_id=self.assistant_id,
                assistant_overrides={
                    "serverUrl": webhook_url
                }
            )

            print("\n✅ Voice session started!")
            print(f"📱 Call ID: {call.id if hasattr(call, 'id') else 'N/A'}")

            print("\n" + "=" * 80)
            print("🎤 VOICE SESSION ACTIVE - Start speaking!")
            print("=" * 80)
            print("\n💡 Try saying:")
            print("   - 'Turn on the fan'")
            print("   - 'Set fan to medium speed'")
            print("   - 'Turn off the fan'")
            print("\n🔗 Function calls will route to:")
            print(f"   {webhook_url}")
            print("\n🔄 Process will restart when call ends")
            print("🔴 Press Ctrl+C to stop the service")
            print("=" * 80)

            # Keep session alive
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Service stopped by user")
            try:
                self.vapi.stop()
                print("✅ Session ended")
            except:
                pass
            sys.exit(0)
        except Exception as e:
            print(f"\n⚠️  Call ended or error: {e}")
            try:
                self.vapi.stop()
            except:
                pass
            # Exit with code 2 to signal restart needed
            sys.exit(2)


def main():
    """Main entry point."""
    try:
        client = SecureVapiClient()
        client.start_single_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
