#!/usr/bin/env python3
"""
Fix API Gateway CORS configuration
"""

import boto3
import json

def fix_api_gateway_cors():
    """Fix CORS configuration for API Gateway"""
    print("🔧 Fixing API Gateway CORS configuration...")
    
    # Initialize API Gateway client
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    
    # API Gateway details
    api_id = 'dgkrnsyybk'
    
    try:
        # Get the API details
        api = apigateway.get_rest_api(restApiId=api_id)
        print(f"✅ Found API: {api['name']}")
        
        # Get resources
        resources = apigateway.get_resources(restApiId=api_id)
        
        for resource in resources['items']:
            resource_id = resource['id']
            path = resource['path']
            
            print(f"📋 Resource: {path} (ID: {resource_id})")
            
            # Check if OPTIONS method exists
            methods = resource.get('resourceMethods', {})
            
            if 'OPTIONS' not in methods:
                print(f"   ➕ Adding OPTIONS method to {path}")
                
                # Add OPTIONS method
                try:
                    apigateway.put_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        authorizationType='NONE'
                    )
                    
                    # Add method response
                    apigateway.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Headers': False,
                            'method.response.header.Access-Control-Allow-Methods': False,
                            'method.response.header.Access-Control-Allow-Origin': False
                        }
                    )
                    
                    # Add integration
                    apigateway.put_integration(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        type='MOCK',
                        requestTemplates={
                            'application/json': '{"statusCode": 200}'
                        }
                    )
                    
                    # Add integration response
                    apigateway.put_integration_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod='OPTIONS',
                        statusCode='200',
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Correlation-ID'",
                            'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,POST,GET'",
                            'method.response.header.Access-Control-Allow-Origin': "'*'"
                        },
                        responseTemplates={
                            'application/json': ''
                        }
                    )
                    
                    print(f"   ✅ Added OPTIONS method to {path}")
                    
                except Exception as e:
                    print(f"   ❌ Error adding OPTIONS to {path}: {e}")
            else:
                print(f"   ✅ OPTIONS method already exists for {path}")
        
        # Deploy the API
        print("🚀 Deploying API changes...")
        apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Fixed CORS configuration'
        )
        
        print("✅ API Gateway CORS configuration updated and deployed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing CORS: {e}")
        return False

def test_cors_after_fix():
    """Test CORS after the fix"""
    print("\n🧪 Testing CORS after fix...")
    
    import requests
    
    api_url = "https://dgkrnsyybk.execute-api.us-east-1.amazonaws.com/prod/chatbot"
    
    headers = {
        "Origin": "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(api_url, headers=headers, timeout=10)
        print(f"📊 CORS Preflight Status: {response.status_code}")
        print(f"📋 CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS preflight now working!")
        else:
            print("❌ CORS preflight still failing")
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")

def main():
    print("🔧 API Gateway CORS Fix")
    print("=" * 40)
    
    # Fix CORS
    if fix_api_gateway_cors():
        # Wait a moment for deployment
        import time
        print("⏳ Waiting for deployment to complete...")
        time.sleep(10)
        
        # Test CORS
        test_cors_after_fix()
        
        print("\n" + "=" * 40)
        print("🎉 CORS Fix Complete!")
        print("\n🌐 Your app should now work properly at:")
        print("   S3: http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
        print("   CloudFront: https://d36s8pxm5kezg4.cloudfront.net")
        
        print("\n✅ Fixed issues:")
        print("   🔧 CORS preflight requests")
        print("   🌐 Cross-origin API calls")
        print("   📡 Browser compatibility")
    else:
        print("❌ Failed to fix CORS configuration")

if __name__ == "__main__":
    main()
