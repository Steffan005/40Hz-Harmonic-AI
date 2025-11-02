#!/usr/bin/env python3
"""
System configuration loader for Unity
Loads system.yaml and provides it as Python dict
"""

import yaml
from pathlib import Path
from typing import Dict, Any

_config_cache = None

def load_system_config() -> Dict[str, Any]:
    """Load system configuration from system.yaml"""
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    config_path = Path(__file__).parent / "system.yaml"

    if not config_path.exists():
        # Return default config if file doesn't exist
        return {
            "cloud_llm": {
                "enabled": False,
                "provider": "together",
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "fallback_to_local": True,
                "timeout_seconds": 30,
                "max_tokens": 4096
            }
        }

    with open(config_path, 'r') as f:
        _config_cache = yaml.safe_load(f)

    return _config_cache


def get_cloud_llm_config() -> Dict[str, Any]:
    """Get cloud LLM configuration"""
    config = load_system_config()
    return config.get('cloud_llm', {})


if __name__ == "__main__":
    # Test the config loader
    config = load_system_config()
    print("System configuration loaded:")
    print(f"  Cloud LLM enabled: {config.get('cloud_llm', {}).get('enabled', False)}")
    print(f"  Provider: {config.get('cloud_llm', {}).get('provider', 'unknown')}")
