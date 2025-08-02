#!/bin/bash

# =============================================================================
# Brand Intelligence Hub - iOS Deployment Script
# =============================================================================
# One-click deployment script for deploying Flutter app to connected iOS device
# Automatically detects device, builds release/debug, and verifies installation
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

# Default build mode
BUILD_MODE="release"

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
    echo "  --debug      Build in debug mode"
    echo "  --release    Build in release mode (default)"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Deploy release build"
    echo "  $0 --debug          # Deploy debug build"
    echo "  $0 --release        # Deploy release build (explicit)"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --debug)
                BUILD_MODE="debug"
                shift
                ;;
            --release)
                BUILD_MODE="release"
                shift
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
        print_info "Continuing with deployment..."
    else
        print_success "All backend services are running"
    fi
}

# Function to detect iOS devices
detect_ios_device() {
    print_status "Detecting connected iOS devices..."
    
    # Get list of iOS devices
    local ios_devices=$(flutter devices | grep "ios" | grep -v "simulator" || true)
    
    if [ -z "$ios_devices" ]; then
        print_error "No iOS devices found"
        print_info "Please connect an iOS device and ensure it's trusted"
        print_info "You can check connected devices with: flutter devices"
        exit 1
    fi
    
    # Count number of devices
    local device_count=$(echo "$ios_devices" | wc -l | tr -d ' ')
    
    if [ "$device_count" -gt 1 ]; then
        print_warning "Multiple iOS devices detected ($device_count devices)"
        print_info "Using the first device found:"
    fi
    
    # Extract device ID from first device
    DEVICE_ID=$(echo "$ios_devices" | head -n1 | sed -n 's/.*• \([0-9A-F-]*\) •.*/\1/p')
    DEVICE_NAME=$(echo "$ios_devices" | head -n1 | sed -n 's/^\([^(]*\).*/\1/p' | xargs)
    
    if [ -z "$DEVICE_ID" ]; then
        print_error "Could not extract device ID from Flutter devices output"
        print_info "Flutter devices output:"
        flutter devices
        exit 1
    fi
    
    print_success "Selected device: $DEVICE_NAME"
    print_info "Device ID: $DEVICE_ID"
}

# Function to clean Flutter project
clean_flutter_project() {
    print_status "Cleaning Flutter project..."
    
    cd "$FLUTTER_DIR"
    
    if flutter clean > /dev/null 2>&1; then
        print_success "Flutter project cleaned"
    else
        print_error "Failed to clean Flutter project"
        exit 1
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

# Function to install iOS dependencies
install_ios_dependencies() {
    print_status "Installing iOS dependencies (CocoaPods)..."
    
    cd ios
    
    if pod install > /dev/null 2>&1; then
        print_success "CocoaPods dependencies installed"
    else
        print_warning "CocoaPods installation completed with warnings"
        print_info "This is usually not critical for deployment"
    fi
    
    cd ..
}

# Function to build iOS app
build_ios_app() {
    local build_flag=""
    local build_desc=""
    
    if [ "$BUILD_MODE" = "debug" ]; then
        build_flag="--debug"
        build_desc="debug"
    else
        build_flag="--release"
        build_desc="release"
    fi
    
    print_status "Building iOS app ($build_desc mode)..."
    
    local build_output=$(flutter build ios $build_flag 2>&1)
    local build_exit_code=$?
    
    if [ $build_exit_code -eq 0 ]; then
        # Extract app size from build output
        local app_size=$(echo "$build_output" | grep -o '([0-9.]*MB)' | tail -n1)
        print_success "iOS build completed $app_size"
        
        # Extract build path
        local build_path=$(echo "$build_output" | grep "Built build/ios" | sed -n 's/.*Built \(.*\) .*/\1/p')
        if [ -n "$build_path" ]; then
            print_info "Build location: $build_path"
        fi
    else
        print_error "iOS build failed"
        print_info "Build output:"
        echo "$build_output"
        exit 1
    fi
}

# Function to install app on device
install_app_on_device() {
    print_status "Installing app on device: $DEVICE_NAME"
    print_info "This may take a moment..."
    
    local install_output=$(flutter install --device-id="$DEVICE_ID" 2>&1)
    local install_exit_code=$?
    
    if [ $install_exit_code -eq 0 ]; then
        print_success "App installed successfully"
    else
        print_error "App installation failed"
        print_info "Installation output:"
        echo "$install_output"
        
        # Check for common issues
        if echo "$install_output" | grep -q "No target device found"; then
            print_info "Device might have disconnected. Please reconnect and try again."
        elif echo "$install_output" | grep -q "Code signing"; then
            print_info "Code signing issue. Please check Xcode project settings."
        fi
        
        exit 1
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying app installation..."
    
    # Check if app is installed using xcrun devicectl
    local app_info=$(xcrun devicectl device info apps --device "$DEVICE_ID" 2>/dev/null | grep -A 1 "Brand Intelligence Hub" || true)
    
    if [ -n "$app_info" ]; then
        print_success "App verification successful"
        
        # Extract app details
        local bundle_id=$(echo "$app_info" | grep "com\." | xargs)
        local version=$(echo "$app_info" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -n1)
        
        if [ -n "$bundle_id" ]; then
            print_info "Bundle ID: $bundle_id"
        fi
        if [ -n "$version" ]; then
            print_info "Version: $version"
        fi
    else
        print_warning "Could not verify app installation using xcrun"
        print_info "App may still be installed successfully"
    fi
}

# Function to show completion summary
show_completion_summary() {
    echo
    print_header "🎉 iOS Deployment Completed Successfully!"
    print_header "============================================"
    echo
    print_info "📱 Device: $DEVICE_NAME"
    print_info "📦 Build Mode: $BUILD_MODE"
    print_info "🆔 Device ID: $DEVICE_ID"
    print_info "📋 App Name: Brand Intelligence Hub"
    echo
    print_header "📲 Next Steps:"
    print_info "1. Look for 'Brand Intelligence Hub' on your device"
    print_info "2. Tap the app icon to launch it"
    print_info "3. Test the app functionality"
    echo
    print_header "🔧 Backend Services:"
    print_info "Make sure backend services are running for full functionality:"
    print_info "  ./start_all_services.sh"
    echo
    print_header "🔄 To redeploy:"
    print_info "  $0                    # Release build"
    print_info "  $0 --debug            # Debug build"
    echo
}

# Function to handle script interruption
cleanup() {
    echo
    print_warning "Deployment interrupted"
    exit 130
}

# Main execution function
main() {
    # Handle Ctrl+C gracefully
    trap cleanup INT
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Print header
    echo
    print_header "📱 Brand Intelligence Hub - iOS Deployment"
    print_header "==========================================="
    print_info "Build Mode: $BUILD_MODE"
    echo
    
    # Execute deployment steps
    check_flutter_directory
    check_backend_services
    detect_ios_device
    
    echo
    print_status "Starting deployment process..."
    
    clean_flutter_project
    get_flutter_dependencies
    install_ios_dependencies
    build_ios_app
    install_app_on_device
    verify_installation
    
    # Show completion summary
    show_completion_summary
    
    return 0
}

# Run main function with all arguments
main "$@"