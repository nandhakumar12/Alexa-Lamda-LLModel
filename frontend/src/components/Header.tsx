import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface HeaderProps {
  onAuthClick: () => void;
  onProfileClick: () => void;
  onSettingsClick: () => void;
  onHomeClick: () => void;
  currentPage: string;
}

const Header: React.FC<HeaderProps> = ({
  onAuthClick,
  onProfileClick,
  onSettingsClick,
  onHomeClick,
  currentPage
}) => {
  const { user, isAuthenticated, signOut } = useAuth();
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const handleSignOut = async () => {
    try {
      await signOut();
      setShowProfileMenu(false);
    } catch (error) {
      console.error('Sign out error:', error);
    }
  };

  return (
    <header style={{
      background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(59, 130, 246, 0.2)',
      padding: '12px 24px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
    }}>
      {/* Left Side - Logo and Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
        {/* Logo */}
        <div
          onClick={onHomeClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          <div style={{
            width: '40px',
            height: '40px',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)'
          }}>
            🤖
          </div>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '20px',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              AI Assistant
            </h1>
            <p style={{
              margin: 0,
              fontSize: '12px',
              color: 'rgba(255, 255, 255, 0.6)',
              fontWeight: '400'
            }}>
              Powered by Claude Haiku
            </p>
          </div>
        </div>

        {/* Navigation Menu */}
        {isAuthenticated && (
          <nav style={{ display: 'flex', gap: '24px' }}>
            <button
              onClick={onHomeClick}
              style={{
                background: currentPage === 'home' ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                border: 'none',
                color: currentPage === 'home' ? '#3b82f6' : 'rgba(255, 255, 255, 0.8)',
                padding: '8px 16px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                if (currentPage !== 'home') {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.color = '#ffffff';
                }
              }}
              onMouseLeave={(e) => {
                if (currentPage !== 'home') {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
                }
              }}
            >
              🏠 Home
            </button>
            <button
              onClick={onSettingsClick}
              style={{
                background: currentPage === 'settings' ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                border: 'none',
                color: currentPage === 'settings' ? '#3b82f6' : 'rgba(255, 255, 255, 0.8)',
                padding: '8px 16px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                if (currentPage !== 'settings') {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.color = '#ffffff';
                }
              }}
              onMouseLeave={(e) => {
                if (currentPage !== 'settings') {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
                }
              }}
            >
              ⚙️ Settings
            </button>
          </nav>
        )}
      </div>

      {/* Right Side - Social Media and Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Social Media Links */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <a
            href="https://youtube.com/@nandhakumar"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              width: '36px',
              height: '36px',
              background: 'rgba(255, 0, 0, 0.1)',
              border: '1px solid rgba(255, 0, 0, 0.3)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ff0000',
              textDecoration: 'none',
              fontSize: '16px',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 0, 0, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(255, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 0, 0, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            📺
          </a>
          <a
            href="https://linkedin.com/in/nandhakumar"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              width: '36px',
              height: '36px',
              background: 'rgba(0, 119, 181, 0.1)',
              border: '1px solid rgba(0, 119, 181, 0.3)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#0077b5',
              textDecoration: 'none',
              fontSize: '16px',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(0, 119, 181, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 119, 181, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(0, 119, 181, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            💼
          </a>
          <a
            href="https://github.com/nandhakumar"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              width: '36px',
              height: '36px',
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              textDecoration: 'none',
              fontSize: '16px',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(255, 255, 255, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            💻
          </a>
        </div>

        {/* Authentication/Profile Section */}
        {isAuthenticated ? (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              style={{
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                borderRadius: '12px',
                padding: '8px 12px',
                color: '#ffffff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{
                width: '28px',
                height: '28px',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px'
              }}>
                👤
              </div>
              <span>{user?.email?.split('@')[0] || 'User'}</span>
              <span style={{ fontSize: '10px', opacity: 0.7 }}>▼</span>
            </button>

            {/* Profile Dropdown */}
            {showProfileMenu && (
              <div style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '8px',
                background: 'rgba(15, 15, 35, 0.95)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(59, 130, 246, 0.2)',
                borderRadius: '12px',
                padding: '8px',
                minWidth: '200px',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
                zIndex: 1001
              }}>
                <button
                  onClick={() => {
                    onProfileClick();
                    setShowProfileMenu(false);
                  }}
                  style={{
                    width: '100%',
                    background: 'transparent',
                    border: 'none',
                    color: 'rgba(255, 255, 255, 0.8)',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    textAlign: 'left',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                    e.currentTarget.style.color = '#ffffff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
                  }}
                >
                  👤 Profile
                </button>
                <button
                  onClick={handleSignOut}
                  style={{
                    width: '100%',
                    background: 'transparent',
                    border: 'none',
                    color: 'rgba(255, 255, 255, 0.8)',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    textAlign: 'left',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                    e.currentTarget.style.color = '#ef4444';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
                  }}
                >
                  🚪 Sign Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={onAuthClick}
            style={{
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              border: 'none',
              borderRadius: '12px',
              padding: '10px 20px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              transition: 'all 0.3s ease',
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
            Sign In / Sign Up
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
