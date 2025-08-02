#!/bin/bash

# =============================================================================
# Brand Intelligence Hub - Flutter Web Startup Script
# =============================================================================
# One-click script to start Flutter web development server on port 3000
# Handles port conflicts, backend service checks, and proper initialization
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLUTTER_DIR="$SCRIPT_DIR/flutter"
WEB_PORT=3000

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --port PORT     Use specific port (default: 3000)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start on port 3000"
    echo "  $0 --port 3001       # Start on port 3001"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                WEB_PORT="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to check if Flutter directory exists
check_flutter_directory() {
    if [ ! -d "$FLUTTER_DIR" ]; then
        print_error "Flutter directory not found: $FLUTTER_DIR"
        print_info "Make sure you're running this script from the project root"
        exit 1
    fi
    print_success "Flutter directory found"
}

# Function to check if Flutter is installed
check_flutter_installation() {
    if ! command -v flutter &> /dev/null; then
        print_error "Flutter is not installed or not in PATH"
        print_info "Please install Flutter: https://flutter.dev/docs/get-started/install"
        exit 1
    fi
    
    local flutter_version=$(flutter --version | head -n1)
    print_success "Flutter installation verified: $flutter_version"
}

# Function to check backend services
check_backend_services() {
    print_status "Checking backend services..."
    
    local services=("brand-service:8001" "data-collection:8002" "analysis-engine:8003")
    local unhealthy_services=()
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_info"
        
        if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
            print_success "$service_name: Running on port $port"
        else
            unhealthy_services+=("$service_name (port $port)")
            print_warning "$service_name: Not responding on port $port"
        fi
    done
    
    if [ ${#unhealthy_services[@]} -gt 0 ]; then
        print_warning "Some backend services are not running:"
        for service in "${unhealthy_services[@]}"; do
            print_info "  • $service"
        done
        print_info "To start all services: ./start_all_services.sh"
        print_info "Continuing with Flutter web startup..."
    else
        print_success "All backend services are running"
    fi
}

# Function to kill processes using the web port
clear_port() {
    print_status "Checking port $WEB_PORT..."
    
    local port_pid=$(lsof -ti:$WEB_PORT 2>/dev/null || true)
    
    if [ -n "$port_pid" ]; then
        print_warning "Port $WEB_PORT is in use by process $port_pid"
        print_status "Stopping existing process..."
        
        # Try graceful shutdown first
        kill $port_pid 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if kill -0 $port_pid 2>/dev/null; then
            print_status "Force killing process..."
            kill -9 $port_pid 2>/dev/null || true
            sleep 1
        fi
        
        print_success "Port $WEB_PORT cleared"
    else
        print_success "Port $WEB_PORT is available"
    fi
}

# Function to kill any existing Flutter processes
stop_existing_flutter() {
    print_status "Stopping any existing Flutter processes..."
    
    # Find and list existing Flutter processes first
    local flutter_pids=($(pgrep -f "flutter.*run" 2>/dev/null || true))
    local dart_pids=($(pgrep -f "dart.*web" 2>/dev/null || true))
    local dart_frontend_pids=($(pgrep -f "dart.*frontend_server" 2>/dev/null || true))
    local flutter_tools_pids=($(pgrep -f "flutter_tools" 2>/dev/null || true))
    
    local total_processes=$((${#flutter_pids[@]} + ${#dart_pids[@]} + ${#dart_frontend_pids[@]} + ${#flutter_tools_pids[@]}))
    
    if [ $total_processes -eq 0 ]; then
        print_success "No existing Flutter processes found"
        return 0
    fi
    
    print_info "Found $total_processes Flutter-related processes to stop"
    
    # Kill Flutter processes gracefully
    if [ ${#flutter_pids[@]} -gt 0 ]; then
        print_status "Stopping ${#flutter_pids[@]} Flutter run processes..."
        for pid in "${flutter_pids[@]}"; do
            kill $pid 2>/dev/null || true
        done
    fi
    
    if [ ${#dart_pids[@]} -gt 0 ]; then
        print_status "Stopping ${#dart_pids[@]} Dart web processes..."
        for pid in "${dart_pids[@]}"; do
            kill $pid 2>/dev/null || true
        done
    fi
    
    if [ ${#dart_frontend_pids[@]} -gt 0 ]; then
        print_status "Stopping ${#dart_frontend_pids[@]} Dart frontend server processes..."
        for pid in "${dart_frontend_pids[@]}"; do
            kill $pid 2>/dev/null || true
        done
    fi
    
    if [ ${#flutter_tools_pids[@]} -gt 0 ]; then
        print_status "Stopping ${#flutter_tools_pids[@]} Flutter tools processes..."
        for pid in "${flutter_tools_pids[@]}"; do
            kill $pid 2>/dev/null || true
        done
    fi
    
    # Give processes time to shutdown gracefully
    sleep 3
    
    # Check if any processes are still running and force kill if needed
    local remaining_pids=($(pgrep -f "flutter.*run|dart.*web|dart.*frontend_server|flutter_tools" 2>/dev/null || true))
    
    if [ ${#remaining_pids[@]} -gt 0 ]; then
        print_warning "${#remaining_pids[@]} processes still running, force killing..."
        for pid in "${remaining_pids[@]}"; do
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
    fi
    
    # Also kill any processes using the web port specifically
    local port_pids=($(lsof -ti:$WEB_PORT 2>/dev/null || true))
    if [ ${#port_pids[@]} -gt 0 ]; then
        print_status "Killing ${#port_pids[@]} processes using port $WEB_PORT..."
        for pid in "${port_pids[@]}"; do
            kill -9 $pid 2>/dev/null || true
        done
    fi
    
    print_success "All Flutter processes stopped successfully"
}

# Function to clean Flutter project
clean_flutter_project() {
    print_status "Cleaning Flutter project..."
    
    cd "$FLUTTER_DIR"
    
    if flutter clean > /dev/null 2>&1; then
        print_success "Flutter project cleaned"
    else
        print_warning "Flutter clean completed with warnings"
    fi
}

# Function to get Flutter dependencies
get_flutter_dependencies() {
    print_status "Getting Flutter dependencies..."
    
    if flutter pub get > /dev/null 2>&1; then
        print_success "Flutter dependencies updated"
    else
        print_error "Failed to get Flutter dependencies"
        exit 1
    fi
}

# Function to start Flutter web server
start_flutter_web() {
    print_status "Starting Flutter web server on port $WEB_PORT..."
    print_info "This may take a moment to compile and start..."
    
    # Start Flutter web server in background with output capture
    flutter run -d web-server --web-port=$WEB_PORT > flutter_web.log 2>&1 &
    local flutter_pid=$!
    
    # Wait for server to start with timeout
    local timeout=60
    local elapsed=0
    local server_started=false
    
    while [ $elapsed -lt $timeout ]; do
        if grep -q "lib/main.dart is being served at" flutter_web.log 2>/dev/null; then
            server_started=true
            break
        fi
        
        # Check if process is still running
        if ! kill -0 $flutter_pid 2>/dev/null; then
            print_error "Flutter process died unexpectedly"
            print_info "Check flutter_web.log for details"
            cat flutter_web.log
            exit 1
        fi
        
        sleep 2
        elapsed=$((elapsed + 2))
        
        # Show progress
        if [ $((elapsed % 10)) -eq 0 ]; then
            print_status "Waiting for Flutter web server... (${elapsed}s)"
        fi
    done
    
    if [ "$server_started" = true ]; then
        print_success "Flutter web server started successfully"
        print_info "Server URL: http://localhost:$WEB_PORT"
        
        # Extract any warnings or important info
        local warnings=$(grep -i "warning\|deprecated" flutter_web.log 2>/dev/null | head -3 || true)
        if [ -n "$warnings" ]; then
            print_warning "Build warnings (non-critical):"
            echo "$warnings" | while read -r line; do
                print_info "  $line"
            done
        fi
    else
        print_error "Flutter web server failed to start within $timeout seconds"
        print_info "Check flutter_web.log for details:"
        tail -20 flutter_web.log
        exit 1
    fi
}

# Function to open browser
open_browser() {
    if command -v open &> /dev/null; then
        print_status "Opening browser..."
        sleep 2  # Give server a moment to fully initialize
        open "http://localhost:$WEB_PORT"
        print_success "Browser opened"
    else
        print_info "Open your browser and navigate to: http://localhost:$WEB_PORT"
    fi
}

# Function to show completion summary
show_completion_summary() {
    echo
    print_header "🎉 Flutter Web Server Started Successfully!"
    print_header "=============================================="
    echo
    print_info "🌐 URL: http://localhost:$WEB_PORT"
    print_info "📁 Project: Brand Intelligence Hub"
    print_info "🔧 Mode: Development"
    echo
    print_header "📝 Available Commands:"
    print_info "R - Hot restart"
    print_info "h - List all commands"
    print_info "d - Detach (keep running)"
    print_info "q - Quit server"
    echo
    print_header "🛑 To stop the server:"
    print_info "  Press 'q' in the Flutter console"
    print_info "  Or run: pkill -f 'flutter run'"
    echo
    print_header "📋 Next Steps:"
    print_info "1. The web app should open automatically"
    print_info "2. Test the LAUNCH ANALYSIS functionality"
    print_info "3. Verify real backend integration"
    echo
}

# Function to handle script interruption
cleanup() {
    echo
    print_warning "Script interrupted"
    print_status "Cleaning up..."
    
    # Kill Flutter process if started
    pkill -f "flutter run.*--web-port=$WEB_PORT" 2>/dev/null || true
    
    # Remove log file
    rm -f "$FLUTTER_DIR/flutter_web.log" 2>/dev/null || true
    
    exit 130
}

# Function to monitor Flutter process
monitor_flutter() {
    print_info "Flutter web server is running. Monitoring..."
    print_info "Check the server status at: http://localhost:$WEB_PORT"
    print_info "Press Ctrl+C to stop monitoring (server will continue running)"
    echo
    
    # Monitor the Flutter log for important messages
    tail -f "$FLUTTER_DIR/flutter_web.log" 2>/dev/null | while read -r line; do
        # Filter important messages
        if echo "$line" | grep -qE "(error|Error|ERROR|exception|Exception|failed|Failed)"; then
            print_error "Flutter: $line"
        elif echo "$line" | grep -qE "(warning|Warning|WARNING|deprecated)"; then
            print_warning "Flutter: $line"
        elif echo "$line" | grep -qE "(Hot restart|Hot reload|Synced)"; then
            print_success "Flutter: $line"
        fi
    done
}

# Main execution function
main() {
    # Handle Ctrl+C gracefully
    trap cleanup INT
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Print header
    echo
    print_header "🌐 Brand Intelligence Hub - Flutter Web Startup"
    print_header "==============================================="
    print_info "Target Port: $WEB_PORT"
    echo
    
    # Execute startup steps
    check_flutter_installation
    check_flutter_directory
    check_backend_services
    
    echo
    print_status "Preparing Flutter web environment..."
    
    stop_existing_flutter
    clear_port
    
    cd "$FLUTTER_DIR"
    clean_flutter_project
    get_flutter_dependencies
    
    echo
    start_flutter_web
    open_browser
    
    # Show completion summary
    show_completion_summary
    
    # Monitor the server (optional)
    read -p "Monitor Flutter server logs? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        monitor_flutter
    else
        print_info "Flutter web server is running in the background"
        print_info "Access at: http://localhost:$WEB_PORT"
    fi
    
    return 0
}

# Run main function with all arguments
main "$@"