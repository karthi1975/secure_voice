#!/bin/bash

# Test authentication with a specific session ID
# Usage: ./test_session_manual.sh <session-id>

if [ -z "$1" ]; then
    echo "Usage: $0 <session-id>"
    echo "Example: $0 c3f1f823-0acf-4a23-bd78-578bb5826bf9"
    exit 1
fi

SID=$1

echo "Testing session: $SID"
echo "================================"
echo ""

echo "Step 1: Test home_auth() call..."
curl -s -X POST "https://securevoice-production-eb77.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_manual_auth",
        "type": "function",
        "function": {
          "name": "home_auth",
          "arguments": "{}"
        }
      }]
    }
  }' | jq
echo ""

echo "Step 2: Test control after auth..."
curl -s -X POST "https://securevoice-production-eb77.up.railway.app/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_manual_control",
        "type": "function",
        "function": {
          "name": "control_air_circulator",
          "arguments": "{\"device\": \"power\", \"action\": \"turn_on\"}"
        }
      }]
    }
  }' | jq
