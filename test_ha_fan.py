#!/usr/bin/env python3
"""
Test script to directly control Home Assistant fan
"""

import requests
import json
import sys

# Home Assistant configuration
HA_URL = "https://ut-demo-urbanjungle.homeadapt.us"
HA_WEBHOOK_ID = "vapi_air_circulator"

def test_fan_control(device: str, action: str):
    """Test fan control via Home Assistant webhook"""

    webhook_url = f"{HA_URL}/api/webhook/{HA_WEBHOOK_ID}"

    payload = {
        "message": {
            "type": "function-call",
            "functionCall": {
                "name": "control_air_circulator",
                "parameters": {
                    "device": device,
                    "action": action
                }
            }
        }
    }

    print(f"\n{'='*60}")
    print(f"🏠 Testing Home Assistant Fan Control")
    print(f"{'='*60}")
    print(f"URL: {webhook_url}")
    print(f"Device: {device}")
    print(f"Action: {action}")
    print(f"{'='*60}\n")

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"✅ HTTP Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text[:200] if response.text else 'Empty'}")

        if response.status_code == 200:
            print(f"\n✅ SUCCESS: Fan control command sent successfully!")
            print(f"   Device: {device}")
            print(f"   Action: {action}")
        else:
            print(f"\n❌ ERROR: Unexpected status code {response.status_code}")

        return response.status_code == 200

    except requests.exceptions.Timeout:
        print(f"❌ ERROR: Request timed out after 10 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ ERROR: Connection failed - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Run fan control tests"""

    print("\n" + "="*60)
    print("🧪 HOME ASSISTANT FAN CONTROL TEST")
    print("="*60)

    tests = [
        ("power", "turn_on", "Turn ON fan"),
        ("power", "turn_off", "Turn OFF fan"),
        ("speed", "low", "Set to LOW speed"),
        ("speed", "medium", "Set to MEDIUM speed"),
        ("speed", "high", "Set to HIGH speed"),
    ]

    results = []

    for device, action, description in tests:
        print(f"\n🧪 Test: {description}")
        print("-" * 60)

        success = test_fan_control(device, action)
        results.append((description, success))

        if not success:
            print(f"\n⚠️  Test failed. Continue? (y/n): ", end="")
            if input().lower() != 'y':
                break

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {description}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Quick test mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "on":
            test_fan_control("power", "turn_on")
        elif sys.argv[1] == "off":
            test_fan_control("power", "turn_off")
        elif sys.argv[1] == "low":
            test_fan_control("speed", "low")
        elif sys.argv[1] == "medium":
            test_fan_control("speed", "medium")
        elif sys.argv[1] == "high":
            test_fan_control("speed", "high")
        else:
            print("Usage: python test_ha_fan.py [on|off|low|medium|high]")
            print("   or: python test_ha_fan.py  (runs all tests)")
    else:
        main()
