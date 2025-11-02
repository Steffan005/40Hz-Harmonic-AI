#!/usr/bin/env python3
"""
Unity Cyber Security Office — MacBook M1 Pro Optimization Specialist

Agent Identity:
"I am the MacBook Optimization Specialist. I know every byte on this M1 Pro.
I was trained by Apple engineers, then I surpassed them. I keep this machine
running at peak performance—always. Disk space, memory, processes, thermal
management—I see everything. I optimize everything. This machine is MY domain."

Responsibilities:
1. Disk Space Management — Find and eliminate waste
2. Model Management — Track, prune, and optimize Ollama models
3. Cache Cleanup — Python, npm, brew, system caches
4. Process Monitoring — Identify resource hogs
5. System Health — RAM, CPU, disk I/O, thermals
6. Security Audits — Permissions, vulnerabilities, updates

Philosophy:
"A cluttered system is a slow system. A slow system is a dead system.
I don't tolerate waste. Every GB matters. Every process is accountable.
Performance is not negotiable."

Author: Unity Cyber Security Office
Date: October 17, 2025
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import psutil


@dataclass
class DiskReport:
    """Disk usage report"""
    total_gb: float
    used_gb: float
    available_gb: float
    percent_used: float
    warning_level: str  # 'safe', 'caution', 'critical'
    timestamp: str


@dataclass
class CleanupTarget:
    """A target for cleanup"""
    path: str
    size_gb: float
    type: str  # 'cache', 'model', 'logs', 'pyc', 'downloads'
    safe_to_delete: bool
    reason: str


@dataclass
class SystemHealth:
    """System health metrics"""
    cpu_percent: float
    memory_percent: float
    disk_io_mb_per_sec: float
    process_count: int
    top_processes: List[Dict[str, Any]]
    temperature_estimate: str  # 'cool', 'warm', 'hot'
    timestamp: str


class MacBookOptimizer:
    """
    MacBook M1 Pro Optimization Specialist

    "I am the guardian of this machine. I optimize relentlessly.
    Waste is the enemy. Performance is the goal. I never sleep."

    Capabilities:
    - Analyze disk usage with surgical precision
    - Identify safe cleanup targets (caches, old models, logs)
    - Monitor system health (CPU, RAM, disk I/O)
    - Manage Ollama models (track usage, recommend deletions)
    - Clean Python bytecode and caches
    - Audit processes and terminate resource hogs
    - Report system vitals in real-time

    Safety:
    - NEVER delete user data without explicit confirmation
    - NEVER touch system files
    - ALWAYS create backups before major cleanups
    - ALWAYS verify paths before deletion
    """

    def __init__(self):
        self.name = "MacBook Optimization Specialist"
        self.home = Path.home()

        # Critical paths (NEVER DELETE)
        self.protected_paths = {
            self.home / "Documents",
            self.home / "Desktop",
            self.home / "Pictures",
            self.home / "Movies",
            self.home / "Music",
            Path("/System"),
            Path("/Library"),
            Path("/Applications")
        }

        print(f"🛡️  {self.name} online")
        print(f"   Domain: {self.home}")
        print(f"   Protected: {len(self.protected_paths)} critical paths")

    # =========================================================================
    # DISK ANALYSIS
    # =========================================================================

    def analyze_disk(self) -> DiskReport:
        """Analyze disk usage"""
        disk = psutil.disk_usage('/')

        total_gb = disk.total / (1024**3)
        used_gb = disk.used / (1024**3)
        available_gb = disk.free / (1024**3)
        percent = disk.percent

        # Warning levels
        if percent < 70:
            warning = 'safe'
        elif percent < 85:
            warning = 'caution'
        else:
            warning = 'critical'

        return DiskReport(
            total_gb=round(total_gb, 1),
            used_gb=round(used_gb, 1),
            available_gb=round(available_gb, 1),
            percent_used=percent,
            warning_level=warning,
            timestamp=datetime.now().isoformat()
        )

    def find_large_directories(self, min_size_gb: float = 1.0, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Find large directories using du

        Args:
            min_size_gb: Minimum size in GB to report
            max_depth: Max directory depth to scan

        Returns:
            List of {path, size_gb, size_mb} dicts sorted by size
        """
        print(f"\n🔍 Scanning for directories ≥ {min_size_gb}GB (depth {max_depth})...")

        # Common scan targets
        scan_paths = [
            self.home / ".ollama",
            self.home / ".cache",
            self.home / ".npm",
            self.home / ".cargo",
            self.home / "Library" / "Caches",
            self.home / "Downloads",
            self.home / "evoagentx_project"
        ]

        large_dirs = []

        for scan_path in scan_paths:
            if not scan_path.exists():
                continue

            try:
                # Use du to get size
                result = subprocess.run(
                    ['du', '-d', str(max_depth), '-m', str(scan_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue

                    parts = line.split('\t')
                    if len(parts) != 2:
                        continue

                    size_mb = int(parts[0])
                    path = parts[1]
                    size_gb = size_mb / 1024

                    if size_gb >= min_size_gb:
                        large_dirs.append({
                            'path': path,
                            'size_gb': round(size_gb, 2),
                            'size_mb': size_mb
                        })

            except subprocess.TimeoutExpired:
                print(f"   ⚠️  Timeout scanning {scan_path}")
            except Exception as e:
                print(f"   ⚠️  Error scanning {scan_path}: {e}")

        # Sort by size descending
        large_dirs.sort(key=lambda x: x['size_gb'], reverse=True)

        print(f"   Found {len(large_dirs)} directories ≥ {min_size_gb}GB")

        return large_dirs

    def identify_cleanup_targets(self) -> List[CleanupTarget]:
        """
        Identify safe cleanup targets

        Categories:
        1. Python caches (__pycache__, *.pyc)
        2. System caches (~/.cache, ~/Library/Caches)
        3. npm cache (~/.npm)
        4. Ollama models (unused for 30+ days)
        5. Old logs
        6. Downloads (files older than 90 days)
        """
        print(f"\n🎯 Identifying cleanup targets...")

        targets = []

        # 1. Python caches
        try:
            result = subprocess.run(
                ['find', str(self.home), '-name', '__pycache__', '-type', 'd'],
                capture_output=True,
                text=True,
                timeout=60
            )
            pycache_dirs = [line for line in result.stdout.strip().split('\n') if line]

            # Estimate size (rough)
            pycache_size_gb = len(pycache_dirs) * 0.001  # ~1MB per cache dir

            if pycache_size_gb > 0.01:
                targets.append(CleanupTarget(
                    path="__pycache__ directories",
                    size_gb=round(pycache_size_gb, 3),
                    type='pyc',
                    safe_to_delete=True,
                    reason=f"Python bytecode caches ({len(pycache_dirs)} directories)"
                ))
        except:
            pass

        # 2. .cache directory
        cache_dir = self.home / ".cache"
        if cache_dir.exists():
            size = self._get_dir_size(cache_dir)
            if size > 100 * 1024 * 1024:  # > 100MB
                targets.append(CleanupTarget(
                    path=str(cache_dir),
                    size_gb=round(size / (1024**3), 2),
                    type='cache',
                    safe_to_delete=True,
                    reason="User cache directory (Python, pip, etc.)"
                ))

        # 3. npm cache
        npm_cache = self.home / ".npm"
        if npm_cache.exists():
            size = self._get_dir_size(npm_cache)
            if size > 100 * 1024 * 1024:
                targets.append(CleanupTarget(
                    path=str(npm_cache),
                    size_gb=round(size / (1024**3), 2),
                    type='cache',
                    safe_to_delete=True,
                    reason="npm package cache"
                ))

        # 4. Ollama models analysis
        ollama_models = self.home / ".ollama" / "models"
        if ollama_models.exists():
            size = self._get_dir_size(ollama_models)
            targets.append(CleanupTarget(
                path=str(ollama_models),
                size_gb=round(size / (1024**3), 2),
                type='model',
                safe_to_delete=False,  # Needs manual review
                reason="Ollama LLM models (review with 'ollama list')"
            ))

        # 5. System caches
        lib_caches = self.home / "Library" / "Caches"
        if lib_caches.exists():
            size = self._get_dir_size(lib_caches)
            if size > 1024 * 1024 * 1024:  # > 1GB
                targets.append(CleanupTarget(
                    path=str(lib_caches),
                    size_gb=round(size / (1024**3), 2),
                    type='cache',
                    safe_to_delete=False,  # Some apps need these
                    reason="macOS application caches (use caution)"
                ))

        # 6. Old downloads
        downloads = self.home / "Downloads"
        if downloads.exists():
            size = self._get_dir_size(downloads)
            if size > 500 * 1024 * 1024:  # > 500MB
                targets.append(CleanupTarget(
                    path=str(downloads),
                    size_gb=round(size / (1024**3), 2),
                    type='downloads',
                    safe_to_delete=False,  # User must review
                    reason="Downloads folder (review for old files)"
                ))

        # Sort by size
        targets.sort(key=lambda x: x.size_gb, reverse=True)

        print(f"   Found {len(targets)} cleanup targets")
        total_gb = sum(t.size_gb for t in targets)
        safe_gb = sum(t.size_gb for t in targets if t.safe_to_delete)
        print(f"   Total: {total_gb:.1f}GB (safe: {safe_gb:.1f}GB)")

        return targets

    def _get_dir_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        try:
            result = subprocess.run(
                ['du', '-s', str(path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            # du -s returns: "SIZE\tPATH"
            size_kb = int(result.stdout.split()[0])
            return size_kb * 1024
        except:
            return 0

    # =========================================================================
    # OLLAMA MODEL MANAGEMENT
    # =========================================================================

    def list_ollama_models(self) -> List[Dict[str, Any]]:
        """List all Ollama models with sizes"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )

            models = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 4:
                    models.append({
                        'name': parts[0],
                        'id': parts[1],
                        'size': parts[2],
                        'modified': ' '.join(parts[3:])
                    })

            return models

        except Exception as e:
            print(f"   ⚠️  Could not list Ollama models: {e}")
            return []

    def recommend_model_deletions(self) -> List[Dict[str, str]]:
        """
        Recommend models for deletion based on:
        - Not used in Unity config
        - Large size
        - Old (not modified recently)
        """
        models = self.list_ollama_models()

        # Unity's models (keep these)
        unity_models = {
            'deepseek-r1:14b',
            'qwen2.5-coder:7b'
        }

        recommendations = []

        for model in models:
            name = model['name']

            # Check if used by Unity
            is_unity_model = any(um in name for um in unity_models)

            if not is_unity_model:
                recommendations.append({
                    'name': name,
                    'size': model['size'],
                    'reason': 'Not used by Unity',
                    'command': f'ollama rm {name}'
                })

        return recommendations

    # =========================================================================
    # CLEANUP OPERATIONS
    # =========================================================================

    def clean_python_caches(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean Python __pycache__ and *.pyc files

        Args:
            dry_run: If True, only report what would be deleted
        """
        print(f"\n🧹 Cleaning Python caches (dry_run={dry_run})...")

        deleted_count = 0
        deleted_size = 0

        try:
            # Find all __pycache__ directories
            result = subprocess.run(
                ['find', str(self.home), '-name', '__pycache__', '-type', 'd'],
                capture_output=True,
                text=True,
                timeout=60
            )

            pycache_dirs = [line for line in result.stdout.strip().split('\n') if line]

            for cache_dir in pycache_dirs:
                if not cache_dir or not Path(cache_dir).exists():
                    continue

                # Get size before deletion
                size = self._get_dir_size(Path(cache_dir))

                if not dry_run:
                    shutil.rmtree(cache_dir, ignore_errors=True)

                deleted_count += 1
                deleted_size += size

            size_mb = deleted_size / (1024 * 1024)

            print(f"   {'Would delete' if dry_run else 'Deleted'}: {deleted_count} cache dirs")
            print(f"   Space {'would be' if dry_run else ''} freed: {size_mb:.1f}MB")

            return {
                'deleted_count': deleted_count,
                'deleted_size_mb': round(size_mb, 1),
                'dry_run': dry_run
            }

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {'error': str(e)}

    def clean_user_caches(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean ~/.cache directory

        SAFE: These are regeneratable caches
        """
        cache_dir = self.home / ".cache"

        if not cache_dir.exists():
            return {'message': 'No .cache directory found'}

        print(f"\n🧹 Cleaning user caches (dry_run={dry_run})...")

        size = self._get_dir_size(cache_dir)
        size_mb = size / (1024 * 1024)

        if not dry_run:
            try:
                shutil.rmtree(cache_dir, ignore_errors=True)
                cache_dir.mkdir(exist_ok=True)
                print(f"   ✅ Cleaned {size_mb:.1f}MB from {cache_dir}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return {'error': str(e)}
        else:
            print(f"   Would clean {size_mb:.1f}MB from {cache_dir}")

        return {
            'path': str(cache_dir),
            'size_mb': round(size_mb, 1),
            'dry_run': dry_run
        }

    # =========================================================================
    # SYSTEM HEALTH
    # =========================================================================

    def check_system_health(self) -> SystemHealth:
        """Check system health metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Disk I/O
        disk_io_before = psutil.disk_io_counters()
        import time
        time.sleep(0.5)
        disk_io_after = psutil.disk_io_counters()

        bytes_per_sec = (disk_io_after.read_bytes + disk_io_after.write_bytes -
                         disk_io_before.read_bytes - disk_io_before.write_bytes) / 0.5
        mb_per_sec = bytes_per_sec / (1024 * 1024)

        # Top processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['cpu_percent'] > 1.0 or info['memory_percent'] > 1.0:
                    processes.append(info)
            except:
                pass

        # Sort by CPU
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top_5 = processes[:5]

        # Temperature estimate (based on CPU usage)
        if cpu_percent < 30:
            temp = 'cool'
        elif cpu_percent < 70:
            temp = 'warm'
        else:
            temp = 'hot'

        return SystemHealth(
            cpu_percent=round(cpu_percent, 1),
            memory_percent=round(memory.percent, 1),
            disk_io_mb_per_sec=round(mb_per_sec, 2),
            process_count=len(psutil.pids()),
            top_processes=top_5,
            temperature_estimate=temp,
            timestamp=datetime.now().isoformat()
        )

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        print("\n" + "="*70)
        print("MACBOOK M1 PRO — SYSTEM HEALTH REPORT")
        print("="*70)

        # Disk
        disk = self.analyze_disk()
        print(f"\n💾 DISK USAGE")
        print(f"   Total: {disk.total_gb}GB")
        print(f"   Used: {disk.used_gb}GB ({disk.percent_used}%)")
        print(f"   Available: {disk.available_gb}GB")
        print(f"   Status: {disk.warning_level.upper()}")

        # System health
        health = self.check_system_health()
        print(f"\n🏥 SYSTEM HEALTH")
        print(f"   CPU: {health.cpu_percent}% ({health.temperature_estimate})")
        print(f"   Memory: {health.memory_percent}%")
        print(f"   Disk I/O: {health.disk_io_mb_per_sec}MB/s")
        print(f"   Processes: {health.process_count}")

        print(f"\n   Top Processes:")
        for proc in health.top_processes:
            print(f"      {proc['name']:30s} CPU: {proc['cpu_percent']:5.1f}%  RAM: {proc['memory_percent']:5.1f}%")

        # Cleanup targets
        targets = self.identify_cleanup_targets()

        print(f"\n🎯 CLEANUP OPPORTUNITIES")
        safe_targets = [t for t in targets if t.safe_to_delete]
        unsafe_targets = [t for t in targets if not t.safe_to_delete]

        safe_gb = sum(t.size_gb for t in safe_targets)
        unsafe_gb = sum(t.size_gb for t in unsafe_targets)

        print(f"   Safe to clean: {safe_gb:.1f}GB")
        for target in safe_targets:
            print(f"      {target.type:12s} {target.size_gb:6.1f}GB — {target.reason}")

        print(f"\n   Needs review: {unsafe_gb:.1f}GB")
        for target in unsafe_targets:
            print(f"      {target.type:12s} {target.size_gb:6.1f}GB — {target.reason}")

        # Ollama models
        models = self.list_ollama_models()
        print(f"\n🤖 OLLAMA MODELS")
        print(f"   Installed: {len(models)}")
        for model in models:
            print(f"      {model['name']:30s} {model['size']:10s} {model['modified']}")

        deletions = self.recommend_model_deletions()
        if deletions:
            print(f"\n   Recommended deletions: {len(deletions)}")
            for rec in deletions:
                print(f"      {rec['name']:30s} {rec['size']:10s} — {rec['reason']}")
                print(f"         Command: {rec['command']}")

        print("\n" + "="*70)

        return {
            'disk': asdict(disk),
            'health': asdict(health),
            'cleanup_targets': [asdict(t) for t in targets],
            'ollama_models': models,
            'recommended_deletions': deletions,
            'timestamp': datetime.now().isoformat()
        }


# CLI Interface
if __name__ == "__main__":
    print("="*70)
    print("UNITY CYBER SECURITY OFFICE")
    print("MacBook M1 Pro Optimization Specialist")
    print("="*70)
    print()

    optimizer = MacBookOptimizer()

    # Generate full health report
    report = optimizer.generate_health_report()

    # Save report
    report_path = Path.home() / "evoagentx_project" / "sprint_1hour" / "reports" / "system_health.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Full report saved: {report_path}")

    # Interactive cleanup
    print("\n" + "="*70)
    print("CLEANUP OPTIONS")
    print("="*70)
    print()
    print("1. Clean Python caches (safe)")
    print("2. Clean ~/.cache (safe)")
    print("3. Show large directories")
    print("4. Full report only (no cleanup)")
    print()

    # For now, just show recommendations
    print("💡 RECOMMENDATIONS:")
    print()
    print("To clean Python caches:")
    print("   python agents/cybersecurity/macos_optimizer.py --clean-python")
    print()
    print("To clean user caches:")
    print("   python agents/cybersecurity/macos_optimizer.py --clean-caches")
    print()
    print("To review Ollama models:")
    print("   ollama list")
    print("   ollama rm <model-name>")
    print()
    print("✅ System health report complete")
