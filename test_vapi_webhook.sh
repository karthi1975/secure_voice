#!/bin/bash

echo "Testing VAPI webhook with different payload formats..."
echo ""

# Test 1: Standard VAPI format
echo "Test 1: Standard function-call format"
curl -X POST "https://securevoice-production-eb77.up.railway.app/webhook" \
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
    }
  }' -s | jq
echo ""

# Test 2: With call metadata
echo "Test 2: With call metadata"
curl -X POST "https://securevoice-production-eb77.up.railway.app/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "control_air_circulator",
        "parameters": {
          "device": "power",
          "action": "turn_off"
        }
      }
    },
    "call": {
      "id": "test-call-123"
    }
  }' -s | jq
echo ""

# Test 3: Different speeds
echo "Test 3: Speed control"
curl -X POST "https://securevoice-production-eb77.up.railway.app/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "function-call",
      "functionCall": {
        "name": "control_air_circulator",
        "parameters": {
          "device": "speed",
          "action": "high"
        }
      }
    }
  }' -s | jq
