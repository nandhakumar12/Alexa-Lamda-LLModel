import json
from datetime import datetime


def _ok_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }

def lambda_handler(event, context):
    try:
        if isinstance(event, dict) and event.get('httpMethod') == 'OPTIONS':
            return { 'statusCode': 200, 'headers': _ok_headers(), 'body': '' }
        
        return {
            'statusCode': 200,
            'headers': _ok_headers(),
            'isBase64Encoded': False,
            'body': json.dumps({
                'status': 'healthy',
                'service': 'monitoring-handler',
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'uptime': '100%',
                    'response_time': '< 100ms',
                    'errors': 0
                }
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Monitoring service error'
            })
        }
