import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')

try:
    # List all functions
    response = lambda_client.list_functions()
    voice_functions = [f for f in response['Functions'] if 'voice-assistant' in f['FunctionName']]
    
    print('Voice Assistant Lambda Functions:')
    for func in voice_functions:
        print(f'  - {func["FunctionName"]}')
        
        # Check if function URL exists
        try:
            url_config = lambda_client.get_function_url_config(FunctionName=func['FunctionName'])
            print(f'    URL: {url_config["FunctionUrl"]}')
            print(f'    Auth: {url_config["AuthType"]}')
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f'    URL: Not configured')
        except Exception as e:
            print(f'    URL Error: {e}')
        print()
        
except Exception as e:
    print(f'Error: {e}')
