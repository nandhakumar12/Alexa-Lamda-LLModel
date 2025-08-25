import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import toast from 'react-hot-toast';

// Types
interface VoiceContextType {
  // Speech Recognition
  isListening: boolean;
  isSupported: boolean;
  transcript: string;
  finalTranscript: string;
  interimTranscript: string;
  confidence: number;
  
  // Speech Synthesis
  isSpeaking: boolean;
  voices: SpeechSynthesisVoice[];
  selectedVoice: SpeechSynthesisVoice | null;
  
  // Controls
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  speak: (text: string, options?: SpeechSynthesisOptions) => void;
  stopSpeaking: () => void;
  setSelectedVoice: (voice: SpeechSynthesisVoice | null) => void;
  
  // Settings
  continuous: boolean;
  setContinuous: (continuous: boolean) => void;
  language: string;
  setLanguage: (language: string) => void;
  autoSpeak: boolean;
  setAutoSpeak: (autoSpeak: boolean) => void;
}

interface SpeechSynthesisOptions {
  voice?: SpeechSynthesisVoice;
  rate?: number;
  pitch?: number;
  volume?: number;
}

interface VoiceProviderProps {
  children: React.ReactNode;
}

// Supported languages
const SUPPORTED_LANGUAGES = [
  { code: 'en-US', name: 'English (US)' },
  { code: 'en-GB', name: 'English (UK)' },
  { code: 'es-ES', name: 'Spanish (Spain)' },
  { code: 'es-US', name: 'Spanish (US)' },
  { code: 'fr-FR', name: 'French' },
  { code: 'de-DE', name: 'German' },
  { code: 'it-IT', name: 'Italian' },
  { code: 'pt-BR', name: 'Portuguese (Brazil)' },
  { code: 'ja-JP', name: 'Japanese' },
  { code: 'ko-KR', name: 'Korean' },
  { code: 'zh-CN', name: 'Chinese (Simplified)' },
];

// Create context
const VoiceContext = createContext<VoiceContextType | undefined>(undefined);

// Custom hook to use voice context
export const useVoice = (): VoiceContextType => {
  const context = useContext(VoiceContext);
  if (!context) {
    throw new Error('useVoice must be used within a VoiceProvider');
  }
  return context;
};

