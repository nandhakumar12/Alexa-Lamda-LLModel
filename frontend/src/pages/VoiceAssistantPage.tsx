import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { chatService } from '../services/api';
import toast from 'react-hot-toast';

interface VoiceAssistantPageProps {
  user: any;
  onSignOut: () => void;
}

const VoiceAssistantPage: React.FC<VoiceAssistantPageProps> = ({ user, onSignOut }) => {
  const navigate = useNavigate();
  
  // Voice Assistant State
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [conversations, setConversations] = useState<Array<{id: string, user: string, bot: string, time: string}>>([]);
  const [audioLevel] = useState<number>(0);
  const [recognition, setRecognition] = useState<any>(null);

  // Initialize voice recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setMessage(transcript);
        setIsListening(false);
      };

      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);

        if (event.error === 'not-allowed') {
          toast.error('Microphone access denied. Please allow microphone access and try again.');
        } else if (event.error === 'no-speech') {
          toast.error('No speech detected. Please try speaking again.');
        } else {
          toast.error(`Voice recognition error: ${event.error}`);
        }
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
    }

    // Add welcome message
    const welcomeMessage = `Hello! I'm Nandhakumar's AI Assistant. How can I help you today?`;
    const initialConversation = {
      id: 'welcome-' + Date.now().toString(),
      user: '',
      bot: welcomeMessage,
      time: new Date().toLocaleTimeString()
    };
    setConversations([initialConversation]);
    speakResponse(welcomeMessage);
  }, [user]);

  // Voice input handlers
  const startListening = () => {
    if (recognition) {
      setIsListening(true);
      recognition.start();
      toast.success('Listening... Please speak now');
    } else {
      toast.error('Voice recognition not available. Please type your message.');
    }
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
      setIsListening(false);
    }
  };

  // Test API connection (commented out to avoid unused variable warning)
  // const testApiConnection = async () => {
  //   try {
  //     const testMessage = {
  //       message: "Hello! Testing API connection.",
  //       type: 'text' as const,
  //       session_id: user?.username || 'test-user'
  //     };

  //     toast.loading('Testing API connection...');
  //     const response = await chatService.sendMessage(testMessage);
  //     toast.dismiss();
  //     toast.success('API connection successful!');
  //     console.log('API Test Response:', response);
  //   } catch (error) {
  //     toast.dismiss();
  //     toast.error('API connection failed');
  //     console.error('API Test Error:', error);
  //   }
  // };

  // Text-to-speech function
  const speakResponse = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.2;
      utterance.volume = 0.9;
      
      // Try to find a female voice
      const voices = speechSynthesis.getVoices();
      const femaleVoice = voices.find(voice =>
        voice.name.toLowerCase().includes('female') ||
        voice.name.toLowerCase().includes('zira') ||
        voice.name.toLowerCase().includes('hazel')
      );
      
      if (femaleVoice) {
        utterance.voice = femaleVoice;
      }
      
      speechSynthesis.speak(utterance);
    }
  };

  // Send message handler
  const sendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    const userMessage = message;
    setMessage('');

    // Add user message to conversation
    const newConversation = {
      id: Date.now().toString(),
      user: userMessage,
      bot: '',
      time: new Date().toLocaleTimeString()
    };
    setConversations(prev => [...prev, newConversation]);

    try {
      // Use the real chat service
      const chatMessage = {
        message: userMessage,
        type: 'text' as const,
        session_id: user?.username || 'anonymous'
      };
      const response = await chatService.sendMessage(chatMessage);

      // Update conversation with bot response
      setConversations(prev => prev.map(conv =>
        conv.id === newConversation.id
          ? { ...conv, bot: response.response }
          : conv
      ));

      // Speak the response
      speakResponse(response.response);

    } catch (error: any) {
      console.error('Error sending message:', error);

      let errorResponse = "I'm sorry, I encountered an error. Please try again.";
      let errorMessage = 'Failed to send message. Please try again.';

      // Handle specific error types
      if (error.response?.status === 401) {
        errorResponse = "Authentication error. Please sign in again.";
        errorMessage = 'Authentication failed. Please sign in again.';
      } else if (error.response?.status === 429) {
        errorResponse = "Too many requests. Please wait a moment and try again.";
        errorMessage = 'Rate limit exceeded. Please wait and try again.';
      } else if (error.code === 'ERR_NETWORK' || error.code === 'NETWORK_ERROR') {
        errorResponse = "Network connection error. Please check your internet connection.";
        errorMessage = 'Network error. Please check your connection.';
      } else if (error.response?.status >= 500) {
        errorResponse = "Server error. Our team has been notified.";
        errorMessage = 'Server error. Please try again later.';
      }

      toast.error(errorMessage);

      setConversations(prev => prev.map(conv =>
        conv.id === newConversation.id
          ? { ...conv, bot: errorResponse }
          : conv
      ));

      speakResponse(errorResponse);
    } finally {
      setLoading(false);
    }
  };

  // Basic response function (commented out to avoid unused variable warning)
  // const getBasicResponse = (userMessage: string): string => {
  //   const lowerMessage = userMessage.toLowerCase();
  //   const userName = user?.username || 'there';

  //   if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
  //     return `Hello ${userName}! I'm Nandhakumar's AI assistant. How can I help you today?`;
  //   } else if (lowerMessage.includes('how are you')) {
  //     return "I'm doing great, thank you for asking! I'm here and ready to help you with anything you need.";
  //   } else if (lowerMessage.includes('what can you do')) {
  //     return "I can help you with many things! I can have conversations, answer questions, help with tasks, and much more. What would you like to try?";
  //   } else if (lowerMessage.includes('time')) {
  //     return `The current time is ${new Date().toLocaleTimeString()}.`;
  //   } else if (lowerMessage.includes('date')) {
  //     return `Today's date is ${new Date().toLocaleDateString()}.`;
  //   } else if (lowerMessage.includes('thank')) {
  //     return "You're very welcome! I'm happy to help. Is there anything else you'd like to know or do?";
  //   } else if (lowerMessage.includes('bye') || lowerMessage.includes('goodbye')) {
  //     return `Goodbye ${userName}! It was great talking with you. Feel free to come back anytime you need assistance!`;
  //   } else if (lowerMessage.includes('nandhakumar')) {
  //     return "Nandhakumar is the creator of this AI assistant! He built this using modern AWS services and AI technology to provide you with an intelligent conversational experience.";
  //   } else {
  //     return "I understand you're asking about something, but I'm not sure how to help with that specific request. Could you try rephrasing it or ask me something else?";
  //   }
  // };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a0b2e 0%, #16213e 50%, #0f3460 100%)',
      color: '#ffffff',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Elements */}
      {[...Array(30)].map((_, i) => (
        <div
          key={`bg-particle-${i}`}
          style={{
            position: 'absolute',
            width: `${Math.random() * 4 + 2}px`,
            height: `${Math.random() * 4 + 2}px`,
            borderRadius: '50%',
            background: `rgba(168, 85, 247, ${Math.random() * 0.5 + 0.2})`,
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            animation: `float ${Math.random() * 20 + 10}s linear infinite`,
            animationDelay: `${Math.random() * 20}s`
          }}
        />
      ))}

      {/* Top Navigation */}
      <div style={{
        position: 'fixed',
        top: '20px',
        left: '20px',
        right: '20px',
        zIndex: 10,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {/* Logo */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          background: 'rgba(26, 11, 46, 0.8)',
          padding: '12px 20px',
          borderRadius: '20px',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          backdropFilter: 'blur(20px)'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px'
          }}>
            🤖
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: '700', color: 'white' }}>
              Nandhakumar's AI
            </div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>
              Welcome, {user?.username || 'User'}!
            </div>
          </div>
        </div>

        {/* User Menu */}
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <button
            onClick={() => navigate('/project')}
            style={{
              background: 'rgba(168, 85, 247, 0.2)',
              border: '1px solid rgba(168, 85, 247, 0.4)',
              borderRadius: '15px',
              padding: '12px 20px',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            📖 About
          </button>
          <button
            onClick={onSignOut}
            style={{
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              borderRadius: '15px',
              padding: '12px 20px',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            🚪 Sign Out
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="voice-main-content" style={{
        display: 'flex',
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '120px 20px 40px',
        gap: '40px',
        minHeight: '100vh',
        position: 'relative',
        zIndex: 5
      }}>

        {/* Left Panel - AI Character */}
        <div className="ai-character-panel" style={{
          width: '400px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {/* AI Character Card */}
          <div style={{
            background: 'rgba(26, 11, 46, 0.6)',
            borderRadius: '30px',
            padding: '40px',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            backdropFilter: 'blur(20px)',
            textAlign: 'center',
            width: '100%',
            boxShadow: '0 25px 50px rgba(168, 85, 247, 0.2)'
          }}>
            {/* Animated AI Character */}
            <div style={{
              fontSize: '120px',
              marginBottom: '20px',
              animation: 'bounce 3s ease-in-out infinite'
            }}>
              🤖
            </div>

            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              margin: '0 0 16px 0',
              background: 'linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              How can I help you today?
            </h2>

            <p style={{
              color: 'rgba(255,255,255,0.8)',
              margin: '0 0 20px 0',
              fontSize: '14px',
              lineHeight: '1.6'
            }}>
              I'm Nandhakumar's AI assistant, powered by advanced language models. 
              Ask me anything!
            </p>

            {/* Status Indicators */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              fontSize: '12px',
              color: 'rgba(255,255,255,0.7)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: recognition ? '#10b981' : '#ef4444' }}>●</span>
                Voice: {recognition ? 'Ready' : 'Unavailable'}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#10b981' }}>●</span>
                TTS: Active
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: '#10b981' }}>●</span>
                AI: Claude Powered
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Chat Interface */}
        <div className="chat-interface-panel" style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          {/* Chat Header */}
          <div style={{
            background: 'rgba(26, 11, 46, 0.6)',
            borderRadius: '20px',
            padding: '20px 30px',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            backdropFilter: 'blur(20px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px'
              }}>
                🤖
              </div>
              <div>
                <h3 style={{
                  color: 'white',
                  margin: '0 0 4px 0',
                  fontSize: '18px',
                  fontWeight: '600'
                }}>
                  Nandhakumar's AI Assistant
                </h3>
                <p style={{
                  color: 'rgba(255,255,255,0.7)',
                  margin: 0,
                  fontSize: '14px'
                }}>
                  Ready to help you with anything!
                </p>
              </div>
            </div>

            <div style={{
              background: 'rgba(16, 185, 129, 0.2)',
              borderRadius: '12px',
              padding: '8px 16px',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontSize: '14px',
              color: 'rgba(255,255,255,0.9)'
            }}>
              🟢 Online
            </div>
          </div>

          {/* Conversation History */}
          <div style={{
            flex: 1,
            background: 'rgba(26, 11, 46, 0.4)',
            borderRadius: '20px',
            padding: '30px',
            overflowY: 'auto',
            border: '1px solid rgba(168, 85, 247, 0.2)',
            backdropFilter: 'blur(20px)',
            minHeight: '400px'
          }}>
            {conversations.map(conv => (
              <div key={conv.id} style={{ marginBottom: '30px' }}>
                {conv.user && (
                  <div style={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    marginBottom: '15px'
                  }}>
                    <div style={{
                      background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
                      color: 'white',
                      padding: '18px 24px',
                      borderRadius: '25px 25px 8px 25px',
                      maxWidth: '80%',
                      fontSize: '15px',
                      lineHeight: '1.5',
                      boxShadow: '0 8px 25px rgba(168, 85, 247, 0.3)',
                      fontWeight: '500'
                    }}>
                      {conv.user}
                    </div>
                  </div>
                )}
                {conv.bot && (
                  <div style={{
                    display: 'flex',
                    justifyContent: 'flex-start',
                    alignItems: 'flex-start',
                    gap: '15px'
                  }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '18px',
                      flexShrink: 0,
                      boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
                    }}>
                      🤖
                    </div>
                    <div style={{
                      background: 'rgba(255,255,255,0.08)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      color: 'white',
                      padding: '18px 24px',
                      borderRadius: '25px 25px 25px 8px',
                      maxWidth: '80%',
                      fontSize: '15px',
                      lineHeight: '1.5',
                      backdropFilter: 'blur(10px)'
                    }}>
                      {conv.bot}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div style={{
                display: 'flex',
                justifyContent: 'flex-start',
                alignItems: 'flex-start',
                gap: '15px',
                marginTop: '15px'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '18px',
                  flexShrink: 0,
                  boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
                }}>
                  🤖
                </div>
                <div style={{
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  color: 'rgba(255,255,255,0.8)',
                  padding: '18px 24px',
                  borderRadius: '25px 25px 25px 8px',
                  maxWidth: '80%',
                  fontSize: '15px',
                  lineHeight: '1.5',
                  backdropFilter: 'blur(10px)'
                }}>
                  🤖 Thinking...
                </div>
              </div>
            )}
          </div>

          {/* Voice Amplitude Waves */}
          {isListening && (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '80px',
              marginBottom: '20px',
              gap: '4px',
              background: 'rgba(168, 85, 247, 0.1)',
              borderRadius: '16px',
              padding: '20px',
              border: '1px solid rgba(168, 85, 247, 0.3)'
            }}>
              {[...Array(25)].map((_, i) => (
                <div
                  key={`wave-${i}`}
                  style={{
                    width: '4px',
                    height: `${15 + (audioLevel * 35 * Math.sin(Date.now() * 0.01 + i * 0.4))}px`,
                    background: 'linear-gradient(to top, #a855f7, #ec4899, #06b6d4)',
                    borderRadius: '2px',
                    animation: `wave 0.6s ease-in-out infinite`,
                    animationDelay: `${i * 0.08}s`,
                    boxShadow: '0 0 8px rgba(168, 85, 247, 0.4)'
                  }}
                />
              ))}
              <div style={{
                position: 'absolute',
                color: 'rgba(255,255,255,0.9)',
                fontSize: '14px',
                fontWeight: '500',
                marginTop: '60px'
              }}>
                🎤 Listening...
              </div>
            </div>
          )}

          {/* Input Controls */}
          <div style={{
            background: 'rgba(26, 11, 46, 0.6)',
            borderRadius: '20px',
            padding: '20px',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            backdropFilter: 'blur(20px)',
            display: 'flex',
            gap: '15px',
            alignItems: 'center'
          }}>
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask me something..."
              style={{
                flex: 1,
                padding: '18px 24px',
                fontSize: '16px',
                border: '1px solid rgba(168, 85, 247, 0.4)',
                borderRadius: '15px',
                outline: 'none',
                transition: 'all 0.3s ease',
                background: 'rgba(26, 11, 46, 0.8)',
                color: 'white',
                backdropFilter: 'blur(10px)'
              }}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            />

            <button
              onClick={isListening ? stopListening : startListening}
              style={{
                width: '55px',
                height: '55px',
                borderRadius: '15px',
                border: 'none',
                background: isListening
                  ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                  : 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
                color: 'white',
                fontSize: '22px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: isListening
                  ? '0 8px 25px rgba(239, 68, 68, 0.4)'
                  : '0 8px 25px rgba(168, 85, 247, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              disabled={!recognition}
            >
              {isListening ? '⏹️' : '🎤'}
            </button>

            <button
              onClick={sendMessage}
              disabled={loading || !message.trim()}
              style={{
                width: '55px',
                height: '55px',
                borderRadius: '15px',
                border: 'none',
                background: loading || !message.trim()
                  ? 'rgba(168, 85, 247, 0.3)'
                  : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                fontSize: '20px',
                cursor: loading || !message.trim() ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: loading || !message.trim()
                  ? 'none'
                  : '0 8px 25px rgba(16, 185, 129, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: loading || !message.trim() ? 0.5 : 1
              }}
            >
              {loading ? '⏳' : '➤'}
            </button>
          </div>
        </div>
      </div>

      {/* Responsive CSS */}
      <style>{`
        /* Mobile Responsive Styles */
        @media (max-width: 768px) {
          .voice-main-content {
            flex-direction: column !important;
            padding: 80px 10px 20px !important;
            gap: 20px !important;
          }

          .ai-character-panel {
            width: 100% !important;
            max-width: 400px !important;
            margin: 0 auto !important;
          }

          .chat-interface-panel {
            width: 100% !important;
          }

          /* Top Navigation Mobile */
          .top-nav {
            flex-direction: column !important;
            gap: 10px !important;
            padding: 10px !important;
          }

          .top-nav > div {
            width: 100% !important;
            justify-content: center !important;
          }

          .user-menu {
            justify-content: center !important;
            gap: 10px !important;
          }

          .user-menu button {
            padding: 8px 16px !important;
            font-size: 14px !important;
          }
        }

        @media (max-width: 480px) {
          .voice-main-content {
            padding: 60px 5px 15px !important;
            gap: 15px !important;
          }

          /* AI Character adjustments */
          .ai-character-panel > div {
            padding: 20px !important;
            border-radius: 20px !important;
          }

          .ai-character-panel h2 {
            font-size: 20px !important;
          }

          .ai-character-panel p {
            font-size: 14px !important;
          }

          .ai-character-panel button {
            padding: 12px 24px !important;
            font-size: 14px !important;
          }

          /* Chat Interface adjustments */
          .chat-header {
            padding: 15px 20px !important;
            border-radius: 15px !important;
          }

          .chat-header h3 {
            font-size: 16px !important;
          }

          .chat-header p {
            font-size: 12px !important;
          }

          .conversation-history {
            padding: 20px !important;
            border-radius: 15px !important;
            min-height: 300px !important;
          }

          .message-bubble {
            padding: 12px 16px !important;
            font-size: 14px !important;
            border-radius: 18px !important;
          }

          .input-controls {
            padding: 15px !important;
            border-radius: 15px !important;
            gap: 10px !important;
          }

          .input-controls input {
            padding: 12px 16px !important;
            font-size: 14px !important;
            border-radius: 12px !important;
          }

          .input-controls button {
            width: 45px !important;
            height: 45px !important;
            border-radius: 12px !important;
            font-size: 18px !important;
          }

          /* Voice amplitude waves mobile */
          .voice-waves {
            height: 60px !important;
            padding: 15px !important;
          }

          .voice-waves > div {
            width: 3px !important;
          }
        }

        /* Tablet Responsive Styles */
        @media (min-width: 769px) and (max-width: 1024px) {
          .voice-main-content {
            padding: 100px 15px 30px !important;
            gap: 30px !important;
          }

          .ai-character-panel {
            width: 350px !important;
          }
        }

        /* Large Screen Optimizations */
        @media (min-width: 1400px) {
          .voice-main-content {
            max-width: 1600px !important;
            gap: 50px !important;
          }

          .ai-character-panel {
            width: 450px !important;
          }
        }

        /* Animation Keyframes */
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-10px);
          }
          60% {
            transform: translateY(-5px);
          }
        }

        @keyframes wave {
          0% { height: 15px; }
          50% { height: 35px; }
          100% { height: 15px; }
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
};

export default VoiceAssistantPage;
