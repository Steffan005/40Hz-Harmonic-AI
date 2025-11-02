# Unity Local Systems Orchestrator Implementation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                 Unity Orchestrator Core                  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Watchdog │  │  Model   │  │  Token   │  │Emergency│ │
│  │  System  │  │ Manager  │  │  Handler │  │ Systems │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
├─────────────────────────────────────────────────────────┤
│                    Sidecar Services                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Ollama  │  │  Python  │  │  Redis   │  │  Vault │ │
│  │  :11434  │  │  Backend │  │  :6379   │  │  :8200 │ │
│  │          │  │  :8000   │  │          │  │        │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 1. Watchdog Scripts Implementation

### 1.1 Master Watchdog Service
```python
#!/usr/bin/env python3
# watchdog_master.py

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

logging.basicConfig(level=logging.INFO)
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
                "required_models": ["deepseek-r1:14b", "qwen2.5-coder:7b"]
            },
            "python_backend": {
                "port": 8000,
                "health_endpoint": "http://localhost:8000/health",
                "start_cmd": ["python", "-m", "uvicorn", "main:app", "--port", "8000"],
                "process_name": "python",
                "restart_delay": 3,
                "max_restarts": 5
            },
            "redis": {
                "port": 6379,
                "health_check": self.check_redis,
                "start_cmd": ["redis-server"],
                "process_name": "redis-server",
                "restart_delay": 2,
                "max_restarts": 3
            },
            "vault": {
                "port": 8200,
                "health_endpoint": "http://localhost:8200/v1/sys/health",
                "start_cmd": ["vault", "server", "-config=/etc/vault/config.hcl"],
                "process_name": "vault",
                "restart_delay": 5,
                "max_restarts": 3
            }
        }
        self.restart_counts = {name: 0 for name in self.services}
        self.service_status = {}
        self.resource_limits = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90
        }

    async def check_redis(self) -> bool:
        """Custom health check for Redis"""
        try:
            r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            return r.ping()
        except:
            return False

    async def check_port(self, port: int) -> bool:
        """Check if a port is open"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0

    async def check_health_endpoint(self, url: str) -> bool:
        """Check service health via HTTP endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=3) as response:
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

    async def restart_service(self, name: str, config: Dict):
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
            proc.terminate()
            await asyncio.sleep(2)
            if proc.is_running():
                proc.kill()

        # Start service
        try:
            subprocess.Popen(config["start_cmd"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            await asyncio.sleep(config["restart_delay"])
            self.restart_counts[name] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to restart {name}: {e}")
            return False

    async def monitor_service(self, name: str, config: Dict):
        """Monitor a single service"""
        is_healthy = False

        # Check port
        port_open = await self.check_port(config["port"])

        # Check health
        if "health_endpoint" in config:
            is_healthy = await self.check_health_endpoint(config["health_endpoint"])
        elif "health_check" in config:
            is_healthy = await config["health_check"]()
        else:
            is_healthy = port_open

        self.service_status[name] = {
            "healthy": is_healthy,
            "port_open": port_open,
            "timestamp": datetime.now().isoformat(),
            "restart_count": self.restart_counts[name]
        }

        if not is_healthy:
            logger.warning(f"Service {name} is unhealthy")
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
                async with session.get("http://localhost:11434/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        installed_models = [m['name'] for m in data.get('models', [])]

                        for required in self.services["ollama"]["required_models"]:
                            if not any(required in model for model in installed_models):
                                logger.warning(f"Required model {required} not found. Pulling...")
                                await self.pull_ollama_model(required)
        except Exception as e:
            logger.error(f"Failed to check Ollama models: {e}")

    async def pull_ollama_model(self, model_name: str):
        """Pull an Ollama model"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ollama", "pull", model_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            logger.info(f"Successfully pulled model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")

    async def monitor_resources(self):
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
                logger.warning(f"Resource Alert: {alert}")
                await self.trigger_emergency_alert("RESOURCES", alert)

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3)
        }

    async def trigger_emergency_alert(self, service: str, reason: str):
        """Send emergency alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "reason": reason,
            "action": "AUTOMATIC_RECOVERY_FAILED"
        }

        # Write to emergency log
        with open("/var/log/unity_emergencies.json", "a") as f:
            json.dump(alert, f)
            f.write("\n")

        # Trigger notification (implement based on your notification system)
        logger.critical(f"EMERGENCY: {service} - {reason}")

    async def run_monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                # Monitor all services
                tasks = [
                    self.monitor_service(name, config)
                    for name, config in self.services.items()
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check Ollama models if Ollama is healthy
                if self.service_status.get("ollama", {}).get("healthy", False):
                    await self.check_ollama_models()

                # Monitor resources
                resources = await self.monitor_resources()

                # Write status to file
                status_report = {
                    "timestamp": datetime.now().isoformat(),
                    "services": self.service_status,
                    "resources": resources
                }

                with open("/var/log/unity_status.json", "w") as f:
                    json.dump(status_report, f, indent=2)

                # Sleep before next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    monitor = ServiceMonitor()
    asyncio.run(monitor.run_monitor_loop())
```

