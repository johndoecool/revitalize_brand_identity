#!/usr/bin/env python3
"""
Simple Analysis Engine Test Script
Run this to test the Analysis Engine service
"""

import requests
import json
import time

# Service configuration
BASE_URL = "http://localhost:8003"
API_BASE = f"{BASE_URL}/api/v1"

def test_service():
    """Test the Analysis Engine service"""
    print("🧪 Testing Analysis Engine Service")
    print("=" * 50)
    
    # 1. Health check
    print("\n1️⃣ Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Service is healthy!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        return
    
    # 2. Start analysis
    print("\n2️⃣ Starting Analysis...")
    analysis_data = {
        "brand_data": {
            "brand": {"name": "Oriental Bank", "id": "oriental_bank"},
            "brand_data": {
                "news_sentiment": {"score": 0.75, "articles_count": 45},
                "social_media": {"followers": 50000, "engagement_rate": 0.03},
                "website_performance": {"page_load_time": 2.1, "uptime": 0.995}
            }
        },
        "competitor_data": {
            "competitor": {"name": "Banco Popular", "id": "banco_popular"},
            "brand_data": {
                "news_sentiment": {"score": 0.85, "articles_count": 62},
                "social_media": {"followers": 75000, "engagement_rate": 0.05},
                "website_performance": {"page_load_time": 1.8, "uptime": 0.998}
            }
        },
        "area_id": "self_service_portal",
        "analysis_type": "comprehensive"
    }
    
    try:
        response = requests.post(f"{API_BASE}/analyze", json=analysis_data)
        if response.status_code == 200:
            result = response.json()
            analysis_id = result["analysis_id"]
            print(f"✅ Analysis started!")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   Estimated duration: {result['estimated_duration']} seconds")
            
            # Monitor progress
            print("\n3️⃣ Monitoring Progress...")
            for i in range(10):  # Check for up to 10 times
                time.sleep(3)  # Wait 3 seconds
                status_response = requests.get(f"{API_BASE}/analyze/{analysis_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()["data"]
                    status = status_data["status"]
                    progress = status_data["progress"]
                    
                    print(f"   Status: {status} | Progress: {progress}%")
                    
                    if status == "completed":
                        print("✅ Analysis completed!")
                        
                        # Get results
                        print("\n4️⃣ Getting Results...")
                        results_response = requests.get(f"{API_BASE}/analyze/{analysis_id}/results")
                        if results_response.status_code == 200:
                            results = results_response.json()["data"]
                            print("✅ Results retrieved!")
                            print(f"   Brand Score: {results['overall_comparison']['brand_score']:.2f}")
                            print(f"   Competitor Score: {results['overall_comparison']['competitor_score']:.2f}")
                            print(f"   Total Insights: {len(results['actionable_insights'])}")
                            print(f"   Confidence: {results['confidence_score']:.0%}")
                        break
                    elif status == "failed":
                        error_msg = status_data.get("error_message", "Unknown error")
                        print(f"❌ Analysis failed: {error_msg}")
                        if "OPENAI_API_KEY" in error_msg:
                            print("\n💡 Fix: Add your OpenAI API key to the .env file")
                            print("   OPENAI_API_KEY=your_actual_api_key_here")
                        break
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break
        else:
            print(f"❌ Analysis start failed: {response.status_code}")
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n🎉 Test completed!")
    print("\n📋 Available Endpoints:")
    print("   • Health: http://localhost:8003/health")
    print("   • API Docs: http://localhost:8003/docs")
    print("   • Analysis: POST http://localhost:8003/api/v1/analyze")

if __name__ == "__main__":
    test_service()
