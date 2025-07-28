#!/bin/bash

# Brand Intelligence Hub - Test Execution Script

set -e

echo "🚀 Starting Brand Intelligence Hub Test Suite"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
BROWSER="chromium"
HEADED=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --type)
      TEST_TYPE="$2"
      shift 2
      ;;
    --browser)
      BROWSER="$2"
      shift 2
      ;;
    --headed)
      HEADED=true
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --type     Test type (smoke|theme|navigation|workflow|charts|pdf|responsive|accessibility|performance|all)"
      echo "  --browser  Browser to use (chromium|firefox|webkit)"
      echo "  --headed   Run in headed mode"
      echo "  --help     Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Check if Flutter app is running
echo "📋 Checking if Flutter web app is available..."
if curl -f -s http://localhost:8080 > /dev/null; then
  echo -e "${GREEN}✅ Flutter app is running on localhost:8080${NC}"
else
  echo -e "${RED}❌ Flutter app is not running. Please start it first:${NC}"
  echo "cd ../flutter && python serve.py"
  exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Install Playwright browsers if needed
echo "🌐 Ensuring Playwright browsers are installed..."
npx playwright install

# Build test command
TEST_CMD="npx playwright test"

# Add browser selection
if [ "$BROWSER" != "all" ]; then
  TEST_CMD="$TEST_CMD --project=$BROWSER"
fi

# Add headed mode
if [ "$HEADED" = true ]; then
  TEST_CMD="$TEST_CMD --headed"
fi

# Add test type selection
case $TEST_TYPE in
  smoke)
    TEST_CMD="$TEST_CMD tests/smoke.spec.ts"
    ;;
  theme)
    TEST_CMD="$TEST_CMD tests/theme.spec.ts"
    ;;
  navigation)
    TEST_CMD="$TEST_CMD tests/navigation.spec.ts"
    ;;
  workflow)
    TEST_CMD="$TEST_CMD tests/workflow.spec.ts"
    ;;
  charts)
    TEST_CMD="$TEST_CMD tests/charts.spec.ts"
    ;;
  pdf)
    TEST_CMD="$TEST_CMD tests/pdf.spec.ts"
    ;;
  responsive)
    TEST_CMD="$TEST_CMD tests/responsive.spec.ts"
    ;;
  accessibility)
    TEST_CMD="$TEST_CMD tests/accessibility.spec.ts"
    ;;
  performance)
    TEST_CMD="$TEST_CMD tests/performance.spec.ts"
    ;;
  all)
    # Run all tests
    ;;
  *)
    echo -e "${RED}❌ Unknown test type: $TEST_TYPE${NC}"
    exit 1
    ;;
esac

echo "🧪 Running tests with command: $TEST_CMD"
echo ""

# Run tests
if eval $TEST_CMD; then
  echo ""
  echo -e "${GREEN}✅ All tests completed successfully!${NC}"
  echo ""
  echo "📊 View detailed report:"
  echo "npm run test:report"
else
  echo ""
  echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
  echo ""
  echo "📊 View detailed report:"
  echo "npm run test:report"
  exit 1
fi