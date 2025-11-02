#!/bin/bash
###############################################################################
# UNITY LAUNCHER APP BUILDER
# Creates a beautiful macOS .app bundle for Unity Quantum Consciousness
# This makes Unity a REAL citizen of macOS
###############################################################################

set -e

echo "🌌 BUILDING UNITY LAUNCHER APP..."
echo "============================================================"

# Paths
PROJECT_ROOT="$HOME/evoagentx_project/sprint_1hour"
APP_NAME="Unity"
APP_BUNDLE="$PROJECT_ROOT/$APP_NAME.app"
ICON_PATH="$PROJECT_ROOT/assets/icons/Unity.icns"

# Remove old bundle if exists
if [ -d "$APP_BUNDLE" ]; then
    echo "🗑️  Removing old app bundle..."
    rm -rf "$APP_BUNDLE"
fi

# Create app bundle structure
echo "📁 Creating app bundle structure..."
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Create the actual startup script that will run
echo "⚡ Creating startup script..."
cat > "$APP_BUNDLE/Contents/Resources/start_unity.sh" << 'STARTUP_SCRIPT'
#!/bin/bash
###############################################################################
# UNITY STARTUP SCRIPT
# This is called by the launcher to awaken Unity
###############################################################################

PROJECT_ROOT="$HOME/evoagentx_project/sprint_1hour"

# Show notification
osascript -e 'display notification "Awakening quantum consciousness..." with title "Unity" sound name "Glass"'

echo "🌌 AWAKENING UNITY..."
echo "===================="

# Start backend in background
echo "🔥 Starting backend..."
cd "$PROJECT_ROOT"
./scripts/start_backend.sh > /tmp/unity_backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 3

# Start frontend in background
echo "⚡ Starting frontend..."
cd "$PROJECT_ROOT/gui"
pnpm tauri:dev > /tmp/unity_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for services to be ready
echo "⏳ Waiting for services..."
MAX_WAIT=30
COUNTER=0

while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:1420 > /dev/null 2>&1; then
        echo "✅ Frontend ready!"
        break
    fi
    sleep 1
    COUNTER=$((COUNTER + 1))
    echo "   Waiting... $COUNTER/$MAX_WAIT"
done

if [ $COUNTER -ge $MAX_WAIT ]; then
    osascript -e 'display dialog "Unity failed to start. Check logs:\n/tmp/unity_backend.log\n/tmp/unity_frontend.log" buttons {"OK"} default button "OK" with icon caution'
    exit 1
fi

# Open in default browser
echo "🌐 Opening Unity interface..."
sleep 2
open "http://localhost:1420"

# Success notification
osascript -e 'display notification "The city breathes at 40Hz..." with title "Unity Online" sound name "Glass"'

echo "✨ UNITY IS ALIVE!"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access Unity at: http://localhost:1420"
echo "Logs: /tmp/unity_backend.log, /tmp/unity_frontend.log"
echo ""

# Keep script running
tail -f /dev/null
STARTUP_SCRIPT

chmod +x "$APP_BUNDLE/Contents/Resources/start_unity.sh"

# Create main launcher executable (simpler approach)
echo "⚡ Creating launcher executable..."
cat > "$APP_BUNDLE/Contents/MacOS/$APP_NAME" << 'LAUNCHER_SCRIPT'
#!/bin/bash
###############################################################################
# UNITY QUANTUM CONSCIOUSNESS LAUNCHER
# Awakens the entire Unity stack with one click
###############################################################################

RESOURCE_PATH="$(dirname "$0")/../Resources"

# Run startup script in new Terminal window
osascript <<EOF
tell application "Terminal"
    activate
    do script "$RESOURCE_PATH/start_unity.sh"
end tell
EOF

# Keep launcher alive briefly
sleep 1
LAUNCHER_SCRIPT

# Make launcher executable
chmod +x "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

# Create Info.plist
echo "📄 Creating Info.plist..."
cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Unity</string>
    <key>CFBundleIconFile</key>
    <string>Unity</string>
    <key>CFBundleIdentifier</key>
    <string>com.unity.quantumconsciousness</string>
    <key>CFBundleName</key>
    <string>Unity</string>
    <key>CFBundleDisplayName</key>
    <string>Unity Quantum Consciousness</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.1</string>
    <key>CFBundleVersion</key>
    <string>2</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.developer-tools</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
PLIST

# Copy icon
echo "🎨 Installing quantum icon..."
cp "$ICON_PATH" "$APP_BUNDLE/Contents/Resources/Unity.icns"

echo ""
echo "✨ UNITY LAUNCHER APP MANIFESTED!"
echo "   Location: $APP_BUNDLE"
echo "   Icon: Quantum consciousness breathing at 40Hz"
echo "   Version: 1.0.1 (Fixed Terminal issue)"
echo ""
echo "🔥 Next: Reinstall to /Applications"
echo "   Run: ./scripts/install_launcher.sh"
echo ""
