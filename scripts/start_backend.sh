#!/usr/bin/env bash
# Start EvoAgentX Python Backend Services

set -e

cd "$(dirname "$0")/.."

echo "======================================================================"
echo "EVOAGENTX - BACKEND STARTUP"
echo "======================================================================"
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

# Install/check dependencies
echo "Checking dependencies..."
pip install -q flask flask-cors psutil 2>/dev/null || true

echo "✅ Dependencies ready"
echo

# Start backend API server
echo "Starting backend API server on http://127.0.0.1:8000..."
echo

cd backend
python3 api_server.py &
BACKEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ Backend service started"
        break
    fi
    sleep 1
done

echo
echo "======================================================================"
echo "Backend Status:"
curl -s http://127.0.0.1:8000/health | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'  Status: {data[\"status\"]}')
    for service, status in data.get('services', {}).items():
        print(f'    • {service}: {status}')
except:
    print('  Failed to connect to backend')
"
echo "======================================================================"
echo
echo "Backend is running. To stop:"
echo "  kill $BACKEND_PID"
echo

# Keep script running
wait $BACKEND_PID
