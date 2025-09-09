import json
from datetime import datetime


def _parse_json_body(event):
    raw_body = event.get('body') if isinstance(event, dict) else None
    if raw_body is None or raw_body == "":
        return {}
    if isinstance(raw_body, (dict, list)):
        return raw_body
    try:
        return json.loads(raw_body)
    except Exception:
        return {}

def lambda_handler(event, context):
    try:
        if isinstance(event, dict) and event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'body': ''
            }
        
        body = _parse_json_body(event)
        action = body.get('action', 'health_check')
        
        if action == 'health_check':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'auth-handler',
                    'timestamp': datetime.now().isoformat()
                })
            }
        else:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'message': 'Auth service is working',
                    'action': action,
                    'timestamp': datetime.now().isoformat()
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Auth service error'
            })
        }
