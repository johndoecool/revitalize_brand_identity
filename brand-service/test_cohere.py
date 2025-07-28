#!/usr/bin/env python3
"""
Simple script to test Cohere.ai API connectivity
"""
import requests
import json

def test_cohere_connection():
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
    
    print("🔄 Testing Cohere.ai API connection...")
    print(f"📡 API Key: {api_key[:10]}...{api_key[-10:]}")
    print(f"🌐 Endpoint: {url}")
    print("-" * 50)
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Connected to Cohere.ai successfully!")
            
            # Parse and display the response
            result = response.json()
            print(f"📝 Response: {json.dumps(result, indent=2)}")
            
            # Extract generated text if available
            if 'generations' in result and len(result['generations']) > 0:
                generated_text = result['generations'][0].get('text', '')
                print(f"🤖 Generated Text: '{generated_text.strip()}'")
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response Body: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"🔍 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print("🔍 Could not parse error response as JSON")
                
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: Could not connect to Cohere.ai")
        print(f"🔍 Details: {str(e)}")
        
    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT ERROR: Request timed out")
        print(f"🔍 Details: {str(e)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        print(f"🔍 Error Type: {type(e).__name__}")

def test_cohere_health():
    """Test Cohere API health/status endpoint if available"""
    
    api_key = "LtmUlMQwBnkJGOy1Um4IiNdfFZwS8V5ni3lX9YdC"
    
    # Try to check models endpoint (simpler than generate)
    url = "https://api.cohere.ai/v1/models"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    print("\n🔄 Testing Cohere.ai Models endpoint...")
    print("-" * 50)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
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
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🧪 COHERE.AI API CONNECTION TEST")
    print("=" * 50)
    
    # Test main generate endpoint
    test_cohere_connection()
    
    # Test models endpoint
    test_cohere_health()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
