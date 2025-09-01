import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import './App.css';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://tcuzlzq1af.execute-api.us-east-1.amazonaws.com/prod';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(`session-${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message on load
  useEffect(() => {
    setMessages([{
      id: 1,
      text: "Hello! I'm Nandhakumar's AI Assistant. How can I help you today?",
      sender: 'bot',
      timestamp: new Date()
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chatbot`, {
        message: inputMessage,
        type: 'text',
        session_id: sessionId
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        intent: response.data.intent
      };

      setMessages(prev => [...prev, botMessage]);
      toast.success('Message sent!');
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <div className="bot-avatar">🤖</div>
            <h1>Nandhakumar's AI Assistant</h1>
          </div>
          <div className="status-indicator">
            <div className="status-dot online"></div>
            <span>Online</span>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <main className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-avatar">
                {message.sender === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{message.text}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                  {message.intent && (
                    <span className="message-intent">• {message.intent}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot-message">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              className="message-input"
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="send-button"
            >
              {isLoading ? '⏳' : '🚀'}
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>Powered by AI • Session: {sessionId.slice(-8)}</p>
          <div className="social-links">
            <a href="https://github.com/nandhakumar" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            <a href="https://linkedin.com/in/nandhakumar" target="_blank" rel="noopener noreferrer">
              LinkedIn
            </a>
            <a href="https://youtube.com/@nandhakumar" target="_blank" rel="noopener noreferrer">
              YouTube
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