### 1.2 Health Check Endpoints
```python
# health_checks.py

from fastapi import FastAPI, HTTPException
from typing import Dict
import psutil
import aiohttp
import redis
import asyncio

app = FastAPI()

@app.get("/health")
async def health_check() -> Dict:
    """Comprehensive health check endpoint"""

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {},
        "resources": {}
    }

    # Check Ollama
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=2) as resp:
                health_status["services"]["ollama"] = resp.status == 200
    except:
        health_status["services"]["ollama"] = False
        health_status["status"] = "degraded"

    # Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
        health_status["services"]["redis"] = r.ping()
    except:
        health_status["services"]["redis"] = False
        health_status["status"] = "degraded"

    # Check Python Backend
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health", timeout=2) as resp:
                health_status["services"]["python_backend"] = resp.status == 200
    except:
        health_status["services"]["python_backend"] = False
        health_status["status"] = "degraded"

    # Check Resources
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    health_status["resources"] = {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "disk_percent": disk.percent
    }

    if cpu > 90 or mem.percent > 90 or disk.percent > 95:
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

@app.get("/health/liveness")
async def liveness() -> Dict:
    """Simple liveness check"""
    return {"status": "alive"}

@app.get("/health/readiness")
async def readiness() -> Dict:
    """Readiness check for load balancing"""
    # Check if all critical services are running
    critical_services = ["ollama", "redis"]
    ready = True
    details = {}

    for service in critical_services:
        if service == "ollama":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:11434/api/tags", timeout=1) as resp:
                        details[service] = resp.status == 200
            except:
                details[service] = False
                ready = False
        elif service == "redis":
            try:
                r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
                details[service] = r.ping()
            except:
                details[service] = False
                ready = False

    if not ready:
        raise HTTPException(status_code=503, detail={"ready": False, "services": details})

    return {"ready": True, "services": details}
```

## 2. Model Management System

### 2.1 Model Manager
```python
# model_manager.py

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger("model_manager")

class ModelManager:
    """Manage Ollama models and fallback chains"""

    def __init__(self):
        self.models = {
            "primary": {
                "deepseek-r1:14b": {
                    "type": "reasoning",
                    "context_length": 32768,
                    "priority": 1,
                    "fallback": "qwen2.5-coder:7b"
                },
                "qwen2.5-coder:7b": {
                    "type": "coding",
                    "context_length": 32768,
                    "priority": 2,
                    "fallback": "llama3.2:3b"
                }
            },
            "fallback": {
                "llama3.2:3b": {
                    "type": "general",
                    "context_length": 8192,
                    "priority": 3,
                    "fallback": None
                }
            }
        }
        self.model_stats = {}
        self.ollama_base = "http://localhost:11434"

    async def verify_model(self, model_name: str) -> bool:
        """Verify a model is installed and responsive"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if model exists
                async with session.get(f"{self.ollama_base}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m['name'] for m in data.get('models', [])]
                        if not any(model_name in m for m in models):
                            logger.warning(f"Model {model_name} not found")
                            return False

                # Test model with simple prompt
                test_prompt = {"model": model_name, "prompt": "test", "stream": False}
                async with session.post(
                    f"{self.ollama_base}/api/generate",
                    json=test_prompt,
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Model {model_name} verified successfully")
                        return True

        except Exception as e:
            logger.error(f"Failed to verify model {model_name}: {e}")

        return False

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            async with aiohttp.ClientSession() as session:
                pull_data = {"name": model_name, "stream": False}
                async with session.post(
                    f"{self.ollama_base}/api/pull",
                    json=pull_data,
                    timeout=3600  # 1 hour timeout for large models
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Successfully pulled model: {model_name}")
                        return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")

        return False

    async def measure_response_time(self, model_name: str) -> Optional[float]:
        """Measure model response time"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                test_data = {
                    "model": model_name,
                    "prompt": "What is 2+2?",
                    "stream": False,
                    "options": {"num_predict": 10}
                }
                async with session.post(
                    f"{self.ollama_base}/api/generate",
                    json=test_data,
                    timeout=30
                ) as resp:
                    if resp.status == 200:
                        response_time = time.time() - start_time
                        return response_time
        except:
            pass
        return None

    async def get_best_available_model(self, model_type: str = None) -> Optional[str]:
        """Get the best available model based on type and performance"""
        available_models = []

        for category in ["primary", "fallback"]:
            for model_name, config in self.models[category].items():
                if model_type and config["type"] != model_type:
                    continue

                if await self.verify_model(model_name):
                    response_time = await self.measure_response_time(model_name)
                    if response_time:
                        available_models.append({
                            "name": model_name,
                            "priority": config["priority"],
                            "response_time": response_time
                        })

        if not available_models:
            return None

        # Sort by priority, then by response time
        available_models.sort(key=lambda x: (x["priority"], x["response_time"]))
        return available_models[0]["name"]

    async def implement_fallback_chain(self, primary_model: str, prompt: str) -> Optional[Dict]:
        """Implement fallback chain for model failures"""
        current_model = primary_model
        attempts = 0
        max_attempts = 3

        while current_model and attempts < max_attempts:
            try:
                async with aiohttp.ClientSession() as session:
                    data = {
                        "model": current_model,
                        "prompt": prompt,
                        "stream": False
                    }
                    async with session.post(
                        f"{self.ollama_base}/api/generate",
                        json=data,
                        timeout=60
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            result["model_used"] = current_model
                            result["fallback_level"] = attempts
                            return result
            except Exception as e:
                logger.warning(f"Model {current_model} failed: {e}")

            # Get fallback model
            for category in ["primary", "fallback"]:
                if current_model in self.models[category]:
                    current_model = self.models[category][current_model].get("fallback")
                    break

            attempts += 1

        return None

    async def monitor_models(self):
        """Continuously monitor model health and performance"""
        while True:
            try:
                stats = {}

                for category in ["primary", "fallback"]:
                    for model_name in self.models[category]:
                        is_available = await self.verify_model(model_name)
                        response_time = None

                        if is_available:
                            response_time = await self.measure_response_time(model_name)

                        stats[model_name] = {
                            "available": is_available,
                            "response_time": response_time,
                            "timestamp": datetime.now().isoformat()
                        }

                self.model_stats = stats

                # Write stats to file
                with open("/var/log/model_stats.json", "w") as f:
                    json.dump(stats, f, indent=2)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Model monitoring error: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    manager = ModelManager()
    asyncio.run(manager.monitor_models())
```

