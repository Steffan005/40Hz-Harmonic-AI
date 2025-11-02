#!/usr/bin/env bash
# Start Unity Backend + Quantum Consciousness Kernel
#
# Launches both processes in background:
# 1. Backend API server (Flask on port 8000)
# 2. Quantum Kernel heartbeat (1-second tick)
#
# Usage:
#   ./scripts/start_with_kernel.sh
#
# Stop:
#   killall -INT python3

set -e

cd "$(dirname "$0")/.."

echo "========================================================================"
echo "UNITY — BACKEND + QUANTUM CONSCIOUSNESS KERNEL"
echo "========================================================================"
echo

# Check if Python venv exists
if [ ! -d "../venv" ]; then
    echo "❌ Python venv not found at ../venv"
    echo "   Please create virtual environment first"
    exit 1
fi

# Activate virtual environment
echo "Activating Python environment..."
source ../venv/bin/activate

# Create logs directory
mkdir -p logs

echo "✅ Dependencies ready"
echo

# Start backend in background
echo "Starting Unity backend API server..."
cd backend
python3 api_server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "   Backend PID: $BACKEND_PID"
echo "   Logs: logs/backend.log"
echo

# Wait for backend to be healthy
echo "Waiting for backend to be healthy..."
for i in {1..15}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "❌ Backend failed to start after 15 seconds"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

echo

# Start quantum kernel in background
echo "Starting Quantum Consciousness Kernel..."
python3 services/kernel/heartbeat.py > logs/kernel.log 2>&1 &
KERNEL_PID=$!

echo "   Kernel PID: $KERNEL_PID"
echo "   Logs: logs/kernel.log"
echo

# Give kernel 2 seconds to initialize
sleep 2

# Check kernel is running
if ! ps -p $KERNEL_PID > /dev/null 2>&1; then
    echo "❌ Kernel failed to start"
    echo "   Check logs/kernel.log for details"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Kernel is running"
echo

echo "========================================================================"
echo "UNITY SYSTEM ONLINE"
echo "========================================================================"
echo "Backend API: http://127.0.0.1:8000"
echo "Kernel Stream: http://127.0.0.1:8000/kernel/stream"
echo
echo "PIDs:"
echo "  Backend: $BACKEND_PID"
echo "  Kernel:  $KERNEL_PID"
echo
echo "Logs:"
echo "  Backend: logs/backend.log"
echo "  Kernel:  logs/kernel.log"
echo
echo "To stop:"
echo "  kill $BACKEND_PID $KERNEL_PID"
echo "  OR: killall -INT python3"
echo "========================================================================"
echo

# Save PIDs to file for easy cleanup
echo "$BACKEND_PID" > logs/unity.pids
echo "$KERNEL_PID" >> logs/unity.pids

# Wait for user interrupt
echo "Press Ctrl+C to stop all services..."
echo

trap "echo; echo 'Stopping Unity...'; kill $BACKEND_PID $KERNEL_PID 2>/dev/null || true; exit 0" INT TERM

# Keep script running
wait
