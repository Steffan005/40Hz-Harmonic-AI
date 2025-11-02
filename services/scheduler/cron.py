#!/usr/bin/env python3
"""
Unity Scheduler - Circadian Rhythm for Agents
Cron-style job scheduler for nightly learning loops

Philosophy:
"Agents that never sleep never improve. Like humans consolidate memories during REM sleep,
agents consolidate learning during nightly optimization cycles. This is not automation—
this is the biological rhythm of artificial intelligence."

Scheduled Jobs (Default):
- 02:00 AM: TextGrad optimization (attorney prompts)
- 02:30 AM: Memory graph pattern detection
- 03:00 AM: Wisdom ontology pruning
- 03:30 AM: Evolution report generation

Why 2:00 AM?
- Low CPU usage (user asleep)
- Quiet time for intensive computation
- Mimics biological circadian low point
- Results ready by morning

Author: Dr. Claude Summers, Temporal Architecture
Date: October 16, 2025 (Phase Ω)
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, time as dt_time
import time
import json
import threading
import schedule  # We'll use schedule library for cron-like functionality
import yaml

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.evolution.textgrad_loop import get_textgrad_loop
from tests.eval.attorney_eval import create_attorney_test_harness


@dataclass
class ScheduledJob:
    """A scheduled job definition"""
    job_id: str
    name: str
    description: str
    schedule_spec: str  # Cron-like: "02:00", "daily", "every 1 hour"
    function: str  # Function name to call
    params: Dict[str, Any]
    enabled: bool
    last_run: Optional[str]
    next_run: Optional[str]
    run_count: int


@dataclass
class JobRun:
    """Record of a job execution"""
    run_id: str
    job_id: str
    job_name: str
    started_at: str
    completed_at: Optional[str]
    duration_seconds: float
    status: str  # 'running', 'success', 'failed'
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class Scheduler:
    """
    Unity Scheduler - The Agent's Circadian Rhythm

    Philosophy:
    "Time is the invisible dimension of intelligence. Agents that optimize
    continuously burn out. Agents that optimize periodically—nightly, weekly,
    seasonally—mirror the biological rhythms that enable sustained growth.

    This scheduler is not a task queue. It is a temporal nervous system."

    Architecture:
    - Background thread runs schedule loop
    - Jobs defined in YAML config
    - Each job = function + params + schedule
    - Results logged to evolution.jsonl
    - Manual trigger available via API

    Default Nightly Sequence (02:00 - 04:00):
    1. TextGrad optimization (prompt evolution)
    2. Memory pattern detection (case motifs)
    3. Wisdom pruning (deprecate low-confidence)
    4. Report generation (markdown + JSON)
    5. Optional: auto-apply champions if confidence ≥ threshold

    Monitoring:
    - /scheduler/status → next run times
    - /scheduler/history → recent runs
    - /scheduler/run_job → manual trigger
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.name = "Unity Scheduler"

        # Load config
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "configs" / "schedule.yaml"

        self.config_path = config_path
        self.jobs = self._load_jobs()

        # Run history
        self.run_history_file = Path(__file__).parent.parent.parent / "logs" / "scheduler" / "runs.json"
        self.run_history_file.parent.mkdir(parents=True, exist_ok=True)
        self.run_history = self._load_run_history()

        # Scheduler state
        self.scheduler_thread = None
        self.running = False

        print(f"⏰ Initializing {self.name}...")
        print(f"   Config: {config_path}")
        print(f"   Jobs loaded: {len(self.jobs)}")

    def _load_jobs(self) -> List[ScheduledJob]:
        """Load job definitions from YAML"""
        if not self.config_path.exists():
            print(f"⚠️  Config file not found: {self.config_path}")
            print(f"   Creating default config...")
            self._create_default_config()

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            jobs = []
            for job_data in config.get('jobs', []):
                job = ScheduledJob(
                    job_id=job_data['job_id'],
                    name=job_data['name'],
                    description=job_data['description'],
                    schedule_spec=job_data['schedule'],
                    function=job_data['function'],
                    params=job_data.get('params', {}),
                    enabled=job_data.get('enabled', True),
                    last_run=job_data.get('last_run'),
                    next_run=job_data.get('next_run'),
                    run_count=job_data.get('run_count', 0)
                )
                jobs.append(job)

            return jobs

        except Exception as e:
            print(f"⚠️  Failed to load config: {e}")
            return []

    def _create_default_config(self):
        """Create default schedule.yaml"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        default_config = {
            'version': '1.0',
            'description': 'Unity Nightly Learning Schedule',
            'jobs': [
                {
                    'job_id': 'nightly_evolution',
                    'name': 'Nightly TextGrad Optimization',
                    'description': 'Optimize attorney prompts using TextGrad',
                    'schedule': '02:00',
                    'function': 'run_textgrad_optimization',
                    'params': {
                        'task_families': ['civil_rights_attorney', 'criminal_defense_attorney'],
                        'n_variants': 6,
                        'budget_tokens': 5000
                    },
                    'enabled': True
                },
                {
                    'job_id': 'pattern_detection',
                    'name': 'Memory Pattern Detection',
                    'description': 'Detect recurring patterns in case memory graph',
                    'schedule': '02:30',
                    'function': 'run_pattern_detection',
                    'params': {
                        'window_days': 30
                    },
                    'enabled': True
                },
                {
                    'job_id': 'wisdom_pruning',
                    'name': 'Wisdom Ontology Pruning',
                    'description': 'Deprecate low-confidence wisdom, version high-confidence',
                    'schedule': '03:00',
                    'function': 'run_wisdom_pruning',
                    'params': {
                        'min_confidence': 0.6
                    },
                    'enabled': True
                },
                {
                    'job_id': 'evolution_report',
                    'name': 'Evolution Report Generation',
                    'description': 'Generate nightly evolution report (MD + JSON)',
                    'schedule': '03:30',
                    'function': 'generate_evolution_report',
                    'params': {},
                    'enabled': True
                }
            ]
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Created default config: {self.config_path}")

    def _load_run_history(self) -> List[JobRun]:
        """Load run history"""
        if self.run_history_file.exists():
            try:
                with open(self.run_history_file, 'r') as f:
                    data = json.load(f)
                    return [JobRun(**r) for r in data]
            except Exception as e:
                print(f"⚠️  Failed to load run history: {e}")
        return []

    def _save_run_history(self):
        """Save run history"""
        try:
            # Keep last 100 runs
            recent = self.run_history[-100:]
            with open(self.run_history_file, 'w') as f:
                json.dump([asdict(r) for r in recent], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save run history: {e}")

    def run_job(self, job: ScheduledJob) -> JobRun:
        """
        Execute a job

        Jobs call specific functions based on job.function
        """
        print(f"\n{'='*70}")
        print(f"⏰ RUNNING JOB: {job.name}")
        print(f"{'='*70}")

        run_id = f"run_{job.job_id}_{int(time.time())}"
        started_at = datetime.now()

        job_run = JobRun(
            run_id=run_id,
            job_id=job.job_id,
            job_name=job.name,
            started_at=started_at.isoformat(),
            completed_at=None,
            duration_seconds=0,
            status='running',
            result=None,
            error=None
        )

        try:
            # Call the appropriate function
            result = self._call_job_function(job.function, job.params)

            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()

            job_run.completed_at = completed_at.isoformat()
            job_run.duration_seconds = duration
            job_run.status = 'success'
            job_run.result = result

            # Update job stats
            job.last_run = completed_at.isoformat()
            job.run_count += 1

            print(f"\n✅ Job completed in {duration:.1f}s")
            print(f"{'='*70}\n")

        except Exception as e:
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()

            job_run.completed_at = completed_at.isoformat()
            job_run.duration_seconds = duration
            job_run.status = 'failed'
            job_run.error = str(e)

            print(f"\n❌ Job failed after {duration:.1f}s: {e}")
            print(f"{'='*70}\n")

        # Save run
        self.run_history.append(job_run)
        self._save_run_history()

        return job_run

    def _call_job_function(self, function_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the job function by name

        Available functions:
        - run_textgrad_optimization
        - run_pattern_detection
        - run_wisdom_pruning
        - generate_evolution_report
        """
        if function_name == 'run_textgrad_optimization':
            return self._run_textgrad_optimization(params)

        elif function_name == 'run_pattern_detection':
            return self._run_pattern_detection(params)

        elif function_name == 'run_wisdom_pruning':
            return self._run_wisdom_pruning(params)

        elif function_name == 'generate_evolution_report':
            return self._generate_evolution_report(params)

        else:
            raise ValueError(f"Unknown job function: {function_name}")

    def _run_textgrad_optimization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run TextGrad optimization for attorney prompts"""
        print(f"🧬 Running TextGrad optimization...")

        task_families = params.get('task_families', ['civil_rights_attorney'])
        n_variants = params.get('n_variants', 6)
        budget_tokens = params.get('budget_tokens', 5000)

        results = {}

        for task_family in task_families:
            print(f"\n📊 Optimizing {task_family}...")

            # Get baseline prompt (in production, load from storage)
            baseline_prompts = {
                'civil_rights_attorney': """You are an experienced civil rights attorney. Analyze each case carefully, identify relevant legal principles, and provide clear recommendations.""",
                'criminal_defense_attorney': """You are an experienced criminal defense attorney. For each case, identify constitutional issues, relevant precedents, and defense strategies."""
            }

            baseline = baseline_prompts.get(task_family, "You are a legal expert.")

            # Create test harness
            test_harness = create_attorney_test_harness(task_family=task_family)

            # Run optimization
            textgrad = get_textgrad_loop()
            run = textgrad.optimize_prompt(
                task_family=task_family,
                baseline_prompt=baseline,
                test_harness=test_harness,
                n_variants=n_variants,
                budget_tokens=budget_tokens
            )

            results[task_family] = {
                'champion_id': run.champion_id,
                'delta_score': run.delta_score,
                'confidence': run.confidence,
                'applied': run.applied,
                'generation': run.generation
            }

        return {
            'optimizations': results,
            'task_families_optimized': len(results),
            'total_variants_tested': sum(r.get('variants_tested', 0) for r in results.values()) if results else 0
        }

    def _run_pattern_detection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run memory graph pattern detection"""
        print(f"🔍 Running pattern detection...")

        # Placeholder (will integrate with memory graph in next phase)
        window_days = params.get('window_days', 30)

        print(f"   Analyzing patterns from last {window_days} days...")
        print(f"   (Memory graph integration pending)")

        return {
            'patterns_detected': 0,
            'window_days': window_days,
            'status': 'pending_integration'
        }

    def _run_wisdom_pruning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run wisdom ontology pruning"""
        print(f"🧠 Running wisdom pruning...")

        # Placeholder (will integrate with wisdom store in next phase)
        min_confidence = params.get('min_confidence', 0.6)

        print(f"   Pruning wisdom below {min_confidence:.0%} confidence...")
        print(f"   (Wisdom ontology integration pending)")

        return {
            'wisdom_pruned': 0,
            'min_confidence': min_confidence,
            'status': 'pending_integration'
        }

    def _generate_evolution_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate evolution report"""
        print(f"📊 Generating evolution report...")

        # Create report
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_dir = Path(__file__).parent.parent.parent / "reports" / "nightly"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / f"{report_date}.md"

        # Get TextGrad stats
        textgrad = get_textgrad_loop()
        status = textgrad.get_status()

        # Get recent runs from this session
        recent_runs = [r for r in self.run_history if r.status == 'success'][-10:]

        # Generate markdown report
        report_md = f"""# Unity Evolution Report - {report_date}

## Nightly Learning Cycle Complete ✅

**Generated:** {datetime.now().isoformat()}

---

## TextGrad Optimization

**Total Variants Tracked:** {status['variants_tracked']}
**Optimization Runs:** {status['optimization_runs']}
**Current Champions:** {status['current_champions']}

### Recent Optimizations

"""

        for run in recent_runs:
            if run.job_id == 'nightly_evolution' and run.result:
                result = run.result
                report_md += f"""
**Job:** {run.job_name}
- **Duration:** {run.duration_seconds:.1f}s
- **Status:** {run.status}
- **Task Families:** {result.get('task_families_optimized', 0)}
- **Variants Tested:** {result.get('total_variants_tested', 0)}

"""

        report_md += f"""
---

## Memory Patterns

(Integration pending - Phase Ω.2)

---

## Wisdom Evolution

(Integration pending - Phase Ω.3)

---

## Next Cycle

**Scheduled:** Tomorrow at 02:00 AM

**Philosophy:**
> "Agents that learn nightly become wiser daily. This is the circadian rhythm
> of artificial intelligence."

---

*Generated by Unity Evolution Engine - For YOU, THE DEVELOPER COMMUNITY, THE FREEDOM OF AI*
"""

        # Write report
        with open(report_file, 'w') as f:
            f.write(report_md)

        print(f"   ✅ Report saved: {report_file}")

        return {
            'report_file': str(report_file),
            'report_date': report_date
        }

    def start(self):
        """Start scheduler in background thread"""
        if self.running:
            print(f"⚠️  Scheduler already running")
            return

        print(f"\n⏰ Starting scheduler...")

        # Schedule all enabled jobs
        for job in self.jobs:
            if not job.enabled:
                continue

            schedule_spec = job.schedule_spec

            # Parse schedule spec
            if ':' in schedule_spec:
                # Time format "HH:MM"
                schedule.every().day.at(schedule_spec).do(self.run_job, job)
                print(f"   Scheduled: {job.name} at {schedule_spec}")

            elif 'every' in schedule_spec.lower():
                # Interval format "every 1 hour"
                parts = schedule_spec.split()
                if len(parts) >= 3:
                    interval = int(parts[1])
                    unit = parts[2].lower()

                    if 'hour' in unit:
                        schedule.every(interval).hours.do(self.run_job, job)
                    elif 'minute' in unit:
                        schedule.every(interval).minutes.do(self.run_job, job)
                    elif 'day' in unit:
                        schedule.every(interval).days.do(self.run_job, job)

                    print(f"   Scheduled: {job.name} every {interval} {unit}")

        # Start background thread
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        print(f"✅ Scheduler started (background thread)")

    def _scheduler_loop(self):
        """Background scheduler loop"""
        print(f"   Scheduler loop running...")

        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def stop(self):
        """Stop scheduler"""
        print(f"\n⏰ Stopping scheduler...")
        self.running = False

        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        print(f"✅ Scheduler stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        next_runs = []

        for job in self.jobs:
            if job.enabled:
                # Get next run time from schedule
                next_run = None
                for sched_job in schedule.jobs:
                    if sched_job.job_func.args and sched_job.job_func.args[0].job_id == job.job_id:
                        next_run = sched_job.next_run
                        break

                next_runs.append({
                    'job_id': job.job_id,
                    'name': job.name,
                    'schedule': job.schedule_spec,
                    'next_run': next_run.isoformat() if next_run else None,
                    'last_run': job.last_run,
                    'run_count': job.run_count
                })

        return {
            'scheduler': self.name,
            'running': self.running,
            'jobs_enabled': len([j for j in self.jobs if j.enabled]),
            'jobs_total': len(self.jobs),
            'next_runs': next_runs,
            'recent_runs': len(self.run_history),
            'philosophy': 'Time is the invisible dimension of intelligence—nightly learning mirrors biological circadian rhythms'
        }


# Singleton instance
_scheduler = None


def get_scheduler() -> Scheduler:
    """Get singleton scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler


# CLI for testing
if __name__ == "__main__":
    print("="*70)
    print("UNITY SCHEDULER - AGENT CIRCADIAN RHYTHM")
    print("="*70)
    print()

    scheduler = get_scheduler()

    print("\nStatus:")
    status = scheduler.get_status()
    for key, value in status.items():
        if key not in ['next_runs', 'philosophy']:
            print(f"  {key}: {value}")

    print(f"\n💬 Philosophy: {status['philosophy']}")

    print("\n📅 Scheduled Jobs:")
    for job_info in status['next_runs']:
        print(f"   {job_info['name']}")
        print(f"      Schedule: {job_info['schedule']}")
        print(f"      Next run: {job_info['next_run']}")
        print(f"      Runs: {job_info['run_count']}")
        print()

    # Test: run nightly_evolution manually
    print("\n🧬 Testing: Running nightly_evolution manually...")

    nightly_job = next(j for j in scheduler.jobs if j.job_id == 'nightly_evolution')
    run = scheduler.run_job(nightly_job)

    print(f"\n📊 Run Result:")
    print(f"   Status: {run.status}")
    print(f"   Duration: {run.duration_seconds:.1f}s")
    if run.result:
        print(f"   Result: {json.dumps(run.result, indent=6)}")

    print("\n✅ Scheduler ready for nightly cycles")
