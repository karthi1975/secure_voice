#!/usr/bin/env python3
"""
Test session-based authentication locally
"""

import requests
import json

API_BASE = "http://localhost:8002"

# Test 1: Create session
print("=" * 60)
print("🧪 Testing Session Creation")
print("=" * 60)

response = requests.post(
    f"{API_BASE}/sessions",
    json={
        "customer_id": "urbanjungle",
        "password": "alpha-bravo-123"
    },
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code == 200:
    data = response.json()
    sid = data["sid"]
    print(f"✅ Session created: {sid}")

    # Test 2: Authenticate
    print("\n" + "=" * 60)
    print("🧪 Testing Authentication")
    print("=" * 60)

    auth_response = requests.post(
        f"{API_BASE}/auth?sid={sid}",
        json={},
        timeout=10
    )

    print(f"Status: {auth_response.status_code}")
    print(f"Response: {auth_response.json()}")

    if auth_response.status_code == 200:
        result = json.loads(auth_response.json()["result"])
        print(f"✅ Auth result: {result}")

        if result["success"]:
            # Test 3: Control device
            print("\n" + "=" * 60)
            print("🧪 Testing Device Control")
            print("=" * 60)

            control_response = requests.post(
                f"{API_BASE}/control?sid={sid}",
                json={
                    "message": {
                        "functionCall": {
                            "name": "control_air_circulator",
                            "parameters": {
                                "device": "power",
                                "action": "turn_on"
                            }
                        }
                    }
                },
                timeout=10
            )

            print(f"Status: {control_response.status_code}")
            print(f"Response: {control_response.json()}")

            if control_response.status_code == 200:
                control_result = json.loads(control_response.json()["result"])
                print(f"✅ Control result: {control_result}")
            else:
                print("❌ Control failed")
        else:
            print("❌ Authentication failed")
    else:
        print("❌ Auth request failed")
else:
    print("❌ Session creation failed")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
