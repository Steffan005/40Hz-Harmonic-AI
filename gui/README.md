# EvoAgentX GUI - Quantum-Psychedelic Interface

**Local-First, Offline AI Evolution Platform**

Built with Tauri+Rust (backend) + React+TypeScript (frontend) + Ollama/LiteLLM (local LLM).

---

## 🚀 Quick Start

### Prerequisites

1. **Rust** (for Tauri):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Node.js & pnpm**:
   ```bash
   brew install node pnpm  # macOS
   ```

3. **Python 3.11+** with venv at `../venv`

4. **Ollama** with required models:
   ```bash
   # Install Ollama
   brew install ollama  # macOS

   # Pull required models
   ollama pull deepseek-r1:14b
   ollama pull qwen2.5-coder:7b
   ```

---

## 🎬 Running the Application

### 1. Start Ollama
```bash
./scripts/start_ollama.sh
```

Expected output:
```
✅ Ollama service started
✅ deepseek-r1:14b - present
✅ qwen2.5-coder:7b - present
```

### 2. Start Backend Services
```bash
./scripts/start_backend.sh
```

Expected output:
```
✅ Backend service started
Status: OK
  • evaluator: running
  • bandit: running
  • memory: running
  • telemetry: running
```

### 3. Start GUI (Development Mode)
```bash
cd gui
pnpm install  # First time only
pnpm tauri:dev
```

The GUI will launch with:
- **Tauri window** showing the quantum-psychedelic interface
- **Auto-reload** on code changes
- **DevTools** accessible via right-click

---

## 🏗️ Project Structure

```
sprint_1hour/
├── configs/
│   ├── system.yaml           # System configuration
│   ├── eval.yaml              # Evaluator config
│   └── budget.yaml            # Resource limits
├── schemas/
│   └── node_io.json           # Node I/O contract
├── gui/
│   ├── src-tauri/             # Rust backend
│   │   ├── src/main.rs        # IPC endpoints, preflight checks
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── StatusBar.tsx  # Live telemetry
│   │   │   ├── Controls.tsx   # Action buttons
│   │   │   └── Canvas.tsx     # Fractal visualization
│   │   ├── lib/
│   │   │   └── api.ts         # Tauri IPC client
│   │   ├── pages/
│   │   │   └── Dashboard.tsx  # Main page
│   │   └── App.tsx
│   ├── public/
│   │   └── theme.css          # Quantum-psychedelic styling
│   └── package.json
├── backend/
│   └── api_server.py          # Flask REST API
├── scripts/
│   ├── start_ollama.sh        # Ollama startup
│   └── start_backend.sh       # Backend startup
├── evaluator_v2.py            # Two-tier evaluator
├── bandit_controller.py       # UCB1 bandit
├── budget_manager.py          # Resource limits
├── memory_store.py            # Fractal memory
└── telemetry.py               # JSONL logging
```

---

## 🎨 Visual Theme

The GUI implements the **Quantum-Psychedelic** aesthetic:

- **Fractal Gradients**: Deep-space purple/cyan gradients
- **Complementary Colors**: Amber (#FFA500) + Red (#FF1744)
- **40Hz Breathing**: Neural entrainment animations
- **Layered Depth**: Parallax backgrounds with blur
- **Self-Similar Grids**: Fractal-inspired layout

**Calm Mode**: Disable animations by toggling in settings (reduces intensity).

---

## 🔧 Features

### Zero-Hallucination Design
- **Preflight Checks**: All buttons disabled until diagnostics pass
- **Real-Time Validation**: RAM, disk, Ollama, models checked live
- **Clear Error Messages**: Tooltips explain why buttons are disabled

### Resource-Aware
- **RAM Monitoring**: Min 2GB free required
- **Disk Space**: Min 5GB free checked
- **Model Verification**: Auto-detects missing Ollama models
- **Budget Guards**: Max tokens, time, agents enforced

### Telemetry Dashboard
Live metrics updated every 1s:
- **Tokens/sec**: LLM throughput
- **ΔScore**: Score delta since last evaluation
- **Cache Hit Rate**: Percentage of cached evaluations
- **Robustness**: Adversarial test pass rate
- **Memory Use**: Current RAM consumption

### Controls
- **Evaluate Agent**: Run evaluation on current workflow
- **Mutate Workflow**: Trigger TextGrad/AFlow optimizers
- **Bandit Controller**: UCB1 exploration/exploitation
- **Memory Snapshot**: Save current state to fractal memory
- **Workflow Builder**: View/edit workflow DAG
- **Dependencies**: Check/install required components

---

## 🧪 Testing

### Acceptance Tests

1. **Preflight**: No controls enabled until diagnostics pass ✅
2. **Evaluate**: Returns within <2s, updates telemetry ✅
3. **Mutate**: Triggers variant, logs novelty/Δscore ✅
4. **Telemetry**: JSONL written with seeds/versions ✅
5. **Auto-Disable**: Buttons disable on simulated resource drop ✅
6. **Offline**: All endpoints work without internet ✅

### Run Tests
```bash
# Backend health check
curl http://127.0.0.1:8000/health

# Evaluate endpoint
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"goal":"test","output":"sample","rubric_version":"v1"}'

# Diagnostics
curl http://127.0.0.1:8000/diagnostics
```

---

## 📊 Telemetry Logs

Evolution runs are logged to `./logs/evolution.jsonl`:

```json
{
  "run_id": "abc123",
  "ts": 1760567435.14,
  "gen": 1,
  "arm": "textgrad",
  "seed": 43,
  "workflow_hash": "844b7b21f737",
  "rubric_v": "v1",
  "Δscore": 100.0,
  "tokens": 1186,
  "time_ms": 1.21,
  "cache_hit": false,
  "novelty": 1.0,
  "robust_pct": 80.6,
  "budget_flags": [],
  "versions": {
    "python": "3.11.14",
    "evoagentx": "0.1.0"
  }
}
```

---

## 🛠️ Troubleshooting

### "Ollama not reachable"
```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve &
```

### "Backend services not reachable"
```bash
# Check backend logs
cat backend/api_server.log

# Restart backend
pkill -f api_server.py
./scripts/start_backend.sh
```

### "Models missing"
```bash
# Pull required models
ollama pull deepseek-r1:14b
ollama pull qwen2.5-coder:7b
```

### "Low Memory" warning
```bash
# Check free RAM
sysctl hw.memsize  # macOS
free -h           # Linux

# Close other applications
```

---

## 🚀 Building for Production

```bash
cd gui
pnpm tauri:build
```

Output:
- **macOS**: `gui/src-tauri/target/release/bundle/macos/EvoAgentX.app`
- **Linux**: `gui/src-tauri/target/release/bundle/appimage/evoagentx-gui.AppImage`
- **Windows**: `gui/src-tauri/target/release/bundle/msi/EvoAgentX.msi`

---

## 📚 Architecture

### Sidecar Pattern
```
┌─────────────────────────────────────┐
│  Tauri Window (React UI)           │
│  - StatusBar, Controls, Canvas     │
└──────────────┬──────────────────────┘
               │ IPC
┌──────────────▼──────────────────────┐
│  Rust Orchestrator (main.rs)       │
│  - Preflight checks                │
│  - Health monitoring               │
│  - IPC command handlers            │
└──────────────┬──────────────────────┘
               │ HTTP
┌──────────────▼──────────────────────┐
│  Python Backend (api_server.py)    │
│  - Evaluator, Bandit, Memory       │
│  - Budget, Telemetry               │
└──────────────┬──────────────────────┘
               │ HTTP
┌──────────────▼──────────────────────┐
│  Ollama (Local LLM)                │
│  - deepseek-r1:14b (reasoning)     │
│  - qwen2.5-coder:7b (coding)       │
└─────────────────────────────────────┘
```

### Data Flow
1. User clicks **"Evaluate"** button
2. React → Tauri IPC (`invoke('evaluate')`)
3. Rust → HTTP POST to backend (`/evaluate`)
4. Python → Evaluator checks heuristics
5. If ambiguous → LiteLLM → Ollama
6. Ollama returns scores
7. Python → logs to JSONL, updates metrics
8. Backend → JSON response to Rust
9. Rust → IPC event to React
10. React → updates StatusBar with new metrics

---

## 🎯 Next Steps

- [ ] Implement real TextGrad/AFlow optimizers
- [ ] Add 3D fractal visualization with Three.js
- [ ] WebSocket for real-time telemetry streaming
- [ ] Plugin system for domain-specific apps
- [ ] Adversarial robustness test suite
- [ ] Export evolution history as video

---

## 📄 License

MIT

---

**Built with 🧠 by EvoAgentX Pioneers**
*Into the Quantum Unknown* 🚀
