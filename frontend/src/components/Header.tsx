import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.md};
  box-shadow: 0 2px 4px ${props => props.theme.colors.shadow};
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
`;

const Header: React.FC = () => {
  return (
    <HeaderContainer>
      <Title>🎤 Voice Assistant AI</Title>
    </HeaderContainer>
  );
};

export default Header;
