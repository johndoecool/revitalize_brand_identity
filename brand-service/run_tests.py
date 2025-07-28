#!/usr/bin/env python3
"""
Test runner script for the brand service
"""
import sys
import subprocess
import os

def run_tests():
    """Run all tests"""
    print("Running Brand Service Tests...")
    print("=" * 50)
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run unit tests
    print("\n1. Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", "-v", "--tb=short"
    ], capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        return False
    
    # Test the service can be imported
    print("\n2. Testing service imports...")
    try:
        from app.main import app
        from app.services import BrandService
        from app.models import BrandSearchRequest
        print("✅ All imports successful!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