## 3. Token Expiration Handler

### 3.1 Token Manager with Vault Integration
```python
# token_manager.py

import asyncio
import aiohttp
import hvac
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import jwt

logger = logging.getLogger("token_manager")

class TokenManager:
    """Handle API tokens with automatic rotation and fallback"""

    def __init__(self, vault_url: str = "http://localhost:8200"):
        self.vault_url = vault_url
        self.vault_client = None
        self.tokens = {}
        self.token_expiry = {}
        self.fallback_mode = False
        self.rotation_threshold = 300  # Rotate 5 minutes before expiry

    async def initialize_vault(self, vault_token: str):
        """Initialize Vault connection"""
        self.vault_client = hvac.Client(
            url=self.vault_url,
            token=vault_token
        )

        if not self.vault_client.is_authenticated():
            logger.error("Failed to authenticate with Vault")
            return False

        logger.info("Successfully connected to Vault")
        return True

    async def store_token(self, service: str, token: str, expiry: datetime):
        """Store token in Vault with expiry"""
        if self.vault_client:
            try:
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=f"tokens/{service}",
                    secret={
                        "token": token,
                        "expiry": expiry.isoformat(),
                        "created": datetime.now().isoformat()
                    }
                )
                self.tokens[service] = token
                self.token_expiry[service] = expiry
                logger.info(f"Stored token for {service}, expires: {expiry}")
                return True
            except Exception as e:
                logger.error(f"Failed to store token: {e}")
        return False

    async def retrieve_token(self, service: str) -> Optional[str]:
        """Retrieve token from Vault"""
        if self.vault_client:
            try:
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path=f"tokens/{service}"
                )
                data = response['data']['data']

                expiry = datetime.fromisoformat(data['expiry'])
                if datetime.now() < expiry:
                    self.tokens[service] = data['token']
                    self.token_expiry[service] = expiry
                    return data['token']
                else:
                    logger.warning(f"Token for {service} has expired")

            except Exception as e:
                logger.error(f"Failed to retrieve token: {e}")

        return None

    async def check_token_expiry(self, service: str) -> bool:
        """Check if token is about to expire"""
        if service not in self.token_expiry:
            return True  # Needs renewal if not found

        time_to_expiry = (self.token_expiry[service] - datetime.now()).total_seconds()
        return time_to_expiry <= self.rotation_threshold

    async def rotate_token(self, service: str) -> bool:
        """Rotate an expiring token"""
        logger.info(f"Rotating token for {service}")

        # Service-specific rotation logic
        rotation_handlers = {
            "anthropic": self.rotate_anthropic_token,
            "openai": self.rotate_openai_token,
            "github": self.rotate_github_token
        }

        handler = rotation_handlers.get(service)
        if handler:
            new_token = await handler()
            if new_token:
                expiry = datetime.now() + timedelta(days=30)  # Default 30 day expiry
                return await self.store_token(service, new_token, expiry)

        return False

    async def rotate_anthropic_token(self) -> Optional[str]:
        """Rotate Anthropic API token"""
        # Implement actual rotation logic with Anthropic API
        # This is a placeholder
        logger.warning("Anthropic token rotation not implemented - switching to fallback")
        return None

    async def rotate_openai_token(self) -> Optional[str]:
        """Rotate OpenAI API token"""
        # Implement actual rotation logic
        logger.warning("OpenAI token rotation not implemented")
        return None

    async def rotate_github_token(self) -> Optional[str]:
        """Rotate GitHub token"""
        # Implement actual rotation logic
        logger.warning("GitHub token rotation not implemented")
        return None

    async def detect_token_exhaustion(self, service: str, error_response: Dict) -> bool:
        """Detect if API error indicates token exhaustion"""
        exhaustion_indicators = [
            "rate limit",
            "quota exceeded",
            "token expired",
            "authentication failed",
            "unauthorized",
            "insufficient credits"
        ]

        error_msg = str(error_response).lower()
        return any(indicator in error_msg for indicator in exhaustion_indicators)

    async def enable_fallback_mode(self):
        """Enable fallback to local models"""
        logger.warning("Enabling fallback mode - switching to local models")
        self.fallback_mode = True

        # Notify other services
        notification = {
            "event": "FALLBACK_MODE_ENABLED",
            "timestamp": datetime.now().isoformat(),
            "reason": "Token exhaustion detected"
        }

        # Send notification via Redis pub/sub
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379)
            r.publish('unity_events', json.dumps(notification))
        except:
            pass

        # Update system config
        with open("/etc/unity/fallback_mode.json", "w") as f:
            json.dump({"enabled": True, "timestamp": datetime.now().isoformat()}, f)

    async def monitor_tokens(self):
        """Monitor and rotate tokens proactively"""
        while True:
            try:
                for service in list(self.tokens.keys()):
                    if await self.check_token_expiry(service):
                        success = await self.rotate_token(service)
                        if not success and service == "anthropic":
                            await self.enable_fallback_mode()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Token monitoring error: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    manager = TokenManager()
    # Initialize with Vault token from environment or config
    asyncio.run(manager.monitor_tokens())
```

