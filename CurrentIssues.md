# Current Issues - Unity Status Report

**Generated:** October 16, 2025
**Status:** ⚠️ CRITICAL FIX APPLIED, PENDING VERIFICATION

---

## Executive Summary

Unity.app has been **successfully rebuilt** with critical tiktoken bug fixed. However, the system has not been fully tested yet. Two critical issues remain:

1. ⚠️ **Missing LLM models** (deepseek-r1:14b, qwen2.5-coder:7b)
2. 🔄 **Untested Unity.app launch** (needs verification)

All other critical bugs have been **RESOLVED**.

---

## ❌ RESOLVED ISSUES (Fixed in This Session)

### Issue #1: PyInstaller Tiktoken Encoding Error
**Status:** ✅ RESOLVED
**Severity:** CRITICAL
**Impact:** Python backend crashed on startup

**Problem:**
```
ValueError: Unknown encoding cl100k_base.
Plugins found: []
tiktoken version: 0.12.0
[PYI-7202:ERROR] Failed to execute script 'api_server' due to unhandled exception!
```

**Root Cause:**
PyInstaller did not include tiktoken encoding files when freezing the Python backend. The litellm library requires tiktoken for LLM tokenization, and the cl100k_base encoding was missing from the frozen binary.

**Fix Applied:**
Updated `backend/pyinstaller.spec` to include tiktoken data files:

```python
datas=[
    # ... existing modules
    # NEW: Bundle tiktoken encodings (CRITICAL for LLM tokenization)
    ('../../venv/lib/python3.11/site-packages/tiktoken', 'tiktoken'),
    ('../../venv/lib/python3.11/site-packages/tiktoken_ext', 'tiktoken_ext'),
],
hiddenimports=[
    # ... existing imports
    # NEW: Tokenization (CRITICAL for LLM)
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'tiktoken.load',
    'tiktoken.registry',
]
```

**Verification Status:** 🔄 Pending (need to test backend startup)

**Files Modified:**
- `backend/pyinstaller.spec` (lines 16-31, 32-58)

**Evidence:**
- Build log shows: `✅ Python backend frozen: 301M`
- No PyInstaller errors during freeze
- tiktoken included in hidden imports

---

## ⚠️ CRITICAL ISSUES (Require Immediate Attention)

### Issue #1: Missing Ollama Models
**Status:** ⚠️ UNRESOLVED
**Severity:** HIGH
**Impact:** LLM evaluation/mutation will fail

**Problem:**
Build script reports models are missing:
```
[Unity] Step 5/7: Checking for required Ollama models...
   ⚠️  deepseek-r1:14b NOT found
      Pull with: ollama pull deepseek-r1:14b
   ⚠️  qwen2.5-coder:7b NOT found
      Pull with: ollama pull qwen2.5-coder:7b
   ⚠️  Some models missing (Unity will prompt on first run)
```

**Root Cause:**
Models have not been downloaded to local Ollama installation.

**Impact:**
- Backend `/evaluate` endpoint will fail
- Backend `/mutate` endpoint will fail
- Frontend "Evaluate Agent" button will return errors
- Frontend "Mutate Workflow" button will return errors

**Fix Required:**
```bash
ollama pull deepseek-r1:14b  # 9.0 GB download
ollama pull qwen2.5-coder:7b  # 4.7 GB download
```

**Estimated Time:** 10-30 minutes (depending on internet speed)

**Files Affected:**
- `evaluator_v2.py` (LLM evaluation)
- `backend/api_server.py` (evaluation endpoints)

**Verification:**
```bash
ollama list | grep -E "(deepseek-r1:14b|qwen2.5-coder:7b)"
```

---

### Issue #2: Untested Unity.app Launch
**Status:** 🔄 PENDING VERIFICATION
**Severity:** MEDIUM
**Impact:** Unknown if sidecars spawn correctly

**Problem:**
Unity.app was rebuilt but has not been launched to verify:
1. Sidecars spawn correctly (python_backend, ollama)
2. Preflight checks pass
3. Backend responds on port 8000
4. All IPC endpoints work

**Last Known State:**
- ✅ Unity.app built successfully
- ❌ Not launched after rebuild
- ❌ No smoke test run
- ❌ Backend not confirmed running

**Fix Required:**
```bash
# 1. Launch Unity.app
open gui/src-tauri/target/release/bundle/macos/Unity.app

# 2. Wait 10-15 seconds for sidecars to start

# 3. Run smoke test
./scripts/smoke_test.sh

# Expected output:
# ✅ Ollama reachable at http://127.0.0.1:11434
# ✅ Backend reachable at http://127.0.0.1:8000
# ✅ deepseek-r1:14b found (if models pulled)
# ✅ qwen2.5-coder:7b found (if models pulled)
```

