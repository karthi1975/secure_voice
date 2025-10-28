#!/usr/bin/env python3
"""
VAPI Client with SDK - Secure Multi-Tenant Version (FIXED)
Fixes Daily Core context cleanup for auto-restart functionality
"""

import json
import os
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

    def _init_vapi_client(self):
        """Initialize or re-initialize VAPI SDK client."""
        if self.vapi is not None:
            # Clean up existing client
            try:
                self.vapi.stop()
            except:
                pass
            try:
                del self.vapi
            except:
                pass

            # Give the Daily Core library time to clean up
            time.sleep(0.5)

        # Create fresh VAPI client
        self.vapi = Vapi(api_key=self.api_key)

    def start_session(self):
        """Start voice session with serverUrl override - runs forever with auto-restart."""
        print("=" * 80)
        print("🔊 VAPI Voice Assistant - Fully Secure Mode (FIXED)")
        print("=" * 80)
        print(f"Device: {self.device_id}")
        print("♾️  Mode: Continuous (auto-restart on call end)")
        print("=" * 80)

        # Fetch VAPI config once at startup
        self._fetch_vapi_config()

        # Build webhook URL
        webhook_url = f"{self.proxy_url}/webhook?device_id={self.device_id}"

        try:
            while True:  # Run forever
                try:
                    # Initialize fresh VAPI client for each call
                    print(f"\n🔧 Initializing VAPI client...")
                    self._init_vapi_client()

                    print(f"📞 Starting VAPI call with webhook routing...")
                    print(f"🔗 Webhook: {webhook_url}")

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
                    print("\n♾️  Continuous mode: Call will auto-restart if ended")
                    print("🔴 Press Ctrl+C to stop the service")
                    print("=" * 80)

                    # Keep session alive
                    while True:
                        time.sleep(1)

                except Exception as e:
                    # Call ended or error - auto restart
                    print(f"\n⚠️  Call ended or error: {e}")
                    print(f"🧹 Cleaning up Daily Core context...")

                    # CRITICAL: Properly clean up Daily Core context
                    try:
                        self.vapi.stop()
                    except:
                        pass

                    # Destroy the instance to release Daily Core context
                    try:
                        del self.vapi
                        self.vapi = None
                    except:
                        pass

                    print(f"🔄 Auto-restarting in 3 seconds...")
                    time.sleep(3)  # Wait before restart
                    continue

        except KeyboardInterrupt:
            print("\n\n⏹️  Service stopped by user")
            try:
                if self.vapi:
                    self.vapi.stop()
                print("✅ Session ended")
            except:
                pass


def main():
    """Main entry point."""
    try:
        client = SecureVapiClient()
        client.start_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        exit(1)


if __name__ == "__main__":
    main()
