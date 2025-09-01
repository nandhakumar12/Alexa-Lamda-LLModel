#!/usr/bin/env python3
"""
Step 5: Deploy frontend to S3 and CloudFront
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def deploy_frontend():
    """Deploy frontend to S3 and CloudFront"""
    print("☁️ Deploying frontend to S3...")
    
    region = 'us-east-1'
    s3_client = boto3.client('s3', region_name=region)
    cloudfront_client = boto3.client('cloudfront', region_name=region)
    
    project_name = "nandhakumar-ai-assistant"
    bucket_name = f"{project_name}-frontend-{int(time.time())}"
    
    # Load configurations from previous steps
    try:
        with open('step3-config.json', 'r') as f:
            api_config = json.load(f)
        with open('step4-config.json', 'r') as f:
            cognito_config = json.load(f)
        print("✅ Loaded API and Cognito configurations")
    except Exception as e:
        print(f"❌ Error loading configurations: {e}")
        print("Please run previous steps first")
        return None
    
    # Create HTML content with proper configuration
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nandhakumar's AI Assistant</title>
    <script src="https://sdk.amazonaws.com/js/aws-sdk-2.1.24.min.js"></script>
    <script src="https://unpkg.com/amazon-cognito-identity-js@6.3.12/dist/amazon-cognito-identity.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 800px;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 5px;
        }}
        
        .status {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
        }}
        
        .auth-section {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}
        
        .auth-form {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .auth-form input {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        .auth-form button {{
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .auth-form button:hover {{
            background: #5a6fd8;
        }}
        
        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }}
        
        .messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .message {{
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }}
        
        .user-message {{
            background: #667eea;
            color: white;
            margin-left: auto;
        }}
        
        .bot-message {{
            background: white;
            border: 1px solid #e0e0e0;
        }}
        
        .input-section {{
            display: flex;
            gap: 10px;
        }}
        
        .input-section input {{
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
        }}
        
        .input-section button {{
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
        }}
        
        .input-section button:hover {{
            background: #5a6fd8;
        }}
        
        .footer {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }}
        
        .social-links {{
            margin-top: 10px;
        }}
        
        .social-links a {{
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .loading {{
            opacity: 0.7;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Nandhakumar's AI Assistant</h1>
            <p>Your Personal AI Companion</p>
            <div class="status" id="status">● Online</div>
        </div>
        
        <div class="auth-section" id="authSection">
            <div class="auth-form">
                <input type="email" id="email" placeholder="Email" value="nandhakumar@example.com">
                <input type="password" id="password" placeholder="Password" value="Nandhakumar123!">
                <button onclick="signIn()">Sign In</button>
                <button onclick="signUp()">Sign Up</button>
                <button onclick="signOut()" id="signOutBtn" class="hidden">Sign Out</button>
                <span id="userInfo" class="hidden"></span>
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer" class="hidden">
            <div class="messages" id="messages">
                <div class="message bot-message">
                    Hello! I'm your AI assistant. Please sign in to start chatting!
                </div>
            </div>
            
            <div class="input-section">
                <input type="text" id="messageInput" placeholder="Type your message here..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div class="footer">
            <div>Powered by Claude LLM • Production Grade • Session: prod_{int(time.time())}</div>
            <div class="social-links">
                <a href="https://github.com" target="_blank">GitHub</a>
                <a href="https://linkedin.com" target="_blank">LinkedIn</a>
                <a href="https://youtube.com" target="_blank">YouTube</a>
            </div>
        </div>
    </div>

    <script>
        // Configuration
        const CONFIG = {{
            API_URL: '{api_config["chat_endpoint"]}',
            COGNITO_USER_POOL_ID: '{cognito_config["user_pool_id"]}',
            COGNITO_CLIENT_ID: '{cognito_config["client_id"]}',
            COGNITO_REGION: '{cognito_config["region"]}'
        }};
        
        // Initialize Cognito
        const poolData = {{
            UserPoolId: CONFIG.COGNITO_USER_POOL_ID,
            ClientId: CONFIG.COGNITO_CLIENT_ID
        }};
        const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
        
        let currentUser = null;
        let userName = 'Nandhakumar';
        
        // Check if user is already signed in
        window.onload = function() {{
            checkAuthState();
        }};
        
        function checkAuthState() {{
            currentUser = userPool.getCurrentUser();
            if (currentUser) {{
                currentUser.getSession((err, session) => {{
                    if (err) {{
                        console.log('Session error:', err);
                        showAuthSection();
                        return;
                    }};
                    if (session.isValid()) {{
                        currentUser.getUserAttributes((err, attributes) => {{
                            if (!err && attributes) {{
                                const nameAttr = attributes.find(attr => attr.Name === 'name');
                                userName = nameAttr ? nameAttr.Value : 'Nandhakumar';
                            }}
                            showChatSection();
                            addBotMessage(`Welcome back, ${{userName}}! I'm your AI assistant. How can I help you today?`);
                        }});
                    }} else {{
                        showAuthSection();
                    }}
                }});
            }} else {{
                showAuthSection();
            }}
        }}
        
        function signIn() {{
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {{
                alert('Please enter email and password');
                return;
            }}
            
            const authenticationData = {{
                Username: email,
                Password: password
            }};
            
            const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
            const userData = {{
                Username: email,
                Pool: userPool
            }};
            
            const cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
            
            cognitoUser.authenticateUser(authenticationDetails, {{
                onSuccess: (result) => {{
                    currentUser = cognitoUser;
                    userName = 'Nandhakumar';
                    showChatSection();
                    addBotMessage(`Hello ${{userName}}! I'm your personal AI assistant. How can I help you today?`);
                }},
                onFailure: (err) => {{
                    alert('Sign in error: ' + err.message);
                }}
            }});
        }}
        
        function signOut() {{
            if (currentUser) {{
                currentUser.signOut();
                currentUser = null;
                userName = 'User';
                showAuthSection();
                document.getElementById('messages').innerHTML = '<div class="message bot-message">Hello! I\\'m your AI assistant. Please sign in to start chatting!</div>';
            }}
        }}
        
        function showAuthSection() {{
            document.getElementById('authSection').classList.remove('hidden');
            document.getElementById('chatContainer').classList.add('hidden');
            document.getElementById('signOutBtn').classList.add('hidden');
            document.getElementById('userInfo').classList.add('hidden');
        }}
        
        function showChatSection() {{
            document.getElementById('authSection').classList.add('hidden');
            document.getElementById('chatContainer').classList.remove('hidden');
            document.getElementById('signOutBtn').classList.remove('hidden');
            document.getElementById('userInfo').classList.remove('hidden');
            document.getElementById('userInfo').textContent = `Signed in as ${{userName}}`;
        }}
        
        async function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            if (!currentUser) {{
                alert('Please sign in first');
                return;
            }}
            
            // Add user message
            addUserMessage(message);
            input.value = '';
            
            // Show loading
            const container = document.querySelector('.container');
            container.classList.add('loading');
            
            try {{
                const response = await fetch(CONFIG.API_URL, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        message: message,
                        userName: userName
                    }})
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    addBotMessage(data.response);
                }} else {{
                    addBotMessage('Sorry, I encountered an error. Please try again.');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                addBotMessage('Sorry, I\\'m having trouble connecting. Please try again.');
            }} finally {{
                container.classList.remove('loading');
            }}
        }}
        
        function addUserMessage(message) {{
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user-message';
            messageDiv.textContent = message;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        function addBotMessage(message) {{
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            messageDiv.textContent = message;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
    </script>
</body>
</html>'''
    
    try:
        # Create S3 bucket
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        print(f"✅ S3 bucket created: {bucket_name}")
        
        # Configure bucket for static website hosting
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}
            }
        )
        
        # Set bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        # Upload HTML file
        s3_client.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=html_content,
            ContentType='text/html'
        )
        
        website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
        print(f"✅ Website deployed to S3: {website_url}")
        
        # Save final configuration
        final_config = {
            'bucket_name': bucket_name,
            'website_url': website_url,
            'api_config': api_config,
            'cognito_config': cognito_config,
            'project_name': project_name
        }
        
        with open('deployment-config.json', 'w') as f:
            json.dump(final_config, f, indent=2)
        
        print("💾 Final configuration saved to deployment-config.json")
        return final_config
        
    except Exception as e:
        print(f"❌ Error deploying frontend: {e}")
        return None

if __name__ == "__main__":
    try:
        print("🚀 Step 5: Deploy Frontend")
        print("=" * 50)
        
        config = deploy_frontend()
        
        if config:
            print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉")
            print("=" * 60)
            print(f"🌐 Website URL: {config['website_url']}")
            print(f"🔗 API Endpoint: {config['api_config']['chat_endpoint']}")
            print(f"👤 Test Login: {config['cognito_config']['test_user']['email']}")
            print(f"🔑 Test Password: {config['cognito_config']['test_user']['password']}")
            print("\n📋 NEXT STEPS:")
            print("1. Visit the website URL above")
            print("2. Sign in with the test credentials")
            print("3. Start chatting with your AI assistant!")
            print("4. Update Lambda environment variable CLAUDE_API_KEY for full Claude integration")
        else:
            print("\n❌ Step 5 failed!")
            
    except Exception as e:
        print(f"\n❌ Error in Step 5: {e}")
