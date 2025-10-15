# EvoAgentX - Quantum Evolution GUI

**Local-first AI evolution framework with quantum-psychedelic interface**

> *Everything we do, we do it for YOU, THE DEVELOPER COMMUNITY, THE FREEDOM OF AI*

![EvoAgentX](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-orange)

## 🌌 What is EvoAgentX?

EvoAgentX is a **zero-cloud, privacy-first** AI evolution framework with a Tauri+Rust GUI. It combines:

- **Local LLM Integration**: Ollama-powered reasoning (DeepSeek-R1 14b) and coding (Qwen2.5-Coder 7b)
- **Multi-Armed Bandit**: UCB1 strategy selection for optimization
- **Two-Tier Evaluation**: Fast heuristics + LLM judge with caching
- **Fractal Memory**: Hierarchical summarization with full artifact storage
- **Quantum-Psychedelic UI**: 40Hz neural entrainment, fractal visualizations, layered parallax

### Key Features

✅ **No API Keys** - Completely offline-capable
✅ **No Cloud Dependencies** - All data stored locally
✅ **Zero-Hallucination Design** - Buttons disabled until preflight passes
✅ **Resource-Aware** - RAM, disk, and model checks before execution
✅ **Telemetry-Driven** - Real-time metrics (tokens/sec, cache hit, memory)
✅ **JSONL Logging** - Reproducible evolution with seeds and versions

## 🚀 Quick Start

### Prerequisites

Install these tools (one-time setup):

```bash
# 1. Rust (for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# 2. Node.js & pnpm (for React frontend)
brew install node
npm install -g pnpm

# 3. Python dependencies (for backend)
source ../venv/bin/activate
pip install flask flask-cors psutil

# 4. Ollama models
ollama pull deepseek-r1:14b
ollama pull qwen2.5-coder:7b
```

### Verify Setup

```bash
cd sprint_1hour
./check_dependencies.sh
```

**Expected output**: All ✅ green checks

### Launch

Open **3 terminals**:

**Terminal 1 - Ollama:**
```bash
./scripts/start_ollama.sh
```

**Terminal 2 - Backend:**
```bash
./scripts/start_backend.sh
```

**Terminal 3 - GUI:**
```bash
cd gui
pnpm tauri:dev
```

### First Launch

1. **Rust compilation** (first time: 2-5 min) - "Compiling evoagentx-gui..."
2. **React dev server** starts on http://localhost:1420
3. **GUI window opens** with quantum-psychedelic interface
4. **Preflight diagnostics** run automatically
5. **All buttons enable** once checks pass ✅

## 🎮 Using the GUI

### Status Bar (Top)
- **Tokens/sec**: Real-time LLM throughput
- **ΔScore**: Score improvement tracking
- **Cache Hit**: Evaluation efficiency %
- **Robust**: Adversarial test pass rate
- **Memory**: RAM usage

### Control Panel (Left)

**System:**
- **Run Diagnostics** - Verify RAM, Ollama, models, backend

**Core Actions:**
- **Evaluate Agent** - Run heuristics + LLM judge on current workflow
- **Mutate Workflow** - Generate new workflow variant via bandit selection
- **Bandit Controller** - View arm statistics and policy
- **Memory Snapshot** - Save current state to JSON

**Workflow:**
- **Workflow Builder** - Construct custom agent workflows
- **Dependencies** - View workflow DAG

### Fractal Canvas (Center)
- Pulsing gradient sphere with 40Hz breathing animation
- Shows active node count
- Responds to system activity

### Telemetry Panel (Right Top)
- **System Status**: OPERATIONAL / WARNING / ERROR
- **LLM Backend**: Ollama Local
- **Mode**: OFFLINE (no cloud)

### Console (Right Bottom)
- Live logs with timestamps
- Color-coded: info (blue), success (green), warning (yellow), error (red)

## 🧪 Quick Test

Once GUI opens:

1. **Click "Run Diagnostics"** → All ✅ green (RAM, Ollama, Models, Backend)
2. **Click "Evaluate Agent"** → Console logs scores, telemetry updates
3. **Click "Mutate Workflow"** → Returns arm ID and novelty score
4. **Click "Bandit Controller"** → Shows arm statistics
5. **Watch Status Bar** → Metrics update every 1 second

## 📁 Project Structure

```
sprint_1hour/
├── configs/
│   ├── system.yaml      # Models, budgets, diagnostics
│   └── eval.yaml        # Evaluation heuristics, LLM judge
├── backend/
│   └── api_server.py    # Flask REST API (8 endpoints)
├── gui/
│   ├── src/
│   │   ├── components/  # Controls, StatusBar, Canvas, etc.
│   │   ├── pages/       # Dashboard layout
│   │   ├── lib/         # api.ts (Tauri IPC client)
│   │   └── main.tsx     # React entry point
│   ├── src-tauri/
│   │   └── src/
│   │       └── main.rs  # Rust orchestrator (600 lines)
│   └── public/
│       └── theme.css    # Quantum-psychedelic styles
├── scripts/
│   ├── start_ollama.sh  # Verify Ollama + models
│   └── start_backend.sh # Start Flask API
├── logs/
│   ├── evolution.jsonl  # Generation-by-generation metrics
│   └── budget.jsonl     # Resource usage events
└── check_dependencies.sh # Verify all prerequisites
```

## 🎨 Customization

### Models

Edit `configs/system.yaml`:

