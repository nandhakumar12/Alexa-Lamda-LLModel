import React, { useRef } from 'react';

interface ChatInputProps {
  message: string;
  setMessage: (message: string) => void;
  handleSendMessage: () => void;
  handleVoiceInput: () => void;
  isListening: boolean;
  loading: boolean;
  audioLevel: number;
}

const ChatInput: React.FC<ChatInputProps> = ({
  message,
  setMessage,
  handleSendMessage,
  handleVoiceInput,
  isListening,
  loading,
  audioLevel
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{
      padding: '24px',
      borderTop: '1px solid rgba(59, 130, 246, 0.2)',
      background: 'rgba(15, 15, 35, 0.8)',
      backdropFilter: 'blur(20px)'
    }}>
      {/* Input Container */}
      <div style={{
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-end',
        marginBottom: '16px'
      }}>
        {/* Text Input */}
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            disabled={loading}
            style={{
              width: '100%',
              padding: '16px 20px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '16px',
              color: '#ffffff',
              fontSize: '14px',
              outline: 'none',
              transition: 'all 0.3s ease',
              boxSizing: 'border-box',
              resize: 'none'
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#3b82f6';
              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          />
        </div>

        {/* Voice Input Button */}
        <button
          onClick={handleVoiceInput}
          disabled={loading}
          style={{
            width: '52px',
            height: '52px',
            background: isListening 
              ? 'linear-gradient(135deg, #ef4444, #dc2626)' 
              : 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            border: 'none',
            borderRadius: '50%',
            color: '#ffffff',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease',
            boxShadow: isListening 
              ? '0 4px 20px rgba(239, 68, 68, 0.4)' 
              : '0 4px 15px rgba(59, 130, 246, 0.3)',
            transform: isListening ? `scale(${1 + audioLevel * 0.2})` : 'scale(1)',
            animation: isListening ? 'pulse 1.5s ease-in-out infinite' : 'none'
          }}
          onMouseEnter={(e) => {
            if (!loading && !isListening) {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            if (!loading && !isListening) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(59, 130, 246, 0.3)';
            }
          }}
        >
          {isListening ? '🔴' : '🎤'}
        </button>

        {/* Send Button */}
        <button
          onClick={handleSendMessage}
          disabled={loading || !message.trim()}
          style={{
            width: '52px',
            height: '52px',
            background: (loading || !message.trim()) 
              ? 'rgba(59, 130, 246, 0.3)' 
              : 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            border: 'none',
            borderRadius: '50%',
            color: '#ffffff',
            cursor: (loading || !message.trim()) ? 'not-allowed' : 'pointer',
            fontSize: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease',
            boxShadow: (loading || !message.trim()) 
              ? 'none' 
              : '0 4px 15px rgba(59, 130, 246, 0.3)'
          }}
          onMouseEnter={(e) => {
            if (!loading && message.trim()) {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.4)';
            }
          }}
          onMouseLeave={(e) => {
            if (!loading && message.trim()) {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(59, 130, 246, 0.3)';
            }
          }}
        >
          {loading ? '⏳' : '📤'}
        </button>
      </div>

      {/* Quick Actions */}
      <div style={{
        display: 'flex',
        gap: '8px',
        flexWrap: 'wrap',
        justifyContent: 'center'
      }}>
        {[
          { text: "Hello! How are you today?", emoji: "👋" },
          { text: "What's the weather like?", emoji: "🌤️" },
          { text: "Tell me a joke", emoji: "😄" },
          { text: "Help me with something", emoji: "🤝" }
        ].map((action, index) => (
          <button
            key={index}
            onClick={() => {
              setMessage(action.text);
              inputRef.current?.focus();
            }}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '8px 12px',
              color: 'rgba(255, 255, 255, 0.8)',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: '500',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
              e.currentTarget.style.color = '#ffffff';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
              e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <span>{action.emoji}</span>
            <span>{action.text}</span>
          </button>
        ))}
      </div>

      {/* Voice Status Indicator */}
      {isListening && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginTop: '16px',
          gap: '8px',
          color: '#ef4444',
          fontSize: '14px',
          fontWeight: '500'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            background: '#ef4444',
            borderRadius: '50%',
            animation: 'pulse 1s ease-in-out infinite'
          }} />
          <span>Listening... Speak now</span>
          <div style={{
            width: '8px',
            height: '8px',
            background: '#ef4444',
            borderRadius: '50%',
            animation: 'pulse 1s ease-in-out infinite'
          }} />
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default ChatInput;
