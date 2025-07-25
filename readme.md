# Revitalize Brand Identity

A comprehensive microservice architecture for brand management, providing APIs for brand search, area suggestions, competitor discovery, and data analysis.

## Features

- Brand Search API
- Area Suggestions API  
- Competitor Discovery API
- Data Collection Service
- Analysis Engine
- Frontend Service
- OpenAPI documentation
- Unit tests

## Table of Contents

- [Python Installation and Configuration](#python-installation-and-configuration)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Project Setup in Visual Studio Code](#project-setup-in-visual-studio-code)
- [Swagger Documentation Setup](#swagger-documentation-setup)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)

## Python Installation and Configuration

### Windows

1. **Download Python:**
   - Visit [python.org](https://www.python.org/downloads/windows/)
   - Download the latest Python 3.11+ installer
   - **Important:** Check "Add Python to PATH" during installation

2. **Verify Installation:**
   ```powershell
   python --version
   pip --version
   ```

3. **Update pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

### macOS

1. **Using Homebrew (Recommended):**
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python
   brew install python@3.11
   ```

2. **Alternative - Direct Download:**
   - Visit [python.org](https://www.python.org/downloads/macos/)
   - Download and install the macOS installer

3. **Verify Installation:**
   ```bash
   python3 --version
   pip3 --version
   ```

### Linux (Ubuntu/Debian)

1. **Update package list:**
   ```bash
   sudo apt update
   ```

2. **Install Python:**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **For CentOS/RHEL/Fedora:**
   ```bash
   sudo yum install python3 python3-pip
   # or for newer versions
   sudo dnf install python3 python3-pip
   ```

4. **Verify Installation:**
   ```bash
   python3 --version
   pip3 --version
   ```

## Virtual Environment Setup

### Creating Virtual Environments

#### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If execution policy error occurs:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Managing Virtual Environments

#### Installing Libraries
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Install individual packages
pip install fastapi uvicorn pytest

# Install with specific versions
pip install fastapi==0.104.1
```

#### Updating Virtual Environment
```bash
# Update all packages
pip list --outdated
pip install --upgrade package_name

# Update pip itself
python -m pip install --upgrade pip
```

#### Generating Requirements File
```bash
# Generate requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt in new environment
pip install -r requirements.txt
```

#### Deleting Virtual Environment
```bash
# Deactivate first
deactivate

# Remove directory (Windows)
Remove-Item -Recurse -Force venv

# Remove directory (macOS/Linux)
rm -rf venv
```

## Project Setup in Visual Studio Code

### VS Code Configuration

1. **Open the project:**
   ```bash
   code .
   ```

2. **Select Python Interpreter:**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment

3. **Configure Settings (`.vscode/settings.json`):**
   ```json
   {
     "python.defaultInterpreterPath": "./venv/bin/python",
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black",
     "python.testing.pytestEnabled": true,
     "python.testing.unittestEnabled": false,
     "files.exclude": {
       "**/__pycache__": true,
       "**/*.pyc": true
     }
   }
   ```

4. **Configure Launch Configuration (`.vscode/launch.json`):**
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: FastAPI",
         "type": "python",
         "request": "launch",
         "module": "uvicorn",
         "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"],
         "jinja": true
       }
     ]
   }
   ```

## Swagger Documentation Setup

### Installing Swagger UI Locally

#### Method 1: Using npm (Recommended)
```bash
# Install Node.js first, then:
npm install -g swagger-ui-dist

# Serve Swagger UI
npx swagger-ui-serve path/to/your/openapi.json
```

#### Method 2: Using Docker
```bash
# Pull Swagger UI Docker image
docker pull swaggerapi/swagger-ui

# Run Swagger UI container
docker run -p 8080:8080 -e SWAGGER_JSON=/docs/openapi.json -v $(pwd)/docs:/docs swaggerapi/swagger-ui
```

#### Method 3: Python HTTP Server
```bash
# Download Swagger UI
curl -L https://github.com/swagger-api/swagger-ui/archive/master.zip -o swagger-ui.zip
unzip swagger-ui.zip

# Copy your OpenAPI spec
cp openapi.json swagger-ui-master/dist/

# Serve with Python
cd swagger-ui-master/dist
python -m http.server 8080
```

### Publishing Swagger Documentation

#### Generating OpenAPI Specification
```python
# Add to your FastAPI app
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Brand Identity API",
        version="1.0.0",
        description="API for brand management and analysis",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### Exporting OpenAPI Specification
```bash
# Export OpenAPI JSON
curl http://localhost:8001/openapi.json > openapi.json

# Or using Python script
python -c "
import json
import requests
response = requests.get('http://localhost:8001/openapi.json')
with open('openapi.json', 'w') as f:
    json.dump(response.json(), f, indent=2)
"
```

## API Endpoints

### Brand Service (`localhost:8001`)
- `POST /api/v1/brands/search` - Search for brands
  ```json
  {
    "query": "tech company",
    "filters": {
      "industry": "technology",
      "size": "large"
    }
  }
  ```

- `GET /api/v1/brands/{brand_id}/areas` - Get area suggestions for a brand
- `GET /api/v1/brands/{brand_id}/competitors` - Get competitors for a brand in a specific area

### Data Collection Service (`localhost:8002`)
- `POST /api/v1/data/collect` - Trigger data collection
- `GET /api/v1/data/status` - Check collection status
- `GET /api/v1/data/sources` - List available data sources

### Analysis Engine (`localhost:8003`)
- `POST /api/v1/analysis/brand` - Analyze brand performance
- `GET /api/v1/analysis/reports/{report_id}` - Get analysis report
- `POST /api/v1/analysis/compare` - Compare multiple brands

### Frontend Service (`localhost:8000`)
- Web interface for all services
- Dashboard for brand analytics
- Interactive data visualization

### Adding New Endpoints

To add new API endpoints:

1. **Define the endpoint in your service:**
   ```python
   @app.post("/api/v1/your-endpoint")
   async def your_endpoint(request: YourRequest):
       # Implementation
       return {"result": "success"}
   ```

2. **Add request/response models:**
   ```python
   from pydantic import BaseModel
   
   class YourRequest(BaseModel):
       field1: str
       field2: int
   
   class YourResponse(BaseModel):
       result: str
       data: dict
   ```

3. **Update documentation:**
   - Add endpoint description to this README
   - Update Postman collection
   - Ensure OpenAPI spec is generated correctly

4. **Add tests:**
   ```python
   def test_your_endpoint():
       response = client.post("/api/v1/your-endpoint", json={"field1": "test"})
       assert response.status_code == 200
   ```

## Running the Services

### Individual Services
```bash
# Brand Service
cd services/brand_service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Data Service
cd services/data_service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Analysis Service
cd services/analysis_service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Using Docker Compose (if available)
```bash
docker-compose up -d
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_brand_service.py

# Run with verbose output
pytest -v
```

### API Documentation Access
- **Brand Service Swagger UI:** http://localhost:8001/docs
- **Data Service Swagger UI:** http://localhost:8002/docs
- **Analysis Service Swagger UI:** http://localhost:8003/docs
- **ReDoc:** http://localhost:800x/redoc (replace x with service port)

## Development Workflow

1. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```

2. **Start Development:**
   ```bash
   # Run services in development mode
   uvicorn app.main:app --reload
   ```

3. **Testing:**
   ```bash
   pytest --cov=app
   ```

4. **Documentation:**
   ```bash
   # Access Swagger UI at http://localhost:800x/docs
   # Export OpenAPI spec
   curl http://localhost:800x/openapi.json > openapi.json
   ```
