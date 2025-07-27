#!/usr/bin/env python3
"""
Simple script to test Cohere.ai API connectivity with SSL options
"""
import requests
import json
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_cohere_connection(verify_ssl=True):
    """Test connection to Cohere.ai API"""
    
    # Cohere API configuration
    api_key = "LtmUlMQwBnkJGOy1Um4IiNdfFZwS8V5ni3lX9YdC"
    base_url = "https://api.cohere.ai"
    
    # Test endpoint - using the generate endpoint with a simple prompt
    url = f"{base_url}/v1/generate"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Simple test payload
    payload = {
        "model": "command",
        "prompt": "Hello, this is a test connection.",
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    ssl_status = "WITH SSL verification" if verify_ssl else "WITHOUT SSL verification (insecure)"
    print(f"🔄 Testing Cohere.ai API connection... {ssl_status}")
    print(f"📡 API Key: {api_key[:10]}...{api_key[-10:]}")
    print(f"🌐 Endpoint: {url}")
    print("-" * 50)
    
    try:
        # Make the API request
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=30,
            verify=verify_ssl
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Connected to Cohere.ai successfully!")
            
            # Parse and display the response
            result = response.json()
            print(f"📝 Response: {json.dumps(result, indent=2)}")
            
            # Extract generated text if available
            if 'generations' in result and len(result['generations']) > 0:
                generated_text = result['generations'][0].get('text', '')
                print(f"🤖 Generated Text: '{generated_text.strip()}'")
            
            return True
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response Body: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"🔍 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print("🔍 Could not parse error response as JSON")
            
            return False
                
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL ERROR: {str(e)}")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: Could not connect to Cohere.ai")
        print(f"🔍 Details: {str(e)}")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT ERROR: Request timed out")
        print(f"🔍 Details: {str(e)}")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        print(f"🔍 Error Type: {type(e).__name__}")
        return False

def test_cohere_models(verify_ssl=True):
    """Test Cohere API models endpoint"""
    
    api_key = "LtmUlMQwBnkJGOy1Um4IiNdfFZwS8V5ni3lX9YdC"
    url = "https://api.cohere.ai/v1/models"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    ssl_status = "WITH SSL verification" if verify_ssl else "WITHOUT SSL verification"
    print(f"\n🔄 Testing Cohere.ai Models endpoint... {ssl_status}")
    print("-" * 50)
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=verify_ssl)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Models endpoint accessible!")
            
            result = response.json()
            if 'models' in result:
                models = result['models']
                print(f"📋 Available Models: {len(models)} found")
                for model in models[:3]:  # Show first 3 models
                    model_name = model.get('name', 'Unknown')
                    print(f"   • {model_name}")
                if len(models) > 3:
                    print(f"   ... and {len(models) - 3} more")
            else:
                print(f"📝 Response: {json.dumps(result, indent=2)}")
            
            return True
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("\n🔄 Testing basic internet connectivity...")
    print("-" * 50)
    
    try:
        # Test connection to a simple endpoint
        response = requests.get("https://httpbin.org/ip", timeout=10)
        if response.status_code == 200:
            print("✅ SUCCESS: Basic internet connectivity working")
            result = response.json()
            print(f"🌐 Your IP: {result.get('origin', 'Unknown')}")
            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 COHERE.AI API CONNECTION TEST")
    print("=" * 50)
    
    # Test basic connectivity first
    internet_ok = test_basic_connectivity()
    
    if internet_ok:
        # Test with SSL verification first
        print("\n🔒 Testing with SSL verification...")
        success_ssl = test_cohere_connection(verify_ssl=True)
        
        if not success_ssl:
            # If SSL fails, try without SSL verification
            print("\n⚠️  SSL failed, trying without SSL verification...")
            success_no_ssl = test_cohere_connection(verify_ssl=False)
            
            if success_no_ssl:
                print("\n✅ SUCCESS: Connection works without SSL verification")
                print("⚠️  NOTE: This may indicate corporate firewall/proxy issues")
            else:
                print("\n❌ FAILED: Connection failed even without SSL verification")
        
        # Test models endpoint
        test_cohere_models(verify_ssl=not success_ssl)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n📝 SUMMARY:")
    print("   - If SSL errors occur, this usually indicates corporate network restrictions")
    print("   - If API key errors occur, check if the key is valid and has proper permissions")
    print("   - If connection works without SSL, configure your environment for corporate proxy")
