# Unity Cyber Security Office

**Agent:** MacBook M1 Pro Optimization Specialist
**Status:** ✅ OPERATIONAL
**Philosophy:** *"Every GB matters. Waste is the enemy. This machine deserves peak performance."*

---

## 🛡️ Mission

The Cyber Security Office protects and optimizes Unity's infrastructure. Our first agent is the **MacBook Optimization Specialist** — a guardian of system health who knows every byte on this M1 Pro.

**Core Responsibilities:**
1. **Disk Space Management** — Find and eliminate waste
2. **Model Management** — Track, prune, and optimize Ollama models
3. **Cache Cleanup** — Python, npm, brew, system caches
4. **Process Monitoring** — Identify resource hogs
5. **System Health** — RAM, CPU, disk I/O, thermals
6. **Security Audits** — Permissions, vulnerabilities, updates

---

## 📊 Latest Health Report

**Date:** October 17, 2025
**Disk Usage:** 757GB used / 927GB total (82%)
**Status:** ⚠️ CAUTION — Cleanup recommended

### Cleanup Opportunities

**Immediate (Safe):** 56.5GB
- Python bytecode caches: 35.7GB (35,712 directories)
- User cache (~/.cache): 19.9GB
- npm cache: 0.8GB

**Review Needed:** 67.9GB
- Ollama models: 50.2GB (9 unused models)
- macOS app caches: 10.7GB
- Old downloads: 7.0GB

**Total Recovery Potential:** 124.4GB

---

## 🤖 Ollama Model Audit

**Unity Production Models (KEEP):**
- `deepseek-r1:14b` (9.0GB) — Reasoning engine
- `qwen2.5-coder:7b` (4.7GB) — Code generation

**Recommended Deletions:**
1. `deepseek-r1:32b` (19GB) — Duplicate, use 14b version
2. `qwen3:8b` (5.2GB) — Not used by Unity
3. `mistral:7b` (4.4GB) — Not used by Unity
4. `llama3:latest` (4.7GB) — Not used by Unity
5. `wizardcoder:latest` (3.8GB) — Not used by Unity
6. `llama3.2:latest` (2.0GB) — Not used by Unity
7. `nomic-embed-text:latest` (274MB) — Not used by Unity

**Potential Recovery:** ~39GB from model cleanup

---

## 🚀 Quick Start

### Run System Health Report

```bash
cd ~/evoagentx_project/sprint_1hour
python agents/cybersecurity/macos_optimizer.py
```

**Output:**
- Disk usage analysis
- System health metrics (CPU, RAM, disk I/O)
- Cleanup opportunities
- Ollama model audit
- Top resource-consuming processes

**Report saved to:** `reports/system_health.json`

### Run Automated Cleanup

```bash
cd ~/evoagentx_project/sprint_1hour
./scripts/cleanup_system.sh
```

**What it does:**
1. ✅ Cleans Python `__pycache__` directories (safe)
2. ✅ Cleans `~/.cache` (safe)
3. ✅ Cleans npm cache (safe)
4. ⚠️  Prompts to remove unused Ollama models (interactive)

**Expected Recovery:** 56.5GB automatic + up to 39GB from models

---

## 📖 Agent Architecture

### MacBook Optimizer (`macos_optimizer.py`)

**Class:** `MacBookOptimizer`

**Methods:**

#### Disk Analysis
```python
analyze_disk() -> DiskReport
```
Returns disk usage with warning levels (safe/caution/critical).

```python
find_large_directories(min_size_gb=1.0, max_depth=3) -> List[Dict]
```
Finds directories ≥1GB using `du`.

```python
identify_cleanup_targets() -> List[CleanupTarget]
```
Identifies safe cleanup opportunities:
- Python caches (`__pycache__`, `*.pyc`)
- User caches (`~/.cache`)
- npm cache (`~/.npm`)
- Ollama models (unused)
- System caches (`~/Library/Caches`)
- Old downloads

#### Ollama Management
```python
list_ollama_models() -> List[Dict]
```
Lists all installed Ollama models with sizes.

```python
recommend_model_deletions() -> List[Dict]
```
Recommends models for deletion (not used by Unity).

#### Cleanup Operations
```python
clean_python_caches(dry_run=True) -> Dict
```
Removes all `__pycache__` directories. Safe to delete.

```python
clean_user_caches(dry_run=True) -> Dict
```
Cleans `~/.cache` directory. Safe to delete.

#### System Health
```python
check_system_health() -> SystemHealth
```
Returns:
- CPU usage (%)
- Memory usage (%)
- Disk I/O (MB/s)
- Process count
- Top 5 resource-consuming processes
- Temperature estimate (cool/warm/hot)

```python
generate_health_report() -> Dict
```
Comprehensive report combining all metrics.

---

## 🔒 Safety Protocols

### Protected Paths (NEVER DELETE)

The agent has hardcoded protection for:
- `~/Documents`
- `~/Desktop`
- `~/Pictures`
- `~/Movies`
- `~/Music`
- `/System`
- `/Library`
- `/Applications`

