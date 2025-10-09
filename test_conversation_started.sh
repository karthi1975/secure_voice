#!/bin/bash

# Test conversation-started authentication flow
BASE_URL="https://securevoice-production.up.railway.app"

echo "=========================================================="
echo "🧪 CONVERSATION-STARTED AUTHENTICATION TEST"
echo "=========================================================="

# Step 1: Create Session
echo ""
echo "1️⃣  Creating session..."
SESSION_JSON=$(curl -s -X POST "$BASE_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "urbanjungle",
    "password": "alpha-bravo-123"
  }')

SID=$(echo "$SESSION_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['sid'])")
echo "✅ Session ID: $SID"

# Step 2: Simulate VAPI sending conversation-started with firstMessageMode
echo ""
echo "=========================================================="
echo "2️⃣  Testing conversation-started event (firstMessageMode)"
echo "=========================================================="

RESPONSE=$(curl -s -X POST "$BASE_URL/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "conversation-started"
    },
    "call": {
      "id": "test-call-123",
      "assistantId": "31377f1e-dd62-43df-bc3c-ca8e87e08138"
    }
  }')

echo "Server Response:"
echo "$RESPONSE" | python3 -m json.tool

FIRST_MESSAGE=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'firstMessage' in data:
        print(data['firstMessage'])
    else:
        print('ERROR: No firstMessage field')
except Exception as e:
    print(f'ERROR: {e}')
")

echo ""
echo "=========================================================="
if echo "$FIRST_MESSAGE" | grep -q "Welcome"; then
    echo "✅ AUTHENTICATION SUCCESS VIA conversation-started!"
    echo ""
    echo "Luna will speak: \"$FIRST_MESSAGE\""
    echo ""
    echo "This approach bypasses the LLM entirely and forces authentication"
    echo "at call start using VAPI's firstMessageMode."
else
    echo "❌ AUTHENTICATION FAILED: $FIRST_MESSAGE"
fi
echo "=========================================================="
