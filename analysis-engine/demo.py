#!/usr/bin/env python3
"""
Analysis Service Demo Script
Demonstrates how to use the Analysis Engine API with sample data
"""

import requests
import json
import time
import sys
from pathlib import Path

# Service configuration
BASE_URL = "http://localhost:8003"
API_BASE = f"{BASE_URL}/api/v1"

def load_demo_data():
    """Load demo data from the project's demo data files"""
    # Try to load banking demo data
    demo_data_path = Path(__file__).parent.parent.parent / "demodata" / "banking-demo.json"
    
    if demo_data_path.exists():
        with open(demo_data_path, 'r') as f:
            return json.load(f)
    else:
        # Return sample data if demo file not found
        return {
            "brand_data": {
                "brand": {"name": "Oriental Bank", "id": "oriental_bank_pr"},
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
            "area": {"id": "self_service_portal", "name": "Self Service Portal"}
        }

def check_service_health():
    """Check if the analysis service is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data['service']}")
            return True
        else:
            print(f"❌ Service health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to service: {e}")
        print(f"🔧 Make sure the service is running on {BASE_URL}")
        return False

def start_analysis(demo_data):
    """Start a new analysis"""
    print("\n🚀 Starting brand analysis...")
    
    analysis_request = {
        "brand_data": demo_data["brand_data"],
        "competitor_data": demo_data["competitor_data"],
        "area_id": demo_data["area"]["id"],
        "analysis_type": "comprehensive"
    }
    
    try:
        response = requests.post(f"{API_BASE}/analyze", json=analysis_request)
        if response.status_code == 200:
            data = response.json()
            analysis_id = data["analysis_id"]
            print(f"✅ Analysis started successfully!")
            print(f"📊 Analysis ID: {analysis_id}")
            print(f"⏱️  Estimated duration: {data['estimated_duration']} seconds")
            return analysis_id
        else:
            print(f"❌ Failed to start analysis: {response.status_code}")
            print(f"Error: {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def monitor_progress(analysis_id):
    """Monitor analysis progress"""
    print(f"\n📈 Monitoring progress for analysis: {analysis_id}")
    
    while True:
        try:
            response = requests.get(f"{API_BASE}/analyze/{analysis_id}/status")
            if response.status_code == 200:
                data = response.json()["data"]
                status = data["status"]
                progress = data["progress"]
                
                print(f"Status: {status} | Progress: {progress}%")
                
                if status == "completed":
                    print("✅ Analysis completed!")
                    return True
                elif status == "failed":
                    print(f"❌ Analysis failed: {data.get('error_message', 'Unknown error')}")
                    return False
                
                time.sleep(2)  # Wait 2 seconds before checking again
            else:
                print(f"❌ Failed to get status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Status check failed: {e}")
            return False

def get_results(analysis_id):
    """Get analysis results"""
    print(f"\n📊 Retrieving results for analysis: {analysis_id}")
    
    try:
        response = requests.get(f"{API_BASE}/analyze/{analysis_id}/results")
        if response.status_code == 200:
            data = response.json()["data"]
            
            print("✅ Results retrieved successfully!")
            print("\n🏆 OVERALL COMPARISON:")
            overall = data["overall_comparison"]
            print(f"   Brand Score: {overall['brand_score']:.2f}")
            print(f"   Competitor Score: {overall['competitor_score']:.2f}")
            print(f"   Gap: {overall['gap']:+.3f}")
            print(f"   Brand Ranking: {overall['brand_ranking']}")
            
            print("\n📈 DETAILED COMPARISON:")
            for category, scores in data["detailed_comparison"].items():
                print(f"   {category.replace('_', ' ').title()}:")
                print(f"     Brand: {scores['brand_score']:.2f}")
                print(f"     Competitor: {scores['competitor_score']:.2f}")
                print(f"     Insight: {scores['insight']}")
            
            print(f"\n💡 ACTIONABLE INSIGHTS ({len(data['actionable_insights'])} total):")
            for i, insight in enumerate(data["actionable_insights"][:3], 1):  # Show top 3
                print(f"   {i}. {insight['title']} (Priority: {insight['priority']})")
                print(f"      {insight['description']}")
                print(f"      Effort: {insight['estimated_effort']}")
                print(f"      Impact: {insight['expected_impact']}")
            
            print(f"\n🎯 MARKET POSITIONING:")
            positioning = data["market_positioning"]
            print(f"   Brand Position: {positioning['brand_position']}")
            print(f"   Competitor Position: {positioning['competitor_position']}")
            print(f"   Opportunity: {positioning['differentiation_opportunity']}")
            
            print(f"\n🔍 CONFIDENCE SCORE: {data['confidence_score']:.0%}")
            
            return data
        else:
            print(f"❌ Failed to get results: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Results retrieval failed: {e}")
        return None

def get_formatted_report(analysis_id):
    """Get formatted analysis report"""
    print(f"\n📄 Generating formatted report...")
    
    try:
        response = requests.get(f"{API_BASE}/analyze/{analysis_id}/report")
        if response.status_code == 200:
            report = response.json()["report"]
            
            print("✅ Report generated successfully!")
            print("\n📋 EXECUTIVE SUMMARY:")
            summary = report["comparison_summary"]
            print(f"   Analysis: {summary['brand']} vs {summary['competitor']}")
            print(f"   Winner: {summary['overall_winner']}")
            print(f"   Performance Gap: {summary['performance_gap']:.1%}")
            
            print("\n🔝 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"][:2], 1):
                print(f"   {i}. {rec['title']} ({rec['priority']} priority)")
                print(f"      Timeline: {rec['implementation_timeline']}")
                print(f"      Impact: {rec['business_impact']}")
            
            return report
        else:
            print(f"❌ Failed to generate report: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Report generation failed: {e}")
        return None

def get_insights_summary(analysis_id):
    """Get actionable insights summary"""
    print(f"\n💡 Getting insights summary...")
    
    try:
        response = requests.get(f"{API_BASE}/analyze/{analysis_id}/insights")
        if response.status_code == 200:
            summary = response.json()["insights_summary"]
            
            print("✅ Insights summary retrieved!")
            print(f"   Total Insights: {summary['total_insights']}")
            print(f"   High Priority: {summary['high_priority']}")
            print(f"   Medium Priority: {summary['medium_priority']}")
            print(f"   Low Priority: {summary['low_priority']}")
            print(f"   Estimated Effort: {summary['estimated_total_effort']}")
            print(f"   Confidence: {summary['confidence_score']:.0%}")
            
            return summary
        else:
            print(f"❌ Failed to get insights summary: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Insights summary failed: {e}")
        return None

def main():
    """Main demo function"""
    print("🎭 Analysis Engine Service Demo")
    print("=" * 50)
    
    # Check service health
    if not check_service_health():
        print("\n🔧 Please ensure the Analysis Engine service is running:")
        print("   python app/main.py")
        return
    
    # Load demo data
    print("\n📥 Loading demo data...")
    demo_data = load_demo_data()
    brand_name = demo_data["brand_data"]["brand"]["name"]
    competitor_name = demo_data["competitor_data"]["competitor"]["name"]
    area_name = demo_data["area"]["name"]
    
    print(f"✅ Demo data loaded:")
    print(f"   Brand: {brand_name}")
    print(f"   Competitor: {competitor_name}")
    print(f"   Analysis Area: {area_name}")
    
    # Start analysis
    analysis_id = start_analysis(demo_data)
    if not analysis_id:
        return
    
    # Monitor progress
    if not monitor_progress(analysis_id):
        return
    
    # Get results
    results = get_results(analysis_id)
    if not results:
        return
    
    # Get formatted report
    report = get_formatted_report(analysis_id)
    
    # Get insights summary
    insights = get_insights_summary(analysis_id)
    
    print("\n🎉 Demo completed successfully!")
    print(f"📊 Analysis ID: {analysis_id}")
    print(f"🔗 View full documentation at: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
