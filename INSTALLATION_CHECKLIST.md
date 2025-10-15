# EvoAgentX GUI - Installation Checklist

## ✅ What You Already Have

Based on our earlier work, you already have:

- ✅ **Ollama** - Running and confirmed
- ✅ **Ollama Models** - deepseek-r1:14b and qwen2.5-coder:7b installed
- ✅ **Python venv** - Located at `../venv` with all EvoAgentX modules
- ✅ **Python Dependencies** - evaluator_v2, bandit_controller, etc.

---

## 📦 What You Need to Install

### 1. **Rust** (for Tauri)

**Check if installed:**
```bash
rustc --version
cargo --version
```

**If not installed:**
```bash
# macOS/Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Follow prompts, then:
source $HOME/.cargo/env
```

**Expected output:**
```
rustc 1.75.0 (or newer)
cargo 1.75.0 (or newer)
```

---

### 2. **Node.js & pnpm** (for React frontend)

**Check if installed:**
```bash
node --version
pnpm --version
```

**If not installed:**
```bash
# Install Node.js (macOS)
brew install node

# Install pnpm
npm install -g pnpm
```

**Expected output:**
```
node v20.x.x (or newer)
pnpm 8.x.x (or newer)
```

---

### 3. **Tauri CLI** (build tool)

**Install:**
```bash
cargo install tauri-cli
```

**Or use via pnpm:**
```bash
# This will be installed automatically when you run pnpm install
```

---

### 4. **Python Dependencies** (Flask for backend API)

**Install additional packages:**
```bash
source ../venv/bin/activate
pip install flask flask-cors psutil
```

**Verify:**
```bash
python -c "import flask, flask_cors, psutil; print('✅ All Python deps installed')"
```

---

### 5. **System Dependencies** (Tauri requirements)

**macOS:**
```bash
# Install Xcode Command Line Tools (if not already)
xcode-select --install

# Install additional dependencies
brew install pkg-config
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev
```

---

## 🚫 What You DON'T Need

❌ **API Keys** - Everything runs locally
❌ **Cloud Accounts** - No cloud services used
❌ **Internet Connection** - Offline-capable after initial install
❌ **Login Credentials** - No authentication required
❌ **Database Setup** - Uses local JSONL files
❌ **Docker** - Native binaries only

---

## 🧪 Quick Verification Script

Run this to check everything:

