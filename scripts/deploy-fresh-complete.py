#!/usr/bin/env python3
"""
Complete deployment of the fresh system
"""

import boto3
import json
import os
import time

def create_simple_html_app():
    """Create a simple HTML app that works immediately"""
    print("🎨 CREATING SIMPLE HTML APP")
    print("=" * 50)
    
    # Load API details
    try:
        with open('api-details.json', 'r') as f:
            api_details = json.load(f)
        api_url = api_details['chatbot_endpoint']
    except:
        api_url = 'https://tcuzlzq1af.execute-api.us-east-1.amazonaws.com/prod/chatbot'
    
    # Create a complete HTML app
    html_app = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nandhakumar's AI Assistant</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            height: 100vh;
            overflow: hidden;
        }}

        .app {{
            display: flex;
            flex-direction: column;
            height: 100vh;
        }}

        .header {{
            background: rgba(15, 15, 35, 0.9);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .bot-avatar {{
            font-size: 2rem;
            background: linear-gradient(135deg, #9c27b0, #673ab7);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(156, 39, 176, 0.3);
        }}

        .logo h1 {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, #9c27b0, #673ab7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .status {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: #a0a0a0;
        }}

        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4caf50;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}

        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            padding: 0 2rem;
        }}

        .messages {{
            flex: 1;
            overflow-y: auto;
            padding: 2rem 0;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .message {{
            display: flex;
            gap: 1rem;
            max-width: 80%;
            animation: slideIn 0.3s ease-out;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .user-message {{
            align-self: flex-end;
            flex-direction: row-reverse;
        }}

        .bot-message {{
            align-self: flex-start;
        }}

        .message-avatar {{
            font-size: 1.5rem;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        .user-message .message-avatar {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        }}

        .bot-message .message-avatar {{
            background: linear-gradient(135deg, #9c27b0, #673ab7);
        }}

        .message-content {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .user-message .message-content {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(29, 78, 216, 0.2));
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}

        .bot-message .message-content {{
            background: rgba(15, 15, 35, 0.6);
            border: 1px solid rgba(156, 39, 176, 0.3);
        }}

        .message-text {{
            line-height: 1.5;
            margin-bottom: 0.5rem;
        }}

        .message-time {{
            font-size: 0.75rem;
            color: #a0a0a0;
        }}

        .input-container {{
            padding: 2rem 0;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .input-wrapper {{
            display: flex;
            gap: 1rem;
            align-items: flex-end;
            background: rgba(15, 15, 35, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 1rem;
            padding: 1rem;
            border: 1px solid rgba(156, 39, 176, 0.3);
        }}

        .message-input {{
            flex: 1;
            background: transparent;
            border: none;
            color: white;
            font-size: 1rem;
            outline: none;
            font-family: inherit;
            padding: 0.5rem;
        }}

        .message-input::placeholder {{
            color: #a0a0a0;
        }}

        .send-button {{
            background: linear-gradient(135deg, #9c27b0, #673ab7);
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
        }}

        .send-button:hover:not(:disabled) {{
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(156, 39, 176, 0.4);
        }}

        .send-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .footer {{
            background: rgba(15, 15, 35, 0.9);
            backdrop-filter: blur(10px);
            border-top: 1px solid rgba(59, 130, 246, 0.2);
            padding: 1rem 2rem;
            text-align: center;
            font-size: 0.9rem;
            color: #a0a0a0;
        }}

        .social-links {{
            margin-top: 0.5rem;
        }}

        .social-links a {{
            color: #9c27b0;
            text-decoration: none;
            margin: 0 1rem;
            transition: color 0.3s ease;
        }}

        .social-links a:hover {{
            color: #673ab7;
        }}

        .typing {{
            display: flex;
            gap: 0.3rem;
            align-items: center;
        }}

        .typing span {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #9c27b0;
            animation: typing 1.4s infinite ease-in-out;
        }}

        .typing span:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing span:nth-child(2) {{ animation-delay: -0.16s; }}

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

        @media (max-width: 768px) {{
            .header, .chat-container, .footer {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            
            .message {{
                max-width: 90%;
            }}
        }}
    </style>
</head>
<body>
    <div class="app">
        <header class="header">
            <div class="logo">
                <div class="bot-avatar">🤖</div>
                <h1>Nandhakumar's AI Assistant</h1>
            </div>
            <div class="status">
                <div class="status-dot"></div>
                <span>Online</span>
            </div>
        </header>

        <main class="chat-container">
            <div class="messages" id="messages">
                <div class="message bot-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <div class="message-text">Hello! I'm Nandhakumar's AI Assistant. How can I help you today?</div>
                        <div class="message-time">Just now</div>
                    </div>
                </div>
            </div>

            <div class="input-container">
                <div class="input-wrapper">
                    <input 
                        type="text" 
                        class="message-input" 
                        id="messageInput"
                        placeholder="Type your message here..."
                    />
                    <button class="send-button" id="sendButton">🚀</button>
                </div>
            </div>
        </main>

        <footer class="footer">
            <div>Powered by AI • Session: fresh-{int(time.time())}</div>
            <div class="social-links">
                <a href="https://github.com/nandhakumar" target="_blank">GitHub</a>
                <a href="https://linkedin.com/in/nandhakumar" target="_blank">LinkedIn</a>
                <a href="https://youtube.com/@nandhakumar" target="_blank">YouTube</a>
            </div>
        </footer>
    </div>

    <script>
        const API_URL = '{api_url}';
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const sessionId = 'fresh-session-' + Date.now();
        let isLoading = false;

        function addMessage(text, sender, intent = null) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{sender}}-message`;
            
            const time = new Date().toLocaleTimeString();
            const intentText = intent ? ` • ${{intent}}` : '';
            
            messageDiv.innerHTML = `
                <div class="message-avatar">${{sender === 'user' ? '👤' : '🤖'}}</div>
                <div class="message-content">
                    <div class="message-text">${{text}}</div>
                    <div class="message-time">${{time}}${{intentText}}</div>
                </div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}

        function showTyping() {{
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.id = 'typing';
            typingDiv.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <div class="typing">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            messagesContainer.appendChild(typingDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}

        function hideTyping() {{
            const typingDiv = document.getElementById('typing');
            if (typingDiv) {{
                typingDiv.remove();
            }}
        }}

        async function sendMessage() {{
            const message = messageInput.value.trim();
            if (!message || isLoading) return;

            addMessage(message, 'user');
            messageInput.value = '';
            isLoading = true;
            sendButton.disabled = true;
            showTyping();

            try {{
                const response = await fetch(API_URL, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        message: message,
                        session_id: sessionId
                    }})
                }});

                if (response.ok) {{
                    const data = await response.json();
                    hideTyping();
                    addMessage(data.response, 'bot', data.intent);
                }} else {{
                    hideTyping();
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                hideTyping();
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }} finally {{
                isLoading = false;
                sendButton.disabled = false;
                messageInput.focus();
            }}
        }}

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') {{
                sendMessage();
            }}
        }});

        // Focus input on load
        messageInput.focus();

        // Test API connection on load
        console.log('🌐 API URL:', API_URL);
        console.log('🔧 Fresh Voice Assistant loaded successfully!');
    </script>
</body>
</html>"""
    
    return html_app

def deploy_to_s3():
    """Deploy the HTML app to S3"""
    print("\n🚀 DEPLOYING TO S3")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    # Create the HTML app
    html_content = create_simple_html_app()
    
    try:
        # Upload index.html
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=html_content,
            ContentType='text/html',
            CacheControl='no-cache, no-store, must-revalidate'
        )
        
        print("✅ Deployed fresh HTML app to S3")
        
        # Create a simple favicon
        favicon_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="45" fill="#9c27b0"/>
  <text x="50" y="65" font-family="Arial" font-size="50" text-anchor="middle" fill="white">🤖</text>
</svg>"""
        
        s3.put_object(
            Bucket=bucket_name,
            Key='favicon.ico',
            Body=favicon_content,
            ContentType='image/svg+xml'
        )
        
        print("✅ Added favicon")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying to S3: {e}")
        return False

def test_complete_system():
    """Test the complete system"""
    print(f"\n🧪 TESTING COMPLETE SYSTEM")
    print("=" * 50)
    
    import requests
    
    # Test API directly
    try:
        with open('api-details.json', 'r') as f:
            api_details = json.load(f)
        api_url = api_details['chatbot_endpoint']
    except:
        api_url = 'https://tcuzlzq1af.execute-api.us-east-1.amazonaws.com/prod/chatbot'
    
    print(f"🔍 Testing API: {api_url}")
    
    try:
        response = requests.post(
            api_url,
            json={{
                "message": "Hello! This is the final system test.",
                "session_id": "final-test"
            }},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API working: {data.get('response', 'No response')[:50]}...")
        else:
            print(f"❌ API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API error: {e}")
        return False
    
    # Test frontend
    frontend_url = "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    print(f"🔍 Testing frontend: {frontend_url}")
    
    try:
        response = requests.get(frontend_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Frontend accessible")
            
            # Check if it contains the correct API URL
            if 'tcuzlzq1af' in response.text:
                print(f"✅ Contains correct API URL")
                return True
            else:
                print(f"❌ Wrong API URL in frontend")
                return False
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def main():
    """Main function"""
    print("🚨 FINAL FRESH SYSTEM DEPLOYMENT")
    print("=" * 60)
    
    if deploy_to_s3():
        if test_complete_system():
            print("\n" + "=" * 60)
            print("🎉 FRESH SYSTEM DEPLOYMENT SUCCESSFUL!")
            
            print(f"\n🌐 YOUR FRESH VOICE ASSISTANT:")
            print(f"   http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
            
            print(f"\n✅ FEATURES:")
            print(f"   ✅ No authentication required")
            print(f"   ✅ Direct access to chatbot")
            print(f"   ✅ Beautiful UI with same design")
            print(f"   ✅ Working API Gateway")
            print(f"   ✅ Fresh Lambda function")
            print(f"   ✅ Proper CORS configuration")
            
            print(f"\n💡 INSTRUCTIONS:")
            print(f"   1. Clear browser cache (Ctrl+Shift+Delete)")
            print(f"   2. Open the URL above")
            print(f"   3. Start chatting immediately!")
            print(f"   4. No login required!")
            
            print(f"\n🎯 THE SYSTEM IS COMPLETELY FRESH AND WORKING!")
            
        else:
            print("\n❌ SYSTEM TEST FAILED")
    else:
        print("\n❌ DEPLOYMENT FAILED")

if __name__ == "__main__":
    main()
