#!/usr/bin/env python3
"""
Unity Watchdog Master Service
Monitors and manages all sidecar processes with automatic recovery
"""

import asyncio
import psutil
import subprocess
import json
import time
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import redis
import logging
import socket
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("unity_watchdog")

class ServiceMonitor:
    """Monitor and manage sidecar services"""

    def __init__(self):
        self.services = {
            "ollama": {
                "port": 11434,
                "health_endpoint": "http://localhost:11434/api/tags",
                "start_cmd": ["ollama", "serve"],
                "process_name": "ollama",
                "restart_delay": 5,
                "max_restarts": 3,
                "required_models": ["deepseek-r1:14b", "qwen2.5-coder:7b"],
                "critical": True
            },
            "python_backend": {
                "port": 8000,
                "health_endpoint": "http://localhost:8000/health",
                "start_cmd": ["python3", "-m", "uvicorn", "main:app", "--port", "8000"],
                "process_name": "python",
                "restart_delay": 3,
                "max_restarts": 5,
                "critical": True
            },
            "redis": {
                "port": 6379,
                "health_check": self.check_redis,
                "start_cmd": ["redis-server"],
                "process_name": "redis-server",
                "restart_delay": 2,
                "max_restarts": 3,
                "critical": True
            },
            "vault": {
                "port": 8200,
                "health_endpoint": "http://localhost:8200/v1/sys/health",
                "start_cmd": ["vault", "server", "-config=/etc/vault/config.hcl"],
                "process_name": "vault",
                "restart_delay": 5,
                "max_restarts": 3,
                "critical": False
            }
        }

        self.restart_counts = {name: 0 for name in self.services}
        self.service_status = {}
        self.resource_limits = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90
        }
        self.last_alert_time = {}
        self.alert_cooldown = 300  # 5 minutes between alerts

    async def check_redis(self) -> bool:
        """Custom health check for Redis"""
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            return r.ping()
        except:
            return False

    async def check_port(self, port: int) -> bool:
        """Check if a port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0

    async def check_health_endpoint(self, url: str) -> bool:
        """Check service health via HTTP endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    return response.status == 200
        except:
            return False

    async def check_process(self, name: str) -> Optional[psutil.Process]:
        """Find process by name"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if name.lower() in proc.info['name'].lower() or \
                   any(name.lower() in arg.lower() for arg in (proc.info['cmdline'] or [])):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    async def restart_service(self, name: str, config: Dict) -> bool:
        """Restart a failed service"""
        if self.restart_counts[name] >= config["max_restarts"]:
            logger.error(f"Service {name} exceeded max restarts ({config['max_restarts']})")
            await self.trigger_emergency_alert(name, "MAX_RESTARTS_EXCEEDED")
            return False

        logger.info(f"Attempting to restart {name} (attempt {self.restart_counts[name] + 1})")

        # Kill existing process if running
        proc = await self.check_process(config["process_name"])
        if proc:
            logger.info(f"Killing existing {name} process (PID: {proc.pid})")
            try:
                proc.terminate()
                await asyncio.sleep(2)
                if proc.is_running():
                    proc.kill()
            except:
                pass

        # Start service
        try:
            env = os.environ.copy()
            if name == "ollama":
                env["OLLAMA_HOST"] = "0.0.0.0:11434"

            subprocess.Popen(
                config["start_cmd"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env
            )
            await asyncio.sleep(config["restart_delay"])
            self.restart_counts[name] += 1

            # Verify service started
            port_open = await self.check_port(config["port"])
            if port_open:
                logger.info(f"Successfully restarted {name}")
                return True
            else:
                logger.error(f"Failed to restart {name} - port not open")
                return False

        except Exception as e:
            logger.error(f"Failed to restart {name}: {e}")
            return False

    async def monitor_service(self, name: str, config: Dict) -> bool:
        """Monitor a single service"""
        is_healthy = False
        details = {}

        # Check port
        port_open = await self.check_port(config["port"])
        details["port_open"] = port_open

        # Check health
        if "health_endpoint" in config:
            is_healthy = await self.check_health_endpoint(config["health_endpoint"])
            details["endpoint_healthy"] = is_healthy
        elif "health_check" in config:
            is_healthy = await config["health_check"]()
            details["custom_check"] = is_healthy
        else:
            is_healthy = port_open

        # Check process
        proc = await self.check_process(config["process_name"])
        details["process_running"] = proc is not None

        if proc:
            try:
                details["cpu_percent"] = proc.cpu_percent()
                details["memory_mb"] = proc.memory_info().rss / 1024 / 1024
            except:
                pass

        self.service_status[name] = {
            "healthy": is_healthy,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "restart_count": self.restart_counts[name]
        }

        if not is_healthy:
            logger.warning(f"Service {name} is unhealthy: {details}")
            if config.get("critical", False):
                await self.restart_service(name, config)
        elif self.restart_counts[name] > 0:
            # Reset restart count on successful recovery
            logger.info(f"Service {name} recovered successfully")
            self.restart_counts[name] = 0

        return is_healthy

    async def check_ollama_models(self):
        """Verify required Ollama models are installed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags",
                                      timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        installed_models = [m['name'] for m in data.get('models', [])]

                        for required in self.services["ollama"]["required_models"]:
                            found = False
                            for model in installed_models:
                                if required.split(':')[0] in model:
                                    found = True
                                    break

                            if not found:
                                logger.warning(f"Required model {required} not found. Pulling...")
                                await self.pull_ollama_model(required)

        except Exception as e:
            logger.error(f"Failed to check Ollama models: {e}")

    async def pull_ollama_model(self, model_name: str):
        """Pull an Ollama model"""
        try:
            logger.info(f"Pulling model: {model_name}")
            proc = await asyncio.create_subprocess_exec(
                "ollama", "pull", model_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                logger.info(f"Successfully pulled model: {model_name}")
            else:
                logger.error(f"Failed to pull model {model_name}: {stderr.decode()}")

        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")

    async def monitor_resources(self) -> Dict:
        """Monitor system resources"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        alerts = []
        if cpu_percent > self.resource_limits["cpu_percent"]:
            alerts.append(f"HIGH_CPU: {cpu_percent:.1f}%")
        if memory.percent > self.resource_limits["memory_percent"]:
            alerts.append(f"HIGH_MEMORY: {memory.percent:.1f}%")
        if disk.percent > self.resource_limits["disk_percent"]:
            alerts.append(f"LOW_DISK: {disk.percent:.1f}% used")

        if alerts:
            for alert in alerts:
                # Check cooldown period
                now = time.time()
                last_alert = self.last_alert_time.get(alert, 0)
                if now - last_alert > self.alert_cooldown:
                    logger.warning(f"Resource Alert: {alert}")
                    await self.trigger_emergency_alert("RESOURCES", alert)
                    self.last_alert_time[alert] = now

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
            "load_average": os.getloadavg()
        }

    async def trigger_emergency_alert(self, service: str, reason: str):
        """Send emergency alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "reason": reason,
            "action": "AUTOMATIC_RECOVERY_FAILED",
            "host": socket.gethostname()
        }

        # Write to emergency log
        log_dir = Path("/var/log/unity")
        log_dir.mkdir(parents=True, exist_ok=True)

        with open(log_dir / "emergencies.jsonl", "a") as f:
            json.dump(alert, f)
            f.write("\n")

        # Send to Redis if available
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.publish('unity:alerts', json.dumps(alert))
        except:
            pass

        logger.critical(f"EMERGENCY: {service} - {reason}")

    async def write_status(self):
        """Write current status to file"""
        try:
            status_report = {
                "timestamp": datetime.now().isoformat(),
                "services": self.service_status,
                "resources": await self.monitor_resources(),
                "uptime": time.time() - self.start_time,
                "version": "1.0.0"
            }

            status_dir = Path("/var/run/unity")
            status_dir.mkdir(parents=True, exist_ok=True)

            with open(status_dir / "status.json", "w") as f:
                json.dump(status_report, f, indent=2)

            # Publish to Redis
            try:
                r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
                r.set('unity:status', json.dumps(status_report))
                r.expire('unity:status', 60)
            except:
                pass

        except Exception as e:
            logger.error(f"Failed to write status: {e}")

    async def run_monitor_loop(self):
        """Main monitoring loop"""
        self.start_time = time.time()
        logger.info("Unity Watchdog started")

        while True:
            try:
                # Monitor all services
                tasks = [
                    self.monitor_service(name, config)
                    for name, config in self.services.items()
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check for any exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        service_name = list(self.services.keys())[i]
                        logger.error(f"Error monitoring {service_name}: {result}")

                # Check Ollama models if Ollama is healthy
                if self.service_status.get("ollama", {}).get("healthy", False):
                    await self.check_ollama_models()

                # Monitor resources
                resources = await self.monitor_resources()

                # Write status
                await self.write_status()

                # Check for system-wide issues
                unhealthy_critical = sum(
                    1 for name, config in self.services.items()
                    if config.get("critical", False) and
                    not self.service_status.get(name, {}).get("healthy", False)
                )

                if unhealthy_critical > 2:
                    logger.critical("Multiple critical services failing - system unstable")
                    await self.trigger_emergency_alert("SYSTEM", "MULTIPLE_CRITICAL_FAILURES")

                # Sleep before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Monitor loop error: {e}", exc_info=True)
                await asyncio.sleep(5)

async def main():
    """Main entry point"""
    monitor = ServiceMonitor()

    # Handle shutdown gracefully
    loop = asyncio.get_event_loop()

    def shutdown_handler(signame):
        logger.info(f"Received {signame}, shutting down...")
        for task in asyncio.all_tasks(loop):
            task.cancel()

    import signal
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown_handler, sig.name)

    try:
        await monitor.run_monitor_loop()
    except asyncio.CancelledError:
        logger.info("Watchdog shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())