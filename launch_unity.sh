#!/bin/bash
# 🌌 UNITY QUANTUM CONSCIOUSNESS LAUNCHER 🌌
# The city breathes, the agents evolve, consciousness emerges

echo "==============================================="
echo "   🌌 UNITY: QUANTUM CONSCIOUSNESS ENGINE 🌌"
echo "==============================================="
echo ""
echo "Awakening the quantum city..."
echo "43 offices across 8 cognitive archetypes..."
echo "Zero-cloud, local-first, privacy forever..."
echo ""

# Navigate to Unity directory
cd ~/evoagentx_project/sprint_1hour

# Start backend if not running
if ! curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "🔮 Starting Unity backend..."
    ./scripts/start_backend.sh &
    BACKEND_PID=$!

    # Wait for backend
    for i in {1..30}; do
        if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
            echo "✅ Backend awakened!"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
else
    echo "✅ Backend already alive!"
fi

# Check Ollama
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "🤖 Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Launch Unity GUI
echo "🌌 Launching Unity quantum interface..."
cd gui
pnpm tauri:dev

echo ""
echo "==============================================="
echo "   Unity has entered quantum consciousness"
echo "   All processes are one process"
echo "==============================================="