#!/usr/bin/env bash
# EvoAgentX GUI - Dependency Verification Script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "EVOAGENTX GUI - DEPENDENCY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

ALL_PASS=true

# 1. Rust
echo "1. Rust Toolchain:"
if command -v rustc &> /dev/null; then
    echo "   ✅ rustc $(rustc --version | awk '{print $2}')"
else
    echo "   ❌ Rust not found"
    echo "      Install: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    ALL_PASS=false
fi

if command -v cargo &> /dev/null; then
    echo "   ✅ cargo $(cargo --version | awk '{print $2}')"
else
    echo "   ❌ Cargo not found"
    ALL_PASS=false
fi

# 2. Node.js
echo
echo "2. Node.js:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ node $NODE_VERSION"
else
    echo "   ❌ Node.js not found"
    echo "      Install: brew install node"
    ALL_PASS=false
fi

# 3. pnpm
echo
echo "3. pnpm:"
if command -v pnpm &> /dev/null; then
    echo "   ✅ pnpm $(pnpm --version)"
else
    echo "   ❌ pnpm not found"
    echo "      Install: npm install -g pnpm"
    ALL_PASS=false
fi

# 4. Python venv
echo
echo "4. Python Environment:"
if [ -d "../venv" ]; then
    echo "   ✅ venv found at ../venv"
    source ../venv/bin/activate 2>/dev/null || true
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "   ✅ Python $PYTHON_VERSION"
else
    echo "   ❌ venv not found at ../venv"
    echo "      Create: python3 -m venv ../venv"
    ALL_PASS=false
fi

# 5. Python packages
echo
echo "5. Python Packages:"

# Activate venv if exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

if python -c "import flask" 2>/dev/null; then
    echo "   ✅ flask"
else
    echo "   ❌ flask"
    echo "      Install: pip install flask"
    ALL_PASS=false
fi

if python -c "import flask_cors" 2>/dev/null; then
    echo "   ✅ flask-cors"
else
    echo "   ❌ flask-cors"
    echo "      Install: pip install flask-cors"
    ALL_PASS=false
fi

if python -c "import psutil" 2>/dev/null; then
    echo "   ✅ psutil"
else
    echo "   ❌ psutil"
    echo "      Install: pip install psutil"
    ALL_PASS=false
fi

# Check existing modules
if python -c "from evaluator_v2 import EvaluatorV2" 2>/dev/null; then
    echo "   ✅ evaluator_v2"
else
    echo "   ⚠️  evaluator_v2 (may not be in path)"
fi

# 6. Ollama
echo
echo "6. Ollama:"
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama running at http://127.0.0.1:11434"

    # Check models
    MODELS=$(curl -s http://127.0.0.1:11434/api/tags 2>/dev/null)

    # Check for 14b model (correct version - 32b too large)
    if echo "$MODELS" | grep -q "deepseek-r1:14b" || ollama list 2>/dev/null | grep -q "deepseek-r1:14b"; then
        echo "   ✅ deepseek-r1:14b installed (optimal performance)"
    else
        echo "   ⚠️  deepseek-r1:14b missing"
        echo "      Install: ollama pull deepseek-r1:14b"
    fi

    # Note if 32b is present (too large, will timeout)
    if echo "$MODELS" | grep -q "deepseek-r1:32b" || ollama list 2>/dev/null | grep -q "deepseek-r1:32b"; then
        echo "   ℹ️  deepseek-r1:32b detected (not used - too large)"
    fi

    if echo "$MODELS" | grep -q "qwen2.5-coder:7b" || ollama list 2>/dev/null | grep -q "qwen2.5-coder:7b"; then
        echo "   ✅ qwen2.5-coder:7b installed"
    else
        echo "   ⚠️  qwen2.5-coder:7b missing"
        echo "      Install: ollama pull qwen2.5-coder:7b"
    fi
else
    echo "   ❌ Ollama not running"
    echo "      Start: ollama serve"
    ALL_PASS=false
fi

# 7. System info
echo
echo "7. System Info:"
if command -v sw_vers &> /dev/null; then
    # macOS
    echo "   Platform: macOS $(sw_vers -productVersion)"
elif [ -f /etc/os-release ]; then
    # Linux
    . /etc/os-release
    echo "   Platform: $NAME $VERSION"
else
    echo "   Platform: Unknown"
fi

# RAM check
if command -v free &> /dev/null; then
    # Linux
    FREE_RAM=$(free -g | awk 'NR==2 {print $7}')
    echo "   Free RAM: ${FREE_RAM}GB"
elif command -v vm_stat &> /dev/null; then
    # macOS
    FREE_PAGES=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    FREE_GB=$((FREE_PAGES * 4096 / 1073741824))
    echo "   Free RAM: ~${FREE_GB}GB"
fi

# 8. GUI directory check
echo
echo "8. GUI Directory:"
if [ -d "gui" ]; then
    echo "   ✅ gui/ directory found"

    if [ -f "gui/package.json" ]; then
        echo "   ✅ package.json exists"
    else
        echo "   ❌ package.json missing"
        ALL_PASS=false
    fi

    if [ -d "gui/src-tauri" ]; then
        echo "   ✅ src-tauri/ directory found"
    else
        echo "   ❌ src-tauri/ missing"
        ALL_PASS=false
    fi

    # Check if node_modules installed
    if [ -d "gui/node_modules" ]; then
        echo "   ✅ node_modules installed"
    else
        echo "   ⚠️  node_modules not installed"
        echo "      Run: cd gui && pnpm install"
    fi
else
    echo "   ❌ gui/ directory not found"
    ALL_PASS=false
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ALL_PASS" = true ]; then
    echo "✅ ALL DEPENDENCIES SATISFIED"
    echo
    echo "You're ready to run:"
    echo "  Terminal 1: ./scripts/start_ollama.sh"
    echo "  Terminal 2: ./scripts/start_backend.sh"
    echo "  Terminal 3: cd gui && pnpm tauri:dev"
else
    echo "❌ SOME DEPENDENCIES MISSING"
    echo
    echo "Please install missing items (see above) then run this script again."
    echo
    echo "Quick install commands:"
    echo "  Rust:   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo "  Node:   brew install node"
    echo "  pnpm:   npm install -g pnpm"
    echo "  Flask:  pip install flask flask-cors psutil"
    echo "  GUI:    cd gui && pnpm install"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
