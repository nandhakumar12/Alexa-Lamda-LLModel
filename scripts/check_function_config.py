import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

try:
    response = lambda_client.get_function(FunctionName='voice-assistant-llm-chatbot')
    config = response['Configuration']
    
    print(f"Function Name: {config['FunctionName']}")
    print(f"Handler: {config['Handler']}")
    print(f"Runtime: {config['Runtime']}")
    print(f"Last Modified: {config['LastModified']}")
    print(f"Code Size: {config['CodeSize']}")
    
except Exception as e:
    print(f"Error: {e}")
