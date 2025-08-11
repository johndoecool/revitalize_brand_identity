# 🚀 Brand Intelligence Hub - Service Management Guide

## Overview

This document provides comprehensive instructions for starting, stopping, and managing all Brand Intelligence Hub services including the complete monitoring stack.

## 📋 Quick Reference Card

| Action                  | Command                                             | What It Does                            |
| ----------------------- | --------------------------------------------------- | --------------------------------------- |
| **Start Everything**    | `./start_all_services.sh start --with-monitoring`   | Starts all services + monitoring        |
| **Start Services Only** | `./start_all_services.sh start`                     | Starts only Brand Intelligence services |
| **Stop Everything**     | `./start_all_services.sh stop --with-monitoring`    | Stops all services + monitoring         |
| **Stop Services Only**  | `./start_all_services.sh stop`                      | Stops only Brand Intelligence services  |
| **Check Status**        | `./start_all_services.sh status --with-monitoring`  | Shows status of everything              |
| **Restart Everything**  | `./start_all_services.sh restart --with-monitoring` | Restarts all services + monitoring      |

## 🎯 Service Architecture

### Brand Intelligence Hub Services

| Service             | Port | Purpose                         | Log File                   |
| ------------------- | ---- | ------------------------------- | -------------------------- |
| **brand-service**   | 8001 | Core brand analysis API         | `logs/brand-service.log`   |
| **data-collection** | 8002 | Web scraping and data gathering | `logs/data-collection.log` |
| **analysis-engine** | 8003 | AI-powered analysis processing  | `logs/analysis-engine.log` |

### Monitoring Stack Services

| Service           | Port | Purpose                         | Access                | Health Check |
| ----------------- | ---- | ------------------------------- | --------------------- | ------------ |
| **Grafana**       | 3200 | Dashboard and visualization     | http://localhost:3200 | /api/health  |
| **Prometheus**    | 9090 | Metrics collection and alerting | http://localhost:9090 | /-/healthy   |
| **Loki**          | 3100 | Log aggregation                 | http://localhost:3100 | /ready       |
| **AlertManager**  | 9093 | Alert routing and notifications | http://localhost:9093 | /-/healthy   |
| **Node Exporter** | 9100 | System metrics collection       | http://localhost:9100 | /metrics     |
| **cAdvisor**      | 8080 | Container metrics collection    | http://localhost:8080 | /metrics     |
| **Promtail**      | -    | Log collection & shipping       | (Internal service)    | (No port)    |

### 🎯 Dashboard Access & Credentials

**Grafana Login:**

- **URL:** http://localhost:3200
- **Username:** admin
- **Password:** admin123
- **Note:** Change password in production environments

**Available Professional Dashboards:**

1. **Executive Dashboard** - Business KPIs, service health, performance overview
2. **Technical Dashboard** - Detailed metrics, resource usage, container stats
3. **Alert Dashboard** - Active alerts, alert history, escalation status

## 🚀 Starting Services

### Start Complete Solution (Recommended for Demo)

```bash
./start_all_services.sh start --with-monitoring
```

**What this does:**

- ✅ Starts all 3 Brand Intelligence services
- ✅ Starts complete monitoring stack (Grafana + Prometheus + Loki + AlertManager)
- ✅ Sets up log aggregation
- ✅ Configures email alerts
- ✅ Loads professional dashboards

**Expected Output:**

```
🚀 Brand Intelligence Hub - Service Startup
=================================================

[INFO] Starting brand-service on port 8001...
[INFO] Starting data-collection on port 8002...
[INFO] Starting analysis-engine on port 8003...
[INFO] Starting monitoring stack...
✅ All services started successfully!

Access your complete monitoring stack:
• Grafana Dashboards: http://localhost:3200
• Prometheus Metrics:  http://localhost:9090
• Log Analysis:        http://localhost:3100
```

### 📊 Monitoring Stack Detailed Setup

When you start with `--with-monitoring`, the following monitoring services are deployed:

#### **Core Monitoring Services**

```bash
cd monitoring
docker-compose up -d
```

