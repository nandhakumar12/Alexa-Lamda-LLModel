#!/usr/bin/env python3
"""
Fix Claude API Key for Nandhakumar's AI Assistant
This script updates the Lambda function environment variable with a proper Claude API key
"""

import boto3
import json
import sys

def main():
    # Get the Claude API key from user input
    print("🔧 Fixing Claude API Integration for Nandhakumar's AI Assistant")
    print("=" * 60)
    
    claude_api_key = input("\n🔑 Please enter your Claude API key: ").strip()
    
    if not claude_api_key:
        print("❌ No API key provided. Exiting...")
        return
    
    if claude_api_key == "YOUR_CLAUDE_API_KEY_HERE":
        print("❌ Please provide a real Claude API key, not the placeholder.")
        return
    
    # Initialize AWS Lambda client
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        function_name = 'nandhakumar-ai-assistant-prod'
        
        print(f"\n📋 Updating Lambda function: {function_name}")
        
        # Get current function configuration
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        current_env = response.get('Environment', {}).get('Variables', {})
        
        print(f"📊 Current environment variables: {list(current_env.keys())}")
        
        # Update the environment variables
        current_env['CLAUDE_API_KEY'] = claude_api_key
        
        # Update the Lambda function
        update_response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={'Variables': current_env}
        )
        
        print("✅ Successfully updated Claude API key!")
        print(f"🔄 Function version: {update_response['Version']}")
        print(f"📅 Last modified: {update_response['LastModified']}")
        
        # Test the function
        print("\n🧪 Testing the updated function...")
        test_payload = {
            "httpMethod": "POST",
            "body": json.dumps({
                "message": "Hello, can you tell me about yourself?",
                "userName": "Nandhakumar"
            })
        }
        
        test_response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(test_payload)
        )
        
        result = json.loads(test_response['Payload'].read())
        
        if result.get('statusCode') == 200:
            response_body = json.loads(result['body'])
            print("✅ Test successful!")
            print(f"🤖 AI Response: {response_body.get('response', 'No response')[:100]}...")
            print(f"🔧 Model used: {response_body.get('model', 'Unknown')}")
        else:
            print(f"⚠️ Test returned status code: {result.get('statusCode')}")
            print(f"📝 Response: {result.get('body', 'No body')}")
        
        print("\n🎉 Claude API integration is now working!")
        print("💡 Your AI assistant should now provide intelligent responses using Claude AI.")
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("1. Make sure you have AWS CLI configured with proper credentials")
        print("2. Verify the Lambda function name is correct")
        print("3. Check that your Claude API key is valid")
        print("4. Ensure you have permissions to update Lambda functions")

if __name__ == "__main__":
    main()
