#!/usr/bin/env python3
"""
Fix API Gateway integration issues
"""

import subprocess
import json

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def fix_api_integration():
    print("🔧 Fixing API Gateway integration...")
    
    api_id = "u4cly0taa7"
    
    # Get resources
    resources_result = run_command(f'aws apigateway get-resources --rest-api-id {api_id} --output json')
    if not resources_result:
        print("❌ Failed to get resources")
        return False
    
    resources = json.loads(resources_result)
    chat_resource_id = None
    
    for resource in resources['items']:
        if resource.get('pathPart') == 'chat':
            chat_resource_id = resource['id']
            break
    
    if not chat_resource_id:
        print("❌ Chat resource not found")
        return False
    
    print(f"✅ Found chat resource: {chat_resource_id}")
    
    # Fix CORS integration
    print("🔧 Fixing CORS integration...")
    run_command(f'aws apigateway put-integration --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --type MOCK --request-templates \'{{"application/json": "{{\\"statusCode\\": 200}}"}}\'')
    
    # Add method response for OPTIONS
    run_command(f'aws apigateway put-method-response --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --status-code 200 --response-parameters method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false')
    
    # Add integration response for OPTIONS
    run_command(f'aws apigateway put-integration-response --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --status-code 200 --response-parameters method.response.header.Access-Control-Allow-Headers=\\"\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'\\",method.response.header.Access-Control-Allow-Methods=\\"\'GET,POST,OPTIONS\'\\",method.response.header.Access-Control-Allow-Origin=\\"\'*\'\\"')
    
    # Redeploy API
    print("🚀 Redeploying API...")
    run_command(f'aws apigateway create-deployment --rest-api-id {api_id} --stage-name prod --description "Fixed deployment"')
    
    print("✅ API Gateway integration fixed!")
    return True

def test_api():
    print("🧪 Testing API endpoint...")
    
    import requests
    
    api_url = "https://u4cly0taa7.execute-api.us-east-1.amazonaws.com/prod/chat"
    
    test_payload = {
        "message": "Hello",
        "userName": "Nandhakumar"
    }
    
    try:
        response = requests.post(api_url, json=test_payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Test Successful!")
            print(f"Response: {data.get('response', 'No response')}")
            return True
        else:
            print(f"❌ API Test Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Test Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing API Gateway Issues")
    print("=" * 40)
    
    # Fix integration
    if fix_api_integration():
        print("\n🧪 Testing API...")
        test_api()
    
    print("\n✅ Fix completed!")