| Container                          | Service       | Port | Purpose                    | Health Check                     |
| ---------------------------------- | ------------- | ---- | -------------------------- | -------------------------------- |
| `brand-intelligence-grafana`       | Grafana       | 3200 | Dashboards & Visualization | http://localhost:3200/api/health |
| `brand-intelligence-prometheus`    | Prometheus    | 9090 | Metrics Collection         | http://localhost:9090/-/healthy  |
| `brand-intelligence-loki`          | Loki          | 3100 | Log Aggregation            | http://localhost:3100/ready      |
| `brand-intelligence-alertmanager`  | AlertManager  | 9093 | Alert Management           | http://localhost:9093/-/healthy  |
| `brand-intelligence-node-exporter` | Node Exporter | 9100 | System Metrics             | http://localhost:9100/metrics    |
| `brand-intelligence-cadvisor`      | cAdvisor      | 8080 | Container Metrics          | http://localhost:8080/metrics    |
| `brand-intelligence-promtail`      | Promtail      | -    | Log Shipping               | (No direct port)                 |

#### **Professional Dashboards Available**

```bash
# Access after starting monitoring stack
open http://localhost:3200  # Login: admin/admin123
```

| Dashboard               | Purpose                             | Key Metrics                                 | Access URL                                  |
| ----------------------- | ----------------------------------- | ------------------------------------------- | ------------------------------------------- |
| **Executive Dashboard** | Business KPIs & High-level Overview | Service Uptime, Request Volume, Error Rates | http://localhost:3200/d/executive-dashboard |
| **Technical Dashboard** | Detailed System Performance         | CPU, Memory, Disk, Network, Container Stats | http://localhost:3200/d/technical-dashboard |
| **Alert Dashboard**     | Real-time Alerts & Warnings         | Active Alerts, Alert History, Escalations   | http://localhost:3200/d/alert-dashboard     |

#### **Monitoring Stack Initialization**

```bash
# Wait for services to fully start (recommended)
./start_all_services.sh start --with-monitoring
sleep 30  # Allow 30 seconds for full initialization

# Test monitoring stack health
cd monitoring
./test_monitoring.sh

# Generate demo data for dashboards
./test_monitoring.sh demo
```

### Start Only Brand Intelligence Services

```bash
./start_all_services.sh start
```

**What this does:**

- ✅ Starts brand-service, data-collection, analysis-engine
- ❌ Does not start monitoring stack
- 💡 Use this for development or when you only need the core services

## 🛑 Stopping Services

### Stop Everything (Complete Shutdown)

```bash
./start_all_services.sh stop --with-monitoring
```

**What this does:**

- 🛑 Stops all Brand Intelligence services
- 🛑 Stops complete monitoring stack
- 🛑 Frees all ports (8001, 8002, 8003, 3200, 9090, 3100, 9093)
- 🛑 Stops all Docker containers

**Expected Output:**

```
[INFO] Stopping all services...
[INFO] Stopping analysis-engine (PID: 12345)...
✅ analysis-engine stopped
[INFO] Stopping brand-service (PID: 12346)...
✅ brand-service stopped
[INFO] Stopping data-collection (PID: 12347)...
✅ data-collection stopped
✅ All services stopped
[INFO] Stopping monitoring stack...
✅ Monitoring stack stopped
```

### Stop Only Brand Intelligence Services

```bash
./start_all_services.sh stop
```

**What this does:**

- 🛑 Stops brand-service, data-collection, analysis-engine
- ✅ Leaves monitoring stack running (if it was started)
- 💡 Use this to restart services while keeping monitoring active

### Stop Only Monitoring Stack

```bash
cd monitoring
docker-compose down
```

**What this does:**

- 🛑 Stops Grafana, Prometheus, Loki, AlertManager
- ✅ Leaves Brand Intelligence services running
- 💡 Use this when you want to restart just the monitoring

## 📊 Monitoring System Operations

### 🔍 Health Checks & Validation

#### **Quick Health Check All Services**

```bash
# Check all monitoring services status
cd monitoring
docker-compose ps

# Detailed health check with tests
./test_monitoring.sh

# Expected output:
# ✅ All tests passed! (6/6)
# 🎉 Monitoring stack is ready for hackathon demo!
```

#### **Individual Service Health Checks**

```bash
# Check Grafana
curl -f http://localhost:3200/api/health

# Check Prometheus
curl -f http://localhost:9090/-/healthy

# Check Loki
curl -f http://localhost:3100/ready

# Check AlertManager
curl -f http://localhost:9093/-/healthy
```

### 📈 Generating Demo Data & Alerts

#### **Generate Demo Alerts for Presentation**

```bash
cd monitoring

# Generate demo log entries and sample alerts
./test_monitoring.sh demo

# Run advanced demo alert generator
python3 demo_alerts.py

# Generate continuous metrics for live demo
python3 metrics_generator.py &  # Runs in background
```

