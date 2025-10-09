#!/bin/bash

echo "Testing Authentication Flow"
echo "==========================="
echo ""

# Step 1: Create session
echo "Step 1: Creating session..."
RESPONSE=$(curl -s -X POST "https://securevoice-production-eb77.up.railway.app/sessions" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "urbanjungle", "password": "alpha-bravo-123"}')

SID=$(echo $RESPONSE | jq -r '.sid')
echo "Session ID: $SID"
echo ""

# Step 2: Test authentication
echo "Step 2: Testing authentication..."
curl -s -X POST "https://securevoice-production-eb77.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_auth_test",
        "type": "function",
        "function": {
          "name": "home_auth",
          "arguments": "{}"
        }
      }]
    }
  }' | jq
echo ""

# Step 3: Test device control (should work after auth)
echo "Step 3: Testing device control after authentication..."
curl -s -X POST "https://securevoice-production-eb77.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_control_test",
        "type": "function",
        "function": {
          "name": "control_air_circulator",
          "arguments": "{\"device\": \"power\", \"action\": \"turn_on\"}"
        }
      }]
    }
  }' | jq
echo ""

echo "==========================="
echo "Authentication flow test complete!"
