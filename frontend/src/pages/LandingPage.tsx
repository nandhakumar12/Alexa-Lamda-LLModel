import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [showBlast, setShowBlast] = useState(true);

  useEffect(() => {
    // Show blast animation for 3 seconds
    const timer = setTimeout(() => {
      setShowBlast(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  if (showBlast) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'linear-gradient(135deg, #1a0b2e 0%, #16213e 50%, #0f3460 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        overflow: 'hidden'
      }}>
        {/* Blast Flowers Animation */}
        {[...Array(50)].map((_, i) => (
          <div
            key={`flower-${i}`}
            style={{
              position: 'absolute',
              fontSize: `${Math.random() * 30 + 20}px`,
              color: `hsl(${Math.random() * 360}, 70%, 60%)`,
              animation: `blastFlower ${2 + Math.random() * 2}s ease-out forwards`,
              animationDelay: `${Math.random() * 1}s`,
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
              opacity: 0
            }}
          >
            🌸
          </div>
        ))}

        {/* Welcome Text */}
        <div style={{
          textAlign: 'center',
          zIndex: 10,
          animation: 'fadeInScale 2s ease-out forwards',
          opacity: 0
        }}>
          <div style={{
            fontSize: '80px',
            marginBottom: '20px',
            animation: 'bounce 2s ease-in-out infinite'
          }}>
            🤖
          </div>
          <h1 style={{
            fontSize: '48px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 0 20px 0',
            textAlign: 'center'
          }}>
            Welcome to Nandhakumar's AI Assistant!
          </h1>
          <p style={{
            fontSize: '24px',
            color: 'rgba(255,255,255,0.8)',
            margin: 0
          }}>
            Your intelligent companion is ready to help
          </p>
        </div>

        <style>{`
          @keyframes blastFlower {
            0% {
              opacity: 1;
              transform: translate(-50%, -50%) scale(0) rotate(0deg);
            }
            50% {
              opacity: 1;
              transform: translate(
                calc(-50% + ${Math.random() * 800 - 400}px), 
                calc(-50% + ${Math.random() * 800 - 400}px)
              ) scale(1.5) rotate(180deg);
            }
            100% {
              opacity: 0;
              transform: translate(
                calc(-50% + ${Math.random() * 1200 - 600}px), 
                calc(-50% + ${Math.random() * 1200 - 600}px)
              ) scale(0.5) rotate(360deg);
            }
          }
          
          @keyframes fadeInScale {
            0% {
              opacity: 0;
              transform: scale(0.8);
            }
            100% {
              opacity: 1;
              transform: scale(1);
            }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a0b2e 0%, #16213e 50%, #0f3460 100%)',
      color: '#ffffff',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Particles */}
      {[...Array(30)].map((_, i) => (
        <div
          key={`particle-${i}`}
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

      {/* Navigation */}
      <nav style={{
        position: 'fixed',
        top: '10px',
        left: '10px',
        right: '10px',
        zIndex: 10,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '10px'
      }}>
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
              Powered by AWS & Claude
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '15px' }}>
          <button
            onClick={() => navigate('/project')}
            style={{
              background: 'rgba(168, 85, 247, 0.2)',
              border: '1px solid rgba(168, 85, 247, 0.4)',
              borderRadius: '15px',
              padding: '12px 24px',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            About Project
          </button>
          <button
            onClick={() => navigate('/auth')}
            style={{
              background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
              border: 'none',
              borderRadius: '15px',
              padding: '12px 24px',
              color: 'white',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="main-content" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '100px 20px 20px',
        textAlign: 'center'
      }}>
        <div style={{
          maxWidth: '800px',
          animation: 'fadeInUp 1s ease-out'
        }}>
          <div className="ai-emoji">
            🤖
          </div>
          
          <h1 className="main-title">
            Nandhakumar's AI Assistant
          </h1>

          <p className="main-description">
            Experience the future of AI conversation with advanced voice recognition,
            natural language processing, and seamless AWS integration.
          </p>

          <div className="button-container" style={{
            display: 'flex',
            gap: '20px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => navigate('/auth')}
              style={{
                background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '25px',
                padding: '20px 40px',
                fontSize: '18px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 30px rgba(168, 85, 247, 0.4)'
              }}
            >
              🚀 Start Chatting
            </button>

            <button
              onClick={() => navigate('/project')}
              style={{
                background: 'rgba(255,255,255,0.1)',
                color: 'white',
                border: '2px solid rgba(168, 85, 247, 0.5)',
                borderRadius: '25px',
                padding: '18px 38px',
                fontSize: '18px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
            >
              📖 Learn More
            </button>
          </div>
        </div>
      </div>

      {/* Responsive CSS */}
      <style>{`
        .ai-emoji {
          font-size: 120px;
          margin-bottom: 30px;
          animation: bounce 3s ease-in-out infinite;
        }

        .main-title {
          font-size: 64px;
          font-weight: 700;
          background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin: 0 0 30px 0;
          line-height: 1.2;
        }

        .main-description {
          font-size: 24px;
          color: rgba(255,255,255,0.8);
          margin: 0 0 50px 0;
          line-height: 1.6;
        }

        /* Mobile Responsive Styles */
        @media (max-width: 768px) {
          .ai-emoji {
            font-size: 80px;
            margin-bottom: 20px;
          }

          .main-title {
            font-size: 36px;
            margin: 0 0 20px 0;
          }

          .main-description {
            font-size: 18px;
            margin: 0 0 30px 0;
            padding: 0 10px;
          }

          nav {
            top: 5px !important;
            left: 5px !important;
            right: 5px !important;
            flex-direction: column;
            gap: 10px;
          }

          nav > div {
            padding: 8px 16px !important;
          }

          nav button {
            padding: 8px 16px !important;
            font-size: 14px !important;
          }
        }

        @media (max-width: 480px) {
          .ai-emoji {
            font-size: 60px;
            margin-bottom: 15px;
          }

          .main-title {
            font-size: 28px;
            margin: 0 0 15px 0;
          }

          .main-description {
            font-size: 16px;
            margin: 0 0 25px 0;
            padding: 0 15px;
          }

          .main-content {
            padding: 80px 10px 20px !important;
          }

          .button-container {
            flex-direction: column !important;
            gap: 15px !important;
          }

          .button-container button {
            width: 100% !important;
            max-width: 280px !important;
            padding: 16px 24px !important;
            font-size: 16px !important;
          }
        }

        /* Tablet Responsive Styles */
        @media (min-width: 769px) and (max-width: 1024px) {
          .ai-emoji {
            font-size: 100px;
          }

          .main-title {
            font-size: 48px;
          }

          .main-description {
            font-size: 20px;
          }
        }

        /* Animation Keyframes */
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

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

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
