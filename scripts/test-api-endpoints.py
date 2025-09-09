#!/usr/bin/env python3
"""
Test Voice Assistant AI API Endpoints
This script tests all the deployed API endpoints
"""

import requests
import json
import time
import os
from typing import Dict, Any, List, Optional

try:
    import boto3  # type: ignore
    from botocore.exceptions import BotoCoreError, ClientError  # type: ignore
except Exception:  # boto3 may not be installed in some environments
    boto3 = None
    BotoCoreError = ClientError = Exception

# API Configuration
API_BASE_URL = "https://7orgj957oe.execute-api.us-east-1.amazonaws.com/v1"
LLM_API_URL = "https://ga551kmg0f.execute-api.us-east-1.amazonaws.com/prod/chat"

# Optional Cognito configuration (populate via environment variables for convenience)
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "")
COGNITO_USERNAME = os.getenv("COGNITO_USERNAME", "")
COGNITO_PASSWORD = os.getenv("COGNITO_PASSWORD", "")

class APITester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'VoiceAssistantAI-Tester/1.0'
        })
        self.id_token: Optional[str] = None
        self._maybe_fetch_cognito_token()

    def _maybe_fetch_cognito_token(self) -> None:
        """Fetch id_token from Cognito using USER_PASSWORD_AUTH if config is present."""
        if not (COGNITO_CLIENT_ID and COGNITO_USERNAME and COGNITO_PASSWORD):
            return
        if boto3 is None:
            print("⚠️ boto3 not available; skipping Cognito token fetch.")
            return
        try:
            client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
            resp = client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": COGNITO_USERNAME,
                    "PASSWORD": COGNITO_PASSWORD,
                },
            )
            auth_result = resp.get("AuthenticationResult", {})
            token = auth_result.get("IdToken")
            if token:
                self.id_token = token
                print("🔑 Acquired Cognito id_token for /chatbot tests.")
        except (BotoCoreError, ClientError) as e:
            print(f"⚠️ Cognito auth failed: {e}")
    
    def test_endpoint(self, name: str, method: str, url: str, data: Dict = None, expected_status: int = 200, headers: Optional[Dict[str, str]] = None) -> bool:
        """Test a single API endpoint"""
        print(f"🧪 Testing {name}...")
        
        try:
            if method.upper() == 'GET':
                if headers:
                    response = self.session.get(url, headers=headers, timeout=30)
                else:
                    response = self.session.get(url, timeout=30)
            elif method.upper() == 'POST':
                if headers:
                    response = self.session.post(url, json=data, headers=headers, timeout=30)
                else:
                    response = self.session.post(url, json=data, timeout=30)
            else:
                print(f"❌ Unsupported method: {method}")
                return False
            
            success = response.status_code == expected_status
            
            if success:
                print(f"✅ {name}: {response.status_code} - {response.reason}")
                if response.text:
                    try:
                        json_response = response.json()
                        print(f"   Response: {json.dumps(json_response, indent=2)[:200]}...")
                    except:
                        print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ {name}: {response.status_code} - {response.reason}")
                print(f"   Error: {response.text[:200]}...")
            
            self.results.append({
                'name': name,
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'success': success,
                'response_time': response.elapsed.total_seconds()
            })
            
            return success
            
        except requests.exceptions.Timeout:
            print(f"⏰ {name}: Timeout")
            self.results.append({
                'name': name,
                'method': method,
                'url': url,
                'status_code': 'TIMEOUT',
                'success': False,
                'response_time': 30.0
            })
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: {str(e)}")
            self.results.append({
                'name': name,
                'method': method,
                'url': url,
                'status_code': 'ERROR',
                'success': False,
                'response_time': 0.0
            })
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test health check endpoint"""
        return self.test_endpoint(
            "Health Check",
            "GET",
            f"{API_BASE_URL}/health",
            expected_status=200
        )
    
    def test_auth_endpoint(self) -> bool:
        """Test authentication endpoint"""
        auth_data = {
            "action": "register",
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        return self.test_endpoint(
            "Authentication",
            "POST",
            f"{API_BASE_URL}/auth",
            data=auth_data,
            expected_status=200
        )
    
    def test_chatbot_endpoint(self) -> bool:
        """Test chatbot endpoint"""
        chatbot_data = {
            "message": "Hello, how are you?",
            "type": "text",
            "session_id": "test-session-123"
        }
        headers = None
        if self.id_token:
            headers = {"Authorization": f"Bearer {self.id_token}"}
        return self.test_endpoint(
            "Chatbot",
            "POST",
            f"{API_BASE_URL}/chatbot",
            data=chatbot_data,
            headers=headers,
            expected_status=200
        )
    
    def test_llm_endpoint(self) -> bool:
        """Test LLM endpoint"""
        llm_data = {
            "message": "Hello, this is a test message",
            "user_name": "TestUser"
        }
        return self.test_endpoint(
            "LLM Chat",
            "POST",
            LLM_API_URL,
            data=llm_data,
            expected_status=200
        )
    
    def test_cors_headers(self) -> bool:
        """Test CORS headers"""
        print("🧪 Testing CORS Headers...")
        
        try:
            # Test OPTIONS request
            response = self.session.options(f"{API_BASE_URL}/health", timeout=10)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                print("✅ CORS Headers: Present")
                print(f"   Origin: {cors_headers['Access-Control-Allow-Origin']}")
                print(f"   Methods: {cors_headers['Access-Control-Allow-Methods']}")
                print(f"   Headers: {cors_headers['Access-Control-Allow-Headers']}")
                return True
            else:
                print("❌ CORS Headers: Missing")
                return False
                
        except Exception as e:
            print(f"❌ CORS Test: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests"""
        print("🚀 Starting Voice Assistant AI API Tests")
        print("=" * 50)
        
        # Test all endpoints
        tests = [
            self.test_health_endpoint,
            self.test_auth_endpoint,
            self.test_chatbot_endpoint,
            self.test_llm_endpoint,
            self.test_cors_headers
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Small delay between tests
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['name']}: {result['status_code']} ({result['response_time']:.2f}s)")
        
        return {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': (passed/total)*100,
            'results': self.results
        }

def main():
    """Main function"""
    tester = APITester()
    results = tester.run_all_tests()
    
    if results['success_rate'] >= 80:
        print("\n🎉 API Tests: PASSED! Your Voice Assistant AI is ready!")
    else:
        print("\n⚠️  API Tests: Some issues detected. Check the logs above.")
    
    return results

if __name__ == "__main__":
    main()