#### **Quick Demo Setup for Hackathon**

```bash
# 1. Start everything with monitoring
./start_all_services.sh start --with-monitoring

# 2. Wait for initialization
sleep 30

# 3. Generate demo data
cd monitoring
./test_monitoring.sh demo

# 4. Start metrics generator for live data
python3 metrics_generator.py &

# 5. Open dashboards for demo
open http://localhost:3200/d/executive-dashboard
open http://localhost:3200/d/technical-dashboard
open http://localhost:3200/d/alert-dashboard
```

### 🔧 Monitoring Configuration Management

#### **Customize Alert Rules**

```bash
# Edit Prometheus alert rules
vim monitoring/config/prometheus/alert_rules.yml

# Restart Prometheus to apply changes
cd monitoring
docker-compose restart prometheus
```

#### **Modify Dashboard Settings**

```bash
# Dashboard files location
ls monitoring/config/grafana/dashboards/
# - executive-dashboard.json
# - technical-dashboard.json
# - alert-dashboard.json

# After editing dashboards, restart Grafana
docker-compose restart grafana
```

#### **Configure Email Alerts**

```bash
# Edit AlertManager configuration
vim monitoring/config/alertmanager/alertmanager.yml

# Update SMTP settings for your email provider
# Then restart AlertManager
docker-compose restart alertmanager
```

### 📊 Dashboard Usage Guide

#### **Executive Dashboard Features**

- **Service Health Overview:** Real-time status of all 3 Brand Intelligence services
- **Performance KPIs:** Request rates, response times, error percentages
- **Resource Utilization:** CPU, Memory, Disk usage trends
- **Business Metrics:** API calls, data processing volumes, alert counts

#### **Technical Dashboard Features**

- **Detailed System Metrics:** CPU cores, memory breakdown, network I/O
- **Container Statistics:** Docker container resource usage and health
- **Application Logs:** Filtered log views with search capabilities
- **Infrastructure Monitoring:** Node exporter system metrics

#### **Alert Dashboard Features**

- **Active Alerts:** Current firing alerts with severity levels
- **Alert History:** Timeline of recent alerts and resolutions
- **Escalation Status:** Which alerts have been escalated or acknowledged
- **Alert Rules Status:** Health of alerting rules themselves

### 📁 Log Management & Analysis

#### **View Service Logs via Grafana**

```bash
# Access log explorer in Grafana
open http://localhost:3200/explore

# Query examples:
# {job="brand-intelligence-logs"} |= "ERROR"
# {job="brand-intelligence-logs"} |= "brand-service"
# {job="brand-intelligence-logs"} |~ ".*timeout.*"
```

#### **Direct Log Access**

```bash
# View real-time service logs
tail -f logs/brand-service.log
tail -f logs/data-collection.log
tail -f logs/analysis-engine.log

# View monitoring container logs
cd monitoring
docker-compose logs --follow grafana
docker-compose logs --follow prometheus
docker-compose logs --follow loki
```

#### **Log Aggregation Status**

```bash
# Check if Promtail is shipping logs to Loki
docker-compose logs promtail

# Verify log ingestion in Loki
curl "http://localhost:3100/loki/api/v1/query?query={job=\"brand-intelligence-logs\"}"
```

### 🚨 Advanced Monitoring Operations

## 📊 Checking Service Status

### Check Everything (Services + Monitoring)

```bash
./start_all_services.sh status --with-monitoring
```

**Example Output:**

```
=== SERVICE STATUS ===
✅ brand-service (PID: 12345) - Running on port 8001
✅ data-collection (PID: 12346) - Running on port 8002
✅ analysis-engine (PID: 12347) - Running on port 8003

=== MONITORING STACK STATUS ===
✅ brand-intelligence-grafana - Up (port 3200)
✅ brand-intelligence-prometheus - Up (port 9090)
✅ brand-intelligence-loki - Up (port 3100)
✅ brand-intelligence-alertmanager - Up (port 9093)
✅ brand-intelligence-node-exporter - Up (port 9100)
✅ brand-intelligence-cadvisor - Up (port 8080)
✅ brand-intelligence-promtail - Up (no external port)
```

### Check Only Brand Services

```bash
./start_all_services.sh status
```

### Check Only Monitoring Stack

```bash
# Detailed monitoring stack status
cd monitoring
docker-compose ps

# Health check with testing
./test_monitoring.sh

# Check specific monitoring service logs
docker-compose logs grafana
docker-compose logs prometheus
docker-compose logs loki
```

