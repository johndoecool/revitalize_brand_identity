# Analysis Service Setup and Run Commands

# 1. Setup Virtual Environment
python -m venv analysis_env
analysis_env\Scripts\activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Configure Environment
copy .env.example .env
# Edit .env and add your OpenAI API key

# 4. Run the Service
python app/main.py

# Alternative: Run with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# 5. Run Tests
pytest

# 6. Run with coverage
pytest --cov=app tests/

# 7. Format code
black app/ tests/

# 8. Check health
curl http://localhost:8003/health
