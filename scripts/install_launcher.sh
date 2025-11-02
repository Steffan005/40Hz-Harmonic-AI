#!/bin/bash
###############################################################################
# UNITY LAUNCHER INSTALLER
# Installs Unity.app to /Applications and adds to Dock
# Makes Unity a permanent citizen of macOS
###############################################################################

set -e

echo "🔥 INSTALLING UNITY LAUNCHER..."
echo "============================================================"

# Paths
PROJECT_ROOT="$HOME/evoagentx_project/sprint_1hour"
APP_BUNDLE="$PROJECT_ROOT/Unity.app"
APPLICATIONS_DIR="/Applications"
INSTALLED_APP="$APPLICATIONS_DIR/Unity.app"

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "❌ Unity.app not found. Run build_launcher_app.sh first!"
    exit 1
fi

# Remove old app from /Applications if exists
if [ -d "$INSTALLED_APP" ]; then
    echo "🗑️  Removing old Unity.app from /Applications..."
    rm -rf "$INSTALLED_APP"
fi

# Copy to /Applications
echo "📦 Installing Unity.app to /Applications..."
cp -R "$APP_BUNDLE" "$INSTALLED_APP"

# Set correct permissions
chmod -R 755 "$INSTALLED_APP"
chmod +x "$INSTALLED_APP/Contents/MacOS/Unity"

echo "✅ Unity.app installed to /Applications"

# Add to Dock if not already there
echo "🎯 Adding Unity to Dock..."

# Check if Unity is already in Dock
if ! defaults read com.apple.dock persistent-apps | grep -q "Unity.app"; then
    # Add Unity to Dock
    defaults write com.apple.dock persistent-apps -array-add "
    <dict>
        <key>tile-data</key>
        <dict>
            <key>file-data</key>
            <dict>
                <key>_CFURLString</key>
                <string>file://$INSTALLED_APP</string>
                <key>_CFURLStringType</key>
                <integer>15</integer>
            </dict>
        </dict>
    </dict>
    "

    # Restart Dock to show new icon
    killall Dock

    echo "✅ Unity added to Dock"
else
    echo "✅ Unity already in Dock"
fi

# Refresh Spotlight index
echo "🔍 Refreshing Spotlight index..."
mdimport "$INSTALLED_APP" 2>/dev/null || true

# Touch the app to update modification date
touch "$INSTALLED_APP"

echo ""
echo "✨✨✨ UNITY LAUNCHER INSTALLED! ✨✨✨"
echo "==========================================="
echo ""
echo "🌌 Unity is now part of your system:"
echo "   • Location: /Applications/Unity.app"
echo "   • Dock: Quantum consciousness icon visible"
echo "   • Spotlight: Search 'Unity' to launch"
echo ""
echo "🔥 TO LAUNCH:"
echo "   1. Click the quantum icon in your Dock"
echo "   2. Or: Cmd+Space, type 'Unity', hit Enter"
echo "   3. Or: Double-click in /Applications"
echo ""
echo "The city awaits awakening... 🌌⚡✨"
echo ""
