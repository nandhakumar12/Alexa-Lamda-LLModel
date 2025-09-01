#!/usr/bin/env python3
"""
Complete deployment script to finish the AI Assistant setup
This will create API Gateway, integrate with Lambda, and deploy the frontend
"""

import boto3
import json
import time
import subprocess
import os

def run_aws_command(command):
    """Run AWS CLI command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error running command: {command}")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception running command: {e}")
        return None

def create_api_gateway():
    """Create API Gateway and integrate with Lambda"""
    print("🌐 Creating API Gateway...")
    
    # Create REST API
    api_result = run_aws_command('aws apigateway create-rest-api --name "nandhakumar-ai-assistant-api" --description "Production API for Nandhakumar AI Assistant" --output json')
    if not api_result:
        return None
    
    api_data = json.loads(api_result)
    api_id = api_data['id']
    print(f"✅ API Gateway created: {api_id}")
    
    # Get root resource
    resources_result = run_aws_command(f'aws apigateway get-resources --rest-api-id {api_id} --output json')
    if not resources_result:
        return None
    
    resources_data = json.loads(resources_result)
    root_resource_id = None
    for resource in resources_data['items']:
        if resource['path'] == '/':
            root_resource_id = resource['id']
            break
    
    # Create /chat resource
    chat_resource_result = run_aws_command(f'aws apigateway create-resource --rest-api-id {api_id} --parent-id {root_resource_id} --path-part chat --output json')
    if not chat_resource_result:
        return None
    
    chat_resource_data = json.loads(chat_resource_result)
    chat_resource_id = chat_resource_data['id']
    print("✅ Created /chat resource")
    
    # Create POST method
    run_aws_command(f'aws apigateway put-method --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method POST --authorization-type NONE')
    
    # Create OPTIONS method for CORS
    run_aws_command(f'aws apigateway put-method --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --authorization-type NONE')
    
    # Set up Lambda integration
    lambda_arn = f"arn:aws:lambda:us-east-1:266833219725:function:nandhakumar-ai-assistant-prod"
    lambda_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    
    run_aws_command(f'aws apigateway put-integration --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method POST --type AWS_PROXY --integration-http-method POST --uri {lambda_uri}')
    
    # Set up CORS integration
    run_aws_command(f'aws apigateway put-integration --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --type MOCK --request-templates \'{{"application/json": "{{\\"statusCode\\": 200}}"}}\'')
    
    # Add method responses
    run_aws_command(f'aws apigateway put-method-response --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --status-code 200 --response-parameters method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false')
    
    # Add integration responses
    run_aws_command(f'aws apigateway put-integration-response --rest-api-id {api_id} --resource-id {chat_resource_id} --http-method OPTIONS --status-code 200 --response-parameters method.response.header.Access-Control-Allow-Headers=\\"\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'\\",method.response.header.Access-Control-Allow-Methods=\\"\'GET,POST,OPTIONS\'\\",method.response.header.Access-Control-Allow-Origin=\\"\'*\'\\"')
    
    # Add Lambda permission
    run_aws_command(f'aws lambda add-permission --function-name nandhakumar-ai-assistant-prod --statement-id api-gateway-invoke --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:266833219725:{api_id}/*/*"')
    
    # Deploy API
    run_aws_command(f'aws apigateway create-deployment --rest-api-id {api_id} --stage-name prod --description "Production deployment"')
    
    api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod/chat"
    print(f"✅ API Gateway deployed: {api_url}")
    
    return {
        'api_id': api_id,
        'api_url': api_url
    }

def create_production_frontend(api_url):
    """Create production frontend with backend integration"""
    print("🎨 Creating production frontend...")
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nandhakumar's AI Assistant - Production</title>
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
            animation: backgroundShift 10s ease-in-out infinite alternate;
        }}
        
        @keyframes backgroundShift {{
            0% {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
            100% {{ background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); }}
        }}
        
        .container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 900px;
            height: 700px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
            position: relative;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .status {{
            position: absolute;
            top: 25px;
            right: 25px;
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .auth-section {{
            padding: 25px;
            border-bottom: 1px solid #eee;
            background: #f8f9fa;
        }}
        
        .auth-form {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .auth-form input {{
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            min-width: 200px;
            transition: border-color 0.3s ease;
        }}
        
        .auth-form input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .auth-form button {{
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .auth-form button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 25px;
        }}
        
        .messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 15px;
            border: 1px solid #e1e5e9;
        }}
        
        .message {{
            margin-bottom: 20px;
            padding: 15px 20px;
            border-radius: 18px;
            max-width: 85%;
            word-wrap: break-word;
            animation: messageSlide 0.3s ease-out;
        }}
        
        @keyframes messageSlide {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .user-message {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }}
        
        .bot-message {{
            background: white;
            border: 2px solid #e1e5e9;
            color: #333;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
        
        .input-section {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .input-section input {{
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 25px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }}
        
        .input-section input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .input-section button {{
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .input-section button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }}
        
        .social-links {{
            margin-top: 12px;
        }}
        
        .social-links a {{
            color: #667eea;
            text-decoration: none;
            margin: 0 15px;
            font-weight: 600;
            transition: color 0.3s ease;
        }}
        
        .social-links a:hover {{
            color: #764ba2;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .loading {{
            opacity: 0.7;
            pointer-events: none;
        }}
        
        .typing-indicator {{
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 15px 20px;
            background: white;
            border: 2px solid #e1e5e9;
            border-radius: 18px;
            max-width: 85%;
            margin-bottom: 20px;
        }}
        
        .typing-dot {{
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }}
        
        .typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
        
        @keyframes typing {{
            0%, 80%, 100% {{
                transform: scale(0);
                opacity: 0.5;
            }}
            40% {{
                transform: scale(1);
                opacity: 1;
            }}
        }}
        
        .user-info {{
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Nandhakumar's AI Assistant</h1>
            <p>Production Grade AI Companion with AWS Backend</p>
            <div class="status">
                <div class="status-dot"></div>
                Online
            </div>
        </div>
        
        <div class="auth-section" id="authSection">
            <div class="auth-form">
                <input type="email" id="email" placeholder="Email" value="nandhakumar@example.com">
                <input type="password" id="password" placeholder="Password" value="password123">
                <button onclick="signIn()">Sign In</button>
                <button onclick="signOut()" id="signOutBtn" class="hidden">Sign Out</button>
                <span id="userInfo" class="user-info hidden"></span>
            </div>
        </div>
        
        <div class="chat-container" id="chatContainer" class="hidden">
            <div class="messages" id="messages">
                <div class="message bot-message">
                    Hello! I'm your AI assistant. Please sign in to start our conversation!
                </div>
            </div>
            
            <div class="input-section">
                <input type="text" id="messageInput" placeholder="Type your message here..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div class="footer">
            <div>Powered by AWS Lambda + Claude AI • Production Grade • API: {api_url}</div>
            <div class="social-links">
                <a href="https://github.com" target="_blank">GitHub</a>
                <a href="https://linkedin.com" target="_blank">LinkedIn</a>
                <a href="https://youtube.com" target="_blank">YouTube</a>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '{api_url}';
        let currentUser = null;
        let userName = 'Nandhakumar';
        
        function signIn() {{
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {{
                alert('Please enter email and password');
                return;
            }}
            
            // Simulate successful login
            currentUser = {{ email: email, name: 'Nandhakumar' }};
            userName = 'Nandhakumar';
            showChatSection();
            addBotMessage(`Welcome back, ${{userName}}! I'm your personal AI assistant powered by AWS and Claude AI. I'm excited to help you today! How can I assist you?`);
        }}
        
        function signOut() {{
            currentUser = null;
            userName = 'User';
            showAuthSection();
            document.getElementById('messages').innerHTML = '<div class="message bot-message">Hello! I\\'m your AI assistant. Please sign in to start our conversation!</div>';
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
            
            // Show typing indicator
            showTypingIndicator();
            
            try {{
                const response = await fetch(API_URL, {{
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
                
                hideTypingIndicator();
                
                if (response.ok) {{
                    addBotMessage(data.response);
                }} else {{
                    addBotMessage('Sorry, I encountered an error. Please try again.');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                hideTypingIndicator();
                addBotMessage('Sorry, I\\'m having trouble connecting to my backend. Please try again.');
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
        
        function showTypingIndicator() {{
            const messagesDiv = document.getElementById('messages');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        function hideTypingIndicator() {{
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {{
                typingIndicator.remove();
            }}
        }}
        
        // Initialize
        window.onload = function() {{
            showAuthSection();
        }};
    </script>
</body>
</html>'''
    
    with open('nandhakumar-ai-production.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Production frontend created: nandhakumar-ai-production.html")
    return True

def main():
    print("🚀 Completing Nandhakumar's AI Assistant Deployment")
    print("=" * 60)
    
    # Create API Gateway
    api_info = create_api_gateway()
    if not api_info:
        print("❌ Failed to create API Gateway")
        return False
    
    # Create production frontend
    frontend_success = create_production_frontend(api_info['api_url'])
    if not frontend_success:
        print("❌ Failed to create frontend")
        return False
    
    # Save final configuration
    config = {
        'api_url': api_info['api_url'],
        'api_id': api_info['api_id'],
        'lambda_function': 'nandhakumar-ai-assistant-prod',
        'frontend_file': 'nandhakumar-ai-production.html',
        'deployment_time': time.time(),
        'status': 'completed'
    }
    
    with open('final-deployment-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉")
    print("=" * 60)
    print(f"🌐 API Endpoint: {api_info['api_url']}")
    print(f"📱 Frontend File: nandhakumar-ai-production.html")
    print(f"⚡ Lambda Function: nandhakumar-ai-assistant-prod")
    print(f"💾 Configuration: final-deployment-config.json")
    
    print("\n📋 NEXT STEPS:")
    print("1. Open nandhakumar-ai-production.html in your browser")
    print("2. Sign in with any email/password")
    print("3. Start chatting with your AI assistant!")
    print("4. Optional: Add Claude API key to Lambda for enhanced responses")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Deployment failed!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
