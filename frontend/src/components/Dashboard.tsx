import React from 'react';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  padding: ${props => props.theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Card = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.md};
  box-shadow: 0 2px 4px ${props => props.theme.colors.shadow};
`;

const Dashboard: React.FC = () => {
  return (
    <DashboardContainer>
      <Title>Dashboard</Title>
      <Card>
        <h3>Welcome to Voice Assistant AI</h3>
        <p>Your intelligent voice companion is ready to help you.</p>
      </Card>
      <Card>
        <h3>Quick Stats</h3>
        <p>Voice interactions: 0</p>
        <p>Sessions: 0</p>
      </Card>
    </DashboardContainer>
  );
};

export default Dashboard;
