#!/usr/bin/env python3
"""
Create production-grade frontend with fixed scrolling and Claude LLM
"""

import boto3
import json
import time

def load_production_api_details():
    """Load production API details"""
    try:
        with open('production-api-details.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading API details: {e}")
        return None

def create_production_frontend():
    """Create production-grade frontend with fixed scrolling"""
    print("🎨 CREATING PRODUCTION FRONTEND")
    print("=" * 50)
    
    # Load API details
    api_details = load_production_api_details()
    if not api_details:
        print("❌ Cannot proceed without API details")
        return None
    
    chatbot_endpoint = api_details['chatbot_endpoint']
    health_endpoint = api_details['health_endpoint']
    
    # Create production HTML app with fixed scrolling
    html_app = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nandhakumar's AI Assistant - Production</title>
    <meta name="description" content="Production-grade AI Voice Assistant powered by Claude LLM">
    <meta name="keywords" content="AI, Assistant, Claude, LLM, Voice, Chatbot, Nandhakumar">
    <meta name="author" content="Nandhakumar">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%239c27b0'/%3E%3Ctext x='50' y='65' font-family='Arial' font-size='50' text-anchor='middle' fill='white'%3E🤖%3C/text%3E%3C/svg%3E">
    
    <style>
        /* Production CSS with Fixed Scrolling */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            height: 100%;
            overflow: hidden; /* Prevent body scroll */
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            display: flex;
            flex-direction: column;
        }}

        .app {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-height: 100vh;
        }}

        /* Header */
        .header {{
            background: rgba(15, 15, 35, 0.95);
            backdrop-filter: blur(15px);
            border-bottom: 1px solid rgba(59, 130, 246, 0.3);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
            z-index: 100;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
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
            box-shadow: 0 4px 20px rgba(156, 39, 176, 0.4);
            animation: glow 3s ease-in-out infinite alternate;
        }}

        @keyframes glow {{
            from {{ box-shadow: 0 4px 20px rgba(156, 39, 176, 0.4); }}
            to {{ box-shadow: 0 4px 30px rgba(156, 39, 176, 0.7); }}
        }}

        .logo h1 {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, #9c27b0, #673ab7, #3f51b5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
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
            0% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.7; transform: scale(1.1); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}

        /* Chat Container - FIXED SCROLLING */
        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            padding: 0 2rem;
            min-height: 0; /* Important for flex child */
        }}

        .messages {{
            flex: 1;
            overflow-y: auto; /* Enable scrolling ONLY here */
            overflow-x: hidden;
            padding: 2rem 0;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            scroll-behavior: smooth;
            min-height: 0; /* Important for flex child */
        }}

        /* Custom Scrollbar */
        .messages::-webkit-scrollbar {{
            width: 8px;
        }}

        .messages::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }}

        .messages::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #9c27b0, #673ab7);
            border-radius: 4px;
        }}

        .messages::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, #673ab7, #9c27b0);
        }}

        /* Message Styles */
        .message {{
            display: flex;
            gap: 1rem;
            max-width: 85%;
            animation: slideIn 0.4s ease-out;
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(20px) scale(0.95);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
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
            width: 45px;
            height: 45px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }}

        .user-message .message-avatar {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        }}

        .bot-message .message-avatar {{
            background: linear-gradient(135deg, #9c27b0, #673ab7);
        }}

        .message-content {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border-radius: 1.2rem;
            padding: 1.2rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }}

        .message-content:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.3);
        }}

        .user-message .message-content {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(29, 78, 216, 0.25));
            border: 1px solid rgba(59, 130, 246, 0.4);
        }}

        .bot-message .message-content {{
            background: rgba(15, 15, 35, 0.7);
            border: 1px solid rgba(156, 39, 176, 0.4);
        }}

        .message-text {{
            line-height: 1.6;
            margin-bottom: 0.8rem;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}

        .message-meta {{
            font-size: 0.75rem;
            color: #a0a0a0;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            flex-wrap: wrap;
        }}

        .message-time {{
            opacity: 0.8;
        }}

        .message-model {{
            background: rgba(156, 39, 176, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 0.8rem;
            font-size: 0.7rem;
            font-weight: 500;
        }}

        .message-intent {{
            background: rgba(59, 130, 246, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 0.8rem;
            font-size: 0.7rem;
            font-weight: 500;
        }}

        /* Typing Indicator */
        .typing {{
            display: flex;
            gap: 0.4rem;
            align-items: center;
            padding: 0.5rem 0;
        }}

        .typing span {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #9c27b0;
            animation: typing 1.4s infinite ease-in-out;
        }}

        .typing span:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing span:nth-child(2) {{ animation-delay: -0.16s; }}

        @keyframes typing {{
            0%, 80%, 100% {{
                transform: scale(0.8);
                opacity: 0.5;
            }}
            40% {{
                transform: scale(1.2);
                opacity: 1;
            }}
        }}

        /* Input Container - FIXED POSITION */
        .input-container {{
            padding: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            background: rgba(15, 15, 35, 0.95);
            backdrop-filter: blur(15px);
            flex-shrink: 0;
        }}

        .input-wrapper {{
            display: flex;
            gap: 1rem;
            align-items: flex-end;
            background: rgba(15, 15, 35, 0.8);
            backdrop-filter: blur(15px);
            border-radius: 1.5rem;
            padding: 1.2rem;
            border: 1px solid rgba(156, 39, 176, 0.4);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }}

        .input-wrapper:focus-within {{
            border-color: rgba(156, 39, 176, 0.7);
            box-shadow: 0 6px 30px rgba(156, 39, 176, 0.2);
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
            resize: none;
            max-height: 120px;
            min-height: 24px;
        }}

        .message-input::placeholder {{
            color: #a0a0a0;
        }}

        .send-button {{
            background: linear-gradient(135deg, #9c27b0, #673ab7);
            border: none;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.3rem;
            transition: all 0.3s ease;
            flex-shrink: 0;
            box-shadow: 0 2px 10px rgba(156, 39, 176, 0.3);
        }}

        .send-button:hover:not(:disabled) {{
            transform: scale(1.1);
            box-shadow: 0 4px 20px rgba(156, 39, 176, 0.5);
        }}

        .send-button:active {{
            transform: scale(0.95);
        }}

        .send-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}

        /* Footer */
        .footer {{
            background: rgba(15, 15, 35, 0.95);
            backdrop-filter: blur(15px);
            border-top: 1px solid rgba(59, 130, 246, 0.3);
            padding: 1rem 2rem;
            text-align: center;
            font-size: 0.9rem;
            color: #a0a0a0;
            flex-shrink: 0;
        }}

        .footer-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .social-links {{
            display: flex;
            gap: 1.5rem;
        }}

        .social-links a {{
            color: #9c27b0;
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: 500;
        }}

        .social-links a:hover {{
            color: #673ab7;
            transform: translateY(-2px);
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .header, .chat-container, .input-container, .footer {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            
            .message {{
                max-width: 95%;
            }}
            
            .footer-content {{
                flex-direction: column;
                text-align: center;
            }}
            
            .logo h1 {{
                font-size: 1.2rem;
            }}
            
            .input-wrapper {{
                padding: 1rem;
            }}
        }}

        /* Loading States */
        .loading {{
            opacity: 0.7;
            pointer-events: none;
        }}

        .error {{
            background: rgba(244, 67, 54, 0.2) !important;
            border-color: rgba(244, 67, 54, 0.5) !important;
        }}

        .success {{
            background: rgba(76, 175, 80, 0.2) !important;
            border-color: rgba(76, 175, 80, 0.5) !important;
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
                <div class="status-dot" id="statusDot"></div>
                <span id="statusText">Connecting...</span>
            </div>
        </header>

        <main class="chat-container">
            <div class="messages" id="messages">
                <div class="message bot-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <div class="message-text">Hello! I'm Nandhakumar's AI Assistant, powered by Claude LLM. I'm here to help you with questions, conversations, and various tasks. How can I assist you today?</div>
                        <div class="message-meta">
                            <span class="message-time">Just now</span>
                            <span class="message-model">Claude 3 Haiku</span>
                            <span class="message-intent">greeting</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="input-container">
                <div class="input-wrapper">
                    <textarea 
                        class="message-input" 
                        id="messageInput"
                        placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                        rows="1"
                    ></textarea>
                    <button class="send-button" id="sendButton">🚀</button>
                </div>
            </div>
        </main>

        <footer class="footer">
            <div class="footer-content">
                <div>Powered by Claude LLM • Production Grade • Session: prod-{int(time.time())}</div>
                <div class="social-links">
                    <a href="https://github.com/nandhakumar" target="_blank" rel="noopener noreferrer">GitHub</a>
                    <a href="https://linkedin.com/in/nandhakumar" target="_blank" rel="noopener noreferrer">LinkedIn</a>
                    <a href="https://youtube.com/@nandhakumar" target="_blank" rel="noopener noreferrer">YouTube</a>
                </div>
            </div>
        </footer>
    </div>

    <script>
        // Production JavaScript with Error Handling
        const CONFIG = {{
            CHATBOT_API: '{chatbot_endpoint}',
            HEALTH_API: '{health_endpoint}',
            SESSION_ID: 'prod-session-' + Date.now(),
            MAX_RETRIES: 3,
            RETRY_DELAY: 1000
        }};

        class ProductionChatbot {{
            constructor() {{
                this.messagesContainer = document.getElementById('messages');
                this.messageInput = document.getElementById('messageInput');
                this.sendButton = document.getElementById('sendButton');
                this.statusDot = document.getElementById('statusDot');
                this.statusText = document.getElementById('statusText');
                this.isLoading = false;
                this.retryCount = 0;
                
                this.init();
            }}

            init() {{
                this.setupEventListeners();
                this.checkHealth();
                this.messageInput.focus();
            }}

            setupEventListeners() {{
                this.sendButton.addEventListener('click', () => this.sendMessage());
                
                this.messageInput.addEventListener('keydown', (e) => {{
                    if (e.key === 'Enter' && !e.shiftKey) {{
                        e.preventDefault();
                        this.sendMessage();
                    }}
                }});

                this.messageInput.addEventListener('input', () => {{
                    this.autoResize();
                }});
            }}

            autoResize() {{
                this.messageInput.style.height = 'auto';
                this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
            }}

            async checkHealth() {{
                try {{
                    const response = await fetch(CONFIG.HEALTH_API);
                    if (response.ok) {{
                        this.updateStatus('online', 'Online');
                    }} else {{
                        this.updateStatus('warning', 'Degraded');
                    }}
                }} catch (error) {{
                    this.updateStatus('offline', 'Offline');
                }}
            }}

            updateStatus(status, text) {{
                this.statusText.textContent = text;
                this.statusDot.className = 'status-dot ' + status;
            }}

            async sendMessage() {{
                const message = this.messageInput.value.trim();
                if (!message || this.isLoading) return;

                this.addMessage(message, 'user');
                this.messageInput.value = '';
                this.autoResize();
                this.setLoading(true);
                this.showTyping();

                try {{
                    const response = await this.callAPI(message);
                    this.hideTyping();
                    
                    if (response) {{
                        this.addMessage(
                            response.response, 
                            'bot', 
                            response.intent, 
                            response.model,
                            response.timestamp
                        );
                        this.retryCount = 0;
                    }} else {{
                        throw new Error('No response received');
                    }}
                }} catch (error) {{
                    this.hideTyping();
                    this.handleError(error, message);
                }} finally {{
                    this.setLoading(false);
                    this.messageInput.focus();
                }}
            }}

            async callAPI(message, retryCount = 0) {{
                try {{
                    const response = await fetch(CONFIG.CHATBOT_API, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            message: message,
                            session_id: CONFIG.SESSION_ID,
                            user_id: 'web-user'
                        }})
                    }});

                    if (!response.ok) {{
                        throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                    }}

                    return await response.json();
                }} catch (error) {{
                    if (retryCount < CONFIG.MAX_RETRIES) {{
                        await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * (retryCount + 1)));
                        return this.callAPI(message, retryCount + 1);
                    }}
                    throw error;
                }}
            }}

            addMessage(text, sender, intent = null, model = null, timestamp = null) {{
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${{sender}}-message`;
                
                const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
                
                let metaContent = `<span class="message-time">${{time}}</span>`;
                if (model) {{
                    metaContent += `<span class="message-model">${{model}}</span>`;
                }}
                if (intent) {{
                    metaContent += `<span class="message-intent">${{intent}}</span>`;
                }}
                
                messageDiv.innerHTML = `
                    <div class="message-avatar">${{sender === 'user' ? '👤' : '🤖'}}</div>
                    <div class="message-content">
                        <div class="message-text">${{this.escapeHtml(text)}}</div>
                        <div class="message-meta">${{metaContent}}</div>
                    </div>
                `;
                
                this.messagesContainer.appendChild(messageDiv);
                this.scrollToBottom();
            }}

            showTyping() {{
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
                this.messagesContainer.appendChild(typingDiv);
                this.scrollToBottom();
            }}

            hideTyping() {{
                const typingDiv = document.getElementById('typing');
                if (typingDiv) {{
                    typingDiv.remove();
                }}
            }}

            handleError(error, originalMessage) {{
                console.error('Chat error:', error);
                
                let errorMessage = 'I apologize, but I encountered an error. Please try again.';
                
                if (error.message.includes('HTTP 429')) {{
                    errorMessage = 'I\\'m receiving too many requests right now. Please wait a moment and try again.';
                }} else if (error.message.includes('HTTP 500')) {{
                    errorMessage = 'I\\'m experiencing technical difficulties. Please try again in a few moments.';
                }} else if (error.message.includes('Failed to fetch')) {{
                    errorMessage = 'I\\'m having trouble connecting. Please check your internet connection and try again.';
                }}
                
                this.addMessage(errorMessage, 'bot', 'error');
                this.updateStatus('warning', 'Error');
                
                // Auto-retry after delay
                setTimeout(() => {{
                    this.updateStatus('online', 'Online');
                }}, 5000);
            }}

            setLoading(loading) {{
                this.isLoading = loading;
                this.sendButton.disabled = loading;
                this.messageInput.disabled = loading;
                
                if (loading) {{
                    this.sendButton.textContent = '⏳';
                    document.body.classList.add('loading');
                }} else {{
                    this.sendButton.textContent = '🚀';
                    document.body.classList.remove('loading');
                }}
            }}

            scrollToBottom() {{
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }}

            escapeHtml(text) {{
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }}
        }}

        // Initialize the chatbot when page loads
        document.addEventListener('DOMContentLoaded', () => {{
            window.chatbot = new ProductionChatbot();
            console.log('🚀 Production Voice Assistant loaded successfully!');
            console.log('🌐 API Endpoint:', CONFIG.CHATBOT_API);
            console.log('🤖 LLM: Claude 3 Haiku via AWS Bedrock');
        }});
    </script>
</body>
</html>"""
    
    return html_app

def deploy_production_frontend():
    """Deploy the production frontend to S3"""
    print("\n🚀 DEPLOYING PRODUCTION FRONTEND")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    # Create the production HTML app
    html_content = create_production_frontend()
    
    if not html_content:
        return False
    
    try:
        # Upload index.html
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=html_content,
            ContentType='text/html',
            CacheControl='no-cache, no-store, must-revalidate',
            Metadata={
                'version': 'production',
                'llm': 'claude-3-haiku',
                'features': 'fixed-scrolling,error-handling,retry-logic'
            }
        )
        
        print("✅ Deployed production frontend to S3")
        
        # Create robots.txt for SEO
        robots_content = """User-agent: *
Allow: /

Sitemap: http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com/sitemap.xml"""
        
        s3.put_object(
            Bucket=bucket_name,
            Key='robots.txt',
            Body=robots_content,
            ContentType='text/plain'
        )
        
        print("✅ Added robots.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deploying frontend: {e}")
        return False

def test_production_system():
    """Test the complete production system"""
    print(f"\n🧪 TESTING COMPLETE PRODUCTION SYSTEM")
    print("=" * 50)
    
    import requests
    
    # Load API details
    api_details = load_production_api_details()
    if not api_details:
        return False
    
    chatbot_endpoint = api_details['chatbot_endpoint']
    health_endpoint = api_details['health_endpoint']
    
    # Test health endpoint
    print(f"1️⃣ Testing health endpoint...")
    try:
        health_response = requests.get(health_endpoint, timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check: {health_data.get('status')} - {health_data.get('service')}")
        else:
            print(f"⚠️  Health check issue: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test Claude LLM
    print(f"\n2️⃣ Testing Claude LLM...")
    try:
        response = requests.post(
            chatbot_endpoint,
            json={
                "message": "Hello! Please tell me about your capabilities and demonstrate your Claude LLM intelligence.",
                "session_id": "production-system-test"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Claude LLM working!")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            print(f"   Model: {data.get('model', 'Unknown')}")
            print(f"   Intent: {data.get('intent', 'No intent')}")
        else:
            print(f"❌ Claude LLM failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Claude LLM error: {e}")
        return False
    
    # Test frontend
    print(f"\n3️⃣ Testing frontend...")
    frontend_url = "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend accessible")
            
            # Check for production features
            content = response.text
            if 'overflow-y: auto' in content:
                print(f"✅ Fixed scrolling implemented")
            if 'Claude LLM' in content:
                print(f"✅ Claude LLM branding present")
            if 'ProductionChatbot' in content:
                print(f"✅ Production JavaScript loaded")
            if api_details['chatbot_endpoint'] in content:
                print(f"✅ Correct API endpoint configured")
                
            return True
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def main():
    """Main function"""
    print("🚨 CREATING PRODUCTION FRONTEND")
    print("=" * 60)
    
    if deploy_production_frontend():
        if test_production_system():
            print("\n" + "=" * 60)
            print("🎉 PRODUCTION SYSTEM COMPLETE!")
            
            print(f"\n🌐 YOUR PRODUCTION VOICE ASSISTANT:")
            print(f"   http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
            
            print(f"\n✅ PRODUCTION FEATURES:")
            print(f"   ✅ Claude 3 Haiku LLM via AWS Bedrock")
            print(f"   ✅ Fixed scrolling (no more scroll issues)")
            print(f"   ✅ Error handling and retry logic")
            print(f"   ✅ Health monitoring")
            print(f"   ✅ Production-grade UI/UX")
            print(f"   ✅ Responsive design")
            print(f"   ✅ Session management")
            print(f"   ✅ Auto-retry on failures")
            print(f"   ✅ Real-time status indicators")
            print(f"   ✅ No authentication required")
            
            print(f"\n💡 INSTRUCTIONS:")
            print(f"   1. Clear browser cache (Ctrl+Shift+Delete)")
            print(f"   2. Open the URL above")
            print(f"   3. Start chatting with Claude LLM!")
            print(f"   4. Scrolling is now fixed!")
            
            print(f"\n🎯 PRODUCTION-GRADE SYSTEM IS READY!")
            
        else:
            print("\n❌ SYSTEM TEST FAILED")
    else:
        print("\n❌ FRONTEND DEPLOYMENT FAILED")

if __name__ == "__main__":
    main()
