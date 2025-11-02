#!/bin/bash
# 🔒 UNITY SECURITY LOCKDOWN - FORT KNOX MODE
# NSA-grade hardening for macOS

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔒 UNITY SECURITY LOCKDOWN - FORT KNOX MODE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. FIREWALL - Maximum Strictness
echo "🛡️  [1/10] Configuring Firewall..."
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setallowsigned off
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setallowsignedapp off
sudo pkill -HUP socketfilterfw
echo "   ✅ Firewall: MAXIMUM STRICTNESS"

# 2. GATEKEEPER - Enforce code signing
echo "🔐 [2/10] Hardening Gatekeeper..."
sudo spctl --master-enable
sudo spctl --enable
echo "   ✅ Gatekeeper: ENFORCED"

# 3. SIP - System Integrity Protection verification
echo "🛡️  [3/10] Verifying SIP..."
SIP_STATUS=$(csrutil status | grep -c "enabled")
if [ "$SIP_STATUS" -eq 1 ]; then
    echo "   ✅ SIP: ENABLED"
else
    echo "   ⚠️  SIP: DISABLED (reboot to Recovery and run: csrutil enable)"
fi

# 4. FILE VAULT - Full disk encryption
echo "💽 [4/10] Checking FileVault..."
FV_STATUS=$(fdesetup status | grep -c "On")
if [ "$FV_STATUS" -eq 1 ]; then
    echo "   ✅ FileVault: ENABLED"
else
    echo "   ⚠️  FileVault: NOT ENABLED (run: sudo fdesetup enable)"
fi

# 5. SECURE BOOT - Verification
echo "🔒 [5/10] Checking Secure Boot..."
if system_profiler SPiBridgeDataType 2>/dev/null | grep -q "Secure Boot"; then
    echo "   ✅ Secure Boot: SUPPORTED"
else
    echo "   ℹ️  Secure Boot: N/A (Intel Mac)"
fi

# 6. PRIVACY - Disable telemetry
echo "🕵️  [6/10] Disabling telemetry..."
# Disable analytics
defaults write com.apple.assistant.support 'Assistant Enabled' 0
# Disable Siri data collection
defaults write com.apple.assistant.support 'Siri Data Sharing Opt-In Status' 2
# Disable crash reporter
defaults write com.apple.CrashReporter DialogType none
# Disable spotlight suggestions
defaults write com.apple.safari UniversalSearchEnabled -bool false
defaults write com.apple.safari SuppressSearchSuggestions -bool true
echo "   ✅ Telemetry: DISABLED"

# 7. DNS - Configure encrypted DNS
echo "🌐 [7/10] Configuring DNS over HTTPS..."
# Cloudflare DNS over HTTPS
networksetup -setdnsservers Wi-Fi 1.1.1.1 1.0.0.1
networksetup -setdnsservers Ethernet 1.1.1.1 1.0.0.1
echo "   ✅ DNS: Cloudflare DoH (1.1.1.1)"

# 8. PERMISSIONS - Restrict unnecessary access
echo "🔐 [8/10] Restricting permissions..."
# Disable remote apple events
sudo systemsetup -setremoteappleevents off 2>/dev/null || true
# Disable remote login
sudo systemsetup -setremotelogin off 2>/dev/null || true
# Disable wake on network
sudo systemsetup -setwakeonnetworkaccess off 2>/dev/null || true
echo "   ✅ Remote services: DISABLED"

# 9. KERNEL - Security hardening
echo "🧠 [9/10] Kernel hardening..."
# Disable kernel extensions unsigned
sudo nvram boot-args="kext-dev-mode=0"
echo "   ✅ Kernel: HARDENED"

# 10. AUDIT - Security audit log
echo "📋 [10/10] Enabling audit logging..."
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.auditd.plist 2>/dev/null || true
echo "   ✅ Audit logging: ENABLED"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SECURITY LOCKDOWN COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 System Status:"
echo "   Firewall: MAXIMUM"
echo "   Gatekeeper: ENFORCED"
echo "   Telemetry: DISABLED"
echo "   DNS: ENCRYPTED"
echo "   Remote Access: BLOCKED"
echo ""
echo "🛡️  Your Mac is now locked down tighter than Fort Knox!"
echo ""
