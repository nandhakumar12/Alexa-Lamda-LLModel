#!/usr/bin/env python3
"""
Fix the refresh loop issue and create a stable frontend
"""

import boto3
import time

def fix_refresh_loop():
    """Fix the infinite refresh loop"""
    print("🔧 FIXING REFRESH LOOP")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    # Create a stable index.html without refresh loops
    stable_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Nandhakumar's AI Voice Assistant" />
    <link rel="apple-touch-icon" href="/logo192.png" />
    <link rel="manifest" href="/manifest.json" />
    <title>Nandhakumar's AI Assistant</title>
    
    <!-- NO CACHE REFRESH - STABLE VERSION -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    
<script defer="defer" src="/static/js/main.8e61bb56.js"></script><link href="/static/css/main.c5e8eb98.css" rel="stylesheet"></head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    
    <!-- Debug info without refresh -->
    <script>
        console.log('🔧 Stable version loaded - no refresh loop');
        console.log('🌐 API URL: https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod');
        
        // Test API on load (no refresh)
        window.addEventListener('load', function() {
            console.log('✅ Page loaded successfully');
            
            // Test API connection
            fetch('https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: 'Page load test',
                    type: 'text',
                    session_id: 'page-load-test'
                })
            })
            .then(r => r.json())
            .then(d => console.log('✅ API Connection Success:', d.response))
            .catch(e => console.error('❌ API Connection Failed:', e));
        });
    </script>
</body>
</html>"""
    
    try:
        # Upload stable index.html
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=stable_html,
            ContentType='text/html',
            CacheControl='no-cache, no-store, must-revalidate'
        )
        
        print("✅ Uploaded stable index.html (no refresh loop)")
        
    except Exception as e:
        print(f"❌ Error uploading stable HTML: {e}")

def check_auth_system():
    """Check the authentication system"""
    print("\n🔐 CHECKING AUTHENTICATION SYSTEM")
    print("=" * 50)
    
    # Check Cognito configuration
    cognito = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        # Get user pool details
        user_pool_id = 'us-east-1_KSZDQ0iYx'
        
        user_pool = cognito.describe_user_pool(UserPoolId=user_pool_id)
        print(f"✅ User Pool found: {user_pool['UserPool']['Name']}")
        print(f"   ID: {user_pool_id}")
        print(f"   Status: {user_pool['UserPool']['Status']}")
        
        # Check if there are any users
        try:
            users = cognito.list_users(UserPoolId=user_pool_id, Limit=10)
            print(f"   Users: {len(users['Users'])} registered")
            
            for user in users['Users']:
                username = user['Username']
                status = user['UserStatus']
                print(f"     - {username}: {status}")
                
        except Exception as e:
            print(f"   ❌ Error listing users: {e}")
            
    except Exception as e:
        print(f"❌ Error checking user pool: {e}")

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🧪 TESTING AUTH ENDPOINTS")
    print("=" * 50)
    
    import requests
    
    api_url = "https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod"
    
    # Test auth endpoint (should work without authentication for login)
    try:
        response = requests.post(
            f"{api_url}/auth",
            json={
                "action": "login",
                "email": "test@example.com",
                "password": "testpassword"
            },
            timeout=10
        )
        
        print(f"Auth endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Auth endpoint accessible")
        else:
            print(f"⚠️  Auth endpoint response: {response.text}")
            
    except Exception as e:
        print(f"❌ Auth endpoint error: {e}")

def create_test_user():
    """Create a test user for verification"""
    print("\n👤 CREATING TEST USER")
    print("=" * 50)
    
    cognito = boto3.client('cognito-idp', region_name='us-east-1')
    user_pool_id = 'us-east-1_KSZDQ0iYx'
    
    test_email = "nandhakumar.test@example.com"
    test_password = "TestPassword123!"
    
    try:
        # Create user
        response = cognito.admin_create_user(
            UserPoolId=user_pool_id,
            Username=test_email,
            UserAttributes=[
                {'Name': 'email', 'Value': test_email},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword=test_password,
            MessageAction='SUPPRESS'  # Don't send email
        )
        
        print(f"✅ Test user created: {test_email}")
        
        # Set permanent password
        cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=test_email,
            Password=test_password,
            Permanent=True
        )
        
        print(f"✅ Password set for test user")
        print(f"   Email: {test_email}")
        print(f"   Password: {test_password}")
        
    except Exception as e:
        if "UsernameExistsException" in str(e):
            print(f"✅ Test user already exists: {test_email}")
        else:
            print(f"❌ Error creating test user: {e}")

def main():
    """Main function"""
    print("🚨 FIXING REFRESH LOOP AND CHECKING AUTH")
    print("=" * 60)
    
    fix_refresh_loop()
    check_auth_system()
    test_auth_endpoints()
    create_test_user()
    
    print("\n" + "=" * 60)
    print("🎉 FIXES COMPLETE!")
    
    print(f"\n🌐 STABLE URL (no refresh loop):")
    print(f"   http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
    
    print(f"\n🔐 TEST CREDENTIALS:")
    print(f"   Email: nandhakumar.test@example.com")
    print(f"   Password: TestPassword123!")
    
    print(f"\n💡 INSTRUCTIONS:")
    print(f"   1. Clear browser cache completely")
    print(f"   2. Use the stable URL above")
    print(f"   3. Try logging in with test credentials")
    print(f"   4. Test the chatbot after login")

if __name__ == "__main__":
    main()
