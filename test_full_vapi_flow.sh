#!/bin/bash

# Test Full VAPI Flow - Exactly as VAPI would do it
BASE_URL="https://securevoice-production.up.railway.app"

echo "=========================================================="
echo "🧪 FULL VAPI FLOW TEST"
echo "=========================================================="

# Step 1: Create Session (Client does this)
echo ""
echo "1️⃣  CLIENT: Creating session..."
SESSION_JSON=$(curl -s -X POST "$BASE_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "urbanjungle",
    "password": "alpha-bravo-123"
  }')

echo "$SESSION_JSON" | python3 -m json.tool

SID=$(echo "$SESSION_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['sid'])")

echo ""
echo "✅ Session created with SID: $SID"
echo "   Client will now pass serverUrl: $BASE_URL/webhook?sid=$SID"

# Step 2: VAPI starts call and Luna SHOULD immediately call home_auth()
echo ""
echo "=========================================================="
echo "2️⃣  VAPI: Luna calls home_auth() immediately on connect"
echo "=========================================================="

AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "home_auth",
        "parameters": {}
      }
    },
    "call": {
      "id": "test-call-123",
      "assistantId": "31377f1e-dd62-43df-bc3c-ca8e87e08138"
    }
  }')

echo "Server Response:"
echo "$AUTH_RESPONSE" | python3 -m json.tool

AUTH_RESULT=$(echo "$AUTH_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'results' in data:
        print(data['results'][0]['result'])
    else:
        print('ERROR: No results field')
except Exception as e:
    print(f'ERROR: {e}')
")

echo ""
if echo "$AUTH_RESULT" | grep -q "Welcome"; then
    echo "✅ AUTHENTICATION SUCCESS!"
    echo "   Luna should now speak: \"$AUTH_RESULT\""

    # Step 3: User commands fan
    echo ""
    echo "=========================================================="
    echo "3️⃣  USER: 'Turn on the fan'"
    echo "=========================================================="

    FAN_RESPONSE=$(curl -s -X POST "$BASE_URL/webhook?sid=$SID" \
      -H "Content-Type: application/json" \
      -d '{
        "message": {
          "type": "function-call",
          "functionCall": {
            "name": "control_air_circulator",
            "parameters": {
              "device": "power",
              "action": "turn_on"
            }
          }
        },
        "call": {
          "id": "test-call-123",
          "assistantId": "31377f1e-dd62-43df-bc3c-ca8e87e08138"
        }
      }')

    echo "Server Response:"
    echo "$FAN_RESPONSE" | python3 -m json.tool

    FAN_RESULT=$(echo "$FAN_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'results' in data:
        print(data['results'][0]['result'])
    else:
        print('ERROR: No results field')
except Exception as e:
    print(f'ERROR: {e}')
")

    echo ""
    if echo "$FAN_RESULT" | grep -qE "Power turn|turn_on"; then
        echo "✅ FAN CONTROL SUCCESS!"
        echo "   HA should have received command"
    else
        echo "❌ FAN CONTROL FAILED: $FAN_RESULT"
    fi

else
    echo "❌ AUTHENTICATION FAILED: $AUTH_RESULT"
    echo ""
    echo "🔍 This means:"
    echo "   - Session credentials don't match"
    echo "   - Check customer_id = 'urbanjungle'"
    echo "   - Check password = 'alpha-bravo-123'"
fi

echo ""
echo "=========================================================="
echo "📊 SUMMARY"
echo "=========================================================="
echo "SID: $SID"
echo "Auth Result: $AUTH_RESULT"
if [ ! -z "$FAN_RESULT" ]; then
    echo "Fan Result: $FAN_RESULT"
fi
echo ""
