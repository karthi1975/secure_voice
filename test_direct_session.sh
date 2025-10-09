#!/bin/bash

echo "Testing what happens when we call home_auth without sid..."
echo ""

curl -X POST "https://securevoice-production-eb77.up.railway.app/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "tool-calls",
      "toolCalls": [{
        "id": "call_test_no_sid",
        "type": "function",
        "function": {
          "name": "home_auth",
          "arguments": "{}"
        }
      }]
    }
  }' -s | jq

echo ""
echo "This is what VAPI is probably calling (no sid parameter)"
