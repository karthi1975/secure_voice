#!/bin/bash
################################################################################
# VAPI Client Auto-Restart Wrapper
# Restarts Python process between calls to avoid Daily Core context issues
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/src/vapi_client_sdk_restart.py"

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          VAPI Voice Assistant - Continuous Service (Process Restart)       ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "♾️  Service will automatically restart Python process between calls"
echo "🔴 Press Ctrl+C to stop the service completely"
echo ""

# Trap Ctrl+C to exit cleanly
trap 'echo -e "\n\n⏹️  Service stopped by user"; exit 0' INT

while true; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 Starting new Python process..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Run the Python script
    python3 "$PYTHON_SCRIPT"
    EXIT_CODE=$?

    # Check exit code
    if [ $EXIT_CODE -eq 0 ]; then
        # Clean exit (Ctrl+C) - stop the service
        echo ""
        echo "✅ Clean shutdown"
        exit 0
    elif [ $EXIT_CODE -eq 1 ]; then
        # Fatal error - stop trying
        echo ""
        echo "❌ Fatal error - stopping service"
        exit 1
    elif [ $EXIT_CODE -eq 2 ]; then
        # Call ended - restart
        echo ""
        echo "🔄 Call ended - restarting in 3 seconds..."
        sleep 3
        continue
    else
        # Unknown error - wait and retry
        echo ""
        echo "⚠️  Unexpected exit code: $EXIT_CODE - restarting in 3 seconds..."
        sleep 3
        continue
    fi
done
