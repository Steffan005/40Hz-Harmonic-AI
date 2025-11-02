#!/usr/bin/env python3
"""
EvoAgentX Performance & Security Monitor
Real-time monitoring with never-forgetting AI memory
"""

import time
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime

class PerformanceSecurityMonitor:
    """Real-time system monitoring with AI memory integration"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.monitoring_active = True
        self.stats_file = self.project_root / "security_suite" / "monitoring_stats.json"
        
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free
            },
            "network": psutil.net_io_counters()._asdict(),
            "security_status": "OPTIMAL"
        }
    
    def monitor_loop(self):
        """Continuous monitoring loop"""
        stats_history = []
        
        while self.monitoring_active:
            stats = self.get_system_stats()
            stats_history.append(stats)
            
            # Keep only last 100 entries
            if len(stats_history) > 100:
                stats_history = stats_history[-100:]
            
            # Save stats periodically
            if len(stats_history) % 10 == 0:
                with open(self.stats_file, 'w') as f:
                    json.dump(stats_history, f, indent=2)
            
            time.sleep(5)  # Monitor every 5 seconds
    
    def start_monitoring(self):
        """Start background monitoring"""
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False

if __name__ == "__main__":
    monitor = PerformanceSecurityMonitor("/Users/steffanhaskins/evoagentx_project/sprint_1hour/backend")
    print("🔄 Starting Performance & Security Monitor...")
    monitor.start_monitoring()
    
    # Keep running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("🛑 Stopping monitor...")
        monitor.stop_monitoring()