**Example Detailed Monitoring Status:**

```bash
$ cd monitoring && docker-compose ps
NAME                                    IMAGE                        STATUS              PORTS
brand-intelligence-alertmanager        prom/alertmanager:v0.26.0   Up 2 hours          0.0.0.0:9093->9093/tcp
brand-intelligence-cadvisor            gcr.io/cadvisor/cadvisor     Up 2 hours          0.0.0.0:8080->8080/tcp
brand-intelligence-grafana             grafana/grafana:10.1.0       Up 2 hours          0.0.0.0:3200->3000/tcp
brand-intelligence-loki                grafana/loki:2.9.0           Up 2 hours          0.0.0.0:3100->3100/tcp
brand-intelligence-node-exporter       prom/node-exporter:v1.6.1   Up 2 hours          0.0.0.0:9100->9100/tcp
brand-intelligence-prometheus          prom/prometheus:v2.47.0      Up 2 hours          0.0.0.0:9090->9090/tcp
brand-intelligence-promtail            grafana/promtail:2.9.0       Up 2 hours
```

## 🔄 Restarting Services

### Restart Everything

```bash
./start_all_services.sh restart --with-monitoring
```

**What this does:**

1. Stops all services and monitoring
2. Waits 3 seconds for clean shutdown
3. Starts everything fresh
4. Rebuilds connections and initializes monitoring

### Restart Only Services

```bash
./start_all_services.sh restart
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### **Port Already in Use**

```bash
# Check what's using the port
lsof -i :8001  # Replace with the problematic port

# Kill the process
kill -9 <PID>

# Or stop everything and start fresh
./start_all_services.sh stop --with-monitoring
./start_all_services.sh start --with-monitoring
```

#### **Services Won't Start**

```bash
# Check logs for errors
tail -f logs/brand-service.log
tail -f logs/data-collection.log
tail -f logs/analysis-engine.log

# Check Docker logs
cd monitoring
docker-compose logs grafana
docker-compose logs prometheus
```

#### **Monitoring Stack Issues**

```bash
# Restart just monitoring stack
cd monitoring
docker-compose down
docker-compose up -d

# Check container status and resource usage
docker-compose ps
docker stats

# View detailed logs for troubleshooting
docker-compose logs --follow grafana
docker-compose logs --follow prometheus
docker-compose logs --follow loki

# Check specific service health
curl -f http://localhost:3200/api/health  # Grafana
curl -f http://localhost:9090/-/healthy   # Prometheus
curl -f http://localhost:3100/ready       # Loki

# Test complete monitoring stack
./test_monitoring.sh
```

#### **Dashboard Not Loading / Blank Dashboards**

```bash
# Check Grafana container status
cd monitoring
docker-compose logs grafana

# Verify dashboard files exist
ls -la config/grafana/dashboards/
# Should show: executive-dashboard.json, technical-dashboard.json, alert-dashboard.json

# Restart Grafana to reload dashboards
docker-compose restart grafana

# Check Grafana logs for errors
docker-compose logs --follow grafana

# Verify data sources are configured
curl -u admin:admin123 http://localhost:3200/api/datasources
```

#### **No Metrics Showing in Dashboards**

```bash
# Check Prometheus is scraping targets
open http://localhost:9090/targets

# Verify Node Exporter is running
curl http://localhost:9100/metrics

# Check cAdvisor is collecting container metrics
curl http://localhost:8080/metrics

# Test Prometheus query manually
curl "http://localhost:9090/api/v1/query?query=up"

# Restart metrics collection services
cd monitoring
docker-compose restart prometheus node-exporter cadvisor
```

#### **Alerts Not Working**

```bash
# Check AlertManager status
curl -f http://localhost:9093/-/healthy

# View AlertManager configuration
cd monitoring
cat config/alertmanager/alertmanager.yml

# Check Prometheus alert rules
cat config/prometheus/alert_rules.yml

# View firing alerts in Prometheus
open http://localhost:9090/alerts

# Check AlertManager web UI
open http://localhost:9093

# Generate test alert
cd monitoring
python3 demo_alerts.py
```

#### **Log Aggregation Issues**

```bash
# Check Promtail is shipping logs
cd monitoring
docker-compose logs promtail

