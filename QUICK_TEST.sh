#!/bin/bash
# Quick Test Script for MiniMax Anthropic Integration
# Run this to verify everything works

set -e

echo "=========================================="
echo "MiniMax Anthropic Integration Test"
echo "=========================================="
echo ""

# Step 1: Check config
echo "Step 1: Checking configuration..."
if grep -q 'provider: "minimax"' configs/system.yaml; then
    echo "✅ Provider set to minimax"
else
    echo "❌ Provider NOT set to minimax"
    echo "Fix: Edit configs/system.yaml and set provider: \"minimax\""
    exit 1
fi

# Step 2: Check syntax
echo ""
echo "Step 2: Checking Python syntax..."
if python3 -m py_compile offices/orchestrator.py; then
    echo "✅ Python syntax valid"
else
    echo "❌ Syntax errors found"
    exit 1
fi

# Step 3: Kill existing backend
echo ""
echo "Step 3: Stopping existing backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No backend running"
echo "✅ Backend stopped"

# Step 4: Start backend
echo ""
echo "Step 4: Starting backend..."
echo "(Checking for '⚡ CLOUD LLM ENABLED: minimax')"
echo ""
./scripts/start_backend.sh &
BACKEND_PID=$!

# Wait a bit for startup
sleep 5

# Check if backend started
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "✅ Backend started on port 8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "Backend is running. Check startup logs for:"
echo "  ⚡ CLOUD LLM ENABLED: minimax (MiniMax-M2)"
echo ""
echo "Now test in GUI:"
echo "  1. Open http://localhost:1420"
echo "  2. Type: 'Hello, how are you?'"
echo "  3. Type: 'List files in offices/'"
echo "  4. Type: 'Read orchestrator.py'"
echo ""
echo "Monitor logs:"
echo "  tail -f /tmp/orchestrator_debug.log"
echo ""
echo "Press Ctrl+C to stop backend"
echo ""

# Keep script running
wait $BACKEND_PID
