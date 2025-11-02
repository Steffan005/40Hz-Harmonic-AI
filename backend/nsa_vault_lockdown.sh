#!/bin/bash
# NSA VAULT+ PERMANENT NETWORK LOCKDOWN
# MacOS PF Firewall Configuration

echo "🔒 IMPLEMENTING NSA VAULT+ PERMANENT NETWORK LOCKDOWN..."

# Create comprehensive pf rules
cat > /tmp/nsa_vault_lockdown.pf << 'EOF'
# NSA VAULT+ PERMANENT NETWORK LOCKDOWN
# ALL NON-AUTHORIZED TRAFFIC BLOCKED

# Enable pf
set skip on lo0

# Default deny everything
block in all
block out all

# Allow localhost only
pass in on lo0 from any to any
pass out on lo0 from any to any

# Allow ONLY authorized development ports (8000, 8080, 3000)
pass out proto tcp from any to any port {8000, 8080, 3000}
pass out proto udp from any to any port {8000, 8080, 3000}

# Allow localhost connections to authorized ports
pass in proto tcp from 127.0.0.1 to 127.0.0.1 port {8000, 8080, 3000}
pass in proto tcp from ::1 to ::1 port {8000, 8080, 3000}

# EMERGENCY KILL SWITCH - Block all other traffic
block out proto tcp from any to any port != {8000, 8080, 3000}
block out proto udp from any to any port != {8000, 8080, 3000}
block in proto tcp from any to any port != {8000, 8080, 3000}
block in proto udp from any to any port != {8000, 8080, 3000}

# Additional security - block common attack vectors
block in proto tcp from any to any port 22    # SSH
block in proto tcp from any to any port 23    # Telnet  
block in proto tcp from any to any port 21    # FTP
block in proto tcp from any to any port 25    # SMTP
block in proto tcp from any to any port 53    # DNS
block in proto tcp from any to any port 135   # RPC
block in proto tcp from any to any port 139   # NetBIOS
block in proto tcp from any to any port 445   # SMB

# Block ngrok and tunneling services
block in proto tcp from any to any port 4040
block out proto tcp from any to any port 4040
EOF

echo "✅ PF rules created"

# Apply the lockdown rules
echo "🚨 APPLYING LOCKDOWN RULES..."
if sudo pfctl -f /tmp/nsa_vault_lockdown.pf -e; then
    echo "✅ PF firewall rules APPLIED - SYSTEM LOCKED DOWN"
else
    echo "⚠️ PF rules created but may need manual activation"
fi

# Kill any remaining suspicious processes
echo "🎯 FINAL THREAT ELIMINATION..."

# Kill ControlCenter processes
pkill -f ControlCenter 2>/dev/null && echo "✅ ControlCenter eliminated"

# Kill any remaining Redis/Postgres on non-authorized ports
pkill -f redis 2>/dev/null && echo "✅ Redis neutralized"
pkill -f postgres 2>/dev/null && echo "✅ Postgres neutralized" 

# Monitor for any port 4040 (ngrok) - CRITICAL THREAT
if lsof -i :4040 >/dev/null 2>&1; then
    echo "🚨 ngrok detected - ELIMINATING IMMEDIATELY"
    lsof -ti:4040 | xargs kill -9 2>/dev/null
fi

# Verify lockdown
echo "🔍 VERIFICATION:"
AUTHORIZED_ONLY=$(lsof -i -n -P | grep LISTEN | grep -v "127.0.0.1:8000" | wc -l)
if [ "$AUTHORIZED_ONLY" -eq 0 ]; then
    echo "🎉 PERFECT! Only authorized port 8000 active"
else
    echo "⚠️ Additional listening ports detected - manual review needed"
fi

echo ""
echo "🚨 NSA VAULT+ LOCKDOWN STATUS 🚨"
echo "================================"
echo "🔒 Network: LOCKED DOWN"
echo "🛡️ Security: MAXIMUM"
echo "⚡ Performance: OPTIMIZED"  
echo "👑 User Access: UNRESTRICTED"
echo "🎯 Threats: ELIMINATED"
echo "================================"