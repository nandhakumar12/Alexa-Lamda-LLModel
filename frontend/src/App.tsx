import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Amplify, Auth } from 'aws-amplify';
import './App.css';

// Import pages
import LandingPage from './pages/LandingPage';
import ProjectPage from './pages/ProjectPage';
import VoiceAssistantPage from './pages/VoiceAssistantPage';
import AuthPage from './pages/AuthPage';

// Configure Amplify with your actual AWS resources
Amplify.configure({
  Auth: {
    region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
    userPoolId: process.env.REACT_APP_COGNITO_USER_POOL_ID || '',
    userPoolWebClientId: process.env.REACT_APP_COGNITO_CLIENT_ID || '',
    identityPoolId: process.env.REACT_APP_COGNITO_IDENTITY_POOL_ID || '',
    mandatorySignIn: false,
    authenticationFlowType: 'USER_SRP_AUTH'
  },
  API: {
    endpoints: [
      {
        name: 'ai-assistant-api',
        endpoint: process.env.REACT_APP_API_GATEWAY_URL || 'https://temp.execute-api.us-east-1.amazonaws.com/prod',
        region: process.env.REACT_APP_AWS_REGION || 'us-east-1'
      }
    ]
  }
});

// Main App Component
const App: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      // Check if auth bypass is enabled
      const skipAuth = process.env.REACT_APP_SKIP_AUTH === 'true';

      if (skipAuth) {
        console.log('🔓 Auth bypass enabled - creating mock user');
        setUser({
          username: 'test-user',
          attributes: {
            email: 'test@example.com',
            name: 'Test User'
          }
        });
      } else {
        const currentUser = await Auth.currentAuthenticatedUser();
        setUser(currentUser);
      }
    } catch (error) {
      console.log('No authenticated user:', error);

      // If auth bypass is enabled, still create mock user
      const skipAuth = process.env.REACT_APP_SKIP_AUTH === 'true';
      if (skipAuth) {
        console.log('🔓 Auth bypass enabled - creating mock user after auth error');
        setUser({
          username: 'test-user',
          attributes: {
            email: 'test@example.com',
            name: 'Test User'
          }
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await Auth.signOut();
      setUser(null);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #1a0b2e 0%, #16213e 50%, #0f3460 100%)',
        color: '#ffffff'
      }}>
        <div style={{
          textAlign: 'center'
        }}>
          <div style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #a855f7, #ec4899)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '30px',
            margin: '0 auto 20px',
            animation: 'pulse 2s ease-in-out infinite'
          }}>
            🤖
          </div>
          <h2 style={{ margin: 0, fontSize: '24px', fontWeight: '600' }}>
            Loading Nandhakumar's AI Assistant...
          </h2>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(15, 15, 35, 0.9)',
            color: '#ffffff',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: '12px'
          }
        }}
      />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/project" element={<ProjectPage />} />
        <Route path="/auth" element={<AuthPage onAuthSuccess={checkAuthState} />} />
        <Route
          path="/assistant"
          element={
            user ? (
              <VoiceAssistantPage user={user} onSignOut={handleSignOut} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Global Styles */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }

        @keyframes blink {
          0%, 90%, 100% { opacity: 1; }
          95% { opacity: 0.1; }
        }

        @keyframes wave {
          0%, 100% { transform: rotate(0deg); }
          25% { transform: rotate(10deg); }
          75% { transform: rotate(-10deg); }
        }

        @keyframes rotate {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }

        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-10px); }
          60% { transform: translateY(-5px); }
        }

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

        @keyframes blastFlower {
          0% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(0) rotate(0deg);
          }
          50% {
            opacity: 1;
            transform: translate(
              calc(-50% + 400px),
              calc(-50% + 400px)
            ) scale(1.5) rotate(180deg);
          }
          100% {
            opacity: 0;
            transform: translate(
              calc(-50% + 600px),
              calc(-50% + 600px)
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

        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
            sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }

        ::-webkit-scrollbar {
          width: 8px;
        }

        ::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
          background: rgba(168, 85, 247, 0.5);
          border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: rgba(168, 85, 247, 0.7);
        }
      `}</style>
    </Router>
  );
};

export default App;
