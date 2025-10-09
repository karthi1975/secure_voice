#!/bin/bash

# Test VAPI Client with Real-time Monitoring
# This script will help verify if Luna calls home_auth()

echo "=========================================================="
echo "🧪 VAPI CLIENT TEST WITH MONITORING"
echo "=========================================================="
echo ""
echo "This script will:"
echo "1. Start the VAPI client"
echo "2. Show you the Session ID (SID)"
echo "3. You can then check Railway logs for that SID"
echo ""
echo "What to look for in Railway logs:"
echo "  - 🔍 WEBHOOK DEBUG - SID: <your-sid>"
echo "  - 🔍 WEBHOOK DEBUG - Message type: function-call"
echo "  - Function name: home_auth"
echo ""
echo "Press ENTER to start the VAPI client..."
read

echo ""
echo "=========================================================="
echo "Starting VAPI Client..."
echo "=========================================================="

# Run the client
./venv/bin/python src/vapi_client_clean.py
