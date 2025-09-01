import zipfile
import os
import boto3
import json

# Create a zip file with the updated Lambda function
def create_lambda_zip():
    zip_path = 'llm_function_updated.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the main Lambda function
        zipf.write('../backend/lambda_functions/llm_chatbot_bedrock.py', 'llm_chatbot_bedrock.py')
        
        # Add requirements if they exist
        req_path = '../backend/lambda_functions/requirements.txt'
        if os.path.exists(req_path):
            zipf.write(req_path, 'requirements.txt')
    
    return zip_path

# Update the Lambda function
def update_lambda_function():
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'voice-assistant-llm-chatbot'
    
    try:
        # Create the zip file
        print("Creating deployment package...")
        zip_path = create_lambda_zip()
        
        # Read the zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        # Update the function code
        print("Updating Lambda function...")
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✅ Function updated successfully!")
        print(f"✅ Function ARN: {response['FunctionArn']}")
        print(f"✅ Last Modified: {response['LastModified']}")
        
        # Clean up
        os.remove(zip_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating function: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Updating LLM Lambda Function with CORS support...")
    
    if update_lambda_function():
        print("\n🎉 Lambda function updated successfully!")
        print("✅ CORS preflight requests are now handled")
        print("✅ Function URL should work with web applications")
        
        # Test the updated function
        print("\nTesting updated function...")
        import requests
        
        # Get the current function URL
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        try:
            url_config = lambda_client.get_function_url_config(FunctionName='voice-assistant-llm-chatbot')
            url = url_config['FunctionUrl']
            
            payload = {
                'message': 'Hello! Test the updated LLM function',
                'user_id': 'test-user',
                'conversation_id': 'test-updated'
            }
            
            response = requests.post(url, json=payload, timeout=30)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LLM Response: {data.get('message', 'No message')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test Error: {e}")
    else:
        print("\n❌ Failed to update Lambda function")
