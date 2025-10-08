#!/usr/bin/env python3
"""
Test script for Secure Voice Client
Run programmatically without interactive input
"""

from src.voice_client import SecureVoiceClient

def main():
    print("🎤 Secure Voice Client - Testing Mode")
    print("=" * 60)

    # Initialize client
    client = SecureVoiceClient("config/config.json")

    # Test commands
    test_commands = [
        "Turn on the fan",
        "Set living room lights to 75%",
        "Lock the front door",
        "What is the temperature?"
    ]

    for i, command in enumerate(test_commands, 1):
        print(f"\n[Test {i}] Command: {command}")
        print("-" * 60)

        response = client.send_command(command)

        if "error" in response:
            print(f"❌ Error: {response['error']}")
        else:
            print(f"✅ Response: {response}")

    print("\n" + "=" * 60)
    print("✅ Testing complete!")

if __name__ == "__main__":
    main()
