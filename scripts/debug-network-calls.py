#!/usr/bin/env python3
"""
Debug exactly what network calls the browser is making
"""

import boto3
import json
import requests
import time

def check_all_apis():
    """Check all API Gateways and their status"""
    print("🔍 CHECKING ALL API GATEWAYS")
    print("=" * 50)
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    
    try:
        # Get all APIs
        apis = apigateway.get_rest_apis()
        
        print(f"📊 Found {len(apis['items'])} API Gateways:")
        
        for api in apis['items']:
            api_id = api['id']
            api_name = api['name']
            created = api['createdDate']
            
            print(f"\n🌐 API: {api_name}")
            print(f"   ID: {api_id}")
            print(f"   Created: {created}")
            print(f"   URL: https://{api_id}.execute-api.us-east-1.amazonaws.com/prod")
            
            # Check if this API has deployments
            try:
                deployments = apigateway.get_deployments(restApiId=api_id)
                print(f"   Deployments: {len(deployments['items'])}")
                
                if deployments['items']:
                    latest = deployments['items'][0]
                    print(f"   Latest Deployment: {latest['id']}")
                
                # Check stages
                stages = apigateway.get_stages(restApiId=api_id)
                print(f"   Stages: {[stage['stageName'] for stage in stages['item']]}")
                
                # Test the chatbot endpoint
                test_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chatbot"
                print(f"   Testing: {test_url}")
                
                try:
                    response = requests.post(
                        test_url,
                        json={
                            "message": "test",
                            "type": "text", 
                            "session_id": f"debug-{int(time.time())}"
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ WORKING! Response: {result.get('response', 'No response')[:50]}...")
                    else:
                        print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                        
                except Exception as e:
                    print(f"   ❌ Network Error: {e}")
                    
            except Exception as e:
                print(f"   ❌ Error checking API: {e}")
                
    except Exception as e:
        print(f"❌ Error listing APIs: {e}")

def check_frontend_config():
    """Check what the frontend is actually configured to use"""
    print("\n🔍 CHECKING FRONTEND CONFIGURATION")
    print("=" * 50)
    
    # Check .env file
    try:
        with open('../frontend/.env', 'r') as f:
            env_content = f.read()
        
        print("📄 Frontend .env file:")
        for line in env_content.strip().split('\n'):
            if line.strip():
                print(f"   {line}")
                
        # Extract API URL
        for line in env_content.split('\n'):
            if 'REACT_APP_API_GATEWAY_URL' in line:
                api_url = line.split('=')[1].strip()
                print(f"\n🎯 Frontend configured to use: {api_url}")
                
                # Test this URL
                try:
                    test_response = requests.post(
                        f"{api_url}/chatbot",
                        json={
                            "message": "frontend config test",
                            "type": "text",
                            "session_id": f"frontend-test-{int(time.time())}"
                        },
                        timeout=5
                    )
                    
                    if test_response.status_code == 200:
                        print(f"   ✅ Frontend API URL is WORKING!")
                    else:
                        print(f"   ❌ Frontend API URL FAILED: {test_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Frontend API URL ERROR: {e}")
                break
                
    except Exception as e:
        print(f"❌ Error reading frontend .env: {e}")
    
    # Check the hardcoded fallback in api.ts
    try:
        with open('../frontend/src/services/api.ts', 'r') as f:
            api_ts_content = f.read()
        
        # Find the API_BASE_URL line
        for line_num, line in enumerate(api_ts_content.split('\n'), 1):
            if 'API_BASE_URL' in line and 'process.env' in line:
                print(f"\n📄 api.ts line {line_num}:")
                print(f"   {line.strip()}")
                
                # Extract the fallback URL
                if '||' in line:
                    fallback = line.split('||')[1].strip().strip("';")
                    print(f"\n🎯 Hardcoded fallback: {fallback}")
                    
                    # Test the fallback URL
                    try:
                        fallback_clean = fallback.strip("'\"")
                        test_response = requests.post(
                            f"{fallback_clean}/chatbot",
                            json={
                                "message": "fallback test",
                                "type": "text",
                                "session_id": f"fallback-test-{int(time.time())}"
                            },
                            timeout=5
                        )
                        
                        if test_response.status_code == 200:
                            print(f"   ✅ Hardcoded fallback is WORKING!")
                        else:
                            print(f"   ❌ Hardcoded fallback FAILED: {test_response.status_code}")
                            
                    except Exception as e:
                        print(f"   ❌ Hardcoded fallback ERROR: {e}")
                break
                
    except Exception as e:
        print(f"❌ Error reading api.ts: {e}")

def check_conflicting_deployments():
    """Check for conflicting deployment scripts"""
    print("\n🔍 CHECKING FOR CONFLICTING DEPLOYMENTS")
    print("=" * 50)
    
    # Check deploy-complete-system.py
    try:
        with open('deploy-complete-system.py', 'r') as f:
            deploy_content = f.read()
        
        # Find hardcoded API URLs
        for line_num, line in enumerate(deploy_content.split('\n'), 1):
            if 'dgkrnsyybk' in line or '4po6882mz6' in line:
                print(f"📄 deploy-complete-system.py line {line_num}:")
                print(f"   {line.strip()}")
                
    except Exception as e:
        print(f"❌ Error reading deploy-complete-system.py: {e}")

def main():
    """Main debugging function"""
    print("🚨 COMPLETE NETWORK DEBUGGING")
    print("=" * 60)
    
    check_all_apis()
    check_frontend_config()
    check_conflicting_deployments()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("1. Check which API Gateway is actually working")
    print("2. Verify frontend is using the correct URL")
    print("3. Look for conflicting deployment scripts")
    print("4. Fix any mismatches found")

if __name__ == "__main__":
    main()
