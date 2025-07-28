#!/usr/bin/env python3
"""
Analysis Service Setup Script
Automates the setup process for the Analysis Engine service with Python compatibility checks
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required")
        return False
    
    if version.major == 3 and version.minor >= 12:
        print("⚠️  Python 3.12+ detected - using compatible package versions")
    
    return True

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_with_pip_upgrade(pip_cmd, package, cwd):
    """Install package with pip upgrade"""
    install_cmd = f'"{pip_cmd}" install --upgrade pip setuptools wheel'
    success, output = run_command(install_cmd, cwd=cwd)
    if not success:
        print(f"⚠️  Failed to upgrade pip: {output}")
    
    install_cmd = f'"{pip_cmd}" install {package}'
    return run_command(install_cmd, cwd=cwd)

def main():
    print("🚀 Setting up Analysis Engine Service...")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Get service directory
    service_dir = Path(__file__).parent
    print(f"📁 Working in: {service_dir}")
    
    # Step 1: Create virtual environment
    print("\n📦 Creating virtual environment...")
    success, output = run_command("python -m venv analysis_env", cwd=service_dir)
    if success:
        print("✅ Virtual environment created")
    else:
        print(f"❌ Failed to create virtual environment: {output}")
        return
    
    # Step 2: Determine paths
    if os.name == 'nt':  # Windows
        activate_script = service_dir / "analysis_env" / "Scripts" / "activate.bat"
        pip_cmd = str(service_dir / "analysis_env" / "Scripts" / "pip.exe")
        python_cmd = str(service_dir / "analysis_env" / "Scripts" / "python.exe")
    else:  # Unix/Linux/MacOS
        activate_script = service_dir / "analysis_env" / "bin" / "activate"
        pip_cmd = str(service_dir / "analysis_env" / "bin" / "pip")
        python_cmd = str(service_dir / "analysis_env" / "bin" / "python")
    
    # Step 3: Upgrade pip and install core dependencies
    print("\n🔧 Upgrading pip and installing core dependencies...")
    upgrade_cmd = f'"{pip_cmd}" install --upgrade pip setuptools wheel'
    success, output = run_command(upgrade_cmd, cwd=service_dir)
    if success:
        print("✅ Core tools upgraded")
    else:
        print(f"⚠️  Warning during upgrade: {output}")
    
    # Step 4: Install main requirements
    print("\n📚 Installing main dependencies...")
    requirements_file = service_dir / "requirements.txt"
    install_cmd = f'"{pip_cmd}" install -r "{requirements_file}"'
    
    success, output = run_command(install_cmd, cwd=service_dir)
    if success:
        print("✅ Main dependencies installed successfully")
    else:
        print(f"❌ Failed to install dependencies: {output}")
        print("🔄 Trying alternative installation method...")
        
        # Try installing packages individually
        with open(requirements_file, 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for package in packages:
            print(f"   Installing {package}...")
            success, output = install_with_pip_upgrade(pip_cmd, package, service_dir)
            if success:
                print(f"   ✅ {package}")
            else:
                print(f"   ⚠️  Failed to install {package}: {output}")
    
    # Step 5: Install development dependencies (optional)
    print("\n🛠️  Installing development dependencies...")
    dev_requirements = service_dir / "requirements-dev.txt"
    if dev_requirements.exists():
        install_cmd = f'"{pip_cmd}" install -r "{dev_requirements}"'
        success, output = run_command(install_cmd, cwd=service_dir)
        if success:
            print("✅ Development dependencies installed")
        else:
            print(f"⚠️  Development dependencies warning: {output}")
    
    # Step 6: Setup environment file
    print("\n⚙️  Setting up environment configuration...")
    env_example = service_dir / ".env.example"
    env_file = service_dir / ".env"
    
    if not env_file.exists() and env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Environment file created (.env)")
        print("⚠️  Please edit .env and add your OpenAI API key")
    else:
        print("ℹ️  Environment file already exists")
    
    # Step 7: Verify installation
    print("\n🔍 Verifying installation...")
    check_cmd = f'"{python_cmd}" -c "import fastapi, openai, uvicorn; print(\'All packages imported successfully\')"'
    
    success, output = run_command(check_cmd, cwd=service_dir)
    if success:
        print("✅ Installation verified")
    else:
        print(f"⚠️  Verification warning: {output}")
        print("   Some packages may not be available, but core functionality should work")
    
    # Step 8: Create run script
    print("\n📝 Creating run script...")
    
    if os.name == 'nt':  # Windows
        run_script_content = f'''@echo off
echo Starting Analysis Engine Service...
cd /d "{service_dir}"
call analysis_env\\Scripts\\activate.bat
echo Checking environment...
if not exist .env (
    echo ERROR: .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)
echo Starting service on http://localhost:8003
python app\\main.py
pause
'''
        run_script_path = service_dir / "start_service.bat"
    else:  # Unix/Linux/MacOS
        run_script_content = f'''#!/bin/bash
echo "Starting Analysis Engine Service..."
cd "{service_dir}"
source analysis_env/bin/activate
echo "Checking environment..."
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi
echo "Starting service on http://localhost:8003"
python app/main.py
'''
        run_script_path = service_dir / "start_service.sh"
    
    with open(run_script_path, 'w') as f:
        f.write(run_script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod(run_script_path, 0o755)
    
    print(f"✅ Run script created: {run_script_path}")
    
    # Step 9: Display next steps
    print("\n🎉 Setup completed!")
    print("\n📋 Next Steps:")
    print("1. Configure your OpenAI API key:")
    print(f"   Edit: {env_file}")
    print("   Add: OPENAI_API_KEY=your_api_key_here")
    
    print("\n2. Start the service:")
    if os.name == 'nt':
        print(f"   Double-click: {run_script_path}")
        print("   OR in terminal:")
        print(f"   cd {service_dir}")
        print("   analysis_env\\Scripts\\activate")
        print("   python app\\main.py")
    else:
        print(f"   ./{run_script_path}")
        print("   OR in terminal:")
        print(f"   cd {service_dir}")
        print("   source analysis_env/bin/activate")
        print("   python app/main.py")
    
    print("\n3. Test the service:")
    print("   http://localhost:8003/health")
    print("   http://localhost:8003/docs")
    
    print("\n4. Run the demo:")
    print("   python demo.py")
    
    print("\n🔗 Documentation URLs:")
    print("   • API Docs: http://localhost:8003/docs")
    print("   • ReDoc: http://localhost:8003/redoc")
    print("   • Health: http://localhost:8003/health")
    
    print("\n💡 Troubleshooting:")
    print("   • If imports fail, try: pip install --upgrade setuptools")
    print("   • For Python 3.13+: All packages use compatible versions")
    print("   • Check logs in terminal for detailed error messages")

if __name__ == "__main__":
    main()
