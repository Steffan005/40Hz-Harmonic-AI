#!/usr/bin/env python3
"""
Unity Emergency Control System
Implements kill switch, trading halt, memory purge, and system reset capabilities
"""

import asyncio
import psutil
import subprocess
import shutil
import json
import os
import socket
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import redis
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("emergency_systems")

class EmergencyController:
    """Emergency control systems for Unity"""

    def __init__(self):
        self.emergency_log = []
        self.kill_switch_armed = True
        self.trading_halted = False
        self.emergency_mode = False
        self.authorized_users = ["admin", "operator", "emergency"]
        self.log_dir = Path("/var/log/unity")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def verify_authorization(self, auth_token: str) -> bool:
        """Verify authorization for emergency actions"""
        # In production, implement proper auth verification
        # For now, check against authorized list
        return auth_token in self.authorized_users

    async def kill_switch(self, authorization: str = None) -> Dict:
        """Execute emergency kill switch - IMMEDIATE SHUTDOWN"""

        if not self.kill_switch_armed:
            return {"error": "Kill switch is not armed", "status": "FAILED"}

        logger.critical("KILL SWITCH ACTIVATED - EMERGENCY SHUTDOWN INITIATED")

        # Log the action
        self.log_emergency("KILL_SWITCH", "ACTIVATED", {
            "authorization": authorization,
            "timestamp": datetime.now().isoformat()
        })

        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "EXECUTING",
            "steps": []
        }

        # Step 1: Send emergency stop signal to all services
        logger.info("Step 1: Broadcasting emergency stop signal...")
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.publish('unity:emergency', json.dumps({
                "command": "EMERGENCY_STOP",
                "timestamp": datetime.now().isoformat()
            }))
            results["steps"].append("Emergency signal broadcast")
        except Exception as e:
            logger.error(f"Failed to broadcast emergency signal: {e}")

        # Step 2: Halt all trading operations immediately
        logger.info("Step 2: Halting trading operations...")
        trading_result = await self.halt_trading(emergency=True)
        results["steps"].append(f"Trading halt: {trading_result['status']}")

        # Step 3: Kill all Unity-related processes
        logger.info("Step 3: Terminating all processes...")
        processes_to_kill = [
            "ollama", "python3", "uvicorn", "node", "redis-server",
            "vault", "unity", "orchestrator", "tauri"
        ]

        killed_processes = []
        for proc_name in processes_to_kill:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if proc_name.lower() in proc_info['name'].lower() or \
                       any(proc_name.lower() in str(arg).lower()
                           for arg in (proc_info.get('cmdline') or [])):

                        # Send SIGTERM first
                        proc.terminate()
                        killed_processes.append({
                            "name": proc_info['name'],
                            "pid": proc_info['pid'],
                            "signal": "SIGTERM"
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        # Wait 2 seconds for graceful shutdown
        await asyncio.sleep(2)

        # Force kill any remaining processes
        for proc_name in processes_to_kill:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc_name.lower() in proc.info['name'].lower():
                        proc.kill()
                        killed_processes.append({
                            "name": proc.info['name'],
                            "pid": proc.info['pid'],
                            "signal": "SIGKILL"
                        })
                except:
                    pass

        results["killed_processes"] = killed_processes
        results["steps"].append(f"Terminated {len(killed_processes)} processes")

        # Step 4: Clear all caches and temporary data
        logger.info("Step 4: Clearing caches and temporary data...")
        purge_result = await self.purge_memory(emergency=True)
        results["steps"].append(f"Memory purge: {purge_result['status']}")

        # Step 5: Create emergency shutdown marker
        logger.info("Step 5: Creating shutdown marker...")
        shutdown_marker = Path("/etc/unity/EMERGENCY_SHUTDOWN")
        shutdown_marker.parent.mkdir(parents=True, exist_ok=True)
        with open(shutdown_marker, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "authorization": authorization,
                "reason": "KILL_SWITCH_ACTIVATED"
            }, f)
        results["steps"].append("Shutdown marker created")

        # Step 6: Disable auto-restart
        logger.info("Step 6: Disabling auto-restart...")
        try:
            subprocess.run(["systemctl", "stop", "unity-watchdog"], check=False)
            subprocess.run(["systemctl", "disable", "unity-watchdog"], check=False)
            results["steps"].append("Auto-restart disabled")
        except:
            pass

        results["status"] = "KILLED"
        logger.critical("KILL SWITCH EXECUTION COMPLETE - SYSTEM TERMINATED")

        return results

    async def halt_trading(self, emergency: bool = False) -> Dict:
        """Halt all trading operations"""
        logger.warning(f"HALTING ALL TRADING OPERATIONS (Emergency: {emergency})")
        self.trading_halted = True

        halt_file = Path("/var/run/unity_trading_halt")

        # Create halt marker
        with open(halt_file, "w") as f:
            json.dump({
                "status": "HALTED",
                "emergency": emergency,
                "timestamp": datetime.now().isoformat()
            }, f)

        # Send halt signal via Redis
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.publish('trading_control', json.dumps({
                "command": "HALT",
                "emergency": emergency,
                "timestamp": datetime.now().isoformat()
            }))

            # Set persistent halt flag
            r.set('unity:trading:halted', 'true')
        except Exception as e:
            logger.error(f"Failed to send halt signal: {e}")

        # Kill trading-specific processes if emergency
        if emergency:
            trading_processes = ["trader", "portfolio", "exchange"]
            for proc_name in trading_processes:
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc_name in proc.info['name'].lower():
                            proc.kill()
                    except:
                        pass

        self.log_emergency("TRADING_HALT", "ACTIVATED", {"emergency": emergency})

        return {
            "status": "HALTED",
            "emergency": emergency,
            "timestamp": datetime.now().isoformat()
        }

    async def resume_trading(self, authorization: str) -> Dict:
        """Resume trading operations"""
        if not self.verify_authorization(authorization):
            return {"error": "Unauthorized", "status": "FAILED"}

        logger.info("RESUMING TRADING OPERATIONS")
        self.trading_halted = False

        # Remove halt marker
        halt_file = Path("/var/run/unity_trading_halt")
        if halt_file.exists():
            halt_file.unlink()

        # Send resume signal
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.publish('trading_control', json.dumps({
                "command": "RESUME",
                "timestamp": datetime.now().isoformat(),
                "authorized_by": authorization
            }))
            r.delete('unity:trading:halted')
        except:
            pass

        self.log_emergency("TRADING_RESUME", "ACTIVATED", {"authorization": authorization})

        return {
            "status": "RESUMED",
            "timestamp": datetime.now().isoformat(),
            "authorized_by": authorization
        }

    async def purge_memory(self, emergency: bool = False) -> Dict:
        """Purge system memory and caches"""
        logger.warning(f"PURGING SYSTEM MEMORY (Emergency: {emergency})")

        purged_items = []
        errors = []

        # 1. Clear Redis cache
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.flushall()
            purged_items.append("Redis cache (all databases)")
        except Exception as e:
            errors.append(f"Redis: {str(e)}")

        # 2. Clear Unity temporary directories
        temp_dirs = [
            "/tmp/unity*",
            "/var/tmp/unity*",
            "/var/cache/unity",
            "/tmp/orchestrator*"
        ]

        import glob
        for pattern in temp_dirs:
            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    purged_items.append(path)
                except Exception as e:
                    errors.append(f"{path}: {str(e)}")

        # 3. Clear Python cache
        try:
            import gc
            collected = gc.collect()
            purged_items.append(f"Python garbage collection ({collected} objects)")
        except:
            pass

        # 4. Clear system caches (Linux)
        if os.name == 'posix':
            try:
                # Drop caches
                subprocess.run(["sync"], check=False)
                # Note: This requires root privileges
                # subprocess.run(["echo", "3", ">", "/proc/sys/vm/drop_caches"], shell=True)
                purged_items.append("System sync completed")
            except:
                pass

        # 5. If emergency, also clear logs and persistent data
        if emergency:
            emergency_clear = [
                "/var/log/unity/*.log",
                "/var/lib/unity/cache/*",
                "/home/*/unity/temp/*"
            ]

            for pattern in emergency_clear:
                for path in glob.glob(pattern):
                    try:
                        if os.path.isfile(path):
                            # Truncate log files instead of deleting
                            with open(path, "w") as f:
                                f.write("")
                            purged_items.append(f"{path} (truncated)")
                        elif os.path.isdir(path):
                            shutil.rmtree(path)
                            purged_items.append(f"{path} (removed)")
                    except Exception as e:
                        errors.append(f"{path}: {str(e)}")

        self.log_emergency("MEMORY_PURGE", "COMPLETED", {
            "emergency": emergency,
            "items_purged": len(purged_items)
        })

        return {
            "status": "PURGED",
            "items_cleared": purged_items,
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
            "emergency": emergency
        }

    async def system_reset(self, level: str = "soft", authorization: str = None) -> Dict:
        """Reset system to default state"""

        valid_levels = ["soft", "hard", "factory"]
        if level not in valid_levels:
            return {"error": f"Invalid reset level. Must be one of: {valid_levels}"}

        if level in ["hard", "factory"] and not self.verify_authorization(authorization):
            return {"error": "Authorization required for hard/factory reset"}

        logger.warning(f"SYSTEM RESET INITIATED (Level: {level})")
        reset_actions = []
        errors = []

        if level == "soft":
            # Soft reset - restart services only
            logger.info("Performing soft reset...")

            services = ["unity-watchdog", "unity-models", "unity-emergency"]
            for service in services:
                try:
                    result = subprocess.run(
                        ["systemctl", "restart", service],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        reset_actions.append(f"Restarted {service}")
                    else:
                        errors.append(f"Failed to restart {service}: {result.stderr}")
                except Exception as e:
                    errors.append(f"{service}: {str(e)}")

            # Clear temporary issues
            await self.purge_memory(emergency=False)
            reset_actions.append("Cleared temporary data")

        elif level == "hard":
            # Hard reset - kill everything and restart
            logger.info("Performing hard reset...")

            # Execute kill switch
            kill_result = await self.kill_switch(authorization)
            reset_actions.append("Executed kill switch")

            # Wait for processes to die
            await asyncio.sleep(5)

            # Remove shutdown marker to allow restart
            shutdown_marker = Path("/etc/unity/EMERGENCY_SHUTDOWN")
            if shutdown_marker.exists():
                shutdown_marker.unlink()
                reset_actions.append("Removed shutdown marker")

            # Restart core services
            startup_script = Path("/usr/local/bin/unity_startup.sh")
            if startup_script.exists():
                try:
                    subprocess.Popen([str(startup_script)])
                    reset_actions.append("Executed startup script")
                except Exception as e:
                    errors.append(f"Startup script: {str(e)}")

        elif level == "factory":
            # Factory reset - complete wipe and reinstall
            logger.critical("FACTORY RESET - ALL DATA WILL BE LOST")

            # Execute kill switch first
            await self.kill_switch(authorization)
            reset_actions.append("System terminated")

            # Remove all Unity data and configs
            unity_dirs = [
                "/etc/unity",
                "/var/lib/unity",
                "/var/log/unity",
                "/var/cache/unity",
                "/opt/unity/data"
            ]

            for directory in unity_dirs:
                if os.path.exists(directory):
                    try:
                        shutil.rmtree(directory)
                        reset_actions.append(f"Removed {directory}")
                    except Exception as e:
                        errors.append(f"{directory}: {str(e)}")

            # Recreate default structure
            for directory in unity_dirs:
                try:
                    Path(directory).mkdir(parents=True, exist_ok=True)
                    reset_actions.append(f"Created {directory}")
                except Exception as e:
                    errors.append(f"Create {directory}: {str(e)}")

            # Create default config
            default_config = {
                "version": "1.0.0",
                "mode": "default",
                "created": datetime.now().isoformat(),
                "reset_from": "factory"
            }

            config_path = Path("/etc/unity/config.json")
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            reset_actions.append("Created default configuration")

        self.log_emergency("SYSTEM_RESET", level.upper(), {
            "actions": reset_actions,
            "errors": errors,
            "authorization": authorization
        })

        return {
            "status": "RESET_COMPLETE",
            "level": level,
            "actions": reset_actions,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }

    def log_emergency(self, event_type: str, action: str, details: Dict):
        """Log emergency events"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "action": action,
            "details": details,
            "host": socket.gethostname(),
            "pid": os.getpid()
        }

        self.emergency_log.append(entry)

        # Write to persistent log
        log_file = self.log_dir / "emergency.jsonl"
        with open(log_file, "a") as f:
            json.dump(entry, f)
            f.write("\n")

        # Send to monitoring
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.publish('unity:emergency_events', json.dumps(entry))

            # Also store in sorted set for history
            r.zadd('unity:emergency_history',
                   {json.dumps(entry): datetime.now().timestamp()})
        except:
            pass

    async def check_safety_conditions(self) -> Dict:
        """Check if it's safe to operate"""
        safety_checks = {
            "memory_available": True,
            "cpu_available": True,
            "disk_space": True,
            "critical_services": True,
            "no_emergency_marker": True
        }

        warnings = []

        # Check for emergency shutdown marker
        if Path("/etc/unity/EMERGENCY_SHUTDOWN").exists():
            safety_checks["no_emergency_marker"] = False
            warnings.append("Emergency shutdown marker present")

        # Check memory
        mem = psutil.virtual_memory()
        if mem.percent > 95:
            safety_checks["memory_available"] = False
            warnings.append(f"Critical memory usage: {mem.percent:.1f}%")
        elif mem.percent > 85:
            warnings.append(f"High memory usage: {mem.percent:.1f}%")

        # Check CPU
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 95:
            safety_checks["cpu_available"] = False
            warnings.append(f"Critical CPU usage: {cpu:.1f}%")
        elif cpu > 80:
            warnings.append(f"High CPU usage: {cpu:.1f}%")

        # Check disk
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            safety_checks["disk_space"] = False
            warnings.append(f"Critical disk usage: {disk.percent:.1f}%")
        elif disk.percent > 85:
            warnings.append(f"High disk usage: {disk.percent:.1f}%")

        # Check critical services
        critical_ports = {
            "ollama": 11434,
            "redis": 6379,
            "backend": 8000
        }

        for service, port in critical_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result != 0:
                safety_checks["critical_services"] = False
                warnings.append(f"Service {service} not responding on port {port}")

        all_safe = all(safety_checks.values())

        return {
            "safe_to_operate": all_safe,
            "checks": safety_checks,
            "warnings": warnings,
            "resources": {
                "cpu_percent": cpu,
                "memory_percent": mem.percent,
                "disk_percent": disk.percent
            },
            "timestamp": datetime.now().isoformat()
        }

    async def arm_kill_switch(self, arm: bool = True) -> Dict:
        """Arm or disarm the kill switch"""
        self.kill_switch_armed = arm
        status = "ARMED" if arm else "DISARMED"

        logger.warning(f"Kill switch {status}")
        self.log_emergency("KILL_SWITCH_STATUS", status, {"armed": arm})

        return {
            "status": status,
            "armed": self.kill_switch_armed,
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main entry point for emergency controller"""
    controller = EmergencyController()

    # Setup FastAPI for REST API
    from fastapi import FastAPI, HTTPException, Body
    from fastapi.responses import JSONResponse
    import uvicorn

    app = FastAPI(title="Unity Emergency Controller")

    @app.post("/emergency/kill-switch")
    async def kill_switch(authorization: str = Body(None)):
        """Execute emergency kill switch"""
        return await controller.kill_switch(authorization)

    @app.post("/emergency/halt-trading")
    async def halt_trading():
        """Halt all trading operations"""
        return await controller.halt_trading()

    @app.post("/emergency/resume-trading")
    async def resume_trading(authorization: str = Body(...)):
        """Resume trading operations"""
        return await controller.resume_trading(authorization)

    @app.post("/emergency/purge-memory")
    async def purge_memory(emergency: bool = Body(False)):
        """Purge system memory"""
        return await controller.purge_memory(emergency)

    @app.post("/emergency/system-reset")
    async def system_reset(level: str = Body("soft"), authorization: str = Body(None)):
        """Reset system"""
        return await controller.system_reset(level, authorization)

    @app.get("/emergency/safety-check")
    async def safety_check():
        """Check system safety conditions"""
        result = await controller.check_safety_conditions()
        if not result["safe_to_operate"]:
            raise HTTPException(status_code=503, detail=result)
        return result

    @app.post("/emergency/arm-kill-switch")
    async def arm_kill_switch(arm: bool = Body(True)):
        """Arm or disarm kill switch"""
        return await controller.arm_kill_switch(arm)

    @app.get("/emergency/status")
    async def emergency_status():
        """Get emergency system status"""
        return {
            "kill_switch_armed": controller.kill_switch_armed,
            "trading_halted": controller.trading_halted,
            "emergency_mode": controller.emergency_mode,
            "recent_events": controller.emergency_log[-10:],
            "timestamp": datetime.now().isoformat()
        }

    # Run the server
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())