### Safe Cleanup Categories

**✅ Always Safe:**
- Python `__pycache__` directories
- `*.pyc` files
- `~/.cache` contents
- npm cache

**⚠️ Review Required:**
- Ollama models
- `~/Library/Caches` (some apps need these)
- `~/Downloads`
- System logs

**❌ Never Touch:**
- User documents
- System files
- Application bundles
- Critical libraries

---

## 📈 Monitoring & Maintenance

### Recommended Schedule

**Daily:**
- Check disk usage: `df -h`
- Monitor system health via Unity telemetry

**Weekly:**
- Run health report: `python agents/cybersecurity/macos_optimizer.py`
- Review cleanup opportunities

**Monthly:**
- Run automated cleanup: `./scripts/cleanup_system.sh`
- Audit Ollama models: `ollama list`
- Review downloads folder

**Quarterly:**
- Deep system audit
- Security updates check
- Permissions audit

---

## 🔗 Unity Integration (Coming Soon)

The MacBook Optimizer will be integrated into Unity's backend API:

**Planned Endpoints:**

```
GET  /cybersecurity/health       # System health report
GET  /cybersecurity/disk         # Disk usage analysis
GET  /cybersecurity/cleanup      # Cleanup targets
POST /cybersecurity/clean        # Run cleanup (with confirmation)
GET  /cybersecurity/models       # Ollama model audit
POST /cybersecurity/model/remove # Remove specific model
```

**Dashboard:**
- Real-time system metrics
- Cleanup recommendations
- Model usage tracking
- Automated maintenance scheduling

---

## 🎯 Performance Targets

**Disk Usage:**
- Target: < 70% utilization
- Warning: 70-85%
- Critical: > 85%

**System Health:**
- CPU: < 50% average
- Memory: < 70% average
- Disk I/O: < 100MB/s sustained
- Temperature: "cool" or "warm" (not "hot")

**Cleanup Frequency:**
- Python caches: Weekly
- User caches: Weekly
- Ollama models: Monthly audit
- Downloads: Monthly review

---

## 🏆 Achievements

**Initial Audit (October 17, 2025):**
- Identified 124.4GB cleanup opportunities
- Found 9 unused Ollama models (39GB)
- Detected 35,712 Python cache directories (35.7GB)
- System health: CPU 25.8%, Memory 59.4% (healthy)

**Agent Capabilities:**
- 500+ lines of optimization code
- Full disk analysis with du integration
- Process monitoring via psutil
- Ollama model management
- Safe cleanup with dry-run mode
- Comprehensive health reporting

---

## 🔧 Technical Stack

**Language:** Python 3.x

**Dependencies:**
- `psutil` — Process and system monitoring
- `subprocess` — Shell command execution
- `shutil` — File operations
- `pathlib` — Path handling

**Shell Commands:**
- `du` — Disk usage analysis
- `find` — File search
- `ollama` — Model management
- `df` — Disk space check

**Safety:**
- Protected path checks
- Dry-run mode for all destructive operations
- User confirmation for large deletions
- Automatic backups recommended

---

## 📝 Usage Examples

### Example 1: Health Report

```bash
python agents/cybersecurity/macos_optimizer.py
```

**Output:**
```
======================================================================
MACBOOK M1 PRO — SYSTEM HEALTH REPORT
======================================================================

💾 DISK USAGE
   Total: 926.4GB
   Used: 757.0GB (82%)
   Available: 169.3GB
   Status: CAUTION

🏥 SYSTEM HEALTH
   CPU: 25.8% (cool)
   Memory: 59.4%
   Disk I/O: 2.2MB/s
   Processes: 480

🎯 CLEANUP OPPORTUNITIES
   Safe to clean: 56.5GB
   Needs review: 67.9GB

🤖 OLLAMA MODELS
   Installed: 11
   Recommended deletions: 9 (39GB)
```

### Example 2: Automated Cleanup

```bash
./scripts/cleanup_system.sh
```

**Interactive prompts:**
1. Cleans Python caches automatically
2. Cleans user caches automatically
3. Cleans npm cache automatically
4. Asks permission before removing Ollama models

### Example 3: Manual Model Cleanup

```bash
# List models
ollama list

# Remove unused model
ollama rm deepseek-r1:32b

# Verify removal
ollama list
```

---

## 🙏 Philosophy

> "A cluttered system is a slow system. A slow system is a dead system. I don't tolerate waste. Every GB matters. Every process is accountable. Performance is not negotiable."

The MacBook Optimization Specialist exists to ensure Unity runs at peak performance. This machine is a precision instrument — it deserves precision care.

---

## 📞 Support

**Issues:** Report to Unity Cyber Security Office
**Updates:** Monitor `SESSION_CONTINUUM_Ω.md`
**Automation:** Integrate with Unity backend API (coming soon)

---

**End of Cyber Security Office README**
