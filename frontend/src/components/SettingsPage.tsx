import React, { useState } from 'react';

interface SettingsPageProps {
  isLLMMode: boolean;
  setIsLLMMode: (mode: boolean) => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ isLLMMode, setIsLLMMode }) => {
  const [settings, setSettings] = useState({
    voiceEnabled: true,
    voiceSpeed: 1.0,
    voiceVolume: 0.8,
    voicePitch: 1.0,
    autoPlay: true,
    darkMode: true,
    notifications: true,
    soundEffects: true,
    language: 'en-US',
    aiPersonality: 'friendly',
    responseLength: 'medium',
    contextMemory: true
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const SettingCard: React.FC<{
    title: string;
    description: string;
    children: React.ReactNode;
    icon: string;
  }> = ({ title, description, children, icon }) => (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      transition: 'all 0.3s ease'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px'
        }}>
          {icon}
        </div>
        <div>
          <h3 style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: '600',
            color: '#ffffff',
            marginBottom: '4px'
          }}>
            {title}
          </h3>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: 'rgba(255, 255, 255, 0.6)',
            lineHeight: '1.4'
          }}>
            {description}
          </p>
        </div>
      </div>
      {children}
    </div>
  );

  const Toggle: React.FC<{
    checked: boolean;
    onChange: (checked: boolean) => void;
    label: string;
  }> = ({ checked, onChange, label }) => (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '12px 0'
    }}>
      <span style={{
        fontSize: '14px',
        color: 'rgba(255, 255, 255, 0.8)',
        fontWeight: '500'
      }}>
        {label}
      </span>
      <button
        onClick={() => onChange(!checked)}
        style={{
          width: '48px',
          height: '24px',
          background: checked ? 'linear-gradient(135deg, #3b82f6, #8b5cf6)' : 'rgba(255, 255, 255, 0.2)',
          border: 'none',
          borderRadius: '12px',
          position: 'relative',
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
      >
        <div style={{
          width: '20px',
          height: '20px',
          background: '#ffffff',
          borderRadius: '50%',
          position: 'absolute',
          top: '2px',
          left: checked ? '26px' : '2px',
          transition: 'all 0.3s ease',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
        }} />
      </button>
    </div>
  );

  const Slider: React.FC<{
    value: number;
    onChange: (value: number) => void;
    min: number;
    max: number;
    step: number;
    label: string;
    unit?: string;
  }> = ({ value, onChange, min, max, step, label, unit = '' }) => (
    <div style={{
      padding: '12px 0'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <span style={{
          fontSize: '14px',
          color: 'rgba(255, 255, 255, 0.8)',
          fontWeight: '500'
        }}>
          {label}
        </span>
        <span style={{
          fontSize: '14px',
          color: '#3b82f6',
          fontWeight: '600'
        }}>
          {value}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{
          width: '100%',
          height: '4px',
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: '2px',
          outline: 'none',
          cursor: 'pointer'
        }}
      />
    </div>
  );

  const Select: React.FC<{
    value: string;
    onChange: (value: string) => void;
    options: { value: string; label: string }[];
    label: string;
  }> = ({ value, onChange, options, label }) => (
    <div style={{
      padding: '12px 0'
    }}>
      <label style={{
        display: 'block',
        fontSize: '14px',
        color: 'rgba(255, 255, 255, 0.8)',
        fontWeight: '500',
        marginBottom: '8px'
      }}>
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%',
          padding: '10px 12px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          color: '#ffffff',
          fontSize: '14px',
          outline: 'none',
          cursor: 'pointer'
        }}
      >
        {options.map(option => (
          <option key={option.value} value={option.value} style={{ background: '#1a1a3a' }}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );

  return (
    <div style={{
      padding: '32px',
      background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)',
      minHeight: '100vh',
      color: '#ffffff'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '32px',
        textAlign: 'center'
      }}>
        <h1 style={{
          margin: 0,
          fontSize: '32px',
          fontWeight: '700',
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          marginBottom: '8px'
        }}>
          Settings
        </h1>
        <p style={{
          margin: 0,
          fontSize: '16px',
          color: 'rgba(255, 255, 255, 0.6)'
        }}>
          Customize your AI assistant experience
        </p>
      </div>

      {/* Settings Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '24px',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* AI Settings */}
        <SettingCard
          title="AI Configuration"
          description="Configure your AI assistant's behavior and capabilities"
          icon="🤖"
        >
          <Toggle
            checked={isLLMMode}
            onChange={setIsLLMMode}
            label="Advanced AI Mode (Claude Haiku)"
          />
          
          <Select
            value={settings.aiPersonality}
            onChange={(value) => handleSettingChange('aiPersonality', value)}
            label="AI Personality"
            options={[
              { value: 'friendly', label: 'Friendly & Helpful' },
              { value: 'professional', label: 'Professional' },
              { value: 'casual', label: 'Casual & Fun' },
              { value: 'formal', label: 'Formal & Precise' }
            ]}
          />

          <Select
            value={settings.responseLength}
            onChange={(value) => handleSettingChange('responseLength', value)}
            label="Response Length"
            options={[
              { value: 'short', label: 'Short & Concise' },
              { value: 'medium', label: 'Medium Detail' },
              { value: 'long', label: 'Detailed & Comprehensive' }
            ]}
          />

          <Toggle
            checked={settings.contextMemory}
            onChange={(checked) => handleSettingChange('contextMemory', checked)}
            label="Remember Conversation Context"
          />
        </SettingCard>

        {/* Voice Settings */}
        <SettingCard
          title="Voice & Speech"
          description="Customize voice input and text-to-speech settings"
          icon="🎤"
        >
          <Toggle
            checked={settings.voiceEnabled}
            onChange={(checked) => handleSettingChange('voiceEnabled', checked)}
            label="Enable Voice Input"
          />

          <Toggle
            checked={settings.autoPlay}
            onChange={(checked) => handleSettingChange('autoPlay', checked)}
            label="Auto-play AI Responses"
          />

          <Slider
            value={settings.voiceSpeed}
            onChange={(value) => handleSettingChange('voiceSpeed', value)}
            min={0.5}
            max={2.0}
            step={0.1}
            label="Speech Speed"
            unit="x"
          />

          <Slider
            value={settings.voiceVolume}
            onChange={(value) => handleSettingChange('voiceVolume', value)}
            min={0}
            max={1}
            step={0.1}
            label="Voice Volume"
            unit="%"
          />

          <Slider
            value={settings.voicePitch}
            onChange={(value) => handleSettingChange('voicePitch', value)}
            min={0.5}
            max={2.0}
            step={0.1}
            label="Voice Pitch"
            unit="x"
          />

          <Select
            value={settings.language}
            onChange={(value) => handleSettingChange('language', value)}
            label="Language"
            options={[
              { value: 'en-US', label: 'English (US)' },
              { value: 'en-GB', label: 'English (UK)' },
              { value: 'es-ES', label: 'Spanish' },
              { value: 'fr-FR', label: 'French' },
              { value: 'de-DE', label: 'German' },
              { value: 'it-IT', label: 'Italian' },
              { value: 'pt-BR', label: 'Portuguese' },
              { value: 'ja-JP', label: 'Japanese' },
              { value: 'ko-KR', label: 'Korean' },
              { value: 'zh-CN', label: 'Chinese (Simplified)' }
            ]}
          />
        </SettingCard>

        {/* Interface Settings */}
        <SettingCard
          title="Interface & Experience"
          description="Customize the look and feel of your assistant"
          icon="🎨"
        >
          <Toggle
            checked={settings.darkMode}
            onChange={(checked) => handleSettingChange('darkMode', checked)}
            label="Dark Mode"
          />

          <Toggle
            checked={settings.notifications}
            onChange={(checked) => handleSettingChange('notifications', checked)}
            label="Enable Notifications"
          />

          <Toggle
            checked={settings.soundEffects}
            onChange={(checked) => handleSettingChange('soundEffects', checked)}
            label="Sound Effects"
          />
        </SettingCard>

        {/* Data & Privacy */}
        <SettingCard
          title="Data & Privacy"
          description="Manage your data and privacy preferences"
          icon="🔒"
        >
          <div style={{
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '16px'
          }}>
            <div style={{
              fontSize: '14px',
              color: '#22c55e',
              fontWeight: '500',
              marginBottom: '4px'
            }}>
              🔐 Your Privacy is Protected
            </div>
            <div style={{
              fontSize: '12px',
              color: 'rgba(255, 255, 255, 0.7)',
              lineHeight: '1.4'
            }}>
              All conversations are encrypted and stored securely. We never share your data with third parties.
            </div>
          </div>

          <button
            style={{
              width: '100%',
              padding: '12px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              color: '#ef4444',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              marginBottom: '12px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
            }}
          >
            Clear All Conversation History
          </button>

          <button
            style={{
              width: '100%',
              padding: '12px',
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '8px',
              color: '#3b82f6',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
            }}
          >
            Export My Data
          </button>
        </SettingCard>
      </div>
    </div>
  );
};

export default SettingsPage;
