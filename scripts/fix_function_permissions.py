import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')
function_name = 'voice-assistant-llm-chatbot'

try:
    # Check current resource policy
    print("Checking current resource policy...")
    try:
        policy_response = lambda_client.get_policy(FunctionName=function_name)
        policy = json.loads(policy_response['Policy'])
        print(f"Current policy: {json.dumps(policy, indent=2)}")
        
        # Remove the policy if it exists
        print("Removing restrictive resource policy...")
        lambda_client.remove_permission(
            FunctionName=function_name,
            StatementId='AllowExecutionFromAPIGateway'  # Common statement ID
        )
        print("✅ Removed API Gateway permission")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        print("ℹ️ No resource policy found")
    except Exception as e:
        print(f"⚠️ Error with resource policy: {e}")
    
    # Delete and recreate function URL to ensure clean state
    print("\nRecreating function URL with proper permissions...")
    
    try:
        lambda_client.delete_function_url_config(FunctionName=function_name)
        print("✅ Deleted existing function URL")
    except:
        print("ℹ️ No existing function URL to delete")
    
    # Create new function URL
    response = lambda_client.create_function_url_config(
        FunctionName=function_name,
        AuthType='NONE'
    )
    
    new_url = response['FunctionUrl']
    print(f"✅ Created new function URL: {new_url}")
    
    # Test the new URL
    print("\nTesting new function URL...")
    import requests
    
    payload = {
        'message': 'Hello! Test the fixed LLM function URL',
        'user_id': 'test-user',
        'conversation_id': 'test-fixed-url'
    }
    
    test_response = requests.post(new_url, json=payload, timeout=30)
    print(f"Status Code: {test_response.status_code}")
    
    if test_response.status_code == 200:
        try:
            data = test_response.json()
            print(f"✅ Success! LLM Response: {data.get('message', 'No message')[:100]}...")
        except:
            print(f"✅ Success: {test_response.text[:100]}...")
    else:
        print(f"❌ Still getting error: {test_response.text}")
        
    print(f"\n🔗 New Function URL: {new_url}")
    
except Exception as e:
    print(f"❌ Error: {e}")