// Voice Provider Component
export const VoiceProvider: React.FC<VoiceProviderProps> = ({ children }) => {
  // Speech Recognition
  const {
    transcript,
    finalTranscript,
    interimTranscript,
    listening,
    resetTranscript: resetSpeechTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  // Speech Synthesis
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [currentUtterance, setCurrentUtterance] = useState<SpeechSynthesisUtterance | null>(null);

  // Settings
  const [continuous, setContinuous] = useState(false);
  const [language, setLanguage] = useState('en-US');
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [confidence, setConfidence] = useState(0);

  // Initialize voices
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = speechSynthesis.getVoices();
      setVoices(availableVoices);
      
      // Set default voice (prefer English voices)
      if (!selectedVoice && availableVoices.length > 0) {
        const englishVoice = availableVoices.find(voice => 
          voice.lang.startsWith('en') && voice.default
        ) || availableVoices.find(voice => 
          voice.lang.startsWith('en')
        ) || availableVoices[0];
        
        setSelectedVoice(englishVoice);
      }
    };

    // Load voices immediately
    loadVoices();

    // Also load when voices change (some browsers load them asynchronously)
    speechSynthesis.addEventListener('voiceschanged', loadVoices);

    return () => {
      speechSynthesis.removeEventListener('voiceschanged', loadVoices);
    };
  }, [selectedVoice]);

  // Speech Recognition Commands
  const commands = [
    {
      command: 'clear',
      callback: () => {
        resetSpeechTranscript();
        toast.success('Transcript cleared');
      },
    },
    {
      command: 'stop listening',
      callback: () => {
        stopListening();
        toast.info('Stopped listening');
      },
    },
    {
      command: 'repeat that',
      callback: () => {
        if (finalTranscript) {
          speak(finalTranscript);
        }
      },
    },
  ];

  // Start listening
  const startListening = useCallback(() => {
    if (!browserSupportsSpeechRecognition) {
      toast.error('Speech recognition is not supported in this browser');
      return;
    }

    try {
      SpeechRecognition.startListening({
        continuous,
        language,
        interimResults: true,
      });
      toast.success('Started listening');
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      toast.error('Failed to start listening');
    }
  }, [browserSupportsSpeechRecognition, continuous, language]);

  // Stop listening
  const stopListening = useCallback(() => {
    SpeechRecognition.stopListening();
    toast.info('Stopped listening');
  }, []);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    resetSpeechTranscript();
  }, [resetSpeechTranscript]);

  // Speak text
  const speak = useCallback((
    text: string, 
    options: SpeechSynthesisOptions = {}
  ) => {
    if (!text.trim()) return;

    // Stop current speech
    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set voice
    utterance.voice = options.voice || selectedVoice;
    
    // Set speech parameters
    utterance.rate = options.rate || 1;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 1;
    utterance.lang = language;

    // Event handlers
    utterance.onstart = () => {
      setIsSpeaking(true);
      setCurrentUtterance(utterance);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentUtterance(null);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
      setCurrentUtterance(null);
      toast.error('Speech synthesis failed');
    };

    // Start speaking
    speechSynthesis.speak(utterance);
  }, [selectedVoice, language]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    speechSynthesis.cancel();
    setIsSpeaking(false);
    setCurrentUtterance(null);
  }, []);

  // Handle speech recognition results
  useEffect(() => {
    if (finalTranscript) {
      // Calculate confidence (mock implementation)
      setConfidence(Math.random() * 0.3 + 0.7); // 0.7 - 1.0
      
      // Auto-speak if enabled
      if (autoSpeak && finalTranscript.trim()) {
        speak(`You said: ${finalTranscript}`);
      }
    }
  }, [finalTranscript, autoSpeak, speak]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      speechSynthesis.cancel();
      SpeechRecognition.stopListening();
    };
  }, []);

  // Context value
  const contextValue: VoiceContextType = {
    // Speech Recognition
    isListening: listening,
    isSupported: browserSupportsSpeechRecognition,
    transcript,
    finalTranscript,
    interimTranscript,
    confidence,
    
    // Speech Synthesis
    isSpeaking,
    voices,
    selectedVoice,
    
    // Controls
    startListening,
    stopListening,
    resetTranscript,
    speak,
    stopSpeaking,
    setSelectedVoice,
    
    // Settings
    continuous,
    setContinuous,
    language,
    setLanguage,
    autoSpeak,
    setAutoSpeak,
  };

  return (
    <VoiceContext.Provider value={contextValue}>
      {children}
    </VoiceContext.Provider>
  );
};

// Export supported languages for use in components
export { SUPPORTED_LANGUAGES };

// Utility functions
export const getVoicesByLanguage = (voices: SpeechSynthesisVoice[], language: string) => {
  return voices.filter(voice => voice.lang.startsWith(language.split('-')[0]));
};

export const formatVoiceName = (voice: SpeechSynthesisVoice) => {
  return `${voice.name} (${voice.lang})`;
};

// Voice quality assessment
export const assessVoiceQuality = (voice: SpeechSynthesisVoice) => {
  const quality = {
    isLocal: voice.localService,
    isDefault: voice.default,
    score: 0,
  };

  // Scoring based on various factors
  if (voice.localService) quality.score += 30;
  if (voice.default) quality.score += 20;
  if (voice.name.toLowerCase().includes('premium')) quality.score += 25;
  if (voice.name.toLowerCase().includes('enhanced')) quality.score += 15;
  if (voice.name.toLowerCase().includes('neural')) quality.score += 35;

  return quality;
};

export default VoiceContext;
