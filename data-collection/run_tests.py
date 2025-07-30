#!/usr/bin/env python3
"""
Test Runner for Data Collection Service

Provides easy access to different test suites and testing scenarios.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_pytest_command(args):
    """Run pytest with the given arguments"""
    cmd = ['python', '-m', 'pytest'] + args
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    return subprocess.run(cmd, cwd=Path(__file__).parent)

def run_unit_tests():
    """Run only unit tests"""
    return run_pytest_command([
        'tests/unit/',
        '-v',
        '--tb=short'
    ])

def run_integration_tests():
    """Run only integration tests"""
    return run_pytest_command([
        'tests/integration/',
        '-v',
        '--tb=short'
    ])

def run_all_tests():
    """Run all tests"""
    return run_pytest_command([
        'tests/',
        '-v',
        '--tb=short'
    ])

def run_fast_tests():
    """Run fast tests only (excluding slow markers)"""
    return run_pytest_command([
        'tests/',
        '-v',
        '-m', 'not slow',
        '--tb=short'
    ])

def run_scraping_tests():
    """Run scraping-related tests"""
    return run_pytest_command([
        'tests/',
        '-v',
        '-k', 'scraper or scraping',
        '--tb=short'
    ])

def run_llm_tests():
    """Run LLM-related tests"""
    return run_pytest_command([
        'tests/',
        '-v',
        '-k', 'llm or sentiment',
        '--tb=short'
    ])

def run_coverage():
    """Run tests with coverage report"""
    try:
        # Install coverage if not available
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest-cov'], 
                      capture_output=True, check=False)
        
        return run_pytest_command([
            'tests/',
            '--cov=src',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--tb=short'
        ])
    except Exception as e:
        print(f"Coverage testing failed: {e}")
        print("Try installing pytest-cov: pip install pytest-cov")
        return run_all_tests()

def run_specific_test(test_path):
    """Run a specific test file or test function"""
    return run_pytest_command([
        test_path,
        '-v',
        '--tb=short'
    ])

def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔍 Checking test environment...")
    print("-" * 40)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not installed. Run: pip install pytest pytest-asyncio")
        return False
    
    # Check if pytest-asyncio is installed
    try:
        import pytest_asyncio
        print(f"✅ pytest-asyncio version: {pytest_asyncio.__version__}")
    except ImportError:
        print("❌ pytest-asyncio not installed. Run: pip install pytest-asyncio")
        return False
    
    # Check if src modules can be imported
    try:
        from scrapers import WebScraper
        print("✅ Source modules can be imported")
    except ImportError as e:
        print(f"❌ Cannot import source modules: {e}")
        return False
    
    # Check test structure
    test_dirs = ['tests/unit', 'tests/integration', 'tests/fixtures', 'tests/utils']
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            print(f"✅ {test_dir} directory exists")
        else:
            print(f"❌ {test_dir} directory missing")
            return False
    
    print("\n🎉 Test environment looks good!")
    return True

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Test Runner for Data Collection Service')
    parser.add_argument('command', nargs='?', default='all',
                       choices=['unit', 'integration', 'all', 'fast', 'scraping', 'llm', 
                               'coverage', 'check', 'specific'],
                       help='Test suite to run')
    parser.add_argument('--test', '-t', help='Specific test file or function to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🧪 Data Collection Service Test Runner")
    print("=" * 60)
    
    if args.command == 'check':
        success = check_test_environment()
        sys.exit(0 if success else 1)
    
    if args.command == 'specific':
        if not args.test:
            print("❌ Please specify a test with --test flag")
            print("Example: python run_tests.py specific --test tests/unit/test_web_scraper.py")
            sys.exit(1)
        result = run_specific_test(args.test)
    elif args.command == 'unit':
        result = run_unit_tests()
    elif args.command == 'integration':
        result = run_integration_tests()
    elif args.command == 'fast':
        result = run_fast_tests()
    elif args.command == 'scraping':
        result = run_scraping_tests()
    elif args.command == 'llm':
        result = run_llm_tests()
    elif args.command == 'coverage':
        result = run_coverage()
    else:  # 'all'
        result = run_all_tests()
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(result.returncode)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        sys.exit(1) 