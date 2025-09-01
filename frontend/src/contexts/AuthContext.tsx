import React, { createContext, useContext, useState, useEffect } from 'react';
import { Auth, Hub } from 'aws-amplify';
import { CognitoUser } from '@aws-amplify/auth';
import toast from 'react-hot-toast';

// Types
interface User {
  username: string;
  email: string;
  attributes: Record<string, any>;
  signInUserSession: any;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, attributes?: Record<string, string>) => Promise<void>;
  signOut: () => Promise<void>;
  confirmSignUp: (email: string, code: string) => Promise<void>;
  resendConfirmationCode: (email: string) => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  forgotPasswordSubmit: (email: string, code: string, newPassword: string) => Promise<void>;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
  updateUserAttributes: (attributes: Record<string, string>) => Promise<void>;
  refreshSession: () => Promise<void>;
}

interface AuthProviderProps {
  children: React.ReactNode;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated
  const isAuthenticated = !!user;

  // Initialize auth state
  useEffect(() => {
    checkAuthState();
    
    // Listen for auth events
    const hubListener = (data: any) => {
      const { payload } = data;
      
      switch (payload.event) {
        case 'signIn':
          console.log('User signed in');
          setUser(payload.data);
          toast.success('Successfully signed in!');
          break;
          
        case 'signUp':
          console.log('User signed up');
          toast.success('Account created! Please check your email for verification.');
          break;
          
        case 'signOut':
          console.log('User signed out');
          setUser(null);
          toast.success('Signed out successfully');
          break;
          
        case 'signIn_failure':
          console.error('Sign in failed', payload.data);
          toast.error('Sign in failed. Please check your credentials.');
          break;
          
        case 'tokenRefresh':
          console.log('Token refreshed');
          break;
          
        case 'tokenRefresh_failure':
          console.error('Token refresh failed', payload.data);
          toast.error('Session expired. Please sign in again.');
          setUser(null);
          break;
          
        case 'configured':
          console.log('Auth configured');
          break;
          
        default:
          console.log('Auth event:', payload.event);
      }
    };

    Hub.listen('auth', hubListener);

    return () => {
      Hub.remove('auth', hubListener);
    };
  }, []);

