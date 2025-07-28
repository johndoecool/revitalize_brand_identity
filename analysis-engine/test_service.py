#!/usr/bin/env python3
"""
Quick Test Script for Analysis Engine Service
Tests basic functionality without requiring the full demo data
"""

import requests
import time
import json

BASE_URL = "http://localhost:8003"

def test_health():
    """Test service health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Health: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to service: {e}")
        print("💡 Make sure the service is running on http://localhost:8003")
        return False

def test_api_health():
    """Test API-specific health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status', 'unknown')}")
            print(f"🔧 Active analyses: {data.get('active_analyses', 'unknown')}")
            capabilities = data.get('capabilities', [])
            print(f"⚡ Capabilities: {', '.join(capabilities[:3])}...")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API health check failed: {e}")
        return False

def test_openapi_docs():
    """Test if OpenAPI documentation is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            print(f"✅ OpenAPI Schema: {schema.get('info', {}).get('title', 'Unknown')}")
            print(f"📖 Version: {schema.get('info', {}).get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAPI schema test failed: {e}")
        return False

def test_simple_analysis():
    """Test a simple analysis request (may fail if OpenAI key not configured)"""
    print("\n🧪 Testing simple analysis request...")
    
    simple_request = {
        "brand_data": {
            "brand": {"name": "Test Brand", "id": "test_brand"},
            "brand_data": {
                "news_sentiment": {"score": 0.7, "articles_count": 10}
            }
        },
        "competitor_data": {
            "competitor": {"name": "Test Competitor", "id": "test_competitor"},
            "brand_data": {
                "news_sentiment": {"score": 0.8, "articles_count": 15}
            }
        },
        "area_id": "test_area",
        "analysis_type": "comprehensive"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=simple_request, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                analysis_id = data.get("analysis_id")
                print(f"✅ Analysis started: {analysis_id}")
                print(f"⏱️  Estimated duration: {data.get('estimated_duration', 'unknown')} seconds")
                return True
            else:
                print(f"❌ Analysis request failed: {data}")
                return False
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text[:200]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Analysis request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Analysis Engine Service - Quick Test")
    print("=" * 50)
    
    # Test 1: Basic health
    print("\n1️⃣  Testing basic health...")
    if not test_health():
        print("\n❌ Basic health test failed. Service may not be running.")
        print("💡 Start the service with: python start.py")
        return
    
    # Test 2: API health
    print("\n2️⃣  Testing API health...")
    if not test_api_health():
        print("\n⚠️  API health test failed, but basic service is running.")
    
    # Test 3: OpenAPI docs
    print("\n3️⃣  Testing OpenAPI documentation...")
    if test_openapi_docs():
        print("📚 Documentation available at: http://localhost:8003/docs")
    
    # Test 4: Simple analysis (optional)
    print("\n4️⃣  Testing analysis endpoint...")
    if test_simple_analysis():
        print("✅ Analysis endpoint is working!")
        print("💡 Note: Full analysis requires OpenAI API key in .env file")
    else:
        print("⚠️  Analysis endpoint test failed.")
        print("💡 This is expected if OpenAI API key is not configured")
    
    print("\n🎉 Quick test completed!")
    print("\n🔗 Service URLs:")
    print(f"   • API Docs: {BASE_URL}/docs")
    print(f"   • Health: {BASE_URL}/health")
    print(f"   • API Health: {BASE_URL}/api/v1/health")

if __name__ == "__main__":
    main()
