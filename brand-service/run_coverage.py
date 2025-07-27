"""
Script to run comprehensive unit tests with coverage reporting
"""
import os
import sys
import subprocess
from pathlib import Path

def run_coverage_tests():
    """Run tests with coverage and generate reports"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("BRAND SERVICE - UNIT TEST COVERAGE REPORT")
    print("=" * 60)
    print()
    
    # Change to project directory
    os.chdir(project_root)
    
    # Clean previous coverage data
    print("🧹 Cleaning previous coverage data...")
    try:
        os.remove(".coverage")
    except FileNotFoundError:
        pass
    
    # Run tests with coverage
    print("🧪 Running unit tests with coverage...")
    cmd = [
        sys.executable, "-m", "coverage", "run",
        "--source=app",
        "--omit=app/__pycache__/*,app/*/__pycache__/*",
        "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tests completed successfully!")
    else:
        print("❌ Some tests failed:")
        print(result.stdout)
        print(result.stderr)
    
    print()
    
    # Generate coverage report
    print("📊 Generating coverage report...")
    
    # Terminal report
    print("\n" + "=" * 60)
    print("COVERAGE SUMMARY")
    print("=" * 60)
    
    coverage_cmd = [sys.executable, "-m", "coverage", "report", "-m"]
    coverage_result = subprocess.run(coverage_cmd, capture_output=True, text=True)
    print(coverage_result.stdout)
    
    # HTML report
    print("📄 Generating HTML coverage report...")
    html_cmd = [sys.executable, "-m", "coverage", "html", "--directory=htmlcov"]
    subprocess.run(html_cmd, capture_output=True, text=True)
    
    html_report_path = project_root / "htmlcov" / "index.html"
    if html_report_path.exists():
        print(f"✅ HTML coverage report generated: {html_report_path}")
        print("   Open this file in a web browser for detailed coverage analysis")
    
    # JSON report for programmatic analysis
    print("📄 Generating JSON coverage report...")
    json_cmd = [sys.executable, "-m", "coverage", "json"]
    subprocess.run(json_cmd, capture_output=True, text=True)
    
    json_report_path = project_root / "coverage.json"
    if json_report_path.exists():
        print(f"✅ JSON coverage report generated: {json_report_path}")
    
    # Extract overall coverage percentage
    try:
        import json
        with open("coverage.json", "r") as f:
            coverage_data = json.load(f)
        
        total_coverage = coverage_data["totals"]["percent_covered"]
        
        print()
        print("=" * 60)
        print(f"OVERALL COVERAGE: {total_coverage:.1f}%")
        print("=" * 60)
        
        if total_coverage >= 80.0:
            print("🎉 SUCCESS: Coverage target of 80% achieved!")
        else:
            print(f"⚠️  WARNING: Coverage is below 80% target (current: {total_coverage:.1f}%)")
            print("   Consider adding more tests to improve coverage")
        
        print()
        
        # Show files with low coverage
        print("📋 FILES WITH COVERAGE < 80%:")
        print("-" * 40)
        
        low_coverage_files = []
        for filename, file_data in coverage_data["files"].items():
            file_coverage = file_data["summary"]["percent_covered"]
            if file_coverage < 80.0:
                low_coverage_files.append((filename, file_coverage))
        
        if low_coverage_files:
            for filename, coverage in sorted(low_coverage_files, key=lambda x: x[1]):
                print(f"  {filename}: {coverage:.1f}%")
        else:
            print("  All files have >= 80% coverage! 🎉")
        
    except Exception as e:
        print(f"Could not parse coverage data: {e}")
    
    print()
    print("=" * 60)
    print("COVERAGE REPORT COMPLETE")
    print("=" * 60)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_coverage_tests()
    sys.exit(0 if success else 1)
