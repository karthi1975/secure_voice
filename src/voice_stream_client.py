#!/usr/bin/env python3
"""
VAPI Voice Streaming Client - Real-time microphone to VAPI voice assistant
Uses VAPI's Web Call API for browser-based voice interaction
"""

import json
import os
import requests
from typing import Dict, Any, Optional


class VAPIVoiceClient:
    """
    Client for creating VAPI web calls that handle real-time voice interaction.

    VAPI handles:
    - Speech-to-text (microphone → text)
    - LLM processing (with your system prompt)
    - Text-to-speech (response → audio)

    This client creates web call sessions that run in a browser or can be
    integrated with WebRTC for microphone access.
    """

    def __init__(self, config_path: str = "config/config.json"):
        """Initialize VAPI voice client with configuration."""
        self.config = self._load_config(config_path)
        self.assistant_id = self.config['vapi_assistant_id']
        self.api_key = os.getenv('VAPI_API_KEY', self.config.get('vapi_api_key'))
        self.customer_id = self.config.get('customer_id', 'unknown')

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found in environment or config")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def create_web_call(self) -> Dict[str, Any]:
        """
        Create a VAPI web call session.

        Returns:
            Dictionary with webCallUrl and call details

        The webCallUrl can be opened in a browser to start voice interaction.
        """
        url = "https://api.vapi.ai/call/web"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "assistantId": self.assistant_id,
            "metadata": {
                "customer_id": self.customer_id
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def create_phone_call(self, phone_number: str) -> Dict[str, Any]:
        """
        Create an outbound phone call via VAPI.

        Args:
            phone_number: Phone number to call (E.164 format, e.g., +12223334444)

        Returns:
            Call details
        """
        url = "https://api.vapi.ai/call/phone"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "assistantId": self.assistant_id,
            "customer": {
                "number": phone_number
            },
            "metadata": {
                "customer_id": self.customer_id
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get status of an ongoing or completed call.

        Args:
            call_id: The ID of the call to check

        Returns:
            Call status details
        """
        url = f"https://api.vapi.ai/call/{call_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }


def main():
    """Demo the VAPI voice client."""
    print("🎤 VAPI Voice Client")
    print("=" * 60)

    try:
        client = VAPIVoiceClient()

        print("\nOptions:")
        print("1. Create Web Call (browser-based voice)")
        print("2. Create Phone Call (dial a number)")
        print("3. Check Call Status")

        choice = input("\nChoose option (1-3): ").strip()

        if choice == "1":
            print("\n📞 Creating web call session...")
            result = client.create_web_call()

            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"\n✅ Web call created!")
                print(f"📱 Call ID: {result.get('id', 'N/A')}")
                if 'webCallUrl' in result:
                    print(f"🔗 Open this URL in browser:")
                    print(f"   {result['webCallUrl']}")
                else:
                    print("\n📋 Full response:")
                    print(json.dumps(result, indent=2))

        elif choice == "2":
            phone = input("\nEnter phone number (E.164 format, e.g., +12223334444): ").strip()
            print(f"\n📞 Calling {phone}...")
            result = client.create_phone_call(phone)

            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"\n✅ Call initiated!")
                print(f"📱 Call ID: {result.get('id', 'N/A')}")
                print(f"📊 Status: {result.get('status', 'unknown')}")

        elif choice == "3":
            call_id = input("\nEnter call ID: ").strip()
            print(f"\n🔍 Checking status for call {call_id}...")
            result = client.get_call_status(call_id)

            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("\n📋 Call Status:")
                print(json.dumps(result, indent=2))
        else:
            print("❌ Invalid option")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