## 4. Telemetry Dashboard

### 4.1 Unified Orchestrator Dashboard
```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Unity Orchestrator Dashboard</title>
    <style>
        body {
            font-family: 'Monaco', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        .panel {
            border: 1px solid #00ff00;
            padding: 15px;
            background: #0d0d0d;
        }
        .critical { color: #ff0000; }
        .warning { color: #ffaa00; }
        .healthy { color: #00ff00; }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        #emergency-panel {
            background: #1a0000;
            border-color: #ff0000;
        }
        .chart-container {
            height: 200px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>Unity Local Systems Orchestrator</h1>

    <div class="grid">
        <!-- Service Status Panel -->
        <div class="panel">
            <h2>Service Status</h2>
            <div id="services">
                <div class="metric">
                    <span>Ollama</span>
                    <span id="ollama-status" class="healthy">●</span>
                </div>
                <div class="metric">
                    <span>Python Backend</span>
                    <span id="backend-status" class="healthy">●</span>
                </div>
                <div class="metric">
                    <span>Redis</span>
                    <span id="redis-status" class="healthy">●</span>
                </div>
                <div class="metric">
                    <span>Vault</span>
                    <span id="vault-status" class="healthy">●</span>
                </div>
            </div>
        </div>

        <!-- Model Status Panel -->
        <div class="panel">
            <h2>Model Status</h2>
            <div id="models">
                <div class="metric">
                    <span>DeepSeek-R1:14B</span>
                    <span id="deepseek-status">Loading...</span>
                </div>
                <div class="metric">
                    <span>Qwen-2.5-Coder:7B</span>
                    <span id="qwen-status">Loading...</span>
                </div>
                <div class="metric">
                    <span>Active Model</span>
                    <span id="active-model">None</span>
                </div>
                <div class="metric">
                    <span>Fallback Mode</span>
                    <span id="fallback-mode" class="healthy">Disabled</span>
                </div>
            </div>
        </div>

        <!-- Resource Monitor Panel -->
        <div class="panel">
            <h2>System Resources</h2>
            <div id="resources">
                <div class="metric">
                    <span>CPU Usage</span>
                    <span id="cpu-usage">0%</span>
                </div>
                <div class="metric">
                    <span>Memory Usage</span>
                    <span id="memory-usage">0%</span>
                </div>
                <div class="metric">
                    <span>Disk Usage</span>
                    <span id="disk-usage">0%</span>
                </div>
                <div class="chart-container">
                    <canvas id="resource-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Token Status Panel -->
        <div class="panel">
            <h2>Token Management</h2>
            <div id="tokens">
                <div class="metric">
                    <span>Anthropic</span>
                    <span id="anthropic-token">Valid</span>
                </div>
                <div class="metric">
                    <span>Token Rotations</span>
                    <span id="rotation-count">0</span>
                </div>
                <div class="metric">
                    <span>Next Rotation</span>
                    <span id="next-rotation">--:--</span>
                </div>
            </div>
        </div>

        <!-- Evolution Metrics Panel -->
        <div class="panel">
            <h2>Evolution Metrics</h2>
            <div id="evolution">
                <div class="metric">
                    <span>Memory Growth</span>
                    <span id="memory-growth">0 KB/s</span>
                </div>
                <div class="metric">
                    <span>Active Offices</span>
                    <span id="active-offices">0</span>
                </div>
                <div class="metric">
                    <span>Task Queue</span>
                    <span id="task-queue">0</span>
                </div>
                <div class="chart-container">
                    <canvas id="evolution-chart"></canvas>
                </div>
            </div>
        </div>

        <!-- Emergency Controls Panel -->
        <div class="panel" id="emergency-panel">
            <h2>Emergency Controls</h2>
            <button onclick="killSwitch()" style="background: #ff0000; color: white; padding: 10px; margin: 5px;">
                KILL SWITCH
            </button>
            <button onclick="haltTrading()" style="background: #ff6600; color: white; padding: 10px; margin: 5px;">
                HALT TRADING
            </button>
            <button onclick="purgeMemory()" style="background: #ffaa00; color: black; padding: 10px; margin: 5px;">
                PURGE MEMORY
            </button>
            <button onclick="systemReset()" style="background: #0066ff; color: white; padding: 10px; margin: 5px;">
                SYSTEM RESET
            </button>
            <div id="emergency-log" style="margin-top: 10px; max-height: 150px; overflow-y: auto;">
                <!-- Emergency events will be logged here -->
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:8001/telemetry/stream');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        function updateDashboard(data) {
            // Update service status
            if (data.services) {
                for (const [service, status] of Object.entries(data.services)) {
                    const element = document.getElementById(`${service}-status`);
                    if (element) {
                        element.className = status.healthy ? 'healthy' : 'critical';
                        element.textContent = status.healthy ? '●' : '○';
                    }
                }
            }

            // Update resource metrics
            if (data.resources) {
                document.getElementById('cpu-usage').textContent = `${data.resources.cpu_percent.toFixed(1)}%`;
                document.getElementById('memory-usage').textContent = `${data.resources.memory_percent.toFixed(1)}%`;
                document.getElementById('disk-usage').textContent = `${data.resources.disk_percent.toFixed(1)}%`;

                // Update color based on thresholds
                if (data.resources.cpu_percent > 80) {
                    document.getElementById('cpu-usage').className = 'critical';
                } else if (data.resources.cpu_percent > 60) {
                    document.getElementById('cpu-usage').className = 'warning';
                } else {
                    document.getElementById('cpu-usage').className = 'healthy';
                }
            }

            // Update model status
            if (data.models) {
                for (const [model, info] of Object.entries(data.models)) {
                    const element = document.getElementById(`${model.split('-')[0]}-status`);
                    if (element) {
                        element.textContent = info.available ?
                            `Ready (${info.response_time?.toFixed(2)}s)` : 'Unavailable';
                        element.className = info.available ? 'healthy' : 'critical';
                    }
                }
            }

            // Update evolution metrics
            if (data.evolution) {
                document.getElementById('memory-growth').textContent = `${data.evolution.memory_growth} KB/s`;
                document.getElementById('active-offices').textContent = data.evolution.active_offices;
                document.getElementById('task-queue').textContent = data.evolution.task_queue;
            }
        }

        // Emergency control functions
        async function killSwitch() {
            if (confirm('EXECUTE KILL SWITCH? This will terminate all Unity processes.')) {
                const response = await fetch('/emergency/kill-switch', { method: 'POST' });
                const result = await response.json();
                logEmergency('KILL SWITCH ACTIVATED', 'critical');
            }
        }

        async function haltTrading() {
            if (confirm('Halt all trading operations?')) {
                const response = await fetch('/emergency/halt-trading', { method: 'POST' });
                const result = await response.json();
                logEmergency('Trading halted', 'warning');
            }
        }

        async function purgeMemory() {
            if (confirm('Purge all system memory? This action cannot be undone.')) {
                const response = await fetch('/emergency/purge-memory', { method: 'POST' });
                const result = await response.json();
                logEmergency('Memory purged', 'warning');
            }
        }

        async function systemReset() {
            if (confirm('Reset entire system to default state?')) {
                const response = await fetch('/emergency/system-reset', { method: 'POST' });
                const result = await response.json();
                logEmergency('System reset initiated', 'info');
            }
        }

        function logEmergency(message, level) {
            const log = document.getElementById('emergency-log');
            const entry = document.createElement('div');
            entry.className = level;
            entry.textContent = `[${new Date().toISOString()}] ${message}`;
            log.insertBefore(entry, log.firstChild);
        }

        // Auto-refresh every 5 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateDashboard(data);
            } catch (e) {
                console.error('Failed to fetch status:', e);
            }
        }, 5000);
    </script>
</body>
</html>
```