  // Check current auth state
  const checkAuthState = async () => {
    try {
      setLoading(true);
      const currentUser = await Auth.currentAuthenticatedUser();
      
      if (currentUser) {
        const userInfo = await getUserInfo(currentUser);
        setUser(userInfo);
      }
    } catch (error) {
      console.log('No authenticated user found');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Get user information
  const getUserInfo = async (cognitoUser: CognitoUser): Promise<User> => {
    const session = await Auth.currentSession();
    const attributes = await Auth.userAttributes(cognitoUser);
    
    const userAttributes: Record<string, any> = {};
    attributes.forEach(attr => {
      userAttributes[attr.Name] = attr.Value;
    });

    return {
      username: cognitoUser.getUsername(),
      email: userAttributes.email || '',
      attributes: userAttributes,
      signInUserSession: session,
    };
  };

  // Sign in
  const signIn = async (email: string, password: string): Promise<void> => {
    try {
      setLoading(true);
      const cognitoUser = await Auth.signIn(email, password);
      
      if (cognitoUser.challengeName === 'NEW_PASSWORD_REQUIRED') {
        throw new Error('New password required. Please contact support.');
      }
      
      const userInfo = await getUserInfo(cognitoUser);
      setUser(userInfo);
      
    } catch (error: any) {
      console.error('Sign in error:', error);
      
      switch (error.code) {
        case 'UserNotConfirmedException':
          throw new Error('Please verify your email address before signing in.');
        case 'NotAuthorizedException':
          throw new Error('Invalid email or password.');
        case 'UserNotFoundException':
          throw new Error('No account found with this email address.');
        case 'TooManyRequestsException':
          throw new Error('Too many failed attempts. Please try again later.');
        case 'PasswordResetRequiredException':
          throw new Error('Password reset required. Please reset your password.');
        default:
          throw new Error(error.message || 'Sign in failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Sign up
  const signUp = async (
    email: string, 
    password: string, 
    attributes: Record<string, string> = {}
  ): Promise<void> => {
    try {
      setLoading(true);
      
      const signUpAttributes = {
        email,
        ...attributes,
      };

      await Auth.signUp({
        username: email,
        password,
        attributes: signUpAttributes,
      });
      
    } catch (error: any) {
      console.error('Sign up error:', error);
      
      switch (error.code) {
        case 'UsernameExistsException':
          throw new Error('An account with this email already exists.');
        case 'InvalidPasswordException':
          throw new Error('Password does not meet requirements.');
        case 'InvalidParameterException':
          throw new Error('Invalid email address format.');
        case 'TooManyRequestsException':
          throw new Error('Too many requests. Please try again later.');
        default:
          throw new Error(error.message || 'Sign up failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Sign out
  const signOut = async (): Promise<void> => {
    try {
      setLoading(true);
      await Auth.signOut();
      setUser(null);
    } catch (error: any) {
      console.error('Sign out error:', error);
      throw new Error('Sign out failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Confirm sign up
  const confirmSignUp = async (email: string, code: string): Promise<void> => {
    try {
      setLoading(true);
      await Auth.confirmSignUp(email, code);
    } catch (error: any) {
      console.error('Confirm sign up error:', error);
      
      switch (error.code) {
        case 'CodeMismatchException':
          throw new Error('Invalid verification code.');
        case 'ExpiredCodeException':
          throw new Error('Verification code has expired.');
        case 'NotAuthorizedException':
          throw new Error('User is already confirmed.');
        default:
          throw new Error(error.message || 'Verification failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Resend confirmation code
  const resendConfirmationCode = async (email: string): Promise<void> => {
    try {
      setLoading(true);
      await Auth.resendSignUp(email);
      toast.success('Verification code sent to your email.');
    } catch (error: any) {
      console.error('Resend confirmation error:', error);
      throw new Error(error.message || 'Failed to resend verification code.');
    } finally {
      setLoading(false);
    }
  };

  // Forgot password
  const forgotPassword = async (email: string): Promise<void> => {
    try {
      setLoading(true);
      await Auth.forgotPassword(email);
      toast.success('Password reset code sent to your email.');
    } catch (error: any) {
      console.error('Forgot password error:', error);
      
      switch (error.code) {
        case 'UserNotFoundException':
          throw new Error('No account found with this email address.');
        case 'InvalidParameterException':
          throw new Error('Invalid email address format.');
        case 'TooManyRequestsException':
          throw new Error('Too many requests. Please try again later.');
        default:
          throw new Error(error.message || 'Failed to send reset code.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Forgot password submit
  const forgotPasswordSubmit = async (
    email: string, 
    code: string, 
    newPassword: string
  ): Promise<void> => {
    try {
      setLoading(true);
      await Auth.forgotPasswordSubmit(email, code, newPassword);
      toast.success('Password reset successfully!');
    } catch (error: any) {
      console.error('Forgot password submit error:', error);
      
      switch (error.code) {
        case 'CodeMismatchException':
          throw new Error('Invalid reset code.');
        case 'ExpiredCodeException':
          throw new Error('Reset code has expired.');
        case 'InvalidPasswordException':
          throw new Error('Password does not meet requirements.');
        default:
          throw new Error(error.message || 'Password reset failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Change password
  const changePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
    try {
      setLoading(true);
      const currentUser = await Auth.currentAuthenticatedUser();
      await Auth.changePassword(currentUser, oldPassword, newPassword);
      toast.success('Password changed successfully!');
    } catch (error: any) {
      console.error('Change password error:', error);
      
      switch (error.code) {
        case 'NotAuthorizedException':
          throw new Error('Current password is incorrect.');
        case 'InvalidPasswordException':
          throw new Error('New password does not meet requirements.');
        default:
          throw new Error(error.message || 'Password change failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Update user attributes
  const updateUserAttributes = async (attributes: Record<string, string>): Promise<void> => {
    try {
      setLoading(true);
      const currentUser = await Auth.currentAuthenticatedUser();
      await Auth.updateUserAttributes(currentUser, attributes);
      
      // Refresh user info
      const updatedUserInfo = await getUserInfo(currentUser);
      setUser(updatedUserInfo);
      
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      console.error('Update attributes error:', error);
      throw new Error(error.message || 'Profile update failed.');
    } finally {
      setLoading(false);
    }
  };

  // Refresh session
  const refreshSession = async (): Promise<void> => {
    try {
      const session = await Auth.currentSession();
      if (session && user) {
        const currentUser = await Auth.currentAuthenticatedUser();
        const userInfo = await getUserInfo(currentUser);
        setUser(userInfo);
      }
    } catch (error) {
      console.error('Session refresh error:', error);
      setUser(null);
    }
  };

  // Context value
  const contextValue: AuthContextType = {
    user,
    loading,
    isAuthenticated,
    signIn,
    signUp,
    signOut,
    confirmSignUp,
    resendConfirmationCode,
    forgotPassword,
    forgotPasswordSubmit,
    changePassword,
    updateUserAttributes,
    refreshSession,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