```bash
cd sprint_1hour

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "EVOAGENTX GUI - DEPENDENCY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# 1. Rust
echo "1. Rust:"
if command -v rustc &> /dev/null; then
    echo "   ✅ rustc $(rustc --version | awk '{print $2}')"
else
    echo "   ❌ Rust not found - install from https://rustup.rs"
fi

# 2. Cargo
if command -v cargo &> /dev/null; then
    echo "   ✅ cargo $(cargo --version | awk '{print $2}')"
else
    echo "   ❌ Cargo not found"
fi

# 3. Node.js
echo
echo "2. Node.js:"
if command -v node &> /dev/null; then
    echo "   ✅ node $(node --version)"
else
    echo "   ❌ Node.js not found - install from https://nodejs.org"
fi

# 4. pnpm
echo
echo "3. pnpm:"
if command -v pnpm &> /dev/null; then
    echo "   ✅ pnpm $(pnpm --version)"
else
    echo "   ❌ pnpm not found - install: npm install -g pnpm"
fi

# 5. Python venv
echo
echo "4. Python venv:"
if [ -d "../venv" ]; then
    echo "   ✅ venv found at ../venv"
    source ../venv/bin/activate
    echo "   ✅ Python $(python --version | awk '{print $2}')"
else
    echo "   ❌ venv not found at ../venv"
fi

# 6. Python packages
echo
echo "5. Python packages:"
python -c "import flask" 2>/dev/null && echo "   ✅ flask" || echo "   ❌ flask (install: pip install flask)"
python -c "import flask_cors" 2>/dev/null && echo "   ✅ flask-cors" || echo "   ❌ flask-cors (install: pip install flask-cors)"
python -c "import psutil" 2>/dev/null && echo "   ✅ psutil" || echo "   ❌ psutil (install: pip install psutil)"

# 7. Ollama
echo
echo "6. Ollama:"
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama running at http://127.0.0.1:11434"
    # Check models
    if ollama list | grep -q "deepseek-r1:14b"; then
        echo "   ✅ deepseek-r1:14b installed"
    else
        echo "   ⚠️  deepseek-r1:14b missing (install: ollama pull deepseek-r1:14b)"
    fi
    if ollama list | grep -q "qwen2.5-coder:7b"; then
        echo "   ✅ qwen2.5-coder:7b installed"
    else
        echo "   ⚠️  qwen2.5-coder:7b missing (install: ollama pull qwen2.5-coder:7b)"
    fi
else
    echo "   ❌ Ollama not running (start: ollama serve)"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "If all checks pass, you're ready to run:"
echo "  ./scripts/start_ollama.sh"
echo "  ./scripts/start_backend.sh"
echo "  cd gui && pnpm install && pnpm tauri:dev"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

Save this as `check_dependencies.sh` and run:
```bash
chmod +x check_dependencies.sh
./check_dependencies.sh
```

---

## 🎯 Installation Order

**If starting from scratch:**

1. **Install Rust** (5 min)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

2. **Install Node.js & pnpm** (2 min)
   ```bash
   brew install node
   npm install -g pnpm
   ```

3. **Install Python packages** (1 min)
   ```bash
   source ../venv/bin/activate
   pip install flask flask-cors psutil
   ```

4. **Install GUI dependencies** (5 min)
   ```bash
   cd gui
   pnpm install
   ```

5. **Verify Ollama** (already done)
   ```bash
   ./scripts/start_ollama.sh
   ```

**Total time**: ~15 minutes

---

## 🚀 First Run

Once all dependencies installed:

```bash
# Terminal 1
./scripts/start_ollama.sh

# Terminal 2
./scripts/start_backend.sh

# Terminal 3
cd gui && pnpm tauri:dev
```

**Expected behavior:**
1. Ollama starts/confirms running
2. Backend API starts on http://127.0.0.1:8000
3. Tauri compiles Rust backend (first time: 2-5 min)
4. React dev server starts on http://localhost:1420
5. GUI window opens with quantum-psychedelic interface
6. Diagnostics auto-run and all checks pass ✅

---

## 🔧 Troubleshooting

### "cargo: command not found"
```bash
# Restart terminal or run:
source $HOME/.cargo/env
```

### "pnpm: command not found"
```bash
npm install -g pnpm
```

### "Tauri compilation failed"
```bash
# macOS: Install Xcode tools
xcode-select --install

# Linux: Install webkit dependencies (see System Dependencies above)
```

### "Backend not reachable"
```bash
# Check if Flask is installed
pip install flask flask-cors psutil

# Check if port 8000 is available
lsof -i :8000
```

---

## 📦 Optional: Production Build

Once everything works in dev mode:

```bash
cd gui
pnpm tauri:build
```

**Output locations:**
- **macOS**: `gui/src-tauri/target/release/bundle/macos/EvoAgentX.app`
- **Linux**: `gui/src-tauri/target/release/bundle/appimage/`
- **Windows**: `gui/src-tauri/target/release/bundle/msi/`

**Build time**: 5-10 minutes (first time)

---

## ✅ Final Checklist

- [ ] Rust installed (`rustc --version` works)
- [ ] Node.js installed (`node --version` works)
- [ ] pnpm installed (`pnpm --version` works)
- [ ] Python venv activated (`source ../venv/bin/activate`)
- [ ] Flask packages installed (`pip install flask flask-cors psutil`)
- [ ] Ollama running (`curl http://127.0.0.1:11434/api/tags` succeeds)
- [ ] Models installed (deepseek-r1:14b, qwen2.5-coder:7b)
- [ ] GUI dependencies installed (`cd gui && pnpm install`)

**Once all checked:**
```bash
./scripts/start_ollama.sh && ./scripts/start_backend.sh &
cd gui && pnpm tauri:dev
```

🎉 **You're ready to explore the Quantum Unknown!** 🚀
