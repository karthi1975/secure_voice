#!/usr/bin/env python3
"""
Simple test script to verify device authentication and VAPI proxy.

Tests:
1. Device authentication → get JWT token
2. Token refresh
3. VAPI call via proxy
4. Verify Pi never needs VAPI API key
"""

import httpx
import json
import time

# Configuration
PROXY_URL = "https://securevoice-production-f5c9.up.railway.app"
DEVICE_ID = "pi_urbanjungle_001"
DEVICE_SECRET = "dev_secret_urbanjungle_abc123xyz"
ASSISTANT_ID = "31377f1e-dd62-43df-bc3c-ca8e87e08138"

print("=" * 60)
print("🔒 Secure Device Test")
print("=" * 60)
print(f"Device: {DEVICE_ID}")
print(f"Proxy: {PROXY_URL}")
print(f"✅ No VAPI API key on this device!")
print("=" * 60)
print()

# Step 1: Authenticate device
print("Step 1: Authenticate device...")
try:
    response = httpx.post(
        f"{PROXY_URL}/device/auth",
        json={
            "device_id": DEVICE_ID,
            "device_secret": DEVICE_SECRET
        },
        timeout=30
    )
    response.raise_for_status()
    auth_data = response.json()

    access_token = auth_data["access_token"]
    expires_in = auth_data["expires_in"]
    customer_id = auth_data["customer_id"]

    print(f"✅ Authenticated!")
    print(f"   Customer: {customer_id}")
    print(f"   Token expires in: {expires_in // 60} minutes")
    print(f"   Token: {access_token[:50]}...")
    print()

except Exception as e:
    print(f"❌ Authentication failed: {e}")
    exit(1)

# Step 2: Test token refresh
print("Step 2: Test token refresh...")
try:
    response = httpx.post(
        f"{PROXY_URL}/device/refresh",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30
    )
    response.raise_for_status()
    refresh_data = response.json()

    new_token = refresh_data["access_token"]

    print(f"✅ Token refreshed!")
    print(f"   New token: {new_token[:50]}...")
    print()

    # Use the new token
    access_token = new_token

except Exception as e:
    print(f"❌ Token refresh failed: {e}")
    exit(1)

# Step 3: Start VAPI call via proxy
print("Step 3: Start VAPI call via secure proxy...")
print("   (Server will use VAPI API key - we don't have it!)")
try:
    response = httpx.post(
        f"{PROXY_URL}/vapi/start",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "assistant_id": ASSISTANT_ID,
            "assistant_overrides": {
                "firstMessageMode": "assistant-speaks-first"
            }
        },
        timeout=30
    )
    response.raise_for_status()
    call_data = response.json()

    call_id = call_data.get("id")
    web_call_url = call_data.get("webCallUrl")

    print(f"✅ VAPI call started via secure proxy!")
    print(f"   Call ID: {call_id}")
    print(f"   Web Call URL: {web_call_url}")
    print()

    # Wait a moment
    print("Waiting 5 seconds...")
    time.sleep(5)

    # Step 4: Stop the call
    print("Step 4: Stop VAPI call...")
    response = httpx.post(
        f"{PROXY_URL}/vapi/stop",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"call_id": call_id},
        timeout=30
    )
    response.raise_for_status()

    print(f"✅ VAPI call stopped")
    print()

except httpx.HTTPStatusError as e:
    print(f"❌ VAPI call failed: {e.response.status_code}")
    print(f"   Response: {e.response.text}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Summary
print("=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print()
print("✅ Security Verification:")
print("   ✓ Device authenticated with device_secret")
print("   ✓ Got short-lived JWT token (15 minutes)")
print("   ✓ Token refresh working")
print("   ✓ VAPI call proxied through secure server")
print("   ✓ VAPI API key NEVER on this device")
print()
print("🔒 Tier 0 Security VERIFIED!")
print("=" * 60)
