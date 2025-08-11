#!/usr/bin/env python3
"""
Prometheus Metrics Generator for Demo
Creates realistic metrics data for Grafana dashboards
"""

import time
import random
import requests
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import threading

class MetricsGenerator:
    def __init__(self, port=8765):
        self.port = port
        
        # Define metrics
        self.cpu_usage = Gauge('brand_service_cpu_usage_percent', 'CPU usage percentage', ['service'])
        self.memory_usage = Gauge('brand_service_memory_usage_percent', 'Memory usage percentage', ['service'])
        self.response_time = Histogram('brand_service_response_time_seconds', 'Response time in seconds', ['service', 'endpoint'])
        self.error_rate = Gauge('brand_service_error_rate_percent', 'Error rate percentage', ['service'])
        self.disk_usage = Gauge('brand_service_disk_usage_percent', 'Disk usage percentage', ['service'])
        self.active_connections = Gauge('brand_service_active_connections', 'Active connections', ['service'])
        self.request_total = Counter('brand_service_requests_total', 'Total requests', ['service', 'status'])
        
        self.services = ['brand-service', 'data-collection', 'analysis-engine']
        self.running = False
        
    def generate_realistic_metrics(self):
        """Generate realistic metrics that will trigger alerts"""
        while self.running:
            for service in self.services:
                # Generate varying metrics with some high values to trigger alerts
                
                # CPU - occasionally spike above 80%
                cpu = random.uniform(20, 85) if random.random() > 0.3 else random.uniform(85, 95)
                self.cpu_usage.labels(service=service).set(cpu)
                
                # Memory - occasionally spike above 80%
                memory = random.uniform(30, 75) if random.random() > 0.25 else random.uniform(80, 92)
                self.memory_usage.labels(service=service).set(memory)
                
                # Response time - occasionally slow
                resp_time = random.uniform(0.1, 1.5) if random.random() > 0.2 else random.uniform(2.0, 8.0)
                self.response_time.labels(service=service, endpoint='/api/health').observe(resp_time)
                
                # Error rate - occasionally high
                error_rate = random.uniform(0.1, 3.0) if random.random() > 0.3 else random.uniform(8.0, 25.0)
                self.error_rate.labels(service=service).set(error_rate)
                
                # Disk usage - gradually increasing
                disk = random.uniform(60, 85) if random.random() > 0.2 else random.uniform(88, 97)
                self.disk_usage.labels(service=service).set(disk)
                
                # Active connections
                connections = random.randint(10, 150)
                self.active_connections.labels(service=service).set(connections)
                
                # Request counters
                success_requests = random.randint(50, 200)
                error_requests = random.randint(0, 10)
                
                self.request_total.labels(service=service, status='success')._value._value += success_requests
                self.request_total.labels(service=service, status='error')._value._value += error_requests
                
            time.sleep(15)  # Update every 15 seconds
            
    def start_metrics_server(self):
        """Start the metrics server"""
        print(f"🚀 Starting Prometheus metrics server on port {self.port}")
        start_http_server(self.port)
        print(f"📊 Metrics available at: http://localhost:{self.port}/metrics")
        
        self.running = True
        metrics_thread = threading.Thread(target=self.generate_realistic_metrics)
        metrics_thread.daemon = True
        metrics_thread.start()
        
        print("✅ Demo metrics generator started!")
        print("🎯 This will create realistic alerts in your Grafana dashboards")
        print("⚠️  You should see alerts for:")
        print("   - High CPU usage (>80%)")
        print("   - High memory usage (>80%)")
        print("   - Slow response times (>2s)")
        print("   - High error rates (>5%)")
        print("   - High disk usage (>85%)")
        print()
        print("🔄 Metrics update every 15 seconds")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping metrics generator...")
            self.running = False
            print("✅ Metrics generator stopped!")

if __name__ == "__main__":
    generator = MetricsGenerator()
    generator.start_metrics_server()
