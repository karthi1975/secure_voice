#!/bin/bash

# Test Authentication Flow Only
# This script tests ONLY the authentication without any HA calls

BASE_URL="https://securevoice-production.up.railway.app"

echo "=================================================="
echo "🔐 AUTHENTICATION TEST - Step by Step"
echo "=================================================="

# Step 1: Create Session
echo ""
echo "📝 Step 1: Creating session..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "urbanjungle",
    "password": "alpha-bravo-123"
  }')

echo "Response: $SESSION_RESPONSE"

SID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['sid'])")
AUTHENTICATED=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['authenticated'])")

echo "✅ Session ID: $SID"
echo "   Authenticated: $AUTHENTICATED"

# Step 2: Call home_auth using function-call format
echo ""
echo "=================================================="
echo "🔑 Step 2: Testing home_auth() function call"
echo "=================================================="

AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/webhook?sid=$SID" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "home_auth",
        "parameters": {}
      }
    }
  }')

echo "Response:"
echo "$AUTH_RESPONSE" | python3 -m json.tool

# Extract result
RESULT=$(echo "$AUTH_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'results' in data:
        print(data['results'][0]['result'])
    elif 'result' in data:
        print(data['result'])
    else:
        print('NO RESULT FIELD')
except Exception as e:
    print(f'ERROR: {e}')
")

echo ""
echo "=================================================="
echo "🎯 RESULT: $RESULT"
echo "=================================================="

if echo "$RESULT" | grep -q "Welcome"; then
    echo "✅ AUTHENTICATION SUCCESS!"
elif echo "$RESULT" | grep -q "Authentication failed"; then
    echo "❌ AUTHENTICATION FAILED"
    echo ""
    echo "🔍 Debugging info:"
    echo "   - Customer ID sent: urbanjungle"
    echo "   - Password sent: alpha-bravo-123"
    echo "   - SID: $SID"
else
    echo "⚠️  UNEXPECTED RESULT"
fi

echo ""
echo "=================================================="
