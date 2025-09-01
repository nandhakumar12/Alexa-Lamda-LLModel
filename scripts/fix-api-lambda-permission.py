#!/usr/bin/env python3
"""
Fix the Lambda permission for API Gateway
"""

import boto3
import json
import time

def fix_lambda_permission():
    """Fix Lambda permission for API Gateway"""
    print("🔧 FIXING LAMBDA PERMISSION")
    print("=" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Load details
    try:
        with open('lambda-details.json', 'r') as f:
            lambda_details = json.load(f)
        function_name = lambda_details['function_name']
    except:
        function_name = 'nandhakumar-fresh-chatbot'
    
    api_id = 'tcuzlzq1af'  # From the previous output
    
    # Get AWS account ID
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    
    try:
        # Remove any existing permissions first
        try:
            policy = lambda_client.get_policy(FunctionName=function_name)
            policy_doc = json.loads(policy['Policy'])
            
            for statement in policy_doc.get('Statement', []):
                if statement.get('Sid'):
                    try:
                        lambda_client.remove_permission(
                            FunctionName=function_name,
                            StatementId=statement['Sid']
                        )
                        print(f"✅ Removed old permission: {statement['Sid']}")
                    except:
                        pass
        except:
            print("✅ No existing permissions to remove")
        
        # Add correct permission
        statement_id = f'api-gateway-invoke-{int(time.time())}'
        source_arn = f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
        
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=source_arn
        )
        
        print(f"✅ Added correct Lambda permission")
        print(f"   Source ARN: {source_arn}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing permission: {e}")
        return False

def test_api_again():
    """Test the API again"""
    print(f"\n🧪 TESTING API AGAIN")
    print("=" * 50)
    
    import requests
    
    api_id = 'tcuzlzq1af'
    chatbot_endpoint = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    try:
        test_payload = {
            "message": "Hello! Testing after permission fix.",
            "session_id": "permission-fix-test"
        }
        
        response = requests.post(
            chatbot_endpoint,
            json=test_payload,
            timeout=15
        )
        
        print(f"POST request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Gateway now working!")
            print(f"   Response: {data.get('response', 'No response')[:50]}...")
            print(f"   Intent: {data.get('intent', 'No intent')}")
            
            # Save working API details
            api_details = {
                'api_id': api_id,
                'api_url': f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod",
                'chatbot_endpoint': chatbot_endpoint
            }
            
            with open('api-details.json', 'w') as f:
                json.dump(api_details, f, indent=2)
            
            print(f"✅ Saved working API details")
            return True
            
        else:
            print(f"❌ Still failing: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function"""
    print("🚨 FIXING API GATEWAY LAMBDA PERMISSION")
    print("=" * 60)
    
    if fix_lambda_permission():
        # Wait a moment for permission to propagate
        print("⏳ Waiting for permission to propagate...")
        time.sleep(5)
        
        if test_api_again():
            print("\n" + "=" * 60)
            print("🎉 API GATEWAY IS NOW WORKING!")
            print(f"\n🌐 WORKING ENDPOINT:")
            print(f"   https://tcuzlzq1af.execute-api.us-east-1.amazonaws.com/prod/chatbot")
            
            print(f"\n🎯 READY FOR FRONTEND DEPLOYMENT!")
        else:
            print("\n❌ API GATEWAY STILL NOT WORKING")
    else:
        print("\n❌ FAILED TO FIX PERMISSION")

if __name__ == "__main__":
    main()
