import React, { Component, ErrorInfo, ReactNode } from 'react';
import styled from 'styled-components';

const ErrorContainer = styled.div`
  padding: 2rem;
  text-align: center;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin: 2rem;
`;

const ErrorTitle = styled.h2`
  color: #dc3545;
  margin-bottom: 1rem;
`;

const ErrorMessage = styled.p`
  color: #6c757d;
  margin-bottom: 1rem;
`;

const RetryButton = styled.button`
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;

  &:hover {
    background: #0056b3;
  }
`;

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <ErrorContainer>
          <ErrorTitle>🚨 Something went wrong</ErrorTitle>
          <ErrorMessage>
            We're sorry, but something unexpected happened. Please try refreshing the page.
          </ErrorMessage>
          {this.state.error && (
            <ErrorMessage>
              <strong>Error:</strong> {this.state.error.message}
            </ErrorMessage>
          )}
          <RetryButton onClick={this.handleRetry}>
            Try Again
          </RetryButton>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
