#!/bin/bash

# Brand Intelligence Hub - Test Setup Script

set -e

echo "🔧 Setting up Brand Intelligence Hub Test Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node.js version
echo "📋 Checking Node.js version..."
if command -v node &> /dev/null; then
  NODE_VERSION=$(node --version)
  echo -e "${GREEN}✅ Node.js found: $NODE_VERSION${NC}"
  
  # Check if version is 18 or higher
  NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
  if [ "$NODE_MAJOR" -lt 18 ]; then
    echo -e "${YELLOW}⚠️ Node.js 18+ recommended for best compatibility${NC}"
  fi
else
  echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
  exit 1
fi

# Install dependencies
echo "📦 Installing test dependencies..."
npm install

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install

# Create necessary directories
echo "📁 Creating test directories..."
mkdir -p test-results/screenshots
mkdir -p playwright-report

# Check if Flutter app exists
echo "📋 Checking Flutter app..."
if [ -d "../flutter" ]; then
  echo -e "${GREEN}✅ Flutter app directory found${NC}"
  
  # Check if Flutter web build exists
  if [ -d "../flutter/build/web" ]; then
    echo -e "${GREEN}✅ Flutter web build found${NC}"
  else
    echo -e "${YELLOW}⚠️ Flutter web build not found. Building...${NC}"
    cd ../flutter
    flutter build web
    cd ../frontend-test
  fi
else
  echo -e "${RED}❌ Flutter app directory not found at ../flutter${NC}"
  exit 1
fi

# Verify serve.py exists
if [ -f "../flutter/serve.py" ]; then
  echo -e "${GREEN}✅ Flask server script found${NC}"
else
  echo -e "${YELLOW}⚠️ Flask server script not found. Creating...${NC}"
  cat > ../flutter/serve.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = "build/web"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if not os.path.exists(DIRECTORY):
        print(f"Error: {DIRECTORY} not found. Run 'flutter build web' first.")
        sys.exit(1)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving Flutter web app at http://localhost:{PORT}")
        print(f"Directory: {os.path.abspath(DIRECTORY)}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
EOF
  chmod +x ../flutter/serve.py
fi

echo ""
echo -e "${GREEN}✅ Test environment setup complete!${NC}"
echo ""
echo "🚀 To run tests:"
echo "  ./scripts/run-tests.sh --type smoke    # Quick smoke tests"
echo "  ./scripts/run-tests.sh --type all      # Full test suite"
echo "  ./scripts/run-tests.sh --headed        # Run with browser UI"
echo ""
echo "📚 Available test types:"
echo "  - smoke: Basic functionality tests"
echo "  - theme: Theme toggle tests"
echo "  - navigation: Tab navigation tests"
echo "  - workflow: Brand analysis workflow tests"
echo "  - charts: Chart interaction tests"
echo "  - pdf: PDF generation tests"
echo "  - responsive: Responsive design tests"
echo "  - accessibility: Accessibility tests"
echo "  - performance: Performance tests"
echo ""
echo "🎯 Before running tests, start the Flutter web server:"
echo "  cd ../flutter && python serve.py"