import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Auth } from 'aws-amplify';
import toast from 'react-hot-toast';

interface AuthPageProps {
  onAuthSuccess: () => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onAuthSuccess }) => {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(false);
  const [needsConfirmation, setNeedsConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    confirmationCode: '',
    name: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await Auth.signIn(formData.email, formData.password);
      toast.success('Welcome back!');
      onAuthSuccess();
      navigate('/assistant');
    } catch (error: any) {
      console.error('Sign in error:', error);
      if (error.code === 'UserNotConfirmedException') {
        setNeedsConfirmation(true);
        toast.error('Please confirm your account first');
      } else {
        toast.error(error.message || 'Failed to sign in');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      console.log('Attempting to sign up with:', { email: formData.email, name: formData.name });
      const result = await Auth.signUp({
        username: formData.email,
        password: formData.password,
        attributes: {
          email: formData.email,
          name: formData.name || formData.email.split('@')[0] // Use email prefix if name not provided
        }
      });

      console.log('Sign up result:', result);
      setNeedsConfirmation(true);
      toast.success('Please check your email for confirmation code');
    } catch (error: any) {
      console.error('Sign up error:', error);
      console.error('Error details:', {
        code: error.code,
        message: error.message,
        name: error.name
      });
      toast.error(error.message || 'Failed to sign up');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await Auth.confirmSignUp(formData.email, formData.confirmationCode);
      toast.success('Account confirmed! Please sign in.');
      setNeedsConfirmation(false);
      setIsSignUp(false);
    } catch (error: any) {
      console.error('Confirmation error:', error);
      toast.error(error.message || 'Failed to confirm account');
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      await Auth.resendSignUp(formData.email);
      toast.success('Confirmation code resent');
    } catch (error: any) {
      toast.error(error.message || 'Failed to resend code');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a0b2e 0%, #16213e 50%, #0f3460 100%)',
      color: '#ffffff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Particles */}
      {[...Array(20)].map((_, i) => (
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

      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          background: 'rgba(26, 11, 46, 0.8)',
          border: '1px solid rgba(168, 85, 247, 0.3)',
          borderRadius: '15px',
          padding: '12px 20px',
          color: 'white',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          backdropFilter: 'blur(20px)',
          zIndex: 10
        }}
      >
        ← Back to Home
      </button>

      {/* Auth Form */}
      <div style={{
        background: 'rgba(26, 11, 46, 0.8)',
        borderRadius: '20px',
        padding: '40px',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        backdropFilter: 'blur(20px)',
        width: '100%',
        maxWidth: '400px',
        boxShadow: '0 25px 50px rgba(168, 85, 247, 0.2)'
      }}>
        {/* Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '30px'
        }}>
          <div style={{
            fontSize: '60px',
            marginBottom: '15px'
          }}>
            🤖
          </div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: '0 0 10px 0'
          }}>
            {needsConfirmation ? 'Confirm Account' : isSignUp ? 'Create Account' : 'Welcome Back'}
          </h1>
          <p style={{
            color: 'rgba(255,255,255,0.7)',
            margin: 0,
            fontSize: '14px'
          }}>
            {needsConfirmation 
              ? 'Enter the confirmation code sent to your email'
              : isSignUp 
                ? 'Join Nandhakumar\'s AI Assistant'
                : 'Sign in to continue to your AI Assistant'
            }
          </p>
        </div>

        {/* Form */}
        <form onSubmit={needsConfirmation ? handleConfirmSignUp : isSignUp ? handleSignUp : handleSignIn}>
          {needsConfirmation ? (
            <div style={{ marginBottom: '20px' }}>
              <input
                type="text"
                name="confirmationCode"
                placeholder="Confirmation Code"
                value={formData.confirmationCode}
                onChange={handleInputChange}
                required
                style={{
                  width: '100%',
                  padding: '15px',
                  fontSize: '16px',
                  border: '1px solid rgba(168, 85, 247, 0.4)',
                  borderRadius: '10px',
                  background: 'rgba(26, 11, 46, 0.8)',
                  color: 'white',
                  outline: 'none',
                  transition: 'all 0.3s ease'
                }}
              />
              <button
                type="button"
                onClick={handleResendCode}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#a855f7',
                  fontSize: '12px',
                  cursor: 'pointer',
                  marginTop: '5px',
                  textDecoration: 'underline'
                }}
              >
                Resend code
              </button>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '20px' }}>
                <input
                  type="email"
                  name="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    fontSize: '16px',
                    border: '1px solid rgba(168, 85, 247, 0.4)',
                    borderRadius: '10px',
                    background: 'rgba(26, 11, 46, 0.8)',
                    color: 'white',
                    outline: 'none',
                    transition: 'all 0.3s ease'
                  }}
                />
              </div>

              {isSignUp && (
                <div style={{ marginBottom: '20px' }}>
                  <input
                    type="text"
                    name="name"
                    placeholder="Full Name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '15px',
                      fontSize: '16px',
                      border: '1px solid rgba(168, 85, 247, 0.4)',
                      borderRadius: '10px',
                      background: 'rgba(26, 11, 46, 0.8)',
                      color: 'white',
                      outline: 'none',
                      transition: 'all 0.3s ease'
                    }}
                  />
                </div>
              )}

              <div style={{ marginBottom: '20px' }}>
                <input
                  type="password"
                  name="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    fontSize: '16px',
                    border: '1px solid rgba(168, 85, 247, 0.4)',
                    borderRadius: '10px',
                    background: 'rgba(26, 11, 46, 0.8)',
                    color: 'white',
                    outline: 'none',
                    transition: 'all 0.3s ease'
                  }}
                />
              </div>

              {isSignUp && (
                <div style={{ marginBottom: '20px' }}>
                  <input
                    type="password"
                    name="confirmPassword"
                    placeholder="Confirm Password"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '15px',
                      fontSize: '16px',
                      border: '1px solid rgba(168, 85, 247, 0.4)',
                      borderRadius: '10px',
                      background: 'rgba(26, 11, 46, 0.8)',
                      color: 'white',
                      outline: 'none',
                      transition: 'all 0.3s ease'
                    }}
                  />
                </div>
              )}
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '15px',
              fontSize: '16px',
              fontWeight: '600',
              border: 'none',
              borderRadius: '10px',
              background: loading 
                ? 'rgba(168, 85, 247, 0.5)' 
                : 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
              color: 'white',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              marginBottom: '20px',
              boxShadow: '0 10px 30px rgba(168, 85, 247, 0.4)'
            }}
          >
            {loading 
              ? '⏳ Processing...' 
              : needsConfirmation 
                ? 'Confirm Account'
                : isSignUp 
                  ? 'Create Account' 
                  : 'Sign In'
            }
          </button>
        </form>

        {/* Toggle Sign Up/Sign In */}
        {!needsConfirmation && (
          <div style={{
            textAlign: 'center',
            fontSize: '14px',
            color: 'rgba(255,255,255,0.7)'
          }}>
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => setIsSignUp(!isSignUp)}
              style={{
                background: 'none',
                border: 'none',
                color: '#a855f7',
                cursor: 'pointer',
                textDecoration: 'underline',
                fontSize: '14px'
              }}
            >
              {isSignUp ? 'Sign In' : 'Sign Up'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthPage;