## 5. Emergency Systems

### 5.1 Emergency Control System
```python
# emergency_systems.py

import asyncio
import psutil
import subprocess
import shutil
import json
import os
from datetime import datetime
from typing import Dict, List
import redis
import logging

logger = logging.getLogger("emergency_systems")

class EmergencyController:
    """Emergency control systems for Unity"""

    def __init__(self):
        self.emergency_log = []
        self.kill_switch_armed = True
        self.trading_halted = False
        self.emergency_mode = False

    async def kill_switch(self, authorization: str = None) -> Dict:
        """Execute emergency kill switch"""
        logger.critical("KILL SWITCH ACTIVATED")

        # Log the action
        self.log_emergency("KILL_SWITCH", "ACTIVATED", {"authorization": authorization})

        # Step 1: Stop all trading operations
        await self.halt_trading()

        # Step 2: Kill all Unity processes
        processes_to_kill = [
            "ollama", "python", "node", "redis-server",
            "vault", "unity", "orchestrator"
        ]

        killed_processes = []
        for proc_name in processes_to_kill:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc_name.lower() in proc.info['name'].lower():
                        proc.kill()
                        killed_processes.append({
                            "name": proc.info['name'],
                            "pid": proc.info['pid']
                        })
                except:
                    pass

        # Step 3: Clear all caches and temporary data
        await self.purge_memory(emergency=True)

        # Step 4: Disable auto-restart
        with open("/etc/unity/emergency_shutdown", "w") as f:
            f.write(datetime.now().isoformat())

        return {
            "status": "KILLED",
            "processes_terminated": killed_processes,
            "timestamp": datetime.now().isoformat()
        }

    async def halt_trading(self) -> Dict:
        """Halt all trading operations"""
        logger.warning("HALTING ALL TRADING OPERATIONS")
        self.trading_halted = True

        # Send halt signal via Redis
        try:
            r = redis.Redis(host='localhost', port=6379)
            r.publish('trading_control', json.dumps({
                "command": "HALT",
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass

        # Write halt flag
        with open("/var/run/unity_trading_halt", "w") as f:
            f.write("HALTED")

        self.log_emergency("TRADING_HALT", "ACTIVATED", {})

        return {
            "status": "HALTED",
            "timestamp": datetime.now().isoformat()
        }

    async def resume_trading(self, authorization: str) -> Dict:
        """Resume trading operations"""
        if not authorization:
            return {"error": "Authorization required"}

        logger.info("RESUMING TRADING OPERATIONS")
        self.trading_halted = False

        # Remove halt flag
        if os.path.exists("/var/run/unity_trading_halt"):
            os.remove("/var/run/unity_trading_halt")

        # Send resume signal
        try:
            r = redis.Redis(host='localhost', port=6379)
            r.publish('trading_control', json.dumps({
                "command": "RESUME",
                "timestamp": datetime.now().isoformat(),
                "authorized_by": authorization
            }))
        except:
            pass

        self.log_emergency("TRADING_RESUME", "ACTIVATED", {"authorization": authorization})

        return {
            "status": "RESUMED",
            "timestamp": datetime.now().isoformat()
        }

    async def purge_memory(self, emergency: bool = False) -> Dict:
        """Purge system memory and caches"""
        logger.warning("PURGING SYSTEM MEMORY")

        purged_items = []

        # Clear Redis cache
        try:
            r = redis.Redis(host='localhost', port=6379)
            r.flushall()
            purged_items.append("Redis cache")
        except:
            pass

        # Clear temporary directories
        temp_dirs = [
            "/tmp/unity_*",
            "/var/cache/unity",
            "/var/tmp/orchestrator"
        ]

        for pattern in temp_dirs:
            import glob
            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    purged_items.append(path)
                except:
                    pass

        # Clear Python cache
        try:
            subprocess.run(["python", "-c", "import gc; gc.collect()"])
            purged_items.append("Python garbage collection")
        except:
            pass

        # If emergency, also clear logs
        if emergency:
            log_files = glob.glob("/var/log/unity*.log")
            for log_file in log_files:
                try:
                    with open(log_file, "w") as f:
                        f.write("")
                    purged_items.append(log_file)
                except:
                    pass

        self.log_emergency("MEMORY_PURGE", "COMPLETED", {"emergency": emergency})

        return {
            "status": "PURGED",
            "items_cleared": purged_items,
            "timestamp": datetime.now().isoformat()
        }

    async def system_reset(self, level: str = "soft") -> Dict:
        """Reset system to default state"""
        logger.warning(f"SYSTEM RESET INITIATED (Level: {level})")

        reset_actions = []

        if level == "soft":
            # Soft reset - restart services
            services = ["ollama", "redis-server", "python"]
            for service in services:
                try:
                    subprocess.run(["systemctl", "restart", service])
                    reset_actions.append(f"Restarted {service}")
                except:
                    pass

        elif level == "hard":
            # Hard reset - kill and restart everything
            await self.kill_switch()

            # Wait for processes to die
            await asyncio.sleep(5)

            # Restart core services
            startup_script = "/usr/local/bin/unity_startup.sh"
            if os.path.exists(startup_script):
                subprocess.Popen([startup_script])
                reset_actions.append("Executed startup script")

        elif level == "factory":
            # Factory reset - clear all data and configs
            await self.kill_switch()

            # Remove all Unity data
            unity_dirs = [
                "/etc/unity",
                "/var/lib/unity",
                "/var/log/unity",
                "/home/unity/.unity"
            ]

            for directory in unity_dirs:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
                    reset_actions.append(f"Removed {directory}")

            # Recreate default config
            os.makedirs("/etc/unity", exist_ok=True)
            default_config = {
                "version": "1.0.0",
                "mode": "default",
                "created": datetime.now().isoformat()
            }
            with open("/etc/unity/config.json", "w") as f:
                json.dump(default_config, f)
            reset_actions.append("Created default config")

        self.log_emergency("SYSTEM_RESET", level.upper(), {"actions": reset_actions})

        return {
            "status": "RESET_COMPLETE",
            "level": level,
            "actions": reset_actions,
            "timestamp": datetime.now().isoformat()
        }

    def log_emergency(self, event_type: str, action: str, details: Dict):
        """Log emergency events"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "action": action,
            "details": details
        }

        self.emergency_log.append(entry)

        # Write to persistent log
        with open("/var/log/unity_emergency.jsonl", "a") as f:
            json.dump(entry, f)
            f.write("\n")

        # Send to monitoring
        try:
            r = redis.Redis(host='localhost', port=6379)
            r.publish('emergency_events', json.dumps(entry))
        except:
            pass

    async def check_safety_conditions(self) -> Dict:
        """Check if it's safe to operate"""
        safety_checks = {
            "memory_available": True,
            "cpu_available": True,
            "disk_space": True,
            "network_connectivity": True,
            "critical_services": True
        }

        # Check memory
        mem = psutil.virtual_memory()
        if mem.percent > 95:
            safety_checks["memory_available"] = False

        # Check CPU
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 95:
            safety_checks["cpu_available"] = False

        # Check disk
        disk = psutil.disk_usage('/')
        if disk.percent > 95:
            safety_checks["disk_space"] = False

        # Check critical services
        critical_ports = [11434, 6379, 8000]
        for port in critical_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            if result != 0:
                safety_checks["critical_services"] = False
            sock.close()

        all_safe = all(safety_checks.values())

        return {
            "safe_to_operate": all_safe,
            "checks": safety_checks,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    controller = EmergencyController()
    # Run emergency controller
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()

    @app.post("/emergency/kill-switch")
    async def kill_switch():
        return await controller.kill_switch()

    @app.post("/emergency/halt-trading")
    async def halt_trading():
        return await controller.halt_trading()

    @app.post("/emergency/purge-memory")
    async def purge_memory():
        return await controller.purge_memory()

    @app.post("/emergency/system-reset")
    async def system_reset(level: str = "soft"):
        return await controller.system_reset(level)

    @app.get("/emergency/safety-check")
    async def safety_check():
        return await controller.check_safety_conditions()

    uvicorn.run(app, host="0.0.0.0", port=8002)
```

