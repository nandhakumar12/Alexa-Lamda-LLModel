#!/usr/bin/env python3
"""
Final verification that everything is working
"""

import requests
import time
import json

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 TESTING API ENDPOINTS")
    print("=" * 50)

    # Test the working API
    working_api = "https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod"

    endpoints_to_test = [
        ("/chatbot", "POST", {
            "message": "Hello! This is a final test.",
            "type": "text",
            "session_id": f"final-test-{int(time.time())}"
        }),
        ("/health", "GET", None),
        ("/auth", "POST", {
            "action": "validate",
            "token": "test-token"
        })
    ]

    for endpoint, method, payload in endpoints_to_test:
        url = f"{working_api}{endpoint}"
        print(f"\n🔍 Testing {method} {endpoint}")
        print(f"   URL: {url}")

        try:
            if method == "POST":
                response = requests.post(url, json=payload, timeout=10)
            else:
                response = requests.get(url, timeout=10)

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if endpoint == "/chatbot":
                        print(f"   ✅ Response: {data.get('response', 'No response')[:50]}...")
                        print(f"   ✅ Intent: {data.get('intent', 'No intent')}")
                    elif endpoint == "/health":
                        print(f"   ✅ Status: {data.get('overall_status', 'Unknown')}")
                    else:
                        print(f"   ✅ Success: {data.get('success', False)}")
                except:
                    print(f"   ✅ Response received (not JSON)")
            else:
                print(f"   ❌ Failed: {response.text[:100]}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_frontend_urls():
    """Test frontend URLs"""
    print("\n🌐 TESTING FRONTEND URLS")
    print("=" * 50)

    urls_to_test = [
        ("Direct S3", "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"),
        ("Cache-busted S3", "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com?cb=1756276428"),
        ("CloudFront", "https://nandhakumar-voice-assistant-prod3.website.us-east-1.amazonaws.com")
    ]

    for name, url in urls_to_test:
        print(f"\n🔍 Testing {name}")
        print(f"   URL: {url}")

        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                # Check if it contains the correct API URL
                content = response.text
                if '4po6882mz6' in content:
                    print(f"   ✅ Contains CORRECT API URL (4po6882mz6)")
                elif 'dgkrnsyybk' in content:
                    print(f"   ⚠️  Contains OLD API URL (dgkrnsyybk)")
                else:
                    print(f"   ❓ API URL not found in content")

                # Check for cache-busting
                if 'cache-bust' in content.lower() or 'cb=' in content:
                    print(f"   ✅ Cache-busting detected")
                else:
                    print(f"   ❓ No cache-busting found")

            else:
                print(f"   ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_end_to_end():
    """Test complete end-to-end flow"""
    print("\n🎯 END-TO-END TEST")
    print("=" * 50)

    # Simulate what the frontend should do
    api_url = "https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod"
    session_id = f"e2e-test-{int(time.time())}"

    test_messages = [
        "Hello, can you help me?",
        "What's the weather like?",
        "Tell me a joke"
    ]

    print(f"🤖 Simulating conversation with session: {session_id}")

    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Message {i}: {message}")

        try:
            response = requests.post(
                f"{api_url}/chatbot",
                json={
                    "message": message,
                    "type": "text",
                    "session_id": session_id
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'No response')
                intent = data.get('intent', 'No intent')

                print(f"   ✅ AI Response: {ai_response[:100]}...")
                print(f"   ✅ Intent: {intent}")
                print(f"   ✅ Session ID: {data.get('session_id', 'None')}")

                # Small delay between messages
                time.sleep(1)

            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
                break

        except Exception as e:
            print(f"   ❌ Error: {e}")
            break

def main():
    """Main verification function"""
    print("🚨 FINAL SYSTEM VERIFICATION")
    print("=" * 60)

    test_api_endpoints()
    test_frontend_urls()
    test_end_to_end()

    print("\n" + "=" * 60)
    print("🎉 VERIFICATION COMPLETE!")

    print(f"\n📋 SUMMARY:")
    print(f"   ✅ API Gateway 4po6882mz6 should be working")
    print(f"   ✅ Frontend should use correct API URL")
    print(f"   ✅ Direct S3 URL should work immediately")
    print(f"   ⏳ CloudFront may take 5-15 minutes for cache invalidation")

    print(f"\n🌐 RECOMMENDED URL TO USE:")
    print(f"   http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")

    print(f"\n💡 If you still see network errors:")
    print(f"   1. Clear browser cache completely (Ctrl+Shift+Delete)")
    print(f"   2. Use incognito/private browsing mode")
    print(f"   3. Use the Direct S3 URL above")
    print(f"   4. Wait for CloudFront cache invalidation to complete")

if __name__ == "__main__":
    main()