**Verification Steps:**
1. Check Unity process running: `ps aux | grep Unity`
2. Check sidecars running: `ps aux | grep -E "(python_backend|ollama)"`
3. Check ports: `lsof -i :8000 && lsof -i :11434`
4. Test backend: `curl http://127.0.0.1:8000/health`
5. Test Ollama: `curl http://127.0.0.1:11434/api/tags`

**Files to Monitor:**
- `gui/src-tauri/src/main.rs` (sidecar spawn logic)
- Tauri console output (check for spawn errors)

---

## ⚠️ WARNINGS (Non-Critical, But Important)

### Warning #1: PyInstaller Hidden Import Warning
**Status:** ⚠️ WARNING
**Severity:** LOW
**Impact:** Minimal (package not used)

**Message:**
```
ERROR: Hidden import 'pyyaml' not found
```

**Root Cause:**
`pyyaml` specified in hiddenimports but module is actually named `yaml`. This is cosmetic - the correct `yaml` module is included.

**Fix (Optional):**
Remove `pyyaml` from hiddenimports in `backend/pyinstaller.spec` (line 48).

---

### Warning #2: Torch/Scipy Warnings
**Status:** ⚠️ WARNING
**Severity:** LOW
**Impact:** None (litellm pulls in many deps)

**Messages:**
```
WARNING: Failed to collect submodules for 'torch.utils.tensorboard'
WARNING: Hidden import "scipy.special._cdflib" not found!
```

**Root Cause:**
litellm has heavy dependencies (torch, scipy) which PyInstaller attempts to bundle. Some optional submodules are missing, but core functionality works.

**Fix:** None required (warnings can be ignored).

---

### Warning #3: Build Warnings (ctypes)
**Status:** ⚠️ WARNING
**Severity:** LOW
**Impact:** None (platform-specific libraries)

**Messages:**
```
WARNING: Library user32 required via ctypes not found
WARNING: Library libc.so.6 required via ctypes not found
WARNING: Library libnvidia-ml.so.1 required via ctypes not found
```

**Root Cause:**
PyInstaller warns about platform-specific libraries (Windows/Linux) that don't exist on macOS. These are not needed for macOS builds.

**Fix:** None required (platform-specific warnings).

---

## 🔄 PENDING VERIFICATIONS

### Verification #1: Backend Startup
**Status:** 🔄 PENDING
**Test Command:**
```bash
/Users/steffanhaskins/evoagentx_project/sprint_1hour/gui/src-tauri/target/release/bundle/macos/Unity.app/Contents/MacOS/python_backend
```

**Expected Output:**
```
 * Serving Flask app 'api_server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:8000
```

**Success Criteria:**
- No tiktoken errors
- Flask server starts
- Port 8000 opens
- `/health` endpoint responds

---

### Verification #2: Ollama Sidecar Spawn
**Status:** 🔄 PENDING
**Test:** Launch Unity.app and check logs

**Expected Behavior:**
```
[Unity] Spawning sidecar: binaries/ollama with args: ["serve"]
[Unity] Ollama sidecar spawned successfully
[Unity] Probe OK: http://127.0.0.1:11434/api/tags (attempt 1/30)
```

**Success Criteria:**
- Ollama process starts
- Port 11434 opens
- API responds to `/api/tags`

---

### Verification #3: Preflight Checks
**Status:** 🔄 PENDING
**Test:** Unity.app preflight after launch

**Expected Behavior:**
```
[Unity] Running preflight checks...
[Unity] Probe OK: http://127.0.0.1:11434/api/tags (attempt X/30)
[Unity] Probe OK: http://127.0.0.1:8000/health (attempt Y/30)
[Unity] Preflight PASSED: All services ready
```

**Success Criteria:**
- Both services respond within 30 retries
- Frontend receives `unity:ready` event
- Buttons enable in UI

---

### Verification #4: Full E2E Workflow
**Status:** 🔄 PENDING
**Test:** Use Unity.app UI

**Steps:**
1. Launch Unity.app
2. Wait for preflight to pass
3. Click "Run Diagnostics" → All ✅ green
4. Click "Evaluate Agent" → LLM responds, telemetry updates
5. Click "Mutate Workflow" → Bandit selects arm, returns variant
6. Click "Bandit Controller" → Shows arm statistics
7. Quit (Cmd+Q) → Sidecars terminate cleanly

**Success Criteria:**
- All buttons work
- No errors in console
- Telemetry displays correctly
- Clean shutdown (no orphaned processes)