## 6. Service Configuration Files

### 6.1 Systemd Service Files
```ini
# /etc/systemd/system/unity-watchdog.service
[Unit]
Description=Unity Watchdog Service
After=network.target

[Service]
Type=simple
User=unity
WorkingDirectory=/opt/unity
ExecStart=/usr/bin/python3 /opt/unity/watchdog_master.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/unity_watchdog.log
StandardError=append:/var/log/unity_watchdog_error.log

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/unity-models.service
[Unit]
Description=Unity Model Manager
After=ollama.service

[Service]
Type=simple
User=unity
WorkingDirectory=/opt/unity
ExecStart=/usr/bin/python3 /opt/unity/model_manager.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/unity-emergency.service
[Unit]
Description=Unity Emergency Controller
After=network.target

[Service]
Type=simple
User=unity
WorkingDirectory=/opt/unity
ExecStart=/usr/bin/python3 /opt/unity/emergency_systems.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 6.2 Vault Configuration
```hcl
# /etc/vault/config.hcl
storage "file" {
  path = "/var/lib/vault/data"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = 1
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
ui = true

seal "awskms" {
  region     = "us-west-2"
  kms_key_id = "unity-vault-key"
}
```

## 7. Recovery Playbooks

### 7.1 Complete System Failure Recovery
```bash
#!/bin/bash
# recovery_complete.sh

echo "Unity Complete System Recovery - Starting..."

# Step 1: Check system resources
echo "Checking system resources..."
df -h
free -m
top -b -n 1

# Step 2: Clear emergency shutdown flag
rm -f /etc/unity/emergency_shutdown

# Step 3: Start core services
echo "Starting core services..."
systemctl start redis
sleep 2
systemctl start vault
sleep 2
systemctl start ollama
sleep 5

# Step 4: Verify Ollama models
echo "Verifying models..."
ollama list
ollama pull deepseek-r1:14b
ollama pull qwen2.5-coder:7b

# Step 5: Start Unity services
systemctl start unity-watchdog
systemctl start unity-models
systemctl start unity-emergency

# Step 6: Start Python backend
cd /opt/unity/backend
source venv/bin/activate
nohup python -m uvicorn main:app --port 8000 &

# Step 7: Verify all services
sleep 10
curl -s http://localhost:8000/health
curl -s http://localhost:11434/api/tags
redis-cli ping

echo "Recovery complete. Check dashboard at http://localhost:8001"
```

### 7.2 Token Exhaustion Recovery
```bash
#!/bin/bash
# recovery_token_exhaustion.sh

echo "Token Exhaustion Recovery Protocol"

# Step 1: Enable fallback mode
echo '{"fallback_mode": true}' > /etc/unity/fallback_mode.json

# Step 2: Switch to local models
curl -X POST http://localhost:8000/api/models/switch \
  -H "Content-Type: application/json" \
  -d '{"mode": "local"}'

# Step 3: Notify operators
echo "ALERT: Token exhaustion detected. System running in fallback mode." | \
  mail -s "Unity Token Exhaustion" ops@company.com

# Step 4: Attempt token rotation
python3 /opt/unity/token_manager.py --rotate-all

# Step 5: Monitor fallback performance
watch -n 5 'curl -s http://localhost:8000/api/status | jq .'
```

## 8. Monitoring Commands

```bash
# Check service status
systemctl status unity-watchdog unity-models unity-emergency

# View logs
journalctl -u unity-watchdog -f
tail -f /var/log/unity_*.log

# Monitor resources
htop
iotop
nethogs

# Check model performance
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:14b",
  "prompt": "test",
  "stream": false
}' | jq .

# Emergency dashboard
open http://localhost:8001/dashboard.html

# Manual kill switch
curl -X POST http://localhost:8002/emergency/kill-switch

# Safety check
curl http://localhost:8002/emergency/safety-check | jq .
```

## Deployment Instructions

1. Install dependencies:
```bash
pip install psutil aiohttp redis hvac fastapi uvicorn jwt
npm install -g ollama
apt-get install redis-server vault
```

2. Deploy services:
```bash
cp *.py /opt/unity/
cp *.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable unity-watchdog unity-models unity-emergency
```

3. Initialize Vault:
```bash
vault operator init
vault operator unseal
vault login
```

4. Start monitoring:
```bash
systemctl start unity-watchdog
systemctl start unity-models
systemctl start unity-emergency
```

5. Access dashboard:
```
http://localhost:8001/dashboard.html
```

---

This implementation provides comprehensive monitoring, automatic recovery, token management, and emergency controls for the Unity orchestrator. The system ensures continuous operation even when external services fail.