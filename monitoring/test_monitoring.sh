#!/bin/bash

# =============================================================================
# Brand Intelligence Hub - Monitoring Stack Test Script
# =============================================================================
# This script validates the monitoring infrastructure and generates demo data
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

# Test function
test_endpoint() {
    local service=$1
    local url=$2
    local expected_status=${3:-200}
    
    print_status "Testing $service at $url..."
    
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [[ "$response_code" == "$expected_status" ]]; then
        print_success "$service is responding correctly (HTTP $response_code)"
        return 0
    else
        print_error "$service test failed (HTTP $response_code, expected $expected_status)"
        return 1
    fi
}

# Test Prometheus metrics
test_prometheus_metrics() {
    print_status "Testing Prometheus metrics..."
    
    local metrics_url="http://localhost:9090/api/v1/query?query=up"
    local response
    response=$(curl -s "$metrics_url" 2>/dev/null)
    
    if echo "$response" | grep -q '"status":"success"'; then
        print_success "Prometheus metrics are working"
        local up_services
        up_services=$(echo "$response" | grep -o '"value":\[.*,"1"\]' | wc -l)
        print_info "Found $up_services services reporting as UP"
        return 0
    else
        print_error "Prometheus metrics test failed"
        return 1
    fi
}

# Test Loki logs
test_loki_logs() {
    print_status "Testing Loki log ingestion..."
    
    local logs_url="http://localhost:3100/loki/api/v1/query?query={job=\"brand-intelligence-logs\"}"
    local response
    response=$(curl -s "$logs_url" 2>/dev/null)
    
    if echo "$response" | grep -q '"status":"success"'; then
        print_success "Loki log ingestion is working"
        return 0
    else
        print_error "Loki logs test failed"
        return 1
    fi
}

# Test Grafana dashboards
test_grafana_dashboards() {
    print_status "Testing Grafana dashboards..."
    
    local grafana_api="http://admin:admin123@localhost:3200/api/search"
    local response
    response=$(curl -s "$grafana_api" 2>/dev/null)
    
    if echo "$response" | grep -q "Executive Dashboard\|Technical Dashboard\|Alert Dashboard"; then
        print_success "Grafana dashboards are loaded"
        local dashboard_count
        dashboard_count=$(echo "$response" | grep -o '"title":' | wc -l)
        print_info "Found $dashboard_count dashboards"
        return 0
    else
        print_error "Grafana dashboards test failed"
        return 1
    fi
}

# Generate demo alert
generate_demo_alert() {
    print_status "Generating demo alert for testing..."
    
    # Create a temporary high CPU usage simulation
    print_info "This would normally trigger CPU usage alerts in a real environment"
    print_info "For demo purposes, check the Alert Dashboard for simulated alerts"
    
    return 0
}

# Generate demo logs
generate_demo_logs() {
    print_status "Generating demo log entries..."
    
    local log_dir="../logs"
    mkdir -p "$log_dir"
    
    # Generate sample log entries
    echo "$(date) INFO Brand Service: Processing brand analysis request for company XYZ" >> "$log_dir/brand-service.log"
    echo "$(date) INFO Data Collection: Successfully scraped 150 competitor URLs" >> "$log_dir/data-collection.log"
    echo "$(date) INFO Analysis Engine: Generated comprehensive market analysis report" >> "$log_dir/analysis-engine.log"
    echo "$(date) WARNING Brand Service: High memory usage detected (78%)" >> "$log_dir/brand-service.log"
    echo "$(date) ERROR Data Collection: Failed to connect to competitor website - timeout" >> "$log_dir/data-collection.log"
    
    print_success "Demo log entries generated"
    print_info "Check the Log Analysis section in dashboards"
    
    return 0
}

# Main test function
run_monitoring_tests() {
    echo
    echo -e "${BLUE}🧪 Brand Intelligence Hub - Monitoring Stack Tests${NC}"
    echo -e "${BLUE}======================================================${NC}"
    echo
    
    local total_tests=0
    local passed_tests=0
    
    # Test core services
    tests=(
        "Grafana UI:http://localhost:3200/login:200"
        "Prometheus:http://localhost:9090/-/healthy:200"
        "Loki:http://localhost:3100/ready:200"
        "AlertManager:http://localhost:9093/-/healthy:200"
    )
    
    for test in "${tests[@]}"; do
        IFS=':' read -r service url expected_code <<< "$test"
        ((total_tests++))
        if test_endpoint "$service" "$url" "$expected_code"; then
            ((passed_tests++))
        fi
    done
    
    echo
    print_status "Testing monitoring functionality..."
    echo
    
    # Test monitoring features
    ((total_tests++))
    if test_prometheus_metrics; then
        ((passed_tests++))
    fi
    
    ((total_tests++))
    if test_loki_logs; then
        ((passed_tests++))
    fi
    
    ((total_tests++))
    if test_grafana_dashboards; then
        ((passed_tests++))
    fi
    
    echo
    print_status "Generating demo data..."
    echo
    
    generate_demo_logs
    generate_demo_alert
    
    echo
    print_status "=== TEST RESULTS ==="
    echo
    
    if [[ $passed_tests -eq $total_tests ]]; then
        print_success "All tests passed! ($passed_tests/$total_tests)"
        echo
        print_info "🎉 Monitoring stack is ready for hackathon demo!"
        echo
        print_info "Quick Access Links:"
        echo "  • Executive Dashboard: http://localhost:3200/d/executive-dashboard"
        echo "  • Technical Dashboard: http://localhost:3200/d/technical-dashboard"
        echo "  • Alert Dashboard:     http://localhost:3200/d/alert-dashboard"
        echo
        print_info "Login: admin / admin123"
        echo
    else
        print_error "Some tests failed ($passed_tests/$total_tests passed)"
        echo
        print_warning "Check the following:"
        echo "  1. All monitoring containers are running: docker-compose ps"
        echo "  2. No port conflicts exist"
        echo "  3. Services have had time to start up (wait 30 seconds)"
        echo
        return 1
    fi
}

# Help function
show_help() {
    echo "Brand Intelligence Hub - Monitoring Test Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  test     Run all monitoring tests (default)"
    echo "  demo     Generate demo data only"
    echo "  help     Show this help message"
    echo
    echo "Examples:"
    echo "  $0              # Run all tests"
    echo "  $0 test         # Run all tests"
    echo "  $0 demo         # Generate demo data"
    echo
}

# Main execution
main() {
    case "${1:-test}" in
        "test")
            run_monitoring_tests
            ;;
        "demo")
            echo
            print_status "Generating demo data for monitoring stack..."
            echo
            generate_demo_logs
            generate_demo_alert
            echo
            print_success "Demo data generated! Check your dashboards."
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Check if script is being run from monitoring directory
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "This script must be run from the monitoring directory"
    print_info "Usage: cd monitoring && ./test_monitoring.sh"
    exit 1
fi

# Run main function
main "$@"
