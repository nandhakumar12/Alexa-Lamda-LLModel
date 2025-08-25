"""
Voice Assistant AI - Monitoring Handler Lambda Function
Handles health checks, metrics collection, and system monitoring
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

# Import shared utilities
import sys
sys.path.append('/opt/python')
sys.path.append('.')

try:
    from shared.logger import get_logger
    from shared.db import DynamoDBClient
except ImportError:
    # Fallback for local development
    pass

# Initialize AWS Lambda Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Initialize AWS clients
cloudwatch = boto3.client('cloudwatch')
dynamodb = boto3.resource('dynamodb')
lambda_client = boto3.client('lambda')
apigateway = boto3.client('apigateway')

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'voice-assistant-ai')


class MonitoringHandler:
    """Main monitoring class for health checks and metrics"""
    
    def __init__(self):
        self.cloudwatch = cloudwatch
        self.dynamodb = dynamodb
        self.lambda_client = lambda_client
        self.apigateway = apigateway
        self.table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    @tracer.capture_method
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all system components"""
        try:
            health_status = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'environment': ENVIRONMENT,
                'overall_status': 'healthy',
                'components': {}
            }
            
            # Check DynamoDB
            try:
                response = self.table.scan(Limit=1)
                health_status['components']['dynamodb'] = {
                    'status': 'healthy',
                    'response_time_ms': 0,  # Would measure actual response time
                    'table_name': DYNAMODB_TABLE_NAME
                }
            except Exception as e:
                health_status['components']['dynamodb'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
            
            # Check Lambda functions
            lambda_functions = [
                f"{PROJECT_NAME}-{ENVIRONMENT}-chatbot",
                f"{PROJECT_NAME}-{ENVIRONMENT}-auth"
            ]
            
            for function_name in lambda_functions:
                try:
                    response = self.lambda_client.get_function(FunctionName=function_name)
                    health_status['components'][function_name] = {
                        'status': 'healthy',
                        'state': response['Configuration']['State'],
                        'last_modified': response['Configuration']['LastModified']
                    }
                except Exception as e:
                    health_status['components'][function_name] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    health_status['overall_status'] = 'degraded'
            
            # Check API Gateway (if accessible)
            try:
                apis = self.apigateway.get_rest_apis()
                api_found = False
                for api in apis['items']:
                    if f"{PROJECT_NAME}-{ENVIRONMENT}" in api['name']:
                        health_status['components']['api_gateway'] = {
                            'status': 'healthy',
                            'api_id': api['id'],
                            'name': api['name']
                        }
                        api_found = True
                        break
                
                if not api_found:
                    health_status['components']['api_gateway'] = {
                        'status': 'unknown',
                        'message': 'API Gateway not found or not accessible'
                    }
            except Exception as e:
                health_status['components']['api_gateway'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
            
            # Emit custom metrics
            status_value = 1 if health_status['overall_status'] == 'healthy' else 0
            metrics.add_metric(name="SystemHealth", unit=MetricUnit.Count, value=status_value)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            metrics.add_metric(name="HealthCheckError", unit=MetricUnit.Count, value=1)
            raise
    
    @tracer.capture_method
    def collect_metrics(self, time_range_minutes: int = 60) -> Dict[str, Any]:
        """Collect and aggregate system metrics"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=time_range_minutes)
            
            metrics_data = {
                'timestamp': end_time.isoformat(),
                'time_range_minutes': time_range_minutes,
                'metrics': {}
            }
            
            # Lambda metrics
            lambda_metrics = self._get_lambda_metrics(start_time, end_time)
            metrics_data['metrics']['lambda'] = lambda_metrics
            
            # API Gateway metrics
            api_metrics = self._get_api_gateway_metrics(start_time, end_time)
            metrics_data['metrics']['api_gateway'] = api_metrics
            
            # DynamoDB metrics
            dynamodb_metrics = self._get_dynamodb_metrics(start_time, end_time)
            metrics_data['metrics']['dynamodb'] = dynamodb_metrics
            
            # Custom application metrics
            app_metrics = self._get_application_metrics(start_time, end_time)
            metrics_data['metrics']['application'] = app_metrics
            
            # Store metrics in analytics table
            self._store_metrics(metrics_data)
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            metrics.add_metric(name="MetricsCollectionError", unit=MetricUnit.Count, value=1)
            raise
    
    @tracer.capture_method
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including recent metrics"""
        try:
            # Get health check
            health = self.health_check()
            
            # Get recent metrics
            recent_metrics = self.collect_metrics(time_range_minutes=15)
            
            # Get error rates
            error_rates = self._calculate_error_rates()
            
            # Get performance metrics
            performance = self._get_performance_metrics()
            
            system_status = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'environment': ENVIRONMENT,
                'health': health,
                'metrics': recent_metrics,
                'error_rates': error_rates,
                'performance': performance
            }
            
            return system_status
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            raise
    
    def _get_lambda_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get Lambda function metrics from CloudWatch"""
        try:
            lambda_functions = [
                f"{PROJECT_NAME}-{ENVIRONMENT}-chatbot",
                f"{PROJECT_NAME}-{ENVIRONMENT}-auth",
                f"{PROJECT_NAME}-{ENVIRONMENT}-monitoring"
            ]
            
            lambda_metrics = {}
            
            for function_name in lambda_functions:
                try:
                    # Get invocation count
                    invocations = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Invocations',
                        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=300,
                        Statistics=['Sum']
                    )
                    
                    # Get error count
                    errors = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Errors',
                        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=300,
                        Statistics=['Sum']
                    )
                    
                    # Get duration
                    duration = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/Lambda',
                        MetricName='Duration',
                        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=300,
                        Statistics=['Average']
                    )
                    
                    lambda_metrics[function_name] = {
                        'invocations': sum([point['Sum'] for point in invocations['Datapoints']]),
                        'errors': sum([point['Sum'] for point in errors['Datapoints']]),
                        'avg_duration_ms': sum([point['Average'] for point in duration['Datapoints']]) / len(duration['Datapoints']) if duration['Datapoints'] else 0
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not get metrics for {function_name}: {str(e)}")
                    lambda_metrics[function_name] = {'error': str(e)}
            
            return lambda_metrics
            
        except Exception as e:
            logger.error(f"Error getting Lambda metrics: {str(e)}")
            return {}
    
    def _get_api_gateway_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get API Gateway metrics from CloudWatch"""
        try:
            api_name = f"{PROJECT_NAME}-{ENVIRONMENT}-api"
            
            # Get request count
            requests = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='Count',
                Dimensions=[{'Name': 'ApiName', 'Value': api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            # Get 4XX errors
            errors_4xx = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='4XXError',
                Dimensions=[{'Name': 'ApiName', 'Value': api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            # Get 5XX errors
            errors_5xx = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='5XXError',
                Dimensions=[{'Name': 'ApiName', 'Value': api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            # Get latency
            latency = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/ApiGateway',
                MetricName='Latency',
                Dimensions=[{'Name': 'ApiName', 'Value': api_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )
            
            return {
                'requests': sum([point['Sum'] for point in requests['Datapoints']]),
                'errors_4xx': sum([point['Sum'] for point in errors_4xx['Datapoints']]),
                'errors_5xx': sum([point['Sum'] for point in errors_5xx['Datapoints']]),
                'avg_latency_ms': sum([point['Average'] for point in latency['Datapoints']]) / len(latency['Datapoints']) if latency['Datapoints'] else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting API Gateway metrics: {str(e)}")
            return {}
    
    def _get_dynamodb_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get DynamoDB metrics from CloudWatch"""
        try:
            # Get consumed read capacity
            read_capacity = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ConsumedReadCapacityUnits',
                Dimensions=[{'Name': 'TableName', 'Value': DYNAMODB_TABLE_NAME}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            # Get consumed write capacity
            write_capacity = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/DynamoDB',
                MetricName='ConsumedWriteCapacityUnits',
                Dimensions=[{'Name': 'TableName', 'Value': DYNAMODB_TABLE_NAME}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            return {
                'consumed_read_capacity': sum([point['Sum'] for point in read_capacity['Datapoints']]),
                'consumed_write_capacity': sum([point['Sum'] for point in write_capacity['Datapoints']])
            }
            
        except Exception as e:
            logger.error(f"Error getting DynamoDB metrics: {str(e)}")
            return {}
    
    def _get_application_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get custom application metrics"""
        try:
            # Query analytics table for custom metrics
            analytics_table = self.dynamodb.Table(f"{PROJECT_NAME}-{ENVIRONMENT}-analytics")
            
            response = analytics_table.scan(
                FilterExpression='#timestamp BETWEEN :start_time AND :end_time',
                ExpressionAttributeNames={'#timestamp': 'timestamp'},
                ExpressionAttributeValues={
                    ':start_time': int(start_time.timestamp()),
                    ':end_time': int(end_time.timestamp())
                }
            )
            
            # Aggregate metrics by type
            metrics_by_type = {}
            for item in response['Items']:
                metric_type = item['metric_type']
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = 0
                metrics_by_type[metric_type] += item.get('value', 1)
            
            return metrics_by_type
            
        except Exception as e:
            logger.warning(f"Could not get application metrics: {str(e)}")
            return {}
    
    def _calculate_error_rates(self) -> Dict[str, float]:
        """Calculate error rates for different components"""
        try:
            # This would calculate error rates based on recent metrics
            # For now, return placeholder values
            return {
                'lambda_error_rate': 0.0,
                'api_gateway_error_rate': 0.0,
                'overall_error_rate': 0.0
            }
        except Exception as e:
            logger.error(f"Error calculating error rates: {str(e)}")
            return {}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            # This would get performance metrics like response times, throughput, etc.
            return {
                'avg_response_time_ms': 0,
                'p95_response_time_ms': 0,
                'throughput_per_minute': 0
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {}
    
    def _store_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """Store metrics in analytics table"""
        try:
            analytics_table = self.dynamodb.Table(f"{PROJECT_NAME}-{ENVIRONMENT}-analytics")
            
            # Store aggregated metrics
            analytics_table.put_item(
                Item={
                    'metric_type': 'system_metrics',
                    'timestamp': int(datetime.now(timezone.utc).timestamp()),
                    'data': json.dumps(metrics_data),
                    'environment': ENVIRONMENT,
                    'expires_at': int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())
                }
            )
            
        except Exception as e:
            logger.warning(f"Could not store metrics: {str(e)}")


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Main Lambda handler for monitoring functionality"""
    
    try:
        logger.info("Processing monitoring request", extra={"event": event})
        
        # Initialize monitoring handler
        monitoring_handler = MonitoringHandler()
        
        # Parse request
        if 'httpMethod' in event:
            # API Gateway request
            http_method = event['httpMethod']
            path = event.get('path', '')
            query_params = event.get('queryStringParameters') or {}
            
            if http_method == 'GET':
                if path.endswith('/health'):
                    # Health check endpoint
                    response = monitoring_handler.health_check()
                    
                elif path.endswith('/metrics'):
                    # Metrics endpoint
                    time_range = int(query_params.get('time_range_minutes', 60))
                    response = monitoring_handler.collect_metrics(time_range)
                    
                elif path.endswith('/status'):
                    # System status endpoint
                    response = monitoring_handler.get_system_status()
                    
                else:
                    return {
                        'statusCode': 404,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'error': 'Endpoint not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(response)
                }
            
            else:
                return {
                    'statusCode': 405,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'error': 'Method not allowed'})
                }
        
        else:
            # Direct Lambda invocation or scheduled event
            logger.info("Direct Lambda invocation or scheduled event")
            
            # Perform scheduled monitoring tasks
            health = monitoring_handler.health_check()
            metrics_data = monitoring_handler.collect_metrics()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Monitoring tasks completed',
                    'health': health,
                    'metrics': metrics_data
                })
            }
    
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        metrics.add_metric(name="LambdaHandlerError", unit=MetricUnit.Count, value=1)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e) if ENVIRONMENT != 'prod' else 'An error occurred'
            })
        }
