#!/bin/bash
#
# Unity System Startup Script
# Initializes all Unity components in the correct order
#

set -e

UNITY_HOME="/opt/unity"
LOG_DIR="/var/log/unity"
RUN_DIR="/var/run/unity"
CONFIG_DIR="/etc/unity"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running with sufficient privileges
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        if ! groups | grep -q 'unity\|docker\|admin'; then
            error "This script must be run as root or with Unity group privileges"
            exit 1
        fi
    fi
}

# Create required directories
setup_directories() {
    log "Setting up directories..."

    mkdir -p "$LOG_DIR"
    mkdir -p "$RUN_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$UNITY_HOME/data"
    mkdir -p "$UNITY_HOME/models"
    mkdir -p "$UNITY_HOME/cache"

    # Set permissions
    chmod 755 "$LOG_DIR" "$RUN_DIR"
    chmod 700 "$CONFIG_DIR"
}

# Check system requirements
check_system_requirements() {
    log "Checking system requirements..."

    # Check available memory
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$total_mem" -lt 8 ]; then
        warning "System has less than 8GB RAM. Performance may be degraded."
    fi

    # Check disk space
    available_space=$(df -BG / | awk 'NR==2 {print int($4)}')
    if [ "$available_space" -lt 20 ]; then
        error "Less than 20GB disk space available. Cannot proceed."
        exit 1
    fi

    # Check CPU cores
    cpu_cores=$(nproc)
    if [ "$cpu_cores" -lt 2 ]; then
        warning "System has less than 2 CPU cores. Performance will be limited."
    fi

    log "System requirements check completed"
}

# Check for emergency shutdown marker
check_emergency_shutdown() {
    if [ -f "$CONFIG_DIR/EMERGENCY_SHUTDOWN" ]; then
        error "Emergency shutdown marker detected!"
        warning "System was previously shut down via kill switch"

        read -p "Remove emergency marker and continue startup? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            mv "$CONFIG_DIR/EMERGENCY_SHUTDOWN" "$CONFIG_DIR/EMERGENCY_SHUTDOWN.old"
            log "Emergency marker archived to EMERGENCY_SHUTDOWN.old"
        else
            error "Startup aborted. Remove $CONFIG_DIR/EMERGENCY_SHUTDOWN manually to proceed."
            exit 1
        fi
    fi
}

# Start Redis
start_redis() {
    log "Starting Redis..."

    if pgrep -x "redis-server" > /dev/null; then
        log "Redis is already running"
    else
        if command -v redis-server &> /dev/null; then
            redis-server --daemonize yes \
                        --dir "$UNITY_HOME/data" \
                        --logfile "$LOG_DIR/redis.log" \
                        --pidfile "$RUN_DIR/redis.pid"

            # Wait for Redis to start
            for i in {1..10}; do
                if redis-cli ping &> /dev/null; then
                    log "Redis started successfully"
                    return 0
                fi
                sleep 1
            done
            error "Redis failed to start"
            return 1
        else
            error "Redis is not installed"
            return 1
        fi
    fi
}

