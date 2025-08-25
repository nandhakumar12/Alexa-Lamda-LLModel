import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import { Toaster } from 'react-hot-toast';
import { HelmetProvider } from 'react-helmet-async';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';

// Components
import Header from './components/Header';
import ChatUI from './components/ChatUI';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorBoundary from './components/ErrorBoundary';

// Services
import { configureAmplify } from './services/amplify';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { VoiceProvider } from './contexts/VoiceContext';

// Styles
import '@aws-amplify/ui-react/styles.css';
import './App.css';

// Theme configuration
const theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#17a2b8',
    light: '#f8f9fa',
    dark: '#343a40',
    background: '#ffffff',
    surface: '#f8f9fa',
    text: '#212529',
    textSecondary: '#6c757d',
    border: '#dee2e6',
    shadow: 'rgba(0, 0, 0, 0.1)',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem',
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },
  breakpoints: {
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px',
  },
};

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }

  .amplify-authenticator {
    --amplify-colors-brand-primary-60: ${props => props.theme.colors.primary};
    --amplify-colors-brand-primary-80: ${props => props.theme.colors.primary};
    --amplify-colors-brand-primary-90: ${props => props.theme.colors.primary};
    --amplify-colors-brand-primary-100: ${props => props.theme.colors.primary};
  }

  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.light};
  }

  ::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.secondary};
    border-radius: ${props => props.theme.borderRadius.full};
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${props => props.theme.colors.dark};
  }
`;

// Styled components
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: ${props => props.theme.colors.background};
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: ${props => props.theme.spacing.md};
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;

  @media (max-width: ${props => props.theme.breakpoints.md}) {
    padding: ${props => props.theme.spacing.sm};
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
`;

// Main App component
const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [isConfigured, setIsConfigured] = useState(false);

  useEffect(() => {
    const initializeApp = async () => {
      try {
        await configureAmplify();
        setIsConfigured(true);
      } catch (error) {
        console.error('Failed to configure Amplify:', error);
      }
    };

    initializeApp();
  }, []);

  if (!isConfigured || loading) {
    return (
      <LoadingContainer>
        <LoadingSpinner size="large" />
      </LoadingContainer>
    );
  }

  return (
    <AppContainer>
      <Header />
      <MainContent>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ChatUI />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </MainContent>
    </AppContainer>
  );
};

// Authenticated app wrapper
const AuthenticatedApp: React.FC = () => {
  return (
    <VoiceProvider>
      <Router>
        <AppContent />
      </Router>
    </VoiceProvider>
  );
};

// Main App component with authentication
const App: React.FC = () => {
  return (
    <HelmetProvider>
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <ErrorBoundary>
          <AuthProvider>
            <Authenticator.Provider>
              <Authenticator
                hideSignUp={false}
                variation="modal"
                components={{
                  Header() {
                    return (
                      <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <h1>🎤 Voice Assistant AI</h1>
                        <p>Your intelligent voice companion</p>
                      </div>
                    );
                  },
                }}
                formFields={{
                  signIn: {
                    username: {
                      placeholder: 'Enter your email',
                      isRequired: true,
                      label: 'Email',
                    },
                  },
                  signUp: {
                    username: {
                      placeholder: 'Enter your email',
                      isRequired: true,
                      label: 'Email',
                      order: 1,
                    },
                    email: {
                      placeholder: 'Enter your email',
                      isRequired: true,
                      label: 'Email',
                      order: 2,
                    },
                    password: {
                      placeholder: 'Enter your password',
                      isRequired: true,
                      label: 'Password',
                      order: 3,
                    },
                    confirm_password: {
                      placeholder: 'Confirm your password',
                      isRequired: true,
                      label: 'Confirm Password',
                      order: 4,
                    },
                  },
                }}
              >
                {({ signOut, user }) => (
                  <AuthenticatedApp />
                )}
              </Authenticator>
            </Authenticator.Provider>
          </AuthProvider>
        </ErrorBoundary>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: theme.colors.surface,
              color: theme.colors.text,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              boxShadow: theme.shadows.md,
            },
            success: {
              iconTheme: {
                primary: theme.colors.success,
                secondary: theme.colors.background,
              },
            },
            error: {
              iconTheme: {
                primary: theme.colors.danger,
                secondary: theme.colors.background,
              },
            },
          }}
        />
      </ThemeProvider>
    </HelmetProvider>
  );
};

export default App;
