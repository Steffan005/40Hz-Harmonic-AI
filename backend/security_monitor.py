#!/usr/bin/env python3
import os
import time
import json
import hashlib
from pathlib import Path

def monitor_file_changes():
    """Monitor critical files for unauthorized changes"""
    critical_files = [
        "orchestrator.py", "api_server.py", "base_office.py",
        "security_lockdown.py", "security_config.json"
    ]
    
    checksums = {}
    for file_path in critical_files:
        full_path = Path(file_path)
        if full_path.exists():
            with open(full_path, 'rb') as f:
                checksums[file_path] = hashlib.sha256(f.read()).hexdigest()
    
    while True:
        time.sleep(60)  # Check every minute
        for file_path in critical_files:
            full_path = Path(file_path)
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    current_hash = hashlib.sha256(f.read()).hexdigest()
                
                if checksums.get(file_path) != current_hash:
                    print(f"🚨 SECURITY ALERT: {file_path} has been modified!")
                    # Log the alert
                    with open("security_alerts.log", "a") as log:
                        log.write(f"{time.ctime()}: {file_path} modified\n")

if __name__ == "__main__":
    monitor_file_changes()
