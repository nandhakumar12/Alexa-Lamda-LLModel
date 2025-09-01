import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  user: string;
  bot: string;
  time: string;
}

interface EnhancedChatInterfaceProps {
  conversations: Message[];
  message: string;
  setMessage: (message: string) => void;
  handleSendMessage: () => void;
  handleVoiceInput: () => void;
  isListening: boolean;
  loading: boolean;
  isLLMMode: boolean;
  setIsLLMMode: (mode: boolean) => void;
  audioLevel: number;
}

const EnhancedChatInterface: React.FC<EnhancedChatInterfaceProps> = ({
  conversations,
  message,
  setMessage,
  handleSendMessage,
  handleVoiceInput,
  isListening,
  loading,
  isLLMMode,
  setIsLLMMode,
  audioLevel
}) => {
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations]);

  useEffect(() => {
    if (loading) {
      setIsTyping(true);
      const timer = setTimeout(() => setIsTyping(false), 3000);
      return () => clearTimeout(timer);
    } else {
      setIsTyping(false);
    }
  }, [loading]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{
      display: 'flex',
      height: '100%',
      background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)',
      borderRadius: '20px',
      overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
    }}>
      {/* Left Sidebar - Bot Character */}
      <div style={{
        width: '300px',
        background: 'rgba(15, 15, 35, 0.8)',
        backdropFilter: 'blur(20px)',
        borderRight: '1px solid rgba(59, 130, 246, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
        position: 'relative'
      }}>
        {/* Animated Bot Character */}
        <div style={{
          width: '120px',
          height: '120px',
          background: `linear-gradient(135deg, #3b82f6, #8b5cf6)`,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '48px',
          marginBottom: '24px',
          boxShadow: '0 8px 32px rgba(59, 130, 246, 0.4)',
          animation: isListening ? 'pulse 1.5s ease-in-out infinite' : 
                    loading ? 'bounce 1s ease-in-out infinite' : 'none',
          transform: isListening ? `scale(${1 + audioLevel * 0.3})` : 'scale(1)',
          transition: 'transform 0.1s ease'
        }}>
          🤖
        </div>

        {/* Bot Info */}
        <h2 style={{
          margin: 0,
          fontSize: '24px',
          fontWeight: '700',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          textAlign: 'center',
          marginBottom: '8px'
        }}>
          Best Personal AI Assistant
        </h2>

        <p style={{
          margin: 0,
          fontSize: '14px',
          color: 'rgba(255, 255, 255, 0.6)',
          textAlign: 'center',
          lineHeight: '1.5',
          marginBottom: '32px'
        }}>
          Nice to meet you! How can I help you today?<br />
          I'm here to assist with any questions or tasks.
        </p>

        {/* AI Mode Toggle */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '12px',
          padding: '16px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          width: '100%',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.6)',
            marginBottom: '8px',
            fontWeight: '500'
          }}>
            AI Mode
          </div>
          <button
            onClick={() => setIsLLMMode(!isLLMMode)}
            style={{
              background: isLLMMode ? 'linear-gradient(135deg, #3b82f6, #8b5cf6)' : 'rgba(255, 255, 255, 0.1)',
              border: 'none',
              borderRadius: '20px',
              padding: '8px 16px',
              color: '#ffffff',
              fontSize: '12px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              width: '100%',
              position: 'relative',
              overflow: 'hidden'
            }}
            onMouseEnter={(e) => {
              if (!isLLMMode) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLLMMode) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }
            }}
          >
            <span style={{
              display: 'inline-block',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: isLLMMode ? '#22c55e' : '#6b7280',
              marginRight: '8px'
            }} />
            {isLLMMode ? 'Claude Haiku' : 'Basic Mode'}
          </button>
        </div>

        {/* Quick Start Button */}
        <button
          onClick={() => {
            setMessage("Hello! How are you today?");
            inputRef.current?.focus();
          }}
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            border: 'none',
            borderRadius: '12px',
            padding: '12px 24px',
            color: '#ffffff',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            marginTop: '20px',
            boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 4px 15px rgba(59, 130, 246, 0.3)';
          }}
        >
          Let's start chatting
        </button>

        {/* Floating Particles Animation */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          pointerEvents: 'none',
          overflow: 'hidden'
        }}>
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              style={{
                position: 'absolute',
                width: '4px',
                height: '4px',
                background: 'rgba(59, 130, 246, 0.3)',
                borderRadius: '50%',
                left: `${20 + i * 15}%`,
                top: `${30 + (i % 3) * 20}%`,
                animation: `float ${3 + i * 0.5}s ease-in-out infinite`,
                animationDelay: `${i * 0.5}s`
              }}
            />
          ))}
        </div>
      </div>

      {/* Right Side - Chat Area */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}>
        {/* Chat Messages */}
        <div style={{
          flex: 1,
          padding: '24px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          {conversations.length === 0 ? (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              flexDirection: 'column',
              gap: '16px'
            }}>
              <div style={{
                fontSize: '48px',
                opacity: 0.3
              }}>
                💬
              </div>
              <div style={{
                fontSize: '18px',
                color: 'rgba(255, 255, 255, 0.6)',
                textAlign: 'center'
              }}>
                Start a conversation with your AI assistant
              </div>
              <div style={{
                fontSize: '14px',
                color: 'rgba(255, 255, 255, 0.4)',
                textAlign: 'center'
              }}>
                Type a message or use voice input to get started
              </div>
            </div>
          ) : (
            conversations.map((conv) => (
              <div key={conv.id} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {/* User Message */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'flex-end'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    borderRadius: '18px 18px 4px 18px',
                    padding: '12px 16px',
                    maxWidth: '70%',
                    color: '#ffffff',
                    fontSize: '14px',
                    lineHeight: '1.4',
                    boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)'
                  }}>
                    {conv.user}
                  </div>
                </div>

                {/* Bot Message */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '16px',
                    flexShrink: 0,
                    marginTop: '4px'
                  }}>
                    🤖
                  </div>
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '18px 18px 18px 4px',
                    padding: '12px 16px',
                    maxWidth: '70%',
                    color: 'rgba(255, 255, 255, 0.9)',
                    fontSize: '14px',
                    lineHeight: '1.4',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    {conv.bot}
                  </div>
                </div>
              </div>
            ))
          )}

          {/* Typing Indicator */}
          {isTyping && (
            <div style={{
              display: 'flex',
              justifyContent: 'flex-start',
              alignItems: 'flex-start',
              gap: '12px'
            }}>
              <div style={{
                width: '32px',
                height: '32px',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                flexShrink: 0,
                marginTop: '4px'
              }}>
                🤖
              </div>
              <div style={{
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '18px 18px 18px 4px',
                padding: '12px 16px',
                color: 'rgba(255, 255, 255, 0.9)',
                fontSize: '14px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <span>Thinking</span>
                <div style={{ display: 'flex', gap: '2px' }}>
                  {[...Array(3)].map((_, i) => (
                    <div
                      key={i}
                      style={{
                        width: '4px',
                        height: '4px',
                        background: 'rgba(255, 255, 255, 0.6)',
                        borderRadius: '50%',
                        animation: `bounce 1.4s ease-in-out infinite`,
                        animationDelay: `${i * 0.2}s`
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }
        
        @keyframes bounce {
          0%, 20%, 53%, 80%, 100% { transform: translateY(0); }
          40%, 43% { transform: translateY(-8px); }
          70% { transform: translateY(-4px); }
          90% { transform: translateY(-2px); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
};

export default EnhancedChatInterface;
