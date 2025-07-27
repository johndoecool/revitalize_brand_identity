# Brand Intelligence Hub - Playwright Test Suite

Comprehensive automation test suite for the Brand Intelligence Hub Flutter web application using Playwright.

## Features Tested

- ✅ Theme toggle functionality (Light/Dark mode)
- ✅ Navigation between dashboard tabs
- ✅ Brand selection and analysis workflow
- ✅ Chart interactions and data visualization
- ✅ PDF generation functionality
- ✅ Responsive design across devices
- ✅ Accessibility compliance
- ✅ Performance metrics

## Quick Start

```bash
# 1. Setup test environment (one-time setup)
npm run setup

# 2. Start Flutter web server (in separate terminal)
cd ../flutter && python serve.py

# 3. Run smoke tests to verify everything works
npm run test:smoke

# 4. Run full test suite
npm test
```

## Setup

```bash
# Automated setup (recommended)
npm run setup

# Or manual setup:
npm install
npx playwright install
```

## Running Tests

### Quick Test Commands

```bash
# Smoke tests (fastest, basic functionality)
npm run test:smoke

# Individual test suites
npm run test:theme          # Theme toggle functionality
npm run test:navigation     # Tab navigation
npm run test:workflow       # Brand analysis workflow
npm run test:charts         # Chart interactions
npm run test:pdf           # PDF generation
npm run test:responsive    # Responsive design
npm run test:accessibility # Accessibility compliance
npm run test:performance   # Performance metrics

# All tests
npm test
```

### Advanced Test Options

```bash
# Run with browser UI (see tests executing)
npm run test:headed

# Debug mode (step through tests)
npm run test:debug

# Interactive test runner
npm run test:ui

# View test report
npm run test:report

# Specific browsers
npm run test:chrome
npm run test:firefox
npm run test:safari

# Mobile device testing
npm run test:mobile
```

### Using Test Scripts

```bash
# Full control over test execution
./scripts/run-tests.sh --type smoke --headed
./scripts/run-tests.sh --type all --browser firefox
./scripts/run-tests.sh --help  # See all options
```

## Test Structure

```
frontend-test/
├── tests/                 # Test files
│   ├── theme.spec.ts      # Theme toggle tests
│   ├── navigation.spec.ts # Tab navigation tests
│   ├── workflow.spec.ts   # Brand analysis workflow
│   ├── charts.spec.ts     # Chart interaction tests
│   ├── pdf.spec.ts        # PDF generation tests
│   ├── responsive.spec.ts # Responsive design tests
│   ├── accessibility.spec.ts # A11y tests
│   └── performance.spec.ts   # Performance tests
├── page-objects/          # Page Object Models
│   ├── DashboardPage.ts   # Main dashboard page
│   ├── SetupTab.ts        # Setup tab component
│   ├── AnalysisTab.ts     # Analysis tab component
│   └── components/        # Reusable components
└── utils/                 # Helper utilities
    ├── test-data.ts       # Test data constants
    └── helpers.ts         # Common test functions
```

## Configuration

The test suite is configured to:
- Run against http://localhost:8080 (Flutter web server)
- Test across Chrome, Firefox, Safari browsers
- Include mobile device testing (Pixel 5, iPhone 12)
- Generate HTML, JSON, and JUnit reports
- Capture screenshots and videos on failure
- Record traces for debugging

## Prerequisites

Before running tests, ensure:
1. Flutter web application is built and served on localhost:8080
2. All browser dependencies are installed
3. Node.js 18+ is available