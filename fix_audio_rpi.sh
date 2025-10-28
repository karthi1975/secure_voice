#!/bin/bash
################################################################################
# Fix Audio Configuration on Raspberry Pi (Trixie/Bookworm)
################################################################################

echo "🔊 Fixing Raspberry Pi Audio Configuration..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Please run as root: sudo bash fix_audio_rpi.sh"
    exit 1
fi

# 1. List available audio devices
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Available audio devices:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
arecord -l
echo ""
aplay -l
echo ""

# 2. Test recording
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎤 Testing microphone (3 second test)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
arecord -d 3 -f cd /tmp/test.wav 2>&1
RECORD_STATUS=$?
echo ""

if [ $RECORD_STATUS -eq 0 ]; then
    echo "✅ Microphone test successful"

    # Test playback
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔊 Testing speaker (playing back recording)..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    aplay /tmp/test.wav
    echo "✅ Speaker test complete"
else
    echo "❌ Microphone test failed"
    echo ""
    echo "Common fixes:"
    echo "1. Check if USB microphone is plugged in"
    echo "2. Try: sudo raspi-config → System Options → Audio → Select correct device"
    echo "3. Check audio permissions: sudo usermod -a -G audio \$USER"
    exit 1
fi

# 3. Create ALSA config to suppress warnings
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  Creating ALSA configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get the actual user running sudo
ACTUAL_USER="${SUDO_USER:-$USER}"
USER_HOME=$(eval echo ~$ACTUAL_USER)

# Create .asoundrc
cat > "$USER_HOME/.asoundrc" << 'EOF'
# Default ALSA configuration for Raspberry Pi
# Suppresses spurious device warnings

pcm.!default {
    type asym
    playback.pcm "plughw:0,0"
    capture.pcm "plughw:0,0"
}

ctl.!default {
    type hw
    card 0
}

# Suppress error messages for non-existent devices
pcm.front cards.pcm.front
pcm.rear cards.pcm.rear
pcm.center_lfe cards.pcm.center_lfe
pcm.side cards.pcm.side
pcm.surround21 cards.pcm.surround21
pcm.surround40 cards.pcm.surround40
pcm.surround41 cards.pcm.surround41
pcm.surround50 cards.pcm.surround50
pcm.surround51 cards.pcm.surround51
pcm.surround71 cards.pcm.surround71
pcm.iec958 cards.pcm.iec958
pcm.spdif iec958
pcm.hdmi cards.pcm.hdmi
pcm.modem cards.pcm.modem
pcm.phoneline cards.pcm.phoneline
EOF

chown $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/.asoundrc"
echo "✅ Created $USER_HOME/.asoundrc"

# 4. Check PipeWire/PulseAudio
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Checking audio server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if pgrep -x "pipewire" > /dev/null; then
    echo "✅ PipeWire is running"
elif pgrep -x "pulseaudio" > /dev/null; then
    echo "✅ PulseAudio is running"
else
    echo "⚠️  No audio server running (PipeWire/PulseAudio)"
    echo "   This is OK if using ALSA directly"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Audio configuration complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Verify your microphone is working"
echo "2. Run the VAPI client with: bash vapi_runner.sh"
echo ""
