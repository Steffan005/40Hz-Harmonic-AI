#!/usr/bin/env bash
# Start Unity Backend with Gunicorn (Production)
#
# Usage:
#   ./scripts/start_production.sh
#
# Requires:
#   - gunicorn installed in venv
#   - deploy/gunicorn.conf.py configured

set -e

cd "$(dirname "$0")/.."

echo "======================================================================"
echo "UNITY BACKEND - PRODUCTION STARTUP (GUNICORN)"
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

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Installing gunicorn..."
    pip install -q gunicorn
fi

# Create logs directory
mkdir -p logs

echo "✅ Dependencies ready"
echo

# Start gunicorn
echo "Starting Unity backend with Gunicorn..."
echo "   Config: deploy/gunicorn.conf.py"
echo "   Workers: $(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)')"
echo "   Bind: 127.0.0.1:8000"
echo

cd backend
gunicorn -c ../deploy/gunicorn.conf.py api_server:app
