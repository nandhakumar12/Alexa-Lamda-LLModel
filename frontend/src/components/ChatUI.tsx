import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { FaMicrophone, FaMicrophoneSlash, FaPaperPlane, FaRobot, FaUser } from 'react-icons/fa';
import toast from 'react-hot-toast';

// Components
import Recorder from './Recorder';
import LoadingSpinner from './LoadingSpinner';

// Hooks and services
import { useVoice } from '../contexts/VoiceContext';
import { useAuth } from '../contexts/AuthContext';
import { chatService } from '../services/api';

// Types
interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  messageType: 'text' | 'voice';
  audioUrl?: string;
}

// Styled components
const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  max-width: 800px;
  margin: 0 auto;
  background: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.lg};
  overflow: hidden;
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.info});
  color: white;
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
  
  h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  p {
    margin: ${props => props.theme.spacing.sm} 0 0;
    opacity: 0.9;
    font-size: 0.9rem;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.light};
`;

const MessageBubble = styled(motion.div)<{ isUser: boolean }>`
  display: flex;
  align-items: flex-start;
  margin-bottom: ${props => props.theme.spacing.md};
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

const MessageContent = styled.div<{ isUser: boolean }>`
  max-width: 70%;
  background: ${props => props.isUser ? props.theme.colors.primary : props.theme.colors.background};
  color: ${props => props.isUser ? 'white' : props.theme.colors.text};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.sm};
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 10px;
    ${props => props.isUser ? 'right: -8px' : 'left: -8px'};
    width: 0;
    height: 0;
    border-style: solid;
    border-width: ${props => props.isUser ? '8px 0 8px 8px' : '8px 8px 8px 0'};
    border-color: ${props => props.isUser 
      ? `transparent transparent transparent ${props.theme.colors.primary}` 
      : `transparent ${props.theme.colors.background} transparent transparent`};
  }
`;

const MessageIcon = styled.div<{ isUser: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.full};
  background: ${props => props.isUser ? props.theme.colors.secondary : props.theme.colors.success};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: ${props => props.isUser ? `0 0 0 ${props.theme.spacing.sm}` : `0 ${props.theme.spacing.sm} 0 0`};
  font-size: 1.2rem;
`;

const MessageText = styled.p`
  margin: 0;
  line-height: 1.5;
  word-wrap: break-word;
`;

const MessageTime = styled.span`
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: ${props => props.theme.spacing.xs};
  display: block;
`;

const InputContainer = styled.div`
  padding: ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.background};
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const InputForm = styled.form`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  align-items: flex-end;
`;

const TextInput = styled.textarea`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  min-height: 50px;
  max-height: 120px;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const ActionButton = styled(motion.button)<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: ${props => props.theme.spacing.md};
  border: none;
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
  height: 50px;
  transition: all 0.2s ease;
  
  background: ${props => {
    switch (props.variant) {
      case 'danger': return props.theme.colors.danger;
      case 'secondary': return props.theme.colors.secondary;
      default: return props.theme.colors.primary;
    }
  }};
  
  color: white;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const VoiceControls = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  align-items: center;
`;

const TypingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.textSecondary};
  font-style: italic;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
  
  .icon {
    font-size: 4rem;
    margin-bottom: ${props => props.theme.spacing.lg};
    opacity: 0.5;
  }
  
  h3 {
    margin-bottom: ${props => props.theme.spacing.sm};
    color: ${props => props.theme.colors.text};
  }
  
  p {
    margin: 0;
    line-height: 1.6;
  }
`;

// Main ChatUI component
const ChatUI: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { user } = useAuth();
  const { 
    isListening, 
    isSupported, 
    startListening, 
    stopListening, 
    transcript,
    resetTranscript 
  } = useVoice();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle voice transcript
  useEffect(() => {
    if (transcript) {
      setInputText(transcript);
    }
  }, [transcript]);

  const sendMessage = async (content: string, messageType: 'text' | 'voice' = 'text') => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date(),
      messageType,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await chatService.sendMessage({
        message: content.trim(),
        type: messageType,
        session_id: `session_${user?.username}_${Date.now()}`,
      });

      // Simulate typing delay
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: response.response,
          timestamp: new Date(),
          messageType: 'text',
        };

        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
      }, 1000);

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date(),
        messageType: 'text',
      };

      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
      if (transcript) {
        sendMessage(transcript, 'voice');
        resetTranscript();
      }
    } else {
      startListening();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <h2>🎤 Voice Assistant AI</h2>
        <p>Ask me anything or use voice commands</p>
      </ChatHeader>

      <MessagesContainer>
        {messages.length === 0 ? (
          <EmptyState>
            <div className="icon">🤖</div>
            <h3>Welcome to Voice Assistant AI!</h3>
            <p>
              Start a conversation by typing a message or using voice commands.
              <br />
              I can help you with various tasks and answer your questions.
            </p>
          </EmptyState>
        ) : (
          <>
            <AnimatePresence>
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  isUser={message.type === 'user'}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {message.type === 'bot' && (
                    <MessageIcon isUser={false}>
                      <FaRobot />
                    </MessageIcon>
                  )}
                  
                  <MessageContent isUser={message.type === 'user'}>
                    <MessageText>{message.content}</MessageText>
                    <MessageTime>
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                      {message.messageType === 'voice' && ' 🎤'}
                    </MessageTime>
                  </MessageContent>
                  
                  {message.type === 'user' && (
                    <MessageIcon isUser={true}>
                      <FaUser />
                    </MessageIcon>
                  )}
                </MessageBubble>
              ))}
            </AnimatePresence>

            {isTyping && (
              <TypingIndicator
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <MessageIcon isUser={false}>
                  <FaRobot />
                </MessageIcon>
                <span>Assistant is typing</span>
                <LoadingSpinner size="small" />
              </TypingIndicator>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <InputForm onSubmit={handleSubmit}>
          <TextInput
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isListening ? "Listening... Speak now!" : "Type your message or use voice..."}
            disabled={isLoading || isListening}
            rows={1}
          />
          
          <VoiceControls>
            {isSupported && (
              <ActionButton
                type="button"
                variant={isListening ? 'danger' : 'secondary'}
                onClick={handleVoiceToggle}
                disabled={isLoading}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isListening ? <FaMicrophoneSlash /> : <FaMicrophone />}
              </ActionButton>
            )}
            
            <ActionButton
              type="submit"
              disabled={!inputText.trim() || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isLoading ? <LoadingSpinner size="small" /> : <FaPaperPlane />}
            </ActionButton>
          </VoiceControls>
        </InputForm>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatUI;