# Verify log directory exists and has content
ls -la ../logs/
tail -f ../logs/*.log

# Test Loki API directly
curl "http://localhost:3100/loki/api/v1/query?query={job=\"brand-intelligence-logs\"}&limit=10"

# Restart log collection pipeline
docker-compose restart promtail loki
```

#### **Permission Issues**

```bash
# Make sure scripts are executable
chmod +x start_all_services.sh
chmod +x monitoring/test_monitoring.sh

# Check log directory permissions
ls -la logs/
```

### Emergency Stop Commands

#### **Nuclear Option - Stop All Docker**

```bash
docker stop $(docker ps -q)
```

⚠️ **Warning:** This stops ALL Docker containers on your system!

#### **Kill All Python Processes**

```bash
pkill -f "python.*brand"
```

⚠️ **Warning:** This kills all Python processes with "brand" in the name!

#### **Free Specific Ports**

```bash
# Kill process on specific port
lsof -ti:8001 | xargs kill -9  # Brand service
lsof -ti:8002 | xargs kill -9  # Data collection
lsof -ti:8003 | xargs kill -9  # Analysis engine
lsof -ti:3200 | xargs kill -9  # Grafana
```

## 🎪 Demo Scenarios

## 🎪 Demo Scenarios

### **Scenario 1: Complete Hackathon Demo Setup**

```bash
# 1. Clean start for professional demo
./start_all_services.sh stop --with-monitoring
sleep 5
./start_all_services.sh start --with-monitoring

# 2. Wait for full system initialization
sleep 30

# 3. Test and validate monitoring stack
cd monitoring
./test_monitoring.sh

# 4. Generate demo data for impressive dashboards
./test_monitoring.sh demo
python3 demo_alerts.py
python3 metrics_generator.py &  # Background metrics

# 5. Open professional dashboards for presentation
open http://localhost:3200/d/executive-dashboard
open http://localhost:3200/d/technical-dashboard
open http://localhost:3200/d/alert-dashboard

# 6. Verify everything is working
curl -f http://localhost:8001/health  # Brand service
curl -f http://localhost:8002/health  # Data collection
curl -f http://localhost:8003/health  # Analysis engine
curl -f http://localhost:3200/api/health  # Grafana
```

### **Scenario 2: Live Demo with Real-time Metrics**

```bash
# Start all services
./start_all_services.sh start --with-monitoring

# Generate continuous live metrics for demo
cd monitoring
python3 metrics_generator.py &
python3 quick_demo.py &

# Monitor in real-time (show audience these commands)
watch -n 2 'curl -s http://localhost:9090/api/v1/query?query=up'
tail -f ../logs/brand-service.log
```

### **Scenario 3: Alert Demonstration**

```bash
# Start monitoring
./start_all_services.sh start --with-monitoring

# Generate various types of alerts
cd monitoring
python3 demo_alerts.py

# Show alert escalation in different interfaces:
open http://localhost:3200/d/alert-dashboard  # Grafana alerts
open http://localhost:9090/alerts            # Prometheus alerts
open http://localhost:9093                   # AlertManager
```

### **Scenario 4: Development Mode (No Monitoring Overhead)**

```bash
# Start services only (faster for development)
./start_all_services.sh start

# Later add monitoring when needed for testing
cd monitoring
docker-compose up -d
```

### **Scenario 5: Monitoring-Only for External Services**

```bash
# Just monitoring stack for monitoring external systems
cd monitoring
docker-compose up -d

# Configure Prometheus to monitor external targets
vim config/prometheus/prometheus.yml
# Add external targets, then restart
docker-compose restart prometheus
```

### **Scenario 6: Disaster Recovery Demo**

```bash
# Show resilience - kill services and monitor recovery
./start_all_services.sh start --with-monitoring

# Kill a service to show alerts
kill $(lsof -ti:8001)  # Kill brand-service

# Show alerts firing in dashboards
open http://localhost:3200/d/alert-dashboard

# Restart service and show recovery
./start_all_services.sh start

# Show service recovery in metrics
open http://localhost:3200/d/technical-dashboard
```

## 📝 Log Management & Analysis

### **Real-time Log Monitoring**

```bash
# View real-time service logs
tail -f logs/brand-service.log
tail -f logs/data-collection.log
tail -f logs/analysis-engine.log

# View all service logs together
tail -f logs/*.log

# Filter logs for specific events
tail -f logs/*.log | grep ERROR
tail -f logs/*.log | grep WARNING
tail -f logs/*.log | grep "company analysis"
```

### **Advanced Log Analysis via Grafana**

```bash
# Access Grafana Log Explorer
open http://localhost:3200/explore

# Example LogQL queries for Loki:
# Basic service logs:
{job="brand-intelligence-logs"}

# Error logs only:
{job="brand-intelligence-logs"} |= "ERROR"

# Specific service logs:
{job="brand-intelligence-logs"} |= "brand-service"

# Logs with specific patterns:
{job="brand-intelligence-logs"} |~ ".*timeout.*|.*failed.*"

# Time-based filtering:
{job="brand-intelligence-logs"} |= "ERROR" [5m]
```

### **Monitoring Container Logs**

```bash
# All monitoring container logs
cd monitoring
docker-compose logs --follow

# Specific monitoring service logs
docker-compose logs --follow grafana
docker-compose logs --follow prometheus
docker-compose logs --follow loki
docker-compose logs --follow alertmanager

# Check for errors in monitoring stack
docker-compose logs | grep -i error
docker-compose logs | grep -i warning
```

### **Log Aggregation Verification**

```bash
# Check if Promtail is shipping logs to Loki
cd monitoring
docker-compose logs promtail

# Verify log ingestion in Loki
curl "http://localhost:3100/loki/api/v1/query?query={job=\"brand-intelligence-logs\"}&limit=5"

# Check log volume statistics
curl "http://localhost:3100/loki/api/v1/query?query=rate({job=\"brand-intelligence-logs\"}[1m])"
```

### **Log Locations & Structure**

```bash
# Service log directory structure
ls -la logs/
# brand-service.log     - Core API logs
# data-collection.log   - Scraping activity logs
# analysis-engine.log   - AI processing logs

# Monitoring logs (Docker container logs)
docker-compose logs grafana 2>&1 | head -20      # Grafana logs
docker-compose logs prometheus 2>&1 | head -20   # Prometheus logs
docker-compose logs loki 2>&1 | head -20         # Loki logs
```

### **Demo Log Generation**

```bash
# Generate sample log entries for demonstration
cd monitoring
./test_monitoring.sh demo

# Generate continuous demo logs
python3 demo_alerts.py  # Creates alerts and log entries
```

## 🔧 Advanced Operations

## 🔧 Advanced Operations

### **Monitoring Configuration Management**

```bash
# Edit Prometheus configuration
vim monitoring/config/prometheus/prometheus.yml

# Edit alert rules
vim monitoring/config/prometheus/alert_rules.yml

# Edit Grafana data sources
vim monitoring/config/grafana/provisioning/datasources/datasources.yml

# Edit AlertManager configuration (email settings)
vim monitoring/config/alertmanager/alertmanager.yml

# After configuration changes, restart affected services
cd monitoring
docker-compose restart prometheus  # For Prometheus changes
docker-compose restart grafana     # For Grafana changes
docker-compose restart alertmanager # For AlertManager changes
```

### **Dashboard Customization**

```bash
# Dashboard files location
ls monitoring/config/grafana/dashboards/
# executive-dashboard.json   - Business KPIs
# technical-dashboard.json   - System metrics
# alert-dashboard.json       - Alert management

# After editing dashboards, restart Grafana
cd monitoring
docker-compose restart grafana

# Import additional dashboards via Grafana UI
open http://localhost:3200/dashboard/import
```

### **Metrics & Alerting Customization**

```bash
# Add custom metrics collection targets
vim monitoring/config/prometheus/prometheus.yml

# Add custom alert rules
vim monitoring/config/prometheus/alert_rules.yml

# Example custom alert rule:
# - alert: CustomHighErrorRate
#   expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
#   for: 2m
#   labels:
#     severity: warning
#   annotations:
#     summary: "High error rate detected"

# Restart to apply changes
docker-compose restart prometheus
```

### **Data Retention & Storage**

```bash
# Prometheus data retention (configured for 30 days)
# Location: monitoring/config/prometheus/prometheus.yml
# --storage.tsdb.retention.time=30d

# Loki data retention (configured for 30 days)
# Location: monitoring/config/loki/loki.yml

# View data usage
docker-compose exec prometheus df -h /prometheus
docker-compose exec loki df -h /loki

# Clean old data manually (if needed)
docker-compose exec prometheus rm -rf /prometheus/data/01*
```

### **Scaling & Performance Tuning**

```bash
# Monitor monitoring stack resource usage
docker stats

# Tune Prometheus for high cardinality
vim monitoring/config/prometheus/prometheus.yml
# Adjust scrape_interval and evaluation_interval

# Tune Grafana for performance
vim monitoring/config/grafana/provisioning/datasources/datasources.yml
# Adjust query timeout and max_concurrent_queries

# Scale monitoring for production
vim monitoring/docker-compose.yml
# Add resource limits and replicas
```

### **Backup and Restore**

```bash
# Backup Prometheus data
docker-compose exec prometheus tar czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp brand-intelligence-prometheus:/tmp/prometheus-backup.tar.gz ./prometheus-backup.tar.gz

# Backup Grafana data (dashboards already in git)
docker-compose exec grafana tar czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp brand-intelligence-grafana:/tmp/grafana-backup.tar.gz ./grafana-backup.tar.gz

# Backup monitoring configuration
tar czf monitoring-config-backup.tar.gz monitoring/config/

# Restore (if needed)
# 1. Stop monitoring: docker-compose down
# 2. Extract backups to appropriate volumes
# 3. Start monitoring: docker-compose up -d
```

### **Monitoring the Monitoring Stack**

```bash
# Monitor Prometheus itself
curl http://localhost:9090/metrics | grep prometheus_

# Monitor Grafana performance
curl -u admin:admin123 http://localhost:3200/api/admin/stats

# Monitor Loki ingestion
curl http://localhost:3100/metrics | grep loki_

# Set up external monitoring for the monitoring stack
# (Recommended for production environments)
```

## 🏆 Production Deployment Notes

### **Security Hardening for Production**

```bash
# 1. Change default Grafana credentials
# Edit: monitoring/config/grafana/provisioning/datasources/datasources.yml
# Set strong password and disable admin user signup

# 2. Enable HTTPS/TLS
# Add reverse proxy (nginx/traefik) with SSL certificates
# Configure secure headers and authentication

# 3. Network Security
# Use docker networks with restricted access
# Configure firewall rules for monitoring ports
# Enable authentication for Prometheus/AlertManager

# 4. Secrets Management
# Move passwords/API keys to environment variables
# Use Docker secrets or external secret management
```

### **Resource Requirements & Scaling**

| Deployment Type | RAM   | CPU       | Disk   | Notes                |
| --------------- | ----- | --------- | ------ | -------------------- |
| **Development** | 4GB   | 2 cores   | 10GB   | Local testing        |
| **Staging**     | 8GB   | 4 cores   | 50GB   | Full feature testing |
| **Production**  | 16GB+ | 8+ cores  | 100GB+ | High availability    |
| **Enterprise**  | 32GB+ | 16+ cores | 500GB+ | Multi-tenancy        |

### **High Availability Setup**

```bash
# 1. Prometheus HA with federation
# Set up multiple Prometheus instances
# Configure federation for data aggregation

# 2. Grafana HA with external database
# Use PostgreSQL/MySQL for dashboard storage
# Configure session storage (Redis/Database)

# 3. Loki HA with object storage
# Configure S3/GCS for log storage
# Set up Loki clustering

# 4. Load balancing
# Use nginx/haproxy for load balancing
# Configure health checks and failover
```

### **Monitoring Best Practices**

```bash
# 1. Alert Fatigue Prevention
# Set appropriate alert thresholds
# Use alert grouping and inhibition rules
# Implement escalation policies

# 2. Data Retention Strategy
# Short-term: High resolution (1m for 7 days)
# Medium-term: Medium resolution (5m for 30 days)
# Long-term: Low resolution (1h for 1 year)

# 3. Dashboard Organization
# Executive: Business KPIs and SLAs
# Technical: Infrastructure and application metrics
# Operational: Alerts and troubleshooting views

# 4. Performance Optimization
# Use recording rules for expensive queries
# Optimize label cardinality
# Regular housekeeping and cleanup
```

### **Compliance & Auditing**

```bash
# 1. Audit Logging
# Enable Grafana audit logs
# Configure Prometheus query logging
# Set up centralized log collection

# 2. Data Privacy
# Implement data retention policies
# Configure data anonymization
# Ensure GDPR/compliance requirements

# 3. Access Control
# Configure RBAC in Grafana
# Set up SSO integration
# Implement API key management
```

### **External Integrations**

```bash
# 1. Cloud Monitoring Integration
# AWS CloudWatch integration
# Google Cloud Monitoring
# Azure Monitor integration

# 2. Incident Management
# PagerDuty integration
# OpsGenie integration
# ServiceNow integration

# 3. Communication Platforms
# Slack notifications
# Microsoft Teams integration
# Custom webhook integrations
```

### **Maintenance Procedures**

```bash
# 1. Regular Health Checks
# Weekly: ./test_monitoring.sh
# Monthly: Review alert rules and thresholds
# Quarterly: Capacity planning review

# 2. Update Procedures
# Update container images regularly
# Test updates in staging first
# Implement blue-green deployments

# 3. Backup Procedures
# Daily: Automated data backups
# Weekly: Configuration backups
# Monthly: Disaster recovery testing
```

---

## 📞 Quick Help & Reference

### **Emergency Commands Quick Reference**

```bash
# EMERGENCY STOP EVERYTHING
./start_all_services.sh stop --with-monitoring

# NUCLEAR OPTION - Stop all Docker (USE WITH CAUTION!)
docker stop $(docker ps -q)

# KILL SPECIFIC PORTS
lsof -ti:8001 | xargs kill -9  # Brand service
lsof -ti:8002 | xargs kill -9  # Data collection
lsof -ti:8003 | xargs kill -9  # Analysis engine
lsof -ti:3200 | xargs kill -9  # Grafana

# RESTART EVERYTHING FROM SCRATCH
./start_all_services.sh stop --with-monitoring
sleep 5
./start_all_services.sh start --with-monitoring
```

### **Quick Access URLs**

| Service                 | URL                                         | Credentials    |
| ----------------------- | ------------------------------------------- | -------------- |
| **Grafana Dashboards**  | http://localhost:3200                       | admin/admin123 |
| **Executive Dashboard** | http://localhost:3200/d/executive-dashboard | admin/admin123 |
| **Technical Dashboard** | http://localhost:3200/d/technical-dashboard | admin/admin123 |
| **Alert Dashboard**     | http://localhost:3200/d/alert-dashboard     | admin/admin123 |
| **Prometheus Metrics**  | http://localhost:9090                       | No auth        |
| **Prometheus Alerts**   | http://localhost:9090/alerts                | No auth        |
| **AlertManager**        | http://localhost:9093                       | No auth        |
| **Loki Logs**           | http://localhost:3100                       | No auth        |
| **System Metrics**      | http://localhost:9100/metrics               | No auth        |
| **Container Metrics**   | http://localhost:8080/metrics               | No auth        |

### **Monitoring Health Check Commands**

```bash
# Complete health check
cd monitoring && ./test_monitoring.sh

# Individual service checks
curl -f http://localhost:3200/api/health   # Grafana
curl -f http://localhost:9090/-/healthy    # Prometheus
curl -f http://localhost:3100/ready        # Loki
curl -f http://localhost:9093/-/healthy    # AlertManager

# Brand Intelligence service checks
curl -f http://localhost:8001/health       # Brand service
curl -f http://localhost:8002/health       # Data collection
curl -f http://localhost:8003/health       # Analysis engine
```

### **Demo Data Generation**

```bash
# Generate demo alerts and logs
cd monitoring
./test_monitoring.sh demo

# Generate continuous demo metrics
python3 metrics_generator.py &

# Generate sample alerts
python3 demo_alerts.py
```

### **Getting Help**

```bash
# Command help
./start_all_services.sh help

# Monitoring test help
cd monitoring
./test_monitoring.sh help

# Check this documentation
cat SERVICE_MANAGEMENT.md

# Project overview
cat PROJECT_ANALYSIS.md
```

### **Support & Troubleshooting**

🐛 **Common Issues:**

- Port conflicts → Use emergency stop commands above
- Blank dashboards → Check data source UIDs and restart Grafana
- No metrics → Verify Prometheus targets and Node Exporter
- Alerts not firing → Check AlertManager configuration

🔧 **Debug Mode:**

```bash
# Enable debug logging
cd monitoring
docker-compose logs --follow | grep -i error
```

🚨 **Emergency Contact:**

- Documentation: `SERVICE_MANAGEMENT.md` (this file)
- Project Details: `PROJECT_ANALYSIS.md`
- Architecture: `monitoring/README.md`

---

**🎯 Built for VibeCoding Hackathon 2025 - Professional Monitoring Solution**

⚡ **Ready for Demo:** Complete enterprise-grade monitoring and alerting infrastructure
🏆 **Production Ready:** Professional dashboards, automated alerts, comprehensive logging
🚀 **One-Command Deployment:** `./start_all_services.sh start --with-monitoring`
