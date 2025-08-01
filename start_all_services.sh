#!/bin/bash

# =============================================================================
# Brand Intelligence Hub - Service Startup Script
# =============================================================================
# This script starts all three microservices for the Brand Reputation Analysis
# & Competitive Intelligence Platform built for VibeCoding Hackathon 2025
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Service configuration
BRAND_SERVICE_PORT=8001
DATA_COLLECTION_PORT=8002
ANALYSIS_ENGINE_PORT=8003

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        print_warning "Port $port is already in use (may be $service_name already running)"
        echo -n "Kill existing process and continue? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Killing processes on port $port..."
            pkill -f ".*:$port" || true
            sleep 2
            print_success "Port $port cleared"
        else
            print_error "Cannot start $service_name - port $port is in use"
            return 1
        fi
    else
        print_success "Port $port is available for $service_name"
    fi
}

# Function to check if virtual environment exists
check_venv() {
    local service_dir=$1
    local service_name=$2
    
    if [ ! -d "$service_dir/venv" ]; then
        print_error "Virtual environment not found for $service_name at $service_dir/venv"
        print_info "Run: cd $service_dir && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi
    print_success "Virtual environment found for $service_name"
}

# Function to check if required files exist
check_service_files() {
    local service_dir=$1
    local service_name=$2
    local startup_file=$3
    
    if [ ! -f "$service_dir/$startup_file" ]; then
        print_error "Startup file not found: $service_dir/$startup_file"
        return 1
    fi
    
    if [ ! -f "$service_dir/requirements.txt" ]; then
        print_error "Requirements file not found: $service_dir/requirements.txt"
        return 1
    fi
    
    print_success "$service_name files verified"
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    local start_command=$4
    local log_file="$LOG_DIR/${service_name}.log"
    
    print_status "Starting $service_name on port $port..."
    
    cd "$service_dir"
    
    # Start the service in background and redirect output to log file
    nohup bash -c "source venv/bin/activate && $start_command" > "$log_file" 2>&1 &
    local service_pid=$!
    
    # Wait a moment for the service to start
    sleep 3
    
    # Check if the service is still running
    if ps -p $service_pid > /dev/null; then
        print_success "$service_name started successfully (PID: $service_pid)"
        print_info "Logs: $log_file"
        echo "$service_pid" > "$LOG_DIR/${service_name}.pid"
        return 0
    else
        print_error "$service_name failed to start"
        print_info "Check logs: $log_file"
        return 1
    fi
}

# Function to verify service health
verify_service_health() {
    local service_name=$1
    local port=$2
    local max_attempts=10
    local attempt=1
    
    print_status "Verifying $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1 || curl -s "http://localhost:$port/" >/dev/null 2>&1; then
            print_success "$service_name is responding on port $port"
            return 0
        fi
        
        print_info "Attempt $attempt/$max_attempts - waiting for $service_name to be ready..."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name is not responding after $max_attempts attempts"
    return 1
}

# Function to display service status
show_service_status() {
    echo
    print_status "=== SERVICE STATUS ==="
    echo
    
    local services=("brand-service:$BRAND_SERVICE_PORT" "data-collection:$DATA_COLLECTION_PORT" "analysis-engine:$ANALYSIS_ENGINE_PORT")
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_info"
        
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            print_success "$service_name: http://localhost:$port (HEALTHY)"
        elif curl -s "http://localhost:$port/" >/dev/null 2>&1; then
            print_success "$service_name: http://localhost:$port (RUNNING)"
        else
            print_error "$service_name: http://localhost:$port (NOT RESPONDING)"
        fi
    done
    
    echo
    print_info "API Documentation:"
    echo "  • Data Collection: http://localhost:$DATA_COLLECTION_PORT/docs"
    echo "  • Analysis Engine: http://localhost:$ANALYSIS_ENGINE_PORT/docs"
    echo
    print_info "Logs Directory: $LOG_DIR"
    echo "  • brand-service.log"
    echo "  • data-collection.log" 
    echo "  • analysis-engine.log"
    echo
}

