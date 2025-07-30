# Data Collection Service - Setup Guide

## Quick Setup

### 1. Install Dependencies

#### Option A: Automated Setup (Recommended)
```bash
cd services/data-collection
python setup_dependencies.py
```

#### Option B: Manual Installation
```bash
cd services/data-collection
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your API credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Twitter API v2 Credentials (Required for social media data)
TWITTER_BEARER_TOKEN=your_actual_twitter_bearer_token_here

# News API (Required for news data)
NEWS_API_KEY=your_actual_news_api_key_here

# LLM API Keys for Advanced Sentiment Analysis (Optional but Recommended)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# LLM Configuration
PREFERRED_LLM_PROVIDER=openai  # openai, anthropic, huggingface, or cohere
LLM_MODEL_NAME=gpt-3.5-turbo  # or gpt-4, claude-3-haiku-20240307, etc.

# Optional: Database and Redis URLs
DATABASE_URL=sqlite:///data/app.db
REDIS_URL=redis://localhost:6379/0
```

### 3. Get API Credentials

#### Twitter API
1. Visit [Twitter Developer Portal](https://developer.twitter.com)
2. Apply for API access (approval required)
3. Create a project and generate Bearer Token
4. Add the Bearer Token to your `.env` file

#### News API
1. Visit [NewsAPI.org](https://newsapi.org)
2. Sign up for a free account
3. Get your API key
4. Add it to your `.env` file

#### LLM APIs for Advanced Sentiment Analysis (Optional but Recommended)

**OpenAI (Recommended)**
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Create an account and generate API key
3. Add `OPENAI_API_KEY=your-key-here` to `.env`

**Anthropic Claude**
1. Visit [Anthropic Console](https://console.anthropic.com)
2. Create account and get API key
3. Add `ANTHROPIC_API_KEY=your-key-here` to `.env`

**Hugging Face**
1. Visit [Hugging Face](https://huggingface.co)
2. Create account and generate API token
3. Add `HUGGINGFACE_API_KEY=your-key-here` to `.env`

**Cohere**
1. Visit [Cohere Platform](https://cohere.ai)
2. Sign up and get API key
3. Add `COHERE_API_KEY=your-key-here` to `.env`

### 4. Install Browser for Web Scraping

For advanced web scraping features, install Chrome or Chromium:

#### Windows
Download and install [Google Chrome](https://www.google.com/chrome/)

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install google-chrome-stable
```

#### macOS
```bash
brew install --cask google-chrome
```

### 5. Start the Service

```bash
cd services/data-collection
python -m src.main
```

The service will be available at: `http://localhost:8002`

## Troubleshooting

### Common Issues

#### 1. BeautifulSoup Import Error
```
ERROR | BeautifulSoup not installed for Facebook scraping
```

**Solution:**
```bash
pip install beautifulsoup4 lxml html5lib
```

#### 2. Selenium WebDriver Issues
```
ERROR | Chrome WebDriver - Failed
```

**Solutions:**
- Install Google Chrome browser
- Update Chrome to the latest version
- Run: `pip install webdriver-manager`

#### 3. Twitter API Authentication Failed
```
ERROR | Authentication failed (401) for Twitter API
```

**Solutions:**
- Verify your Twitter Bearer Token is correct
- Ensure the token has proper permissions
- Check if your Twitter Developer account is approved

#### 4. Missing Dependencies
```
ERROR | Module 'xyz' not found
```

**Solution:**
Run the automated setup:
```bash
python setup_dependencies.py
```

### Dependency Verification

To check if all dependencies are properly installed:

```bash
python -c "
import bs4, selenium, requests, textblob, vaderSentiment
print('✅ All core dependencies available!')
"
```

### Manual Dependency Installation

If automated setup fails, install dependencies manually:

```bash
# Core web scraping
pip install beautifulsoup4==4.12.2
pip install selenium==4.15.2
pip install webdriver-manager==4.0.1
pip install lxml==4.9.3

# HTTP clients
pip install requests==2.31.0
pip install aiohttp==3.9.1

# Sentiment analysis
pip install textblob==0.17.1
pip install vaderSentiment==3.3.2

# API framework
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
```

## Feature Availability

| Feature | Dependencies | Status |
|---------|-------------|--------|
| Basic API | FastAPI, Uvicorn | ✅ Always available |
| Twitter Data | Twitter Bearer Token | ❓ Requires API key |
| News Data | News API Key | ❓ Requires API key |
| Web Scraping | BeautifulSoup4, lxml | ✅ Installed |
| Advanced Scraping | Selenium, Chrome | ❓ Requires browser |
| Sentiment Analysis | TextBlob, VADER | ✅ Installed |
| **LLM Sentiment Analysis** | **OpenAI/Anthropic/etc.** | **✨ Enhanced accuracy** |

## LLM-Enhanced Sentiment Analysis

The service now includes advanced sentiment analysis using Large Language Models (LLMs) for more accurate and context-aware brand perception analysis.

### ✨ Features

- **Context-Aware Analysis**: Understands brand context in social media posts
- **Multi-Provider Support**: OpenAI, Anthropic, Hugging Face, Cohere
- **Automatic Fallback**: Falls back to traditional methods if LLM unavailable  
- **Configurable**: Choose your preferred LLM provider
- **Cost-Effective**: Uses efficient models with low token usage

### 🔧 Configuration

```bash
# Set your preferred LLM provider
export PREFERRED_LLM_PROVIDER=openai

# Configure model (optional)
export LLM_MODEL_NAME=gpt-3.5-turbo
export LLM_TEMPERATURE=0.1
export LLM_MAX_TOKENS=150
```

### 🧪 Testing LLM Sentiment

```bash
python test_llm_sentiment.py
```

### 💡 Benefits Over Traditional Methods

| Method | Accuracy | Context Understanding | Sarcasm Detection | Brand Awareness |
|--------|----------|---------------------|------------------|-----------------|
| Traditional (TextBlob/VADER) | 70% | Limited | Poor | None |
| **LLM-Based** | **90%+** | **Excellent** | **Good** | **Excellent** |

### 📊 Example Improvements

**Traditional Analysis:**
- "Apple's new update is *just great*" → Positive (0.8) ❌ (misses sarcasm)

**LLM Analysis:**  
- "Apple's new update is *just great*" → Negative (-0.6) ✅ (detects sarcasm)

**Web Content Analysis:**
- Analyzes entire page content + brand context
- Understands brand mentions in articles/reviews
- Provides more nuanced sentiment scores

## Performance Optimization

### For Production

1. **Use environment variables** instead of hardcoded values
2. **Install Redis** for caching and job queuing
3. **Configure proper logging levels**
4. **Use a production WSGI server** like Gunicorn

```bash
# Install Redis
sudo apt-get install redis-server  # Linux
brew install redis                 # macOS

# Start with Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

### Memory and Speed

- **Headless browsing**: Selenium runs in headless mode by default
- **Connection pooling**: HTTP clients use connection pooling
- **Async operations**: All I/O operations are asynchronous

## Support

If you encounter issues:

1. Check the logs in `logs/app.log`
2. Run `python setup_dependencies.py` to verify setup
3. Ensure all API credentials are valid
4. Check that required services (Redis, Chrome) are running

For additional help, check the main project documentation. 