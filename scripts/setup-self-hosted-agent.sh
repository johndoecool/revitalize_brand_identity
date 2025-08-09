#!/bin/bash
# =============================================================================
# Azure DevOps Self-Hosted Agent Setup Script
# =============================================================================
# This script installs and configures an Azure DevOps self-hosted agent
# Solves the parallelism limitation for free ADO accounts
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AGENT_POOL_NAME="Brand-Intelligence-Pool"
AGENT_NAME="brand-intelligence-agent-$(hostname)"
WORK_DIRECTORY="_work"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Azure DevOps Self-Hosted Agent      ${NC}"
echo -e "${BLUE}   Brand Intelligence Hub Setup         ${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Function to print step headers
print_step() {
    echo -e "\n${BLUE}🔧 $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

print_step "Step 1: System Requirements Check"

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_success "Linux OS detected"
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_success "macOS detected"
    OS="macos"
else
    print_error "Unsupported OS: $OSTYPE"
    exit 1
fi

# Check required tools
print_info "Checking required tools..."

command -v curl >/dev/null 2>&1 || { print_error "curl is required but not installed"; exit 1; }
command -v tar >/dev/null 2>&1 || { print_error "tar is required but not installed"; exit 1; }
command -v docker >/dev/null 2>&1 || { print_error "Docker is required but not installed"; exit 1; }

print_success "All required tools are installed"

# Check Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is installed but not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

print_step "Step 2: Azure DevOps Configuration"

# Get ADO organization details
echo -e "\nPlease provide your Azure DevOps details:"
read -p "Organization URL (e.g., https://dev.azure.com/yourorg): " ADO_URL
read -p "Project Name: " PROJECT_NAME
read -p "Personal Access Token (PAT): " -s PAT
echo

if [ -z "$ADO_URL" ] || [ -z "$PROJECT_NAME" ] || [ -z "$PAT" ]; then
    print_error "All fields are required"
    exit 1
fi

print_step "Step 3: Download Azure DevOps Agent"

# Create agent directory
AGENT_DIR="$HOME/ado-agent"
mkdir -p "$AGENT_DIR"
cd "$AGENT_DIR"

print_info "Downloading latest agent..."

# Determine agent download URL based on OS
if [ "$OS" == "linux" ]; then
    AGENT_URL="https://vstsagentpackage.azureedge.net/agent/3.232.0/vsts-agent-linux-x64-3.232.0.tar.gz"
else
    AGENT_URL="https://vstsagentpackage.azureedge.net/agent/3.232.0/vsts-agent-osx-x64-3.232.0.tar.gz"
fi

# Download and extract agent
curl -LsS "$AGENT_URL" | tar -xz
print_success "Agent downloaded and extracted"

print_step "Step 4: Configure Agent"

print_info "Configuring agent with your Azure DevOps organization..."

# Configure the agent
./config.sh --unattended \
    --url "$ADO_URL" \
    --auth pat \
    --token "$PAT" \
    --pool "$AGENT_POOL_NAME" \
    --agent "$AGENT_NAME" \
    --work "$WORK_DIRECTORY" \
    --replace

if [ $? -eq 0 ]; then
    print_success "Agent configured successfully"
else
    print_error "Agent configuration failed"
    exit 1
fi

print_step "Step 5: Install Agent as Service"

if [ "$OS" == "linux" ]; then
    # Install as systemd service on Linux
    sudo ./svc.sh install
    sudo ./svc.sh start
    print_success "Agent installed and started as systemd service"
    
    # Check service status
    if systemctl is-active --quiet vsts.agent.*.service; then
        print_success "Agent service is running"
    else
        print_error "Agent service failed to start"
    fi
else
    # Install as LaunchDaemon on macOS
    sudo ./svc.sh install
    sudo ./svc.sh start
    print_success "Agent installed and started as LaunchDaemon"
fi

print_step "Step 6: Verification"

print_info "Verifying agent installation..."

# Test Docker access for the agent
print_info "Testing Docker access..."
docker --version
print_success "Docker is accessible"

# Test Python
if command -v python3 >/dev/null 2>&1; then
    python3 --version
    print_success "Python 3 is available"
else
    print_error "Python 3 not found. Please install Python 3.11+"
fi

print_step "Step 7: Setup Complete"

print_success "Azure DevOps Self-Hosted Agent Setup Complete!"
echo
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Go to your Azure DevOps project"
echo "2. Navigate to Project Settings > Agent Pools"
echo "3. Check '$AGENT_POOL_NAME' pool"
echo "4. Verify '$AGENT_NAME' is online"
echo "5. Update your pipeline to use pool: '$AGENT_POOL_NAME'"
echo
echo -e "${BLUE}📊 Agent Details:${NC}"
echo "Agent Name: $AGENT_NAME"
echo "Agent Pool: $AGENT_POOL_NAME"
echo "Work Directory: $AGENT_DIR/$WORK_DIRECTORY"
echo "Configuration: $AGENT_DIR/.agent"
echo
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "Start:   sudo $AGENT_DIR/svc.sh start"
echo "Stop:    sudo $AGENT_DIR/svc.sh stop"
echo "Status:  sudo $AGENT_DIR/svc.sh status"
echo "Remove:  sudo $AGENT_DIR/svc.sh uninstall"
echo
echo -e "${BLUE}🚀 Pipeline Configuration:${NC}"
echo "Add this to your azure-pipelines.yml:"
echo "pool:"
echo "  name: '$AGENT_POOL_NAME'"
echo
print_success "Ready to run enterprise CI/CD pipelines without parallelism limits!"

# Create a simple status check script
cat > "$HOME/check-ado-agent.sh" << 'EOF'
#!/bin/bash
echo "🔍 Azure DevOps Agent Status"
echo "============================="
echo "Agent Directory: ~/ado-agent"
echo "Service Status:"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    systemctl status vsts.agent.*.service --no-pager -l
else
    sudo ~/ado-agent/svc.sh status
fi
echo
echo "Docker Status:"
docker --version
echo
echo "Python Status:"
python3 --version 2>/dev/null || echo "Python 3 not found"
echo
echo "Disk Space:"
df -h ~/ado-agent
EOF

chmod +x "$HOME/check-ado-agent.sh"
print_success "Status check script created: ~/check-ado-agent.sh"

echo
print_success "🎉 Setup completed successfully! Your self-hosted agent is ready."
print_info "Run ~/check-ado-agent.sh anytime to check agent status"