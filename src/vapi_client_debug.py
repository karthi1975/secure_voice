#!/usr/bin/env python3
"""
VAPI Debug Client - Full handshake logging

This debug version:
1. Gets VAPI API key from proxy for direct debugging
2. Logs all VAPI API requests/responses
3. Monitors WebSocket connection if applicable
4. Shows detailed handshake progress
"""

import json
import os
import time
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()


class VAPIDebugClient:
    """Debug client with full VAPI handshake logging."""

    def __init__(self, config_path: str = "config/device_config.json"):
        """Initialize debug client."""
        self.config = self._load_config(config_path)

        # Device credentials
        self.device_id = os.getenv('DEVICE_ID', self.config.get('device_id'))
        self.device_secret = os.getenv('DEVICE_SECRET', self.config.get('device_secret'))
        self.proxy_url = self.config.get('proxy_url', 'https://securevoice-production-f5c9.up.railway.app')
        self.assistant_id = self.config.get('vapi_assistant_id')

        # Will be populated from proxy
        self.vapi_api_key: Optional[str] = None
        self.access_token: Optional[str] = None

        print("=" * 80)
        print("🐛 VAPI DEBUG CLIENT - Full Handshake Logging")
        print("=" * 80)
        print(f"Device ID: {self.device_id}")
        print(f"Proxy URL: {self.proxy_url}")
        print(f"Assistant ID: {self.assistant_id}")
        print("=" * 80)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def authenticate(self) -> None:
        """Authenticate with proxy and get JWT token."""
        print("\n" + "=" * 80)
        print("STEP 1: AUTHENTICATE WITH PROXY")
        print("=" * 80)

        url = f"{self.proxy_url}/device/auth"
        payload = {
            "device_id": self.device_id,
            "device_secret": self.device_secret
        }

        print(f"📤 POST {url}")
        print(f"📦 Request Body: {json.dumps(payload, indent=2)}")

        try:
            response = httpx.post(url, json=payload, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📦 Response Body: {json.dumps(response.json(), indent=2)}")

            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            print(f"\n✅ Authentication successful!")
            print(f"   JWT Token (first 50 chars): {self.access_token[:50]}...")
            print(f"   Customer ID: {data.get('customer_id')}")
            print(f"   Expires in: {data.get('expires_in')} seconds")

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise

    def get_vapi_key(self) -> None:
        """Get VAPI API key from proxy for debugging."""
        print("\n" + "=" * 80)
        print("STEP 2: GET VAPI API KEY (DEBUG ONLY)")
        print("=" * 80)

        url = f"{self.proxy_url}/debug/vapi-key"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        print(f"📤 GET {url}")
        print(f"📋 Headers: Authorization: Bearer {self.access_token[:50]}...")

        try:
            response = httpx.get(url, headers=headers, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📦 Response Body: {json.dumps(response.json(), indent=2)}")

            response.raise_for_status()
            data = response.json()

            self.vapi_api_key = data.get("vapi_api_key")
            print(f"\n✅ VAPI API Key retrieved!")
            print(f"   Key (first 20 chars): {self.vapi_api_key[:20]}...")

        except Exception as e:
            print(f"❌ Failed to get VAPI key: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise

    def get_assistant_config(self) -> Dict[str, Any]:
        """Get VAPI assistant configuration directly."""
        print("\n" + "=" * 80)
        print("STEP 3: GET VAPI ASSISTANT CONFIG")
        print("=" * 80)

        url = f"https://api.vapi.ai/assistant/{self.assistant_id}"
        headers = {"Authorization": f"Bearer {self.vapi_api_key}"}

        print(f"📤 GET {url}")
        print(f"📋 Headers: Authorization: Bearer {self.vapi_api_key[:20]}...")

        try:
            response = httpx.get(url, headers=headers, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")

            response.raise_for_status()
            config = response.json()

            print(f"📦 Assistant Configuration:")
            print(json.dumps(config, indent=2))

            # Check critical fields
            print(f"\n🔍 Critical Configuration Check:")
            print(f"   Name: {config.get('name', 'N/A')}")
            print(f"   Model: {config.get('model', {}).get('provider', 'N/A')}")
            print(f"   Voice: {config.get('voice', {}).get('provider', 'N/A')}")
            print(f"   Transcriber: {config.get('transcriber', {}).get('provider', 'N/A')}")
            print(f"   First Message: {config.get('firstMessage', 'N/A')}")
            print(f"   Server URL: {config.get('serverUrl', 'N/A')}")

            return config

        except Exception as e:
            print(f"❌ Failed to get assistant config: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise

    def start_vapi_call_direct(self) -> Dict[str, Any]:
        """Start VAPI call directly (not via proxy) with full logging."""
        print("\n" + "=" * 80)
        print("STEP 4: START VAPI CALL (DIRECT)")
        print("=" * 80)

        # Build webhook URL
        webhook_url = f"{self.proxy_url}/webhook?device_id={self.device_id}"

        url = "https://api.vapi.ai/call/web"
        headers = {
            "Authorization": f"Bearer {self.vapi_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "assistantId": self.assistant_id,
            "assistantOverrides": {
                "serverUrl": webhook_url
            }
        }

        print(f"📤 POST {url}")
        print(f"📋 Headers:")
        print(f"   Authorization: Bearer {self.vapi_api_key[:20]}...")
        print(f"   Content-Type: application/json")
        print(f"📦 Request Body:")
        print(json.dumps(payload, indent=2))

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📦 Response Body:")

            result = response.json()
            print(json.dumps(result, indent=2))

            response.raise_for_status()

            print(f"\n✅ VAPI call started!")
            print(f"   Call ID: {result.get('id')}")
            print(f"   Web Call URL: {result.get('webCallUrl')}")
            print(f"   Status: {result.get('status')}")

            return result

        except Exception as e:
            print(f"❌ Failed to start VAPI call: {e}")
            if hasattr(e, 'response'):
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise

    def start_vapi_call_via_proxy(self) -> Dict[str, Any]:
        """Start VAPI call via proxy with full logging."""
        print("\n" + "=" * 80)
        print("STEP 4: START VAPI CALL (VIA PROXY)")
        print("=" * 80)

        webhook_url = f"{self.proxy_url}/webhook?device_id={self.device_id}"

        url = f"{self.proxy_url}/vapi/start"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "assistant_id": self.assistant_id,
            "assistant_overrides": {
                "serverUrl": webhook_url
            }
        }

        print(f"📤 POST {url}")
        print(f"📋 Headers:")
        print(f"   Authorization: Bearer {self.access_token[:50]}...")
        print(f"   Content-Type: application/json")
        print(f"📦 Request Body:")
        print(json.dumps(payload, indent=2))

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=30)

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📦 Response Body:")

            result = response.json()
            print(json.dumps(result, indent=2))

            response.raise_for_status()

            print(f"\n✅ VAPI call started via proxy!")
            print(f"   Call ID: {result.get('id')}")
            print(f"   Web Call URL: {result.get('webCallUrl')}")

            return result

        except Exception as e:
            print(f"❌ Failed to start VAPI call via proxy: {e}")
            if hasattr(e, 'response'):
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise

    def monitor_call_status(self, call_id: str, duration: int = 30):
        """Monitor call status for debugging."""
        print("\n" + "=" * 80)
        print(f"STEP 5: MONITOR CALL STATUS (for {duration}s)")
        print("=" * 80)

        url = f"https://api.vapi.ai/call/{call_id}"
        headers = {"Authorization": f"Bearer {self.vapi_api_key}"}

        print(f"📤 GET {url}")
        print(f"📋 Headers: Authorization: Bearer {self.vapi_api_key[:20]}...")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < duration:
            try:
                response = httpx.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get('status')

                    if current_status != last_status:
                        print(f"\n⏱️  [{int(time.time() - start_time)}s] Status changed: {current_status}")
                        print(f"   Full response: {json.dumps(status_data, indent=2)}")
                        last_status = current_status
                    else:
                        print(f"⏱️  [{int(time.time() - start_time)}s] Status: {current_status}")

                time.sleep(2)

            except Exception as e:
                print(f"⚠️  Error checking status: {e}")
                time.sleep(2)

    def run_full_debug(self, use_proxy: bool = True):
        """Run full debug sequence."""
        try:
            # Step 1: Authenticate
            self.authenticate()

            # Step 2: Get VAPI key (for direct debugging)
            self.get_vapi_key()

            # Step 3: Get assistant config
            assistant_config = self.get_assistant_config()

            # Step 4: Start call
            if use_proxy:
                call_result = self.start_vapi_call_via_proxy()
            else:
                call_result = self.start_vapi_call_direct()

            call_id = call_result.get('id')
            web_url = call_result.get('webCallUrl')

            # Summary
            print("\n" + "=" * 80)
            print("🔊 CALL ACTIVE - OPEN WEB URL TO TEST")
            print("=" * 80)
            print(f"Call ID: {call_id}")
            print(f"Web URL: {web_url}")
            print(f"\n📱 Open this URL in your browser and allow microphone access")
            print(f"🎤 Speak to test: 'Turn on the fan'")
            print("=" * 80)

            # Step 5: Monitor for 60 seconds
            if call_id:
                self.monitor_call_status(call_id, duration=60)

            print("\n✅ Debug session complete")

        except KeyboardInterrupt:
            print("\n\n⏹️  Debug session interrupted")
        except Exception as e:
            print(f"\n❌ Debug session failed: {e}")
            raise


def main():
    """Main entry point."""
    import sys

    use_proxy = '--proxy' in sys.argv

    print("🐛 VAPI Debug Client")
    print(f"   Mode: {'Via Proxy' if use_proxy else 'Direct API'}")
    print()

    client = VAPIDebugClient()
    client.run_full_debug(use_proxy=use_proxy)


if __name__ == "__main__":
    main()
