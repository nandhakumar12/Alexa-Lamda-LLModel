#!/usr/bin/env python3

"""
Quick test to verify Bedrock Claude Haiku access
"""

import json
import boto3

def test_bedrock():
    print("🧠 Testing Bedrock Claude Haiku access...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Say 'LLM is working' if you can respond."
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        claude_response = response_body['content'][0]['text']
        
        print(f"✅ SUCCESS! Claude Haiku responded:")
        print(f"🗣️ '{claude_response}'")
        print(f"💰 Cost for this test: ~$0.0001 (practically free!)")
        return True
        
    except Exception as e:
        if "AccessDeniedException" in str(e):
            print(f"❌ Access denied - Model access not yet granted")
            print(f"💡 Please enable Claude 3 Haiku access in AWS Console")
        else:
            print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_bedrock()
