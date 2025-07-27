#!/usr/bin/env python3
"""
Simple Together.ai API connectivity test script
"""
import requests
import json
import urllib3
import ssl
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_together_ai_simple():
    """Simple test with no SSL verification"""
    
    api_key = "tgp_v1_DQRzQY2vHkoS6j6bGTPiWwIVVB0cFJmqLxwx0k4_tMY"
    
    print("🧪 TOGETHER.AI API CONNECTIVITY TEST")
    print("=" * 60)
    print(f"📡 API Key: {api_key[:20]}...{api_key[-20:]}")
    print("⚠️  SSL Verification: DISABLED (for corporate networks)")
    print("-" * 60)
    
    # Test 1: Check available models
    try:
        url = "https://api.together.xyz/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "Python-Test-Client/1.0"
        }
        
        print("🔄 Step 1: Testing API authentication and models...")
        
        # Create session with no SSL verification
        session = requests.Session()
        session.verify = False
        
        response = session.get(url, headers=headers, timeout=30)
        
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📋 Response Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ SUCCESS: API Key is valid and working!")
            
            try:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    models = data['data']
                    print(f"🤖 Available Models: {len(models)}")
                    
                    # Show available models
                    print("📋 Sample Models:")
                    for i, model in enumerate(models[:5]):
                        model_id = model.get('id', 'Unknown')
                        model_type = model.get('type', 'Unknown')
                        print(f"   {i+1}. {model_id} ({model_type})")
                    
                    if len(models) > 5:
                        print(f"   ... and {len(models) - 5} more models")
                        
                elif isinstance(data, list):
                    print(f"🤖 Available Models: {len(data)}")
                    for i, model in enumerate(data[:5]):
                        if isinstance(model, dict):
                            model_id = model.get('id', model.get('name', 'Unknown'))
                            print(f"   {i+1}. {model_id}")
                        else:
                            print(f"   {i+1}. {model}")
                    
                    if len(data) > 5:
                        print(f"   ... and {len(data) - 5} more models")
                else:
                    print(f"📝 Raw Response: {json.dumps(data, indent=2)[:300]}...")
                    
            except json.JSONDecodeError:
                print(f"📝 Response (not JSON): {response.text[:200]}...")
                
        elif response.status_code == 401:
            print("❌ FAILED: Invalid API Key (401 Unauthorized)")
            print("🔍 Check if the API key is correct and active")
            
        elif response.status_code == 403:
            print("❌ FAILED: Access Forbidden (403)")
            print("🔍 API key may not have required permissions")
            
        elif response.status_code == 429:
            print("❌ FAILED: Rate Limited (429)")
            print("🔍 Too many requests, try again later")
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
    except requests.exceptions.SSLError as e:
        print("❌ SSL ERROR (even with verification disabled)")
        print(f"🔍 Details: {str(e)[:200]}...")
        
    except requests.exceptions.ConnectionError as e:
        print("❌ CONNECTION ERROR: Cannot reach Together.ai")
        print("🔍 Possible causes:")
        print("   - Corporate firewall blocking external APIs")
        print("   - Proxy configuration required")
        print("   - Network connectivity issues")
        print(f"📄 Error: {str(e)[:200]}...")
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took too long")
        print("🔍 Network may be slow or blocking the request")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}")
        print(f"🔍 Details: {str(e)[:200]}...")

def test_together_ai_chat():
    """Test chat completions if API key works"""
    
    api_key = "tgp_v1_DQRzQY2vHkoS6j6bGTPiWwIVVB0cFJmqLxwx0k4_tMY"
    
    print("\n🔄 Step 2: Testing chat completions...")
    print("-" * 60)
    
    try:
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": "meta-llama/Llama-2-7b-chat-hf",  # Popular model on Together.ai
            "messages": [
                {"role": "user", "content": "Say hello"}
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        session = requests.Session()
        session.verify = False
        
        response = session.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Chat completions working!")
            
            try:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', '').strip()
                    print(f"🤖 AI Response: '{content}'")
                    
                    # Show usage stats if available
                    if 'usage' in result:
                        usage = result['usage']
                        prompt_tokens = usage.get('prompt_tokens', 0)
                        completion_tokens = usage.get('completion_tokens', 0)
                        print(f"📊 Token Usage: {prompt_tokens} prompt + {completion_tokens} completion = {prompt_tokens + completion_tokens} total")
                else:
                    print(f"📝 Response: {json.dumps(result, indent=2)}")
                    
            except json.JSONDecodeError:
                print(f"📝 Raw response: {response.text}")
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:200]}...")

def test_together_ai_completions():
    """Test text completions endpoint"""
    
    api_key = "tgp_v1_DQRzQY2vHkoS6j6bGTPiWwIVVB0cFJmqLxwx0k4_tMY"
    
    print("\n🔄 Step 3: Testing text completions...")
    print("-" * 60)
    
    try:
        url = "https://api.together.xyz/v1/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": "togethercomputer/RedPajama-INCITE-7B-Base",  # Base model for completions
            "prompt": "The capital of France is",
            "max_tokens": 5,
            "temperature": 0.1
        }
        
        session = requests.Session()
        session.verify = False
        
        response = session.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Text completions working!")
            
            try:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    text = result['choices'][0].get('text', '').strip()
                    print(f"🤖 Completion: 'The capital of France is{text}'")
                else:
                    print(f"📝 Response: {json.dumps(result, indent=2)}")
                    
            except json.JSONDecodeError:
                print(f"📝 Raw response: {response.text}")
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:200]}...")

def check_environment():
    """Check environment variables and proxy settings"""
    
    print("\n🔍 Environment Check:")
    print("-" * 60)
    
    # Check proxy settings
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
    
    if http_proxy:
        print(f"🌐 HTTP Proxy: {http_proxy}")
    if https_proxy:
        print(f"🔒 HTTPS Proxy: {https_proxy}")
    if not http_proxy and not https_proxy:
        print("🌐 No proxy environment variables found")
    
    # Check requests library version
    print(f"📚 Requests version: {requests.__version__}")
    
    # Check SSL configuration
    print(f"🔒 SSL version: {ssl.OPENSSL_VERSION}")

if __name__ == "__main__":
    check_environment()
    test_together_ai_simple()
    test_together_ai_chat()
    test_together_ai_completions()
    
    print("\n" + "=" * 60)
    print("🏁 Together.ai Test Summary:")
    print("✅ If you see 'SUCCESS' messages, Together.ai is accessible")
    print("❌ If you see SSL/Connection errors, corporate network restrictions apply")
    print("🔧 Contact IT team for proxy configuration if needed")
    print("📝 API Key: tgp_v1_DQRzQY2vHkoS6j6bGTPiWwIVVB0cFJmqLxwx0k4_tMY")
    print("\n🌐 Together.ai endpoints tested:")
    print("   - https://api.together.xyz/v1/models")
    print("   - https://api.together.xyz/v1/chat/completions") 
    print("   - https://api.together.xyz/v1/completions")
