#!/bin/bash

# Simple Authentication Unit Test
# Tests the /sessions endpoint directly

SERVER_URL="https://securevoice-production-f5c9.up.railway.app"
CUSTOMER_ID="urbanjungle"
PASSWORD="alpha-bravo-123"

echo "=========================================="
echo "🧪 Simple Authentication Unit Test"
echo "=========================================="
echo "Server: $SERVER_URL"
echo "Customer: $CUSTOMER_ID"
echo "Password: ${PASSWORD:0:5}***"
echo ""

echo "📡 Testing /sessions endpoint..."
echo ""

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
  "$SERVER_URL/sessions" \
  -H "Content-Type: application/json" \
  -d "{
    \"customer_id\": \"$CUSTOMER_ID\",
    \"password\": \"$PASSWORD\"
  }")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "Response Status: $HTTP_CODE"
echo ""
echo "Response Body:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS: Authentication successful!"

    # Extract sid
    SID=$(echo "$BODY" | jq -r '.sid' 2>/dev/null)
    if [ ! -z "$SID" ] && [ "$SID" != "null" ]; then
        echo "🔑 Session ID: $SID"
        echo ""
        echo "=========================================="
        echo "🧪 Testing /webhook?sid=$SID"
        echo "=========================================="
        echo ""

        # Test webhook with sid parameter
        echo "📡 Simulating home_auth() call..."
        WEBHOOK_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
          "$SERVER_URL/webhook?sid=$SID" \
          -H "Content-Type: application/json" \
          -d '{
            "message": {
              "type": "tool-calls",
              "toolCallList": [{
                "type": "function",
                "function": {
                  "name": "home_auth",
                  "arguments": {}
                },
                "id": "test_call_123"
              }]
            }
          }')

        WEBHOOK_HTTP_CODE=$(echo "$WEBHOOK_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
        WEBHOOK_BODY=$(echo "$WEBHOOK_RESPONSE" | sed '/HTTP_CODE:/d')

        echo "Response Status: $WEBHOOK_HTTP_CODE"
        echo ""
        echo "Response Body:"
        echo "$WEBHOOK_BODY" | jq '.' 2>/dev/null || echo "$WEBHOOK_BODY"
        echo ""

        if [ "$WEBHOOK_HTTP_CODE" = "200" ]; then
            echo "✅ SUCCESS: home_auth() call successful!"
        else
            echo "❌ FAILED: home_auth() returned HTTP $WEBHOOK_HTTP_CODE"
        fi
    fi
else
    echo "❌ FAILED: Authentication failed with HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
