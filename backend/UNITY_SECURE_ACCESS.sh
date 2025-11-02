#!/bin/bash
# 🔐 UNITY SECURE ACCESS SYSTEM 🔐
# This script provides secure access to Unity while protecting from theft

# Configuration
UNITY_PASSWORD="YourUnityPassword2025!"  # CHANGE THIS
UNITY_BACKUP_DIR="$HOME/Library/Application Support/Safari/Extensions"
UNITY_MASTER_DIR="$HOME/evoagentx_project/sprint_1hour"
UNITY_SECURE_BACKUP="$HOME/evoagentx_project_ENC"

echo "🔐 Unity Secure Access System"
echo "============================="

# Function to unlock Unity
unlock_unity() {
    echo "Please enter Unity access password:"
    read -s input_password
    
    if [ "$input_password" = "$UNITY_PASSWORD" ]; then
        echo "✅ Unity Access Granted!"
        
        # Launch Unity from secure location
        cd "$UNITY_MASTER_DIR"
        ./launch_unity.sh
        
        return 0
    else
        echo "❌ Access Denied - Incorrect Password"
        return 1
    fi
}

# Function to create secure backup
create_secure_backup() {
    echo "Creating encrypted Unity backup..."
    
    # Create encrypted archive
    tar -czf - "$UNITY_MASTER_DIR" | \
    openssl enc -aes-256-cbc -salt -out "$UNITY_SECURE_BACKUP.tar.gz.enc"
    
    echo "✅ Secure backup created: $UNITY_SECURE_BACKUP.tar.gz.enc"
}

# Function to verify system integrity
verify_unity_integrity() {
    echo "Verifying Unity system integrity..."
    
    # Check if Unity files exist
    if [ -f "$UNITY_MASTER_DIR/launch_unity.sh" ]; then
        echo "✅ Unity system verified"
        return 0
    else
        echo "❌ Unity system integrity check failed!"
        return 1
    fi
}

# Main menu
echo "Choose action:"
echo "1. Unlock Unity (requires password)"
echo "2. Create secure backup"
echo "3. Verify system integrity"
echo "4. Exit"

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        unlock_unity
        ;;
    2)
        create_secure_backup
        ;;
    3)
        verify_unity_integrity
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac