# Brand Intelligence Hub - Integration Tests

This directory contains integration tests for the Brand Intelligence Hub platform, specifically testing the end-to-end workflow across all three microservices.

## Test Structure

```
tests/
├── __init__.py
├── requirements.txt          # Test dependencies
├── README.md                # This file
└── integration/
    ├── __init__.py
    └── test_consumer.py     # End-to-end integration test
```

## Prerequisites

1. **All Services Running**: Ensure all three services are running:
   ```bash
   ./start_all_services.sh
   ```

2. **Test Dependencies**: Install test requirements:
   ```bash
   pip install -r tests/requirements.txt
   ```

## Running Tests

### Quick Health Check
Test if all services are running and healthy:
```bash
cd tests/integration
python test_consumer.py --test-type health
```

### Full Integration Test
Run complete end-to-end workflow test:
```bash
cd tests/integration
python test_consumer.py --test-type full
```

## Test Coverage

### Integration Test Consumer (`test_consumer.py`)

**Services Tested:**
- Brand Service (Port 8001)
- Data Collection Service (Port 8002)  
- Analysis Engine Service (Port 8003)

**Test Workflow:**
1. **Health Check**: Verify all services are running
2. **Brand Search**: Test brand search functionality
3. **Area Discovery**: Get suggested analysis areas for brand
4. **Competitor Discovery**: Find competitors in selected area
5. **Data Collection**: Start and monitor data collection job
6. **Analysis**: Start and monitor AI analysis job
7. **Results Validation**: Verify analysis results and insights

**Test Features:**
- ✅ Service health monitoring
- ✅ API endpoint validation
- ✅ Async job monitoring with progress tracking
- ✅ Error handling and timeout management
- ✅ End-to-end data flow validation
- ✅ Results verification

## Expected Output

### Health Test Success:
```
[INFO 18:45:01] 🏥 Brand Intelligence Hub - Quick Health Test
[INFO 18:45:01] ============================================================
[INFO 18:45:01] ✅ brand-service: healthy  
[INFO 18:45:01] ✅ data-collection: healthy
[INFO 18:45:01] ✅ analysis-engine: healthy
[INFO 18:45:01] ✅ All services are healthy and ready!
```

### Full Integration Test Success:
```
[INFO 18:45:01] 🚀 Brand Intelligence Hub - Full Integration Test
[INFO 18:45:01] ================================================================================
[INFO 18:45:01] Step 1: Checking service health...
[INFO 18:45:01] ✅ brand-service: healthy
[INFO 18:45:01] ✅ data-collection: healthy  
[INFO 18:45:01] ✅ analysis-engine: healthy
[INFO 18:45:01] ✅ All services are healthy

[INFO 18:45:02] Step 2: Searching for brands...
[INFO 18:45:02] 🔍 Searching for brands: 'Apple'
[INFO 18:45:02] ✅ Found 3 brands
[INFO 18:45:02] ✅ Selected brand: Apple Inc. (ID: apple)

... [workflow continues] ...

[INFO 18:47:45] ================================================================================
[INFO 18:47:45] 🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!
[INFO 18:47:45] ================================================================================
[INFO 18:47:45] 📊 Test Summary:
[INFO 18:47:45]   • Request ID: 12345678-1234-5678-9012-123456789012
[INFO 18:47:45]   • Brand: Apple Inc. (ID: apple)
[INFO 18:47:45]   • Competitor: Google LLC (ID: google)
[INFO 18:47:45]   • Area: Employer Branding (ID: employer_branding)
[INFO 18:47:45]   • Data Collection Job: collect_abcd1234
[INFO 18:47:45]   • Analysis Job: analysis_efgh5678
```

## Troubleshooting

### Common Issues

1. **Services Not Running**
   ```
   [ERROR] ❌ brand-service: Connection refused
   Solution: ./start_all_services.sh
   ```

2. **API Timeout**
   ```
   [ERROR] Request timeout after 5 seconds
   Solution: Check service logs in /logs/ directory
   ```

3. **Job Monitoring Timeout**
   ```
   [WARN] ⏰ Data collection monitoring timed out after 300 seconds
   Solution: Check data collection service logs, increase timeout if needed
   ```

### Debugging

1. **Check Service Logs**:
   ```bash
   tail -f logs/brand-service.log
   tail -f logs/data-collection.log  
   tail -f logs/analysis-engine.log
   ```

2. **Manual API Testing**:
   ```bash
   # Test service health
   curl http://localhost:8001/health
   curl http://localhost:8002/health
   curl http://localhost:8003/health
   
   # View API docs
   open http://localhost:8002/docs
   open http://localhost:8003/docs
   ```

3. **Service Status**:
   ```bash
   ./start_all_services.sh status
   ```

## Test Development

To add new integration tests:

1. Create new test files in `tests/integration/`
2. Follow the same pattern as `test_consumer.py`
3. Use minimal dependencies (avoid external packages when possible)
4. Include proper error handling and timeout management
5. Add comprehensive logging for debugging

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```bash
# In CI pipeline
./start_all_services.sh
python tests/integration/test_consumer.py --test-type health
python tests/integration/test_consumer.py --test-type full
./start_all_services.sh stop
```

For questions or issues with integration tests, check the main project documentation in `docs/context.md`.