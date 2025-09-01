import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { signIn, signUp, confirmSignUp, resendConfirmationCode, forgotPassword, forgotPasswordSubmit, loading } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup' | 'confirm' | 'forgot' | 'reset'>('signin');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    code: '',
    newPassword: '',
    firstName: '',
    lastName: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      switch (mode) {
        case 'signin':
          await signIn(formData.email, formData.password);
          onClose();
          break;

        case 'signup':
          if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
          }
          await signUp(formData.email, formData.password, {
            given_name: formData.firstName,
            family_name: formData.lastName
          });
          setMode('confirm');
          setSuccess('Account created! Please check your email for verification code.');
          break;

        case 'confirm':
          await confirmSignUp(formData.email, formData.code);
          setSuccess('Email verified! You can now sign in.');
          setMode('signin');
          break;

        case 'forgot':
          await forgotPassword(formData.email);
          setMode('reset');
          setSuccess('Reset code sent to your email.');
          break;

        case 'reset':
          await forgotPasswordSubmit(formData.email, formData.code, formData.newPassword);
          setSuccess('Password reset successfully! You can now sign in.');
          setMode('signin');
          break;
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    }
  };

  const handleResendCode = async () => {
    try {
      await resendConfirmationCode(formData.email);
      setSuccess('Verification code resent to your email.');
    } catch (err: any) {
      setError(err.message || 'Failed to resend code');
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(10px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
      padding: '20px'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)',
        borderRadius: '20px',
        padding: '40px',
        width: '100%',
        maxWidth: '450px',
        border: '1px solid rgba(59, 130, 246, 0.2)',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
        position: 'relative'
      }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'transparent',
            border: 'none',
            color: 'rgba(255, 255, 255, 0.6)',
            fontSize: '24px',
            cursor: 'pointer',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
            e.currentTarget.style.color = '#ffffff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = 'rgba(255, 255, 255, 0.6)';
          }}
        >
          ×
        </button>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
            borderRadius: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '28px',
            margin: '0 auto 16px',
            boxShadow: '0 8px 25px rgba(59, 130, 246, 0.3)'
          }}>
            🤖
          </div>
          <h2 style={{
            margin: 0,
            fontSize: '24px',
            fontWeight: '700',
            color: '#ffffff',
            marginBottom: '8px'
          }}>
            {mode === 'signin' && 'Welcome Back'}
            {mode === 'signup' && 'Create Account'}
            {mode === 'confirm' && 'Verify Email'}
            {mode === 'forgot' && 'Reset Password'}
            {mode === 'reset' && 'Set New Password'}
          </h2>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: 'rgba(255, 255, 255, 0.6)'
          }}>
            {mode === 'signin' && 'Sign in to access your AI assistant'}
            {mode === 'signup' && 'Join the AI revolution today'}
            {mode === 'confirm' && 'Enter the verification code sent to your email'}
            {mode === 'forgot' && 'Enter your email to reset password'}
            {mode === 'reset' && 'Enter the code and your new password'}
          </p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '20px',
            color: '#ef4444',
            fontSize: '14px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}

        {success && (
          <div style={{
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '20px',
            color: '#22c55e',
            fontSize: '14px',
            textAlign: 'center'
          }}>
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Email Field */}
          {(mode === 'signin' || mode === 'signup' || mode === 'confirm' || mode === 'forgot' || mode === 'reset') && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)'
              }}>
                Email Address
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#ffffff',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }}
                placeholder="Enter your email"
              />
            </div>
          )}

          {/* Name Fields for Signup */}
          {mode === 'signup' && (
            <>
              <div style={{ display: 'flex', gap: '12px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'rgba(255, 255, 255, 0.8)'
                  }}>
                    First Name
                  </label>
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    required
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      color: '#ffffff',
                      fontSize: '14px',
                      outline: 'none',
                      transition: 'all 0.3s ease',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#3b82f6';
                      e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                    }}
                    placeholder="First name"
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: 'rgba(255, 255, 255, 0.8)'
                  }}>
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    required
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      color: '#ffffff',
                      fontSize: '14px',
                      outline: 'none',
                      transition: 'all 0.3s ease',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#3b82f6';
                      e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                    }}
                    placeholder="Last name"
                  />
                </div>
              </div>
            </>
          )}
          {/* Password Field */}
          {(mode === 'signin' || mode === 'signup') && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)'
              }}>
                Password
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#ffffff',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }}
                placeholder="Enter your password"
              />
            </div>
          )}

          {/* Confirm Password Field */}
          {mode === 'signup' && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)'
              }}>
                Confirm Password
              </label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#ffffff',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }}
                placeholder="Confirm your password"
              />
            </div>
          )}

          {/* Verification Code Field */}
          {(mode === 'confirm' || mode === 'reset') && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)'
              }}>
                Verification Code
              </label>
              <input
                type="text"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#ffffff',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }}
                placeholder="Enter verification code"
              />
            </div>
          )}

          {/* New Password Field */}
          {mode === 'reset' && (
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'rgba(255, 255, 255, 0.8)'
              }}>
                New Password
              </label>
              <input
                type="password"
                value={formData.newPassword}
                onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  color: '#ffffff',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'all 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.05)';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }}
                placeholder="Enter new password"
              />
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              background: loading ? 'rgba(59, 130, 246, 0.5)' : 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              border: 'none',
              borderRadius: '12px',
              color: '#ffffff',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: loading ? 'none' : '0 4px 15px rgba(59, 130, 246, 0.3)',
              marginTop: '8px'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(59, 130, 246, 0.3)';
              }
            }}
          >
            {loading ? 'Processing...' : (
              mode === 'signin' ? 'Sign In' :
              mode === 'signup' ? 'Create Account' :
              mode === 'confirm' ? 'Verify Email' :
              mode === 'forgot' ? 'Send Reset Code' :
              'Reset Password'
            )}
          </button>

          {/* Additional Actions */}
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            {mode === 'signin' && (
              <>
                <button
                  type="button"
                  onClick={() => setMode('forgot')}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#3b82f6',
                    fontSize: '14px',
                    cursor: 'pointer',
                    textDecoration: 'underline',
                    marginBottom: '12px'
                  }}
                >
                  Forgot Password?
                </button>
                <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '14px' }}>
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => setMode('signup')}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#3b82f6',
                      fontSize: '14px',
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                  >
                    Sign Up
                  </button>
                </div>
              </>
            )}

            {mode === 'signup' && (
              <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '14px' }}>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setMode('signin')}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#3b82f6',
                    fontSize: '14px',
                    cursor: 'pointer',
                    textDecoration: 'underline'
                  }}
                >
                  Sign In
                </button>
              </div>
            )}

            {mode === 'confirm' && (
              <button
                type="button"
                onClick={handleResendCode}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#3b82f6',
                  fontSize: '14px',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Resend Code
              </button>
            )}

            {(mode === 'forgot' || mode === 'reset') && (
              <button
                type="button"
                onClick={() => setMode('signin')}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#3b82f6',
                  fontSize: '14px',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Back to Sign In
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthModal;
