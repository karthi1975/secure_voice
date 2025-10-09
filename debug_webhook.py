#!/usr/bin/env python3
"""
Add logging to webhook to see what VAPI sends
"""

import sys
import json

# Sample webhook payloads to understand the format

print("=" * 60)
print("VAPI Webhook Payload Examples")
print("=" * 60)
print()

print("1. FUNCTION CALL (what we want to see):")
print(json.dumps({
    "message": {
        "type": "function-call",
        "functionCall": {
            "name": "home_auth",
            "parameters": {}
        }
    }
}, indent=2))
print()

print("2. FUNCTION CALL with parameters:")
print(json.dumps({
    "message": {
        "type": "function-call",
        "functionCall": {
            "name": "control_air_circulator",
            "parameters": {
                "device": "power",
                "action": "turn_on"
            }
        }
    }
}, indent=2))
print()

print("3. USER MESSAGE (conversation, NOT function call):")
print(json.dumps({
    "message": {
        "type": "user-message",
        "role": "user",
        "content": "Turn on the fan"
    }
}, indent=2))
print()

print("4. ASSISTANT MESSAGE:")
print(json.dumps({
    "message": {
        "type": "assistant-message",
        "role": "assistant",
        "content": "Authenticating"
    }
}, indent=2))
print()

print("=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. Check Railway logs when you speak to Luna")
print("2. Look for the 'message.type' field")
print("3. If it says 'function-call' → Functions are working! ✅")
print("4. If it says 'user-message' or 'assistant-message' → Functions NOT working! ❌")
print()
print("Copy the actual JSON from Railway logs and let's compare!")
print("=" * 60)
