#!/usr/bin/env python3
"""
Demo Alert Generator for Brand Intelligence Hub
Creates realistic test alerts and warnings for hackathon demonstration
"""

import time
import requests
import json
import random
from datetime import datetime, timedelta

class DemoAlertGenerator:
    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3200"
        self.services = ["brand-service", "data-collection", "analysis-engine"]
        
    def create_high_cpu_alert(self):
        """Simulate high CPU usage alert"""
        print("🔥 ALERT: High CPU Usage Detected")
        print(f"   Service: {random.choice(self.services)}")
        print(f"   CPU Usage: {random.randint(85, 99)}%")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: WARNING")
        print(f"   Action: Scale up resources recommended")
        print()
        
    def create_memory_alert(self):
        """Simulate memory usage alert"""
        print("⚠️  ALERT: High Memory Usage")
        print(f"   Service: {random.choice(self.services)}")
        print(f"   Memory Usage: {random.randint(82, 95)}%")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: WARNING")
        print(f"   Action: Memory optimization needed")
        print()
        
    def create_response_time_alert(self):
        """Simulate slow response time alert"""
        print("🐌 ALERT: Slow Response Time")
        print(f"   Service: {random.choice(self.services)}")
        print(f"   Response Time: {random.randint(2500, 8000)}ms")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: CRITICAL")
        print(f"   Action: Performance investigation required")
        print()
        
    def create_error_rate_alert(self):
        """Simulate error rate alert"""
        print("❌ ALERT: High Error Rate")
        print(f"   Service: {random.choice(self.services)}")
        print(f"   Error Rate: {random.randint(8, 25)}%")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: CRITICAL")
        print(f"   Action: Immediate investigation required")
        print()
        
    def create_disk_space_alert(self):
        """Simulate disk space alert"""
        print("💾 ALERT: Low Disk Space")
        print(f"   Service: Container Storage")
        print(f"   Disk Usage: {random.randint(88, 97)}%")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: WARNING")
        print(f"   Action: Cleanup or expand storage")
        print()
        
    def create_network_alert(self):
        """Simulate network latency alert"""
        print("🌐 ALERT: Network Latency")
        print(f"   Service: External API calls")
        print(f"   Latency: {random.randint(800, 2500)}ms")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: WARNING")
        print(f"   Action: Check network connectivity")
        print()
        
    def create_security_alert(self):
        """Simulate security alert"""
        print("🔒 ALERT: Security Event")
        print(f"   Event: Suspicious login attempts")
        print(f"   IP: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: CRITICAL")
        print(f"   Action: Security team notified")
        print()
        
    def create_business_alert(self):
        """Simulate business metrics alert"""
        print("📊 ALERT: Business Metrics")
        print(f"   Metric: Analysis processing time")
        print(f"   Value: {random.randint(45, 120)} seconds")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Severity: WARNING")
        print(f"   Action: Optimize analysis algorithms")
        print()
        
    def generate_demo_alerts(self, duration_minutes=5):
        """Generate continuous demo alerts for presentation"""
        print("🚨 BRAND INTELLIGENCE HUB - DEMO ALERT SYSTEM")
        print("=" * 60)
        print(f"📅 Demo Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print("🎯 Purpose: Hackathon Demonstration")
        print("=" * 60)
        print()
        
        alerts = [
            self.create_high_cpu_alert,
            self.create_memory_alert,
            self.create_response_time_alert,
            self.create_error_rate_alert,
            self.create_disk_space_alert,
            self.create_network_alert,
            self.create_security_alert,
            self.create_business_alert
        ]
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        alert_count = 0
        
        while datetime.now() < end_time:
            # Generate random alert
            alert_func = random.choice(alerts)
            alert_func()
            alert_count += 1
            
            # Wait between alerts (10-30 seconds)
            wait_time = random.randint(10, 30)
            print(f"⏳ Next alert in {wait_time} seconds... (Alert #{alert_count})")
            print("-" * 40)
            time.sleep(wait_time)
            
        print("✅ Demo alert session completed!")
        print(f"📈 Total alerts generated: {alert_count}")
        print("🎉 Ready for hackathon presentation!")

if __name__ == "__main__":
    generator = DemoAlertGenerator()
    
    print("Demo Alert Generator Options:")
    print("1. Generate 5-minute demo session")
    print("2. Generate single test alerts")
    print("3. Continuous demo mode")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        generator.generate_demo_alerts(5)
    elif choice == "2":
        print("\n🔥 Generating sample alerts...\n")
        generator.create_high_cpu_alert()
        generator.create_memory_alert()
        generator.create_response_time_alert()
        generator.create_error_rate_alert()
        print("✅ Sample alerts generated!")
    elif choice == "3":
        duration = int(input("Enter duration in minutes: "))
        generator.generate_demo_alerts(duration)
    else:
        print("Invalid choice!")
