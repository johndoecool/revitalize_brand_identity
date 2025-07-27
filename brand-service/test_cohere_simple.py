#!/usr/bin/env python3
"""
Simple Cohere.ai API test with corporate network compatibility
"""
import requests
import json
import urllib3
import ssl
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_cohere_simple():
    """Simple test with no SSL verification"""
    
    api_key = "LtmUlMQwBnkJGOy1Um4IiNdfFZwS8V5ni3lX9YdC"
    
    print("🧪 SIMPLE COHERE.AI TEST (No SSL Verification)")
    print("=" * 60)
    print(f"📡 API Key: {api_key[:15]}...{api_key[-15:]}")
    print("⚠️  SSL Verification: DISABLED (for corporate networks)")
    print("-" * 60)
    
    # Test 1: Simple ping to Cohere API
    try:
        url = "https://api.cohere.ai/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "Python-Test-Client/1.0"
        }
        
        print("🔄 Step 1: Testing API authentication...")
        
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
                if isinstance(data, dict) and 'models' in data:
                    models = data['models']
                    print(f"🤖 Available Models: {len(models)}")
                    
                    # Show available models
                    for i, model in enumerate(models[:5]):
                        name = model.get('name', 'Unknown')
                        print(f"   {i+1}. {name}")
                    
                    if len(models) > 5:
                        print(f"   ... and {len(models) - 5} more models")
                else:
                    print(f"📝 Raw Response: {response.text[:200]}...")
                    
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
        print("❌ CONNECTION ERROR: Cannot reach Cohere.ai")
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

def test_cohere_generate():
    """Test text generation if API key works"""
    
    api_key = "LtmUlMQwBnkJGOy1Um4IiNdfFZwS8V5ni3lX9YdC"
    
    print("\n🔄 Step 2: Testing text generation...")
    print("-" * 60)
    
    try:
        url = "https://api.cohere.ai/v1/generate"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": "command-light",  # Use lighter model for testing
            "prompt": "Say hello",
            "max_tokens": 5,
            "temperature": 0.1
        }
        
        session = requests.Session()
        session.verify = False
        
        response = session.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Text generation working!")
            
            try:
                result = response.json()
                if 'generations' in result and len(result['generations']) > 0:
                    text = result['generations'][0].get('text', '').strip()
                    print(f"🤖 Generated: '{text}'")
                else:
                    print(f"📝 Response: {json.dumps(result, indent=2)}")
                    
            except json.JSONDecodeError:
                print(f"📝 Raw response: {response.text}")
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
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
    test_cohere_simple()
    test_cohere_generate()
    
    print("\n" + "=" * 60)
    print("🏁 Test Summary:")
    print("✅ If you see 'SUCCESS' messages, Cohere.ai is accessible")
    print("❌ If you see SSL/Connection errors, corporate network restrictions apply")
    print("🔧 Contact IT team for proxy configuration if needed")
    print("📝 API Key appears to be: LtmUlMQwBnkJGOy1Um4IiNdfFZwS8V5ni3lX9YdC")
