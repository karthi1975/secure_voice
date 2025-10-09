#!/bin/bash

echo "🔍 Debugging Authentication Issue"
echo "=================================="
echo ""

# Step 1: Create a fresh session
echo "Step 1: Creating new session..."
RESPONSE=$(curl -s -X POST "https://securevoice-production-eb77.up.railway.app/sessions" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "urbanjungle", "password": "alpha-bravo-123"}')

echo "Session creation response:"
echo $RESPONSE | jq
echo ""

SID=$(echo $RESPONSE | jq -r '.sid')
AUTH_STATUS=$(echo $RESPONSE | jq -r '.authenticated')

echo "Extracted:"
echo "  Session ID: $SID"
echo "  Authenticated: $AUTH_STATUS"
echo ""

# Step 2: Immediately test auth with this session
echo "Step 2: Testing home_auth() with session..."
AUTH_RESPONSE=$(curl -s -X POST "https://securevoice-production-eb77.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_debug_auth",
        "type": "function",
        "function": {
          "name": "home_auth",
          "arguments": "{}"
        }
      }]
    }
  }')

echo "Auth response:"
echo $AUTH_RESPONSE | jq
echo ""

# Extract the result
AUTH_RESULT=$(echo $AUTH_RESPONSE | jq -r '.results[0].result')
echo "Auth result message: $AUTH_RESULT"
echo ""

# Step 3: Test control
echo "Step 3: Testing control after auth..."
CONTROL_RESPONSE=$(curl -s -X POST "https://securevoice-production-eb77.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_debug_control",
        "type": "function",
        "function": {
          "name": "control_air_circulator",
          "arguments": "{\"device\": \"power\", \"action\": \"turn_on\"}"
        }
      }]
    }
  }')

echo "Control response:"
echo $CONTROL_RESPONSE | jq
echo ""

CONTROL_RESULT=$(echo $CONTROL_RESPONSE | jq -r '.results[0].result')
echo "Control result message: $CONTROL_RESULT"
echo ""

echo "=================================="
echo "Summary:"
echo "  Session ID: $SID"
echo "  Auth Result: $AUTH_RESULT"
echo "  Control Result: $CONTROL_RESULT"
