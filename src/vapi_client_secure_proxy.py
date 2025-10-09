#!/usr/bin/env python3
"""
VAPI Secure Proxy Client for Raspberry Pi

Tier 0 Security Implementation:
- Never holds VAPI API key
- Authenticates with device_secret → gets short-lived JWT (15 min)
- Uses JWT to call proxy endpoints
- Automatically refreshes token before expiry
- All VAPI calls proxied through secure server

This client is safe to deploy on edge devices (Raspberry Pi).
"""

import json
import os
import time
import threading
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()


class SecureProxyVoiceAssistant:
    """
    Secure VAPI client for Raspberry Pi.

    Uses proxy server to keep VAPI API key secure.
    """

    def __init__(self, config_path: str = "config/device_config.json"):
        """Initialize secure proxy client."""
        self.config = self._load_config(config_path)

        # Device credentials (safe to store on Pi)
        self.device_id = os.getenv('DEVICE_ID', self.config.get('device_id'))
        self.device_secret = os.getenv('DEVICE_SECRET', self.config.get('device_secret'))
        self.proxy_url = self.config.get('proxy_url', 'https://securevoice-production-f5c9.up.railway.app')
        self.assistant_id = self.config.get('vapi_assistant_id')

        if not self.device_id:
            raise ValueError("DEVICE_ID not found")

        if not self.device_secret:
            raise ValueError("DEVICE_SECRET not found")

        if not self.assistant_id:
            raise ValueError("vapi_assistant_id not found")

        # JWT token state
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        self.token_refresh_thread: Optional[threading.Thread] = None
        self.stop_refresh = threading.Event()

        print(f"🔒 Secure Proxy Client initialized")
        print(f"   Device: {self.device_id}")
        print(f"   Proxy: {self.proxy_url}")
        print(f"   ✅ VAPI API key is NEVER stored on this device")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def authenticate(self) -> None:
        """
        Authenticate with proxy server and get JWT token.
        """
        print(f"\n🔑 Authenticating device with proxy...")

        try:
            response = httpx.post(
                f"{self.proxy_url}/device/auth",
                json={
                    "device_id": self.device_id,
                    "device_secret": self.device_secret
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            expires_in = data["expires_in"]
            self.token_expiry = time.time() + expires_in

            print(f"✅ Authentication successful!")
            print(f"   Customer: {data['customer_id']}")
            print(f"   Token valid for: {expires_in // 60} minutes")

        except httpx.HTTPStatusError as e:
            print(f"❌ Authentication failed: {e.response.status_code}")
            print(f"   {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Error authenticating: {e}")
            raise

    def refresh_token(self) -> None:
        """
        Refresh JWT token before it expires.
        """
        if not self.access_token:
            print("⚠️  No token to refresh, authenticating instead...")
            self.authenticate()
            return

        print(f"\n🔄 Refreshing token...")

        try:
            response = httpx.post(
                f"{self.proxy_url}/device/refresh",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            expires_in = data["expires_in"]
            self.token_expiry = time.time() + expires_in

            print(f"✅ Token refreshed! Valid for {expires_in // 60} minutes")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                print("⚠️  Token expired, re-authenticating...")
                self.authenticate()
            else:
                print(f"❌ Token refresh failed: {e.response.status_code}")
                raise
        except Exception as e:
            print(f"❌ Error refreshing token: {e}")
            raise

    def _start_token_refresh_thread(self) -> None:
        """
        Start background thread to refresh token periodically.
        Refreshes at 80% of token lifetime (12 minutes for 15-min tokens).
        """
        def refresh_loop():
            while not self.stop_refresh.is_set():
                if self.access_token and self.token_expiry > 0:
                    time_until_expiry = self.token_expiry - time.time()
                    refresh_at = time_until_expiry * 0.8  # Refresh at 80% of lifetime

                    if refresh_at > 0:
                        print(f"⏰ Next token refresh in {int(refresh_at // 60)} minutes")
                        self.stop_refresh.wait(refresh_at)

                        if not self.stop_refresh.is_set():
                            try:
                                self.refresh_token()
                            except Exception as e:
                                print(f"❌ Token refresh error: {e}")
                                # Try again in 1 minute
                                self.stop_refresh.wait(60)
                else:
                    # Wait 1 second if no token
                    self.stop_refresh.wait(1)

        self.token_refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.token_refresh_thread.start()
        print(f"✅ Automatic token refresh enabled")

    def _stop_token_refresh_thread(self) -> None:
        """Stop the token refresh thread."""
        if self.token_refresh_thread:
            self.stop_refresh.set()
            self.token_refresh_thread.join(timeout=2)
            print(f"🛑 Token refresh stopped")

    def start_vapi_call(self, server_url_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Start VAPI call via proxy.

        The proxy will use the real VAPI API key - Pi never sees it.
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        print(f"\n📞 Starting VAPI call via proxy...")

        # Build assistant overrides
        # Use user-speaks-first so user initiates conversation
        assistant_overrides: Dict[str, Any] = {}

        if server_url_override:
            assistant_overrides["serverUrl"] = server_url_override

        try:
            response = httpx.post(
                f"{self.proxy_url}/vapi/start",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "assistant_id": self.assistant_id,
                    "assistant_overrides": assistant_overrides
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            print(f"✅ VAPI call started!")
            print(f"   Call ID: {result.get('id', 'N/A')}")

            return result

        except httpx.HTTPStatusError as e:
            print(f"❌ VAPI call failed: {e.response.status_code}")
            print(f"   {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Error starting VAPI call: {e}")
            raise

    def stop_vapi_call(self, call_id: str) -> Dict[str, Any]:
        """
        Stop VAPI call via proxy.
        """
        if not self.access_token:
            raise ValueError("Not authenticated")

        print(f"\n🛑 Stopping VAPI call via proxy...")

        try:
            response = httpx.post(
                f"{self.proxy_url}/vapi/stop",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "call_id": call_id
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            print(f"✅ VAPI call stopped")

            return result

        except Exception as e:
            print(f"❌ Error stopping VAPI call: {e}")
            raise

    def start_session(self):
        """Start voice session with automatic token management."""
        print("=" * 60)
        print("🔒 VAPI Secure Proxy Client - Tier 0 Security")
        print("=" * 60)
        print(f"🔒 Device: {self.device_id}")
        print(f"🔒 Proxy: {self.proxy_url}")
        print(f"✅ VAPI API key is NEVER on this device")
        print("=" * 60)

        try:
            # Step 1: Authenticate and get JWT token
            self.authenticate()

            # Step 2: Start automatic token refresh
            self._start_token_refresh_thread()

            # Step 3: Start VAPI call
            call_result = self.start_vapi_call()
            call_id = call_result.get("id")

            print("\n" + "=" * 60)
            print("🔊 Voice session active - YOU SPEAK FIRST")
            print("=" * 60)
            print(f"   Call ID: {call_id}")
            print(f"   Token auto-refresh: ✅ Enabled")
            print(f"   Web Call URL: {call_result.get('webCallUrl', 'N/A')}")
            print("\n💡 Say commands to Luna:")
            print("   - 'Turn on the fan'")
            print("   - 'Set to medium'")
            print("   - 'Turn off the fan'")
            print("\n🎤 Luna will respond after you speak")
            print("🔴 Press Ctrl+C to stop")
            print("=" * 60)

            # Keep session alive
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping session...")
            self._stop_token_refresh_thread()
            if call_id:
                try:
                    self.stop_vapi_call(call_id)
                except:
                    pass
            print("✅ Session ended")

        except Exception as e:
            print(f"❌ Error: {e}")
            self._stop_token_refresh_thread()
            raise


def main():
    """Main entry point."""
    try:
        assistant = SecureProxyVoiceAssistant()
        assistant.start_session()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        exit(1)


if __name__ == "__main__":
    main()
