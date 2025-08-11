#!/usr/bin/env python3
"""
Quick Demo Alert Generator for Hackathon
Shows realistic alerts and warnings in terminal
"""

import time
import random
from datetime import datetime

def show_demo_alerts():
    """Generate impressive demo alerts for hackathon presentation"""
    
    alerts = [
        {
            "type": "🔥 CRITICAL ALERT", 
            "service": "brand-service",
            "metric": "CPU Usage", 
            "value": "94%",
            "threshold": "> 85%",
            "action": "Auto-scaling triggered"
        },
        {
            "type": "⚠️  WARNING", 
            "service": "analysis-engine",
            "metric": "Response Time", 
            "value": "3.2s",
            "threshold": "> 2.0s",
            "action": "Performance optimization needed"
        },
        {
            "type": "🔥 CRITICAL ALERT", 
            "service": "data-collection",
            "metric": "Error Rate", 
            "value": "12%",
            "threshold": "> 5%",
            "action": "Investigation started"
        },
        {
            "type": "⚠️  WARNING", 
            "service": "brand-service",
            "metric": "Memory Usage", 
            "value": "87%",
            "threshold": "> 80%",
            "action": "Memory cleanup recommended"
        },
        {
            "type": "🔥 CRITICAL ALERT", 
            "service": "analysis-engine",
            "metric": "Queue Backlog", 
            "value": "1,247 items",
            "threshold": "> 1000",
            "action": "Additional workers deployed"
        },
        {
            "type": "⚠️  WARNING", 
            "service": "data-collection",
            "metric": "Disk Usage", 
            "value": "91%",
            "threshold": "> 85%",
            "action": "Storage expansion planned"
        },
        {
            "type": "🔒 SECURITY ALERT", 
            "service": "gateway",
            "metric": "Failed Logins", 
            "value": "15 attempts",
            "threshold": "> 10",
            "action": "IP blocked automatically"
        },
        {
            "type": "📊 BUSINESS ALERT", 
            "service": "analytics",
            "metric": "Processing Time", 
            "value": "45 minutes",
            "threshold": "> 30 min",
            "action": "Algorithm optimization required"
        }
    ]
    
    print("🚨 BRAND INTELLIGENCE HUB - LIVE MONITORING SYSTEM")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🎯 HACKATHON DEMO MODE")
    print("=" * 70)
    print()
    
    for i, alert in enumerate(alerts, 1):
        print(f"{alert['type']}")
        print(f"🔧 Service: {alert['service']}")
        print(f"📊 Metric: {alert['metric']}")
        print(f"📈 Value: {alert['value']} (Threshold: {alert['threshold']})")
        print(f"⚡ Action: {alert['action']}")
        print(f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        if i < len(alerts):
            time.sleep(random.uniform(2, 5))  # Wait between alerts
    
    print("✅ MONITORING SYSTEM STATUS: OPERATIONAL")
    print("🎉 All alerts processed successfully!")
    print("📧 Notifications sent to: avishek.das4@cognizant.com")
    print()
    print("🔄 System automatically recovering...")
    print("✨ Ready for live demo!")

if __name__ == "__main__":
    print("Starting demo alert system...")
    time.sleep(1)
    show_demo_alerts()