```yaml
models:
  reasoning: "ollama_chat/deepseek-r1:14b"  # Change to other Ollama model
  coding: "ollama_chat/qwen2.5-coder:7b"
  fallback: "ollama_chat/qwen2.5-coder:7b"
```

### Theme

Edit `gui/public/theme.css`:

```css
:root {
  --quantum-amber: #FFA500;    /* Change primary color */
  --quantum-red: #FF1744;      /* Change accent color */
  --breathing-duration: 25ms;  /* 40Hz = 1/0.025s */
}
```

Or toggle **Calm Mode** in GUI to disable animations.

### Resource Limits

Edit `configs/system.yaml`:

```yaml
budgets:
  max_tokens_per_gen: 12000   # Reduce for faster runs
  max_time_s: 300             # Max 5 minutes per operation
  max_agents: 10              # Concurrent agent limit
  max_concurrency: 2          # Parallel LLM calls
```

## 🏗️ Architecture

### Sidecar Pattern

```
┌─────────────────┐
│   React UI      │  ← User interactions
│  (TypeScript)   │
└────────┬────────┘
         │ Tauri IPC (invoke)
┌────────▼────────┐
│  Rust Backend   │  ← Orchestration, diagnostics
│  (600 lines)    │
└────────┬────────┘
         │ HTTP REST
┌────────▼────────┐
│  Python API     │  ← Core modules (evaluator, bandit, memory)
│  (Flask)        │
└────────┬────────┘
         │ HTTP API
┌────────▼────────┐
│     Ollama      │  ← LLM inference (local models)
└─────────────────┘
```

### IPC Endpoints

- `run_diagnostics()` → Checks RAM, disk, Ollama, models, backend
- `is_preflight_passed()` → Returns boolean (enables/disables buttons)
- `evaluate(request)` → Runs heuristics + LLM judge
- `mutate(request)` → Generates new workflow via bandit
- `get_bandit_status()` → Returns arm statistics
- `update_bandit_policy(policy)` → Changes bandit algorithm
- `create_memory_snapshot()` → Saves state to JSON
- `get_workflow_dag()` → Returns workflow graph

## 🔧 Development

### Run in Dev Mode

```bash
# Terminal 1
./scripts/start_ollama.sh

# Terminal 2
./scripts/start_backend.sh

# Terminal 3
cd gui && pnpm tauri:dev
```

### Build for Production

```bash
cd gui
pnpm tauri:build
```

**Output locations:**
- **macOS**: `gui/src-tauri/target/release/bundle/macos/EvoAgentX.app`
- **Linux**: `gui/src-tauri/target/release/bundle/appimage/`

## 🐛 Troubleshooting

### GUI doesn't open

```bash
cd gui
pnpm tauri:dev

# Check for Rust compilation errors
```

### "Backend not reachable"

```bash
# Check if backend running
curl http://127.0.0.1:8000/health

# If not, restart
pkill -f api_server
./scripts/start_backend.sh
```

### "Ollama not reachable"

```bash
# Check if Ollama running
curl http://127.0.0.1:11434/api/tags

# If not, start
ollama serve &
```

### Buttons stay disabled

```bash
# Run diagnostics
./check_dependencies.sh

# Check logs
tail -f logs/evolution.jsonl
```

### Model timeout (32b too large)

**Issue**: deepseek-r1:32b model takes too long to load and times out.

**Solution**: Use 14b model instead (already configured):

```bash
# Verify 14b is installed
ollama list | grep deepseek-r1:14b

# If missing
ollama pull deepseek-r1:14b
```

The system is **already configured** to use 14b in `configs/system.yaml`.

## 📊 Performance

### Model Sizes
- **deepseek-r1:14b**: 9.0 GB (recommended)
- **qwen2.5-coder:7b**: 4.7 GB
- **Total disk**: ~14 GB

### Runtime RAM
- **14b model**: ~6 GB
- **7b model**: ~3 GB
- **GUI + Backend**: ~500 MB
- **Recommended**: 16 GB system RAM

### Speed
- **Evaluation**: 1-3 seconds (with cache)
- **Mutation**: 2-5 seconds
- **First LLM call**: 5-10 seconds (model loading)

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Development workflow
- Code style guidelines
- Testing procedures
- Pull request process

## 📚 Documentation

- [Installation Checklist](./INSTALLATION_CHECKLIST.md)
- [Setup Status](./YOUR_SETUP_STATUS.md)
- [GUI Sprint Deliverables](./GUI_SPRINT_DELIVERABLES.md)

## 📄 License

MIT License - see [LICENSE](./LICENSE)

**Built for the developer community, by the developer community.**

## 🙏 Acknowledgments

This project embodies the principles of:
- **AI Freedom**: No cloud lock-in, no API keys, no tracking
- **Data Sovereignty**: Your data stays on your machine
- **Developer Empowerment**: Complete control and customization
- **Open Source**: Transparent, auditable, community-driven

---

**🚀 Welcome to the Quantum Unknown, Pioneer!**

*No internet, no cloud, no limits - just pure local AI evolution!*

## 🌟 Star History

If this project helps you, please consider starring it on GitHub! ⭐

## 📬 Contact

- GitHub Issues: [Report bugs or request features]
- Discussions: [Join the conversation]
- Contributing: See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

*"Everything we do, we do it for YOU, THE DEVELOPER COMMUNITY, THE FREEDOM OF AI"*