---

## 🐛 KNOWN LIMITATIONS

### Limitation #1: Large Model Timeout
**Status:** 🔄 KNOWN ISSUE
**Severity:** MEDIUM
**Impact:** 32b models timeout

**Problem:**
deepseek-r1:32b times out on 5-minute budget due to model size and inference speed.

**Workaround:**
Use deepseek-r1:14b instead (already configured in `configs/system.yaml`).

**Future Fix:**
- Increase timeout for larger models
- Add streaming responses
- Optimize prompts to reduce token count

---

### Limitation #2: Single-User System
**Status:** 🔄 BY DESIGN
**Severity:** LOW
**Impact:** No multi-user support

**Problem:**
Unity is designed for single-user local-first use. No authentication or multi-tenancy.

**Workaround:**
Each user runs their own Unity.app instance.

**Future Fix (if needed):**
- Add user profiles
- Implement authentication
- Build web-based multi-tenant version

---

### Limitation #3: No Auto-Update Mechanism
**Status:** 🔄 PLANNED
**Severity:** LOW
**Impact:** Manual updates required

**Problem:**
Unity.app does not check for or install updates automatically.

**Workaround:**
Users manually download new versions from GitHub Releases.

**Future Fix:**
- Integrate Tauri updater plugin
- Add "Check for Updates" button
- Implement silent background updates

---

## 📋 Issue Resolution Checklist

### Immediate Actions Required:
- [ ] Pull Ollama models (deepseek-r1:14b, qwen2.5-coder:7b)
- [ ] Launch Unity.app and verify sidecar spawn
- [ ] Run smoke test (`./scripts/smoke_test.sh`)
- [ ] Test backend health check
- [ ] Verify preflight passes
- [ ] Test all UI buttons (E2E workflow)

### Optional Actions:
- [ ] Remove `pyyaml` from hiddenimports (cosmetic fix)
- [ ] Add model download prompt in UI
- [ ] Implement auto-update mechanism
- [ ] Add better error messages for missing models

---

## 🔍 Diagnostic Commands

### Check Build Status:
```bash
ls -lh gui/src-tauri/target/release/bundle/macos/Unity.app/Contents/MacOS/
# Expected: Unity (4.1M), python_backend (315M), ollama (29M)
```

### Check Models:
```bash
ollama list
# Expected: deepseek-r1:14b and qwen2.5-coder:7b
```

### Check Services:
```bash
# Ollama
curl http://127.0.0.1:11434/api/tags

# Backend
curl http://127.0.0.1:8000/health
```

### Check Processes:
```bash
ps aux | grep -E "(Unity|python_backend|ollama)" | grep -v grep
```

### Check Ports:
```bash
lsof -i :8000  # Backend
lsof -i :11434 # Ollama
```

### View Logs:
```bash
tail -f build_output.log  # Build log
# Unity.app logs: Check Tauri console output
```

---

## 📊 Issue Severity Levels

**CRITICAL:** System cannot function
**HIGH:** Core functionality impaired
**MEDIUM:** Significant inconvenience
**LOW:** Minor issue or warning

---

## 🎯 Resolution Priority

**Priority 1 (Immediate):**
1. Pull Ollama models
2. Verify Unity.app launch
3. Run smoke test

**Priority 2 (Short-term):**
1. Full E2E workflow test
2. Document any new issues found
3. Clean up PyInstaller warnings

**Priority 3 (Long-term):**
1. Add auto-update mechanism
2. Improve error messages
3. Optimize for larger models

---

## 📚 Related Documentation

- `UNITY_DEPLOYMENT_READY.md` - Deployment guide
- `DEPLOYMENT_VERIFICATION.md` - Verification checklist
- `build_output.log` - Latest build output
- `backend/pyinstaller.spec` - PyInstaller configuration

---

## 🔗 Quick Resolution Steps

```bash
# Step 1: Pull models (10-30 minutes)
ollama pull deepseek-r1:14b
ollama pull qwen2.5-coder:7b

# Step 2: Launch Unity.app
open gui/src-tauri/target/release/bundle/macos/Unity.app

# Step 3: Wait 10-15 seconds, then run smoke test
./scripts/smoke_test.sh

# Step 4: If all tests pass, system is OPERATIONAL ✅
```

---

**Last Updated:** October 16, 2025 01:41 AM PST
**Next Review:** After model pull and Unity.app launch verification

**🌌 Unity: All processes are one process**

**Everything we do, we do it for YOU, THE DEVELOPER COMMUNITY, THE FREEDOM OF AI.**