# Function to stop all services
stop_all_services() {
    print_status "Stopping all services..."
    
    for pid_file in "$LOG_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            local service_name=$(basename "$pid_file" .pid)
            
            if ps -p $pid > /dev/null; then
                print_status "Stopping $service_name (PID: $pid)..."
                kill $pid
                sleep 2
                
                if ps -p $pid > /dev/null; then
                    print_warning "Force killing $service_name..."
                    kill -9 $pid
                fi
                
                print_success "$service_name stopped"
            fi
            
            rm -f "$pid_file"
        fi
    done
    
    # Also kill by port just in case
    for port in $BRAND_SERVICE_PORT $DATA_COLLECTION_PORT $ANALYSIS_ENGINE_PORT; do
        pkill -f ".*:$port" >/dev/null 2>&1 || true
    done
    
    print_success "All services stopped"
}

# Main execution
main() {
    echo
    echo -e "${PURPLE}🚀 Brand Intelligence Hub - Service Startup${NC}"
    echo -e "${PURPLE}=================================================${NC}"
    echo
    
    # Handle command line arguments
    case "${1:-start}" in
        "stop")
            stop_all_services
            exit 0
            ;;
        "status")
            show_service_status
            exit 0
            ;;
        "restart")
            stop_all_services
            sleep 3
            ;;
        "start"|"")
            # Continue with startup
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status]"
            exit 1
            ;;
    esac
    
    print_status "Performing pre-flight checks..."
    
    # Check ports
    check_port $BRAND_SERVICE_PORT "brand-service" || exit 1
    check_port $DATA_COLLECTION_PORT "data-collection" || exit 1  
    check_port $ANALYSIS_ENGINE_PORT "analysis-engine" || exit 1
    
    # Check virtual environments and files
    check_venv "$SCRIPT_DIR/brand-service" "brand-service" || exit 1
    check_venv "$SCRIPT_DIR/data-collection" "data-collection" || exit 1
    check_venv "$SCRIPT_DIR/analysis-engine" "analysis-engine" || exit 1
    
    check_service_files "$SCRIPT_DIR/brand-service" "brand-service" "start_server.py" || exit 1
    check_service_files "$SCRIPT_DIR/data-collection" "data-collection" "run.py" || exit 1
    check_service_files "$SCRIPT_DIR/analysis-engine" "analysis-engine" "app/main.py" || exit 1
    
    print_success "Pre-flight checks completed"
    echo
    
    print_status "Starting all services..."
    echo
    
    # Start services
    start_service "brand-service" "$SCRIPT_DIR/brand-service" $BRAND_SERVICE_PORT "python start_server.py" || exit 1
    start_service "data-collection" "$SCRIPT_DIR/data-collection" $DATA_COLLECTION_PORT "python run.py" || exit 1
    start_service "analysis-engine" "$SCRIPT_DIR/analysis-engine" $ANALYSIS_ENGINE_PORT "python -m uvicorn app.main:app --host 0.0.0.0 --port $ANALYSIS_ENGINE_PORT" || exit 1
    
    echo
    print_status "Verifying service health..."
    echo
    
    # Verify health
    verify_service_health "brand-service" $BRAND_SERVICE_PORT || print_warning "brand-service health check failed"
    verify_service_health "data-collection" $DATA_COLLECTION_PORT || print_warning "data-collection health check failed"
    verify_service_health "analysis-engine" $ANALYSIS_ENGINE_PORT || print_warning "analysis-engine health check failed"
    
    # Show final status
    show_service_status
    
    print_success "🎉 All services started successfully!"
    echo
    print_info "To stop all services, run: $0 stop"
    print_info "To check status, run: $0 status"
    print_info "To view logs: tail -f $LOG_DIR/<service-name>.log"
    echo
}

# Trap to handle script interruption
trap 'echo; print_warning "Script interrupted. Use '$0' stop to stop services."; exit 130' INT

# Run main function
main "$@"