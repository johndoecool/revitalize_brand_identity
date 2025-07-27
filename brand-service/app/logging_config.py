import logging
import logging.config
import os
from datetime import datetime


def setup_logging():
    """Setup logging configuration for the brand service"""
    
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(script_dir, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created logs directory: {log_dir}")
    
    # Generate log filename with timestamp
    log_filename = f"brand-service-{datetime.now().strftime('%Y-%m-%d')}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Print debug info
    print(f"Setting up logging with main log file: {log_filepath}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
    
    # Ensure all log files can be created by touching them
    log_files = [
        log_filepath,
        os.path.join(log_dir, 'brand-service-errors.log'),
        os.path.join(log_dir, 'brand-service-cache.log'),
        os.path.join(log_dir, 'brand-service-api.log')
    ]
    
    for log_file in log_files:
        try:
            # Touch the file to ensure it can be created
            with open(log_file, 'a', encoding='utf-8') as f:
                pass
            print(f"Successfully touched log file: {log_file}")
        except Exception as e:
            print(f"Error creating log file {log_file}: {e}")
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': log_filepath,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'brand-service-errors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'cache_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': os.path.join(log_dir, 'brand-service-cache.log'),
                'maxBytes': 5242880,  # 5MB
                'backupCount': 3,
                'encoding': 'utf8'
            },
            'api_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': os.path.join(log_dir, 'brand-service-api.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            'brand_service': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'brand_service.cache': {
                'level': 'DEBUG',
                'handlers': ['console', 'cache_file', 'error_file'],
                'propagate': False
            },
            'brand_service.api': {
                'level': 'INFO',
                'handlers': ['console', 'api_file', 'error_file'],
                'propagate': False
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'uvicorn.error': {
                'level': 'INFO',
                'handlers': ['console', 'error_file'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'INFO',
                'handlers': ['api_file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Force immediate flush by testing all handlers
    test_logger = logging.getLogger('brand_service')
    test_logger.info("Brand Service logging initialized - testing file handlers")
    
    cache_test_logger = logging.getLogger('brand_service.cache')  
    cache_test_logger.info("Cache logging initialized")
    
    api_test_logger = logging.getLogger('brand_service.api')
    api_test_logger.info("API logging initialized")
    
    # Force flush all handlers
    for handler in logging.getLogger().handlers:
        if hasattr(handler, 'flush'):
            handler.flush()
    
    for logger_name in ['brand_service', 'brand_service.cache', 'brand_service.api']:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
    
    print("Logging setup completed - all handlers flushed")
    
    # Create specialized loggers
    main_logger = logging.getLogger('brand_service')
    cache_logger = logging.getLogger('brand_service.cache')
    api_logger = logging.getLogger('brand_service.api')
    
    return main_logger, cache_logger, api_logger


def get_logger(name: str = 'brand_service'):
    """Get a logger instance"""
    return logging.getLogger(name)


def force_log_flush():
    """Force flush all log handlers"""
    try:
        # Flush root logger handlers
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # Flush specific logger handlers
        for logger_name in ['brand_service', 'brand_service.cache', 'brand_service.api', 'uvicorn', 'uvicorn.error', 'uvicorn.access']:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
        print("Log flush completed")
    except Exception as e:
        print(f"Error during log flush: {e}")


def test_file_logging():
    """Test that file logging is working"""
    try:
        main_logger = logging.getLogger('brand_service')
        cache_logger = logging.getLogger('brand_service.cache')
        api_logger = logging.getLogger('brand_service.api')
        
        main_logger.info("Test log message - brand_service")
        cache_logger.info("Test log message - cache")
        api_logger.info("Test log message - api")
        
        force_log_flush()
        
        print("Test logging messages sent and flushed")
        return True
    except Exception as e:
        print(f"Error during test logging: {e}")
        return False


def log_performance(func):
    """Decorator to log function performance"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger('brand_service')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} executed successfully in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            raise
    
    return wrapper


def log_api_request(func):
    """Decorator to log API requests"""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger('brand_service.api')
        
        # Extract request info (this assumes FastAPI context)
        try:
            # Try to get request info from function arguments
            func_name = func.__name__
            logger.info(f"API request started: {func_name}")
            
            result = await func(*args, **kwargs)
            logger.info(f"API request completed successfully: {func_name}")
            return result
            
        except Exception as e:
            logger.error(f"API request failed: {func_name} - {str(e)}")
            raise
    
    return wrapper
