"""
Shared logging utilities for Voice Assistant AI
Provides structured logging with AWS Lambda Powertools integration
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog
from aws_lambda_powertools import Logger


def get_logger(name: str = None, level: str = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (defaults to calling module)
        level: Log level (defaults to environment variable or INFO)
    
    Returns:
        Configured structlog logger
    """
    if name is None:
        # Get the calling module name
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', 'voice-assistant-ai')
    
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger(name)
    
    return logger


class LambdaLogger:
    """
    Enhanced logger for AWS Lambda functions with correlation IDs and metrics
    """
    
    def __init__(self, name: str = None, correlation_id: str = None):
        self.name = name or 'voice-assistant-ai'
        self.correlation_id = correlation_id
        self.logger = get_logger(self.name)
        
        # Bind correlation ID if provided
        if self.correlation_id:
            self.logger = self.logger.bind(correlation_id=self.correlation_id)
    
    def info(self, message: str, **kwargs):
        """Log info message with additional context"""
        self.logger.info(message, **self._add_context(kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with additional context"""
        self.logger.warning(message, **self._add_context(kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with additional context"""
        self.logger.error(message, **self._add_context(kwargs))
    
    def debug(self, message: str, **kwargs):
        """Log debug message with additional context"""
        self.logger.debug(message, **self._add_context(kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with additional context"""
        self.logger.critical(message, **self._add_context(kwargs))
    
    def _add_context(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add common context to log messages"""
        context = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'dev'),
            'service': 'voice-assistant-ai',
            **kwargs
        }
        
        # Add AWS Lambda context if available
        if hasattr(self, '_lambda_context'):
            context.update({
                'aws_request_id': self._lambda_context.aws_request_id,
                'function_name': self._lambda_context.function_name,
                'function_version': self._lambda_context.function_version,
                'memory_limit': self._lambda_context.memory_limit_in_mb,
                'remaining_time': self._lambda_context.get_remaining_time_in_millis()
            })
        
        return context
    
    def set_lambda_context(self, context):
        """Set AWS Lambda context for enhanced logging"""
        self._lambda_context = context
    
    def bind(self, **kwargs):
        """Bind additional context to logger"""
        self.logger = self.logger.bind(**kwargs)
        return self


class MetricsLogger:
    """
    Logger for custom metrics and business events
    """
    
    def __init__(self, namespace: str = "VoiceAssistantAI"):
        self.namespace = namespace
        self.logger = get_logger('metrics')
    
    def log_metric(self, metric_name: str, value: float, unit: str = "Count", **dimensions):
        """
        Log a custom metric
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Metric unit (Count, Seconds, Bytes, etc.)
            **dimensions: Additional dimensions for the metric
        """
        metric_data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'namespace': self.namespace,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'dimensions': dimensions
        }
        
        self.logger.info("Custom metric", **metric_data)
    
    def log_business_event(self, event_name: str, **event_data):
        """
        Log a business event for analytics
        
        Args:
            event_name: Name of the business event
            **event_data: Additional event data
        """
        business_event = {
            'event_name': event_name,
            'event_type': 'business',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'dev'),
            **event_data
        }
        
        self.logger.info("Business event", **business_event)
    
    def log_performance_metric(self, operation: str, duration_ms: float, success: bool = True, **context):
        """
        Log a performance metric
        
        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            success: Whether the operation was successful
            **context: Additional context
        """
        performance_data = {
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success,
            'metric_type': 'performance',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **context
        }
        
        self.logger.info("Performance metric", **performance_data)


class AuditLogger:
    """
    Logger for audit events and security-related activities
    """
    
    def __init__(self):
        self.logger = get_logger('audit')
    
    def log_user_action(self, user_id: str, action: str, resource: str = None, **context):
        """
        Log a user action for audit purposes
        
        Args:
            user_id: ID of the user performing the action
            action: Action being performed
            resource: Resource being acted upon
            **context: Additional context
        """
        audit_event = {
            'event_type': 'user_action',
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'dev'),
            **context
        }
        
        self.logger.info("User action", **audit_event)
    
    def log_security_event(self, event_type: str, severity: str = "medium", **context):
        """
        Log a security event
        
        Args:
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            **context: Additional context
        """
        security_event = {
            'event_type': 'security',
            'security_event_type': event_type,
            'severity': severity,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'dev'),
            **context
        }
        
        self.logger.warning("Security event", **security_event)
    
    def log_authentication_event(self, user_id: str, event_type: str, success: bool, **context):
        """
        Log an authentication event
        
        Args:
            user_id: ID of the user
            event_type: Type of auth event (login, logout, register, etc.)
            success: Whether the authentication was successful
            **context: Additional context
        """
        auth_event = {
            'event_type': 'authentication',
            'user_id': user_id,
            'auth_event_type': event_type,
            'success': success,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('ENVIRONMENT', 'dev'),
            **context
        }
        
        if success:
            self.logger.info("Authentication event", **auth_event)
        else:
            self.logger.warning("Authentication failure", **auth_event)


# Convenience functions for common logging patterns
def log_lambda_start(function_name: str, event: Dict[str, Any], context=None):
    """Log Lambda function start"""
    logger = get_logger('lambda')
    log_data = {
        'event_type': 'lambda_start',
        'function_name': function_name,
        'event_keys': list(event.keys()) if isinstance(event, dict) else str(type(event))
    }
    
    if context:
        log_data.update({
            'aws_request_id': context.aws_request_id,
            'memory_limit': context.memory_limit_in_mb,
            'remaining_time': context.get_remaining_time_in_millis()
        })
    
    logger.info("Lambda function started", **log_data)


def log_lambda_end(function_name: str, duration_ms: float, success: bool = True, error: str = None):
    """Log Lambda function end"""
    logger = get_logger('lambda')
    log_data = {
        'event_type': 'lambda_end',
        'function_name': function_name,
        'duration_ms': duration_ms,
        'success': success
    }
    
    if error:
        log_data['error'] = error
    
    if success:
        logger.info("Lambda function completed", **log_data)
    else:
        logger.error("Lambda function failed", **log_data)


def log_api_request(method: str, path: str, user_id: str = None, **context):
    """Log API request"""
    logger = get_logger('api')
    log_data = {
        'event_type': 'api_request',
        'method': method,
        'path': path,
        'user_id': user_id,
        **context
    }
    
    logger.info("API request", **log_data)


def log_api_response(method: str, path: str, status_code: int, duration_ms: float, **context):
    """Log API response"""
    logger = get_logger('api')
    log_data = {
        'event_type': 'api_response',
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
        **context
    }
    
    if status_code >= 400:
        logger.warning("API response with error", **log_data)
    else:
        logger.info("API response", **log_data)
