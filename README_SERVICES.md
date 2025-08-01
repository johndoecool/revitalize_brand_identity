# Brand Intelligence Hub - Service Management

## Quick Start

### Start All Services
```bash
./start_all_services.sh
```

### Service Management Commands
```bash
./start_all_services.sh start    # Start all services (default)
./start_all_services.sh stop     # Stop all services  
./start_all_services.sh restart  # Restart all services
./start_all_services.sh status   # Check service status
```

## Service URLs

| Service | Port | Health Check | API Documentation |
|---------|------|-------------|-------------------|
| Brand Service | 8001 | http://localhost:8001/health | - |
| Data Collection | 8002 | http://localhost:8002/health | http://localhost:8002/docs |
| Analysis Engine | 8003 | http://localhost:8003/health | http://localhost:8003/docs |

## Logs and Monitoring

- **Logs Directory**: `/logs/`
- **Log Files**: 
  - `brand-service.log`
  - `data-collection.log`
  - `analysis-engine.log`

View live logs:
```bash
tail -f logs/brand-service.log
tail -f logs/data-collection.log  
tail -f logs/analysis-engine.log
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - The script will detect and offer to kill existing processes
   - Manually kill: `pkill -f ".*:8001"` (replace port as needed)

2. **Virtual Environment Missing**
   - Create: `cd <service-directory> && python -m venv venv`
   - Install deps: `source venv/bin/activate && pip install -r requirements.txt`

3. **Service Not Responding**
   - Check logs in `/logs/<service-name>.log`
   - Verify `.env` files for data-collection and analysis-engine
   - Ensure OpenAI API keys are configured

### Manual Service Startup

If you need to start services individually:

```bash
# Brand Service
cd brand-service
source venv/bin/activate
python start_server.py

# Data Collection
cd data-collection  
source venv/bin/activate
python run.py

# Analysis Engine
cd analysis-engine
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

## Development Notes

- All services run with auto-reload enabled for development
- CORS is configured for cross-origin requests
- Health checks verify service availability
- Process management with PID tracking for clean shutdown
- Comprehensive error handling and user guidance

For detailed technical documentation, see `docs/context.md`.