# Start Vault
start_vault() {
    log "Starting Vault..."

    if pgrep -x "vault" > /dev/null; then
        log "Vault is already running"
    else
        if command -v vault &> /dev/null; then
            # Check if config exists
            if [ ! -f "$CONFIG_DIR/vault.hcl" ]; then
                warning "Vault config not found, creating default..."
                cat > "$CONFIG_DIR/vault.hcl" <<EOF
storage "file" {
  path = "$UNITY_HOME/data/vault"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = 1
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
ui = true
EOF
            fi

            vault server -config="$CONFIG_DIR/vault.hcl" \
                        -log-level=info \
                        > "$LOG_DIR/vault.log" 2>&1 &

            echo $! > "$RUN_DIR/vault.pid"
            log "Vault started with PID $(cat $RUN_DIR/vault.pid)"
        else
            warning "Vault is not installed, skipping..."
        fi
    fi
}

# Start Ollama
start_ollama() {
    log "Starting Ollama..."

    if pgrep -x "ollama" > /dev/null; then
        log "Ollama is already running"
    else
        if command -v ollama &> /dev/null; then
            export OLLAMA_HOST="0.0.0.0:11434"
            export OLLAMA_MODELS="$UNITY_HOME/models"

            ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
            echo $! > "$RUN_DIR/ollama.pid"

            # Wait for Ollama to start
            log "Waiting for Ollama to initialize..."
            for i in {1..30}; do
                if curl -s http://localhost:11434/api/tags &> /dev/null; then
                    log "Ollama started successfully"
                    break
                fi
                sleep 1
            done

            # Pull required models if not present
            log "Checking required models..."
            check_and_pull_model "deepseek-r1:14b"
            check_and_pull_model "qwen2.5-coder:7b"

        else
            error "Ollama is not installed"
            return 1
        fi
    fi
}

# Check and pull Ollama model
check_and_pull_model() {
    local model=$1
    log "Checking model: $model"

    if ollama list | grep -q "$model"; then
        log "Model $model is already installed"
    else
        warning "Model $model not found, pulling..."
        ollama pull "$model" || warning "Failed to pull $model"
    fi
}

# Start Python backend
start_python_backend() {
    log "Starting Python backend..."

    if pgrep -f "uvicorn main:app" > /dev/null; then
        log "Python backend is already running"
    else
        cd "$UNITY_HOME/backend" || {
            error "Backend directory not found"
            return 1
        }

        # Activate virtual environment if it exists
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi

        # Check if main.py exists
        if [ ! -f "main.py" ]; then
            error "main.py not found in backend directory"
            return 1
        fi

        python3 -m uvicorn main:app \
                --host 0.0.0.0 \
                --port 8000 \
                --log-config "$CONFIG_DIR/logging.yaml" \
                > "$LOG_DIR/backend.log" 2>&1 &

        echo $! > "$RUN_DIR/backend.pid"
        log "Python backend started with PID $(cat $RUN_DIR/backend.pid)"
    fi
}

# Start watchdog
start_watchdog() {
    log "Starting Unity Watchdog..."

    if pgrep -f "watchdog_master.py" > /dev/null; then
        log "Watchdog is already running"
    else
        cd "$UNITY_HOME" || return 1

        if [ -f "watchdog_master.py" ]; then
            python3 watchdog_master.py > "$LOG_DIR/watchdog.log" 2>&1 &
            echo $! > "$RUN_DIR/watchdog.pid"
            log "Watchdog started with PID $(cat $RUN_DIR/watchdog.pid)"
        else
            warning "Watchdog script not found, skipping..."
        fi
    fi
}

# Start emergency controller
start_emergency_controller() {
    log "Starting Emergency Controller..."

    if pgrep -f "emergency_controller.py" > /dev/null; then
        log "Emergency Controller is already running"
    else
        cd "$UNITY_HOME" || return 1

        if [ -f "emergency_controller.py" ]; then
            python3 emergency_controller.py > "$LOG_DIR/emergency.log" 2>&1 &
            echo $! > "$RUN_DIR/emergency.pid"
            log "Emergency Controller started with PID $(cat $RUN_DIR/emergency.pid)"
        else
            warning "Emergency Controller script not found, skipping..."
        fi
    fi
}

# Verify all services are running
verify_services() {
    log "Verifying services..."

    local all_healthy=true

    # Check Redis
    if redis-cli ping &> /dev/null; then
        log "✓ Redis is healthy"
    else
        error "✗ Redis is not responding"
        all_healthy=false
    fi

    # Check Ollama
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        log "✓ Ollama is healthy"
    else
        error "✗ Ollama is not responding"
        all_healthy=false
    fi

    # Check Python backend
    if curl -s http://localhost:8000/health &> /dev/null; then
        log "✓ Python backend is healthy"
    else
        error "✗ Python backend is not responding"
        all_healthy=false
    fi

    # Check Vault
    if curl -s http://localhost:8200/v1/sys/health &> /dev/null; then
        log "✓ Vault is healthy"
    else
        warning "⚠ Vault is not responding (optional service)"
    fi

    # Check Emergency Controller
    if curl -s http://localhost:8002/emergency/status &> /dev/null; then
        log "✓ Emergency Controller is healthy"
    else
        warning "⚠ Emergency Controller is not responding"
    fi

    if [ "$all_healthy" = true ]; then
        log "All critical services are healthy"
        return 0
    else
        error "Some critical services failed to start"
        return 1
    fi
}

# Write startup status
write_startup_status() {
    local status=$1

    cat > "$RUN_DIR/startup_status.json" <<EOF
{
    "timestamp": "$(date -Iseconds)",
    "status": "$status",
    "services": {
        "redis": $(pgrep -x "redis-server" > /dev/null && echo "true" || echo "false"),
        "ollama": $(pgrep -x "ollama" > /dev/null && echo "true" || echo "false"),
        "backend": $(pgrep -f "uvicorn main:app" > /dev/null && echo "true" || echo "false"),
        "vault": $(pgrep -x "vault" > /dev/null && echo "true" || echo "false"),
        "watchdog": $(pgrep -f "watchdog_master.py" > /dev/null && echo "true" || echo "false"),
        "emergency": $(pgrep -f "emergency_controller.py" > /dev/null && echo "true" || echo "false")
    },
    "pid_files": {
        "redis": "$([ -f $RUN_DIR/redis.pid ] && cat $RUN_DIR/redis.pid || echo null)",
        "ollama": "$([ -f $RUN_DIR/ollama.pid ] && cat $RUN_DIR/ollama.pid || echo null)",
        "backend": "$([ -f $RUN_DIR/backend.pid ] && cat $RUN_DIR/backend.pid || echo null)",
        "vault": "$([ -f $RUN_DIR/vault.pid ] && cat $RUN_DIR/vault.pid || echo null)",
        "watchdog": "$([ -f $RUN_DIR/watchdog.pid ] && cat $RUN_DIR/watchdog.pid || echo null)",
        "emergency": "$([ -f $RUN_DIR/emergency.pid ] && cat $RUN_DIR/emergency.pid || echo null)"
    }
}
EOF
}

# Main startup sequence
main() {
    echo "========================================="
    echo "     Unity System Startup Sequence      "
    echo "========================================="

    # Check privileges
    check_privileges

    # Setup directories
    setup_directories

    # Check system requirements
    check_system_requirements

    # Check for emergency shutdown
    check_emergency_shutdown

    # Start services in order
    log "Starting core services..."

    start_redis || warning "Redis failed to start"
    sleep 2

    start_vault || warning "Vault failed to start"
    sleep 2

    start_ollama || {
        error "Ollama failed to start - this is critical"
        exit 1
    }
    sleep 5

    start_python_backend || warning "Python backend failed to start"
    sleep 3

    start_watchdog || warning "Watchdog failed to start"
    sleep 2

    start_emergency_controller || warning "Emergency Controller failed to start"
    sleep 2

    # Verify all services
    log "Performing health checks..."
    if verify_services; then
        write_startup_status "success"
        echo "========================================="
        echo -e "${GREEN}    Unity System Started Successfully${NC}"
        echo "========================================="
        echo ""
        echo "Dashboard: http://localhost:8001"
        echo "API:       http://localhost:8000"
        echo "Emergency: http://localhost:8002"
        echo ""
        echo "Run 'unity status' to check system status"
        echo "Run 'unity stop' to shutdown gracefully"
        echo ""
    else
        write_startup_status "partial"
        echo "========================================="
        echo -e "${YELLOW}    Unity System Partially Started${NC}"
        echo "========================================="
        echo "Check logs in $LOG_DIR for details"
        exit 1
    fi
}

# Run main function
main "$@"