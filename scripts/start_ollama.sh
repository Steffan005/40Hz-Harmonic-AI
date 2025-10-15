#!/usr/bin/env bash
# Start Ollama and ensure required models are available

set -e

echo "======================================================================"
echo "EVOAGENTX - OLLAMA STARTUP"
echo "======================================================================"
echo

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install from https://ollama.com"
    exit 1
fi

# Check if Ollama is already running
if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is already running"
else
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    echo "Ollama PID: $OLLAMA_PID"

    # Wait for Ollama to be ready
    echo "Waiting for Ollama to start..."
    for i in {1..30}; do
        if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama service started"
            break
        fi
        sleep 1
    done
fi

echo

# Check required models
echo "Checking required models..."
REQUIRED_MODELS=("deepseek-r1:14b" "qwen2.5-coder:7b")

for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "  ✅ $model - present"
    else
        echo "  ❌ $model - missing"
        echo "     To install: ollama pull $model"
    fi
done

echo
echo "======================================================================"
echo "Ollama Status:"
curl -s http://127.0.0.1:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = data.get('models', [])
    print(f'  Available models: {len(models)}')
    for m in models[:5]:
        print(f'    • {m[\"name\"]}')
except:
    print('  Failed to parse models')
"
echo "======================================================================"
