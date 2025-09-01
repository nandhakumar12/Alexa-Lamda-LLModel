import React from 'react';
import { useAuth } from '../contexts/AuthContext';

interface HomePageProps {
  onStartChat: () => void;
  onOpenSettings: () => void;
  conversations: any[];
  musicStatus: { isPlaying: boolean; currentSong: any };
  isLLMMode: boolean;
}

const HomePage: React.FC<HomePageProps> = ({
  onStartChat,
  onOpenSettings,
  conversations,
  musicStatus,
  isLLMMode
}) => {
  const { user } = useAuth();

  const FeatureCard: React.FC<{
    title: string;
    description: string;
    icon: string;
    onClick?: () => void;
    gradient: string;
  }> = ({ title, description, icon, onClick, gradient }) => (
    <div
      onClick={onClick}
      style={{
        background: `linear-gradient(135deg, ${gradient})`,
        borderRadius: '20px',
        padding: '32px',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(-8px)';
          e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.3)';
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = 'none';
        }
      }}
    >
      <div style={{
        fontSize: '48px',
        marginBottom: '16px',
        display: 'block'
      }}>
        {icon}
      </div>
      <h3 style={{
        margin: 0,
        fontSize: '20px',
        fontWeight: '700',
        color: '#ffffff',
        marginBottom: '8px'
      }}>
        {title}
      </h3>
      <p style={{
        margin: 0,
        fontSize: '14px',
        color: 'rgba(255, 255, 255, 0.8)',
        lineHeight: '1.5'
      }}>
        {description}
      </p>
      
      {/* Floating particles */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        overflow: 'hidden'
      }}>
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              width: '4px',
              height: '4px',
              background: 'rgba(255, 255, 255, 0.3)',
              borderRadius: '50%',
              left: `${20 + i * 30}%`,
              top: `${20 + i * 20}%`,
              animation: `float ${3 + i * 0.5}s ease-in-out infinite`,
              animationDelay: `${i * 0.5}s`
            }}
          />
        ))}
      </div>
    </div>
  );

  const StatCard: React.FC<{
    title: string;
    value: string;
    icon: string;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      textAlign: 'center'
    }}>
      <div style={{
        width: '48px',
        height: '48px',
        background: color,
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '24px',
        margin: '0 auto 16px'
      }}>
        {icon}
      </div>
      <div style={{
        fontSize: '24px',
        fontWeight: '700',
        color: '#ffffff',
        marginBottom: '4px'
      }}>
        {value}
      </div>
      <div style={{
        fontSize: '14px',
        color: 'rgba(255, 255, 255, 0.6)'
      }}>
        {title}
      </div>
    </div>
  );

  return (
    <div style={{
      padding: '32px',
      background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)',
      minHeight: '100vh',
      color: '#ffffff'
    }}>
      {/* Hero Section */}
      <div style={{
        textAlign: 'center',
        marginBottom: '48px',
        position: 'relative'
      }}>
        <div style={{
          width: '120px',
          height: '120px',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '60px',
          margin: '0 auto 24px',
          boxShadow: '0 20px 40px rgba(59, 130, 246, 0.3)',
          animation: 'float 3s ease-in-out infinite'
        }}>
          🤖
        </div>
        
        <h1 style={{
          margin: 0,
          fontSize: '48px',
          fontWeight: '700',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '16px'
        }}>
          Welcome{user ? `, ${user.attributes?.given_name || user.email?.split('@')[0]}` : ''}!
        </h1>
        
        <p style={{
          fontSize: '20px',
          color: 'rgba(255, 255, 255, 0.7)',
          maxWidth: '600px',
          margin: '0 auto 32px',
          lineHeight: '1.6'
        }}>
          Your advanced AI assistant powered by Claude Haiku is ready to help you with anything you need.
          From answering questions to controlling music, I'm here to make your life easier.
        </p>

        <button
          onClick={onStartChat}
          style={{
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            border: 'none',
            borderRadius: '16px',
            padding: '16px 32px',
            color: '#ffffff',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: '0 8px 25px rgba(59, 130, 246, 0.3)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '12px'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 12px 35px rgba(59, 130, 246, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 8px 25px rgba(59, 130, 246, 0.3)';
          }}
        >
          <span>🚀</span>
          Start Chatting Now
        </button>
      </div>

      {/* Stats Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '24px',
        marginBottom: '48px',
        maxWidth: '800px',
        margin: '0 auto 48px'
      }}>
        <StatCard
          title="Conversations"
          value={conversations.length.toString()}
          icon="💬"
          color="linear-gradient(135deg, #3b82f6, #8b5cf6)"
        />
        <StatCard
          title="AI Mode"
          value={isLLMMode ? "Advanced" : "Basic"}
          icon="🤖"
          color="linear-gradient(135deg, #10b981, #059669)"
        />
        <StatCard
          title="Music Status"
          value={musicStatus.isPlaying ? "Playing" : "Ready"}
          icon="🎵"
          color="linear-gradient(135deg, #f59e0b, #d97706)"
        />
        <StatCard
          title="Voice Ready"
          value="Active"
          icon="🎤"
          color="linear-gradient(135deg, #ef4444, #dc2626)"
        />
      </div>

      {/* Features Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <FeatureCard
          title="Voice Conversations"
          description="Talk naturally with your AI assistant using advanced voice recognition and text-to-speech technology."
          icon="🎤"
          onClick={onStartChat}
          gradient="rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)"
        />

        <FeatureCard
          title="Music Control"
          description="Control your music playback, discover new songs, and get recommendations tailored to your taste."
          icon="🎵"
          gradient="rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.1)"
        />

        <FeatureCard
          title="Smart Assistance"
          description="Get help with daily tasks, answer questions, solve problems, and boost your productivity."
          icon="🧠"
          gradient="rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1)"
        />

        <FeatureCard
          title="Personalized Experience"
          description="Customize your AI assistant's personality, voice settings, and preferences to match your style."
          icon="⚙️"
          onClick={onOpenSettings}
          gradient="rgba(139, 92, 246, 0.1), rgba(168, 85, 247, 0.1)"
        />

        <FeatureCard
          title="Natural Language"
          description="Communicate in natural language with advanced understanding and context-aware responses."
          icon="💭"
          gradient="rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1)"
        />

        <FeatureCard
          title="Always Learning"
          description="Your assistant gets better over time, learning from interactions to provide more helpful responses."
          icon="📚"
          gradient="rgba(99, 102, 241, 0.1), rgba(79, 70, 229, 0.1)"
        />
      </div>

      {/* Recent Activity */}
      {conversations.length > 0 && (
        <div style={{
          marginTop: '48px',
          maxWidth: '800px',
          margin: '48px auto 0'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '24px',
            textAlign: 'center'
          }}>
            Recent Conversations
          </h2>
          <div style={{
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            {conversations.slice(-3).map((conv, index) => (
              <div
                key={conv.id}
                style={{
                  padding: '16px 0',
                  borderBottom: index < 2 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none'
                }}
              >
                <div style={{
                  fontSize: '14px',
                  color: 'rgba(255, 255, 255, 0.6)',
                  marginBottom: '4px'
                }}>
                  {conv.time}
                </div>
                <div style={{
                  fontSize: '16px',
                  color: '#ffffff',
                  marginBottom: '8px'
                }}>
                  You: {conv.user.length > 60 ? conv.user.substring(0, 60) + '...' : conv.user}
                </div>
                <div style={{
                  fontSize: '14px',
                  color: 'rgba(255, 255, 255, 0.8)'
                }}>
                  AI: {conv.bot.length > 80 ? conv.bot.substring(0, 80) + '...' : conv.bot}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
};

export default HomePage;
