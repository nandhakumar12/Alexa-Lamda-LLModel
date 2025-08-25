import React from 'react';
import styled from 'styled-components';

const SettingsContainer = styled.div`
  padding: ${props => props.theme.spacing.lg};
  max-width: 800px;
  margin: 0 auto;
`;

const Title = styled.h2`
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SettingGroup = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${props => props.theme.spacing.sm};
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const Input = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 4px;
  font-size: 1rem;
`;

const Settings: React.FC = () => {
  return (
    <SettingsContainer>
      <Title>Settings</Title>
      <SettingGroup>
        <h3>Voice Settings</h3>
        <Label htmlFor="language">Language</Label>
        <Input type="text" id="language" defaultValue="English" />
        
        <Label htmlFor="voice-speed">Voice Speed</Label>
        <Input type="range" id="voice-speed" min="0.5" max="2" step="0.1" defaultValue="1" />
      </SettingGroup>
      
      <SettingGroup>
        <h3>Privacy Settings</h3>
        <Label>
          <input type="checkbox" defaultChecked />
          Save conversation history
        </Label>
        <Label>
          <input type="checkbox" defaultChecked />
          Enable analytics
        </Label>
      </SettingGroup>
    </SettingsContainer>
  );
};

export default Settings;
