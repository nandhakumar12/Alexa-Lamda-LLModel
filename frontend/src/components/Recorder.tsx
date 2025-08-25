import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaPlay, FaPause } from 'react-icons/fa';
import toast from 'react-hot-toast';

// Types
interface RecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  onRecordingStart?: () => void;
  onRecordingStop?: () => void;
  maxDuration?: number; // in seconds
  className?: string;
}

interface AudioVisualizerProps {
  isRecording: boolean;
  audioStream?: MediaStream;
}

// Styled components
const RecorderContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.md};
`;

const RecordButton = styled(motion.button)<{ isRecording: boolean }>`
  width: 80px;
  height: 80px;
  border-radius: ${props => props.theme.borderRadius.full};
  border: none;
  background: ${props => props.isRecording ? props.theme.colors.danger : props.theme.colors.primary};
  color: white;
  font-size: 2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: ${props => props.theme.shadows.lg};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const RecordingIndicator = styled(motion.div)`
  position: absolute;
  top: -5px;
  right: -5px;
  left: -5px;
  bottom: -5px;
  border: 3px solid ${props => props.theme.colors.danger};
  border-radius: ${props => props.theme.borderRadius.full};
  opacity: 0.7;
`;

const VisualizerContainer = styled.div`
  width: 200px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  background: ${props => props.theme.colors.background};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.sm};
`;

const VisualizerBar = styled(motion.div)<{ height: number }>`
  width: 4px;
  background: ${props => props.theme.colors.primary};
  border-radius: ${props => props.theme.borderRadius.sm};
  height: ${props => props.height}px;
  min-height: 4px;
`;

const TimerDisplay = styled.div`
  font-size: 1.2rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  font-family: 'Courier New', monospace;
`;

const ControlsContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  align-items: center;
`;

const ControlButton = styled(motion.button)`
  padding: ${props => props.theme.spacing.sm};
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.secondary};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  
  &:hover {
    background: ${props => props.theme.colors.dark};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const StatusText = styled.p`
  margin: 0;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  font-size: 0.9rem;
`;

// Audio Visualizer Component
const AudioVisualizer: React.FC<AudioVisualizerProps> = ({ isRecording, audioStream }) => {
  const [audioData, setAudioData] = useState<number[]>(new Array(20).fill(0));
  const animationRef = useRef<number>();
  const analyserRef = useRef<AnalyserNode>();

  useEffect(() => {
    if (isRecording && audioStream) {
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(audioStream);
      
      analyser.fftSize = 64;
      source.connect(analyser);
      analyserRef.current = analyser;

      const updateAudioData = () => {
        if (analyserRef.current) {
          const bufferLength = analyserRef.current.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          analyserRef.current.getByteFrequencyData(dataArray);
          
          // Convert to heights for visualization
          const heights = Array.from(dataArray).slice(0, 20).map(value => 
            Math.max(4, (value / 255) * 50)
          );
          
          setAudioData(heights);
        }
        
        if (isRecording) {
          animationRef.current = requestAnimationFrame(updateAudioData);
        }
      };

      updateAudioData();
    } else {
      setAudioData(new Array(20).fill(4));
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRecording, audioStream]);

  return (
    <VisualizerContainer>
      {audioData.map((height, index) => (
        <VisualizerBar
          key={index}
          height={height}
          animate={{ height }}
          transition={{ duration: 0.1 }}
        />
      ))}
    </VisualizerContainer>
  );
};

// Main Recorder Component
const Recorder: React.FC<RecorderProps> = ({
  onRecordingComplete,
  onRecordingStart,
  onRecordingStop,
  maxDuration = 60,
  className
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioStream, setAudioStream] = useState<MediaStream>();

  const mediaRecorderRef = useRef<MediaRecorder>();
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout>();
  const audioRef = useRef<HTMLAudioElement>();

  // Format time display
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      });
      
      setAudioStream(stream);
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        onRecordingComplete(blob);
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
        setAudioStream(undefined);
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      setRecordingTime(0);
      onRecordingStart?.();

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          const newTime = prev + 1;
          if (newTime >= maxDuration) {
            stopRecording();
          }
          return newTime;
        });
      }, 1000);

      toast.success('Recording started');
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      onRecordingStop?.();

      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      toast.success('Recording stopped');
    }
  };

  // Pause/Resume recording
  const togglePause = () => {
    if (mediaRecorderRef.current) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
        
        // Resume timer
        timerRef.current = setInterval(() => {
          setRecordingTime(prev => {
            const newTime = prev + 1;
            if (newTime >= maxDuration) {
              stopRecording();
            }
            return newTime;
          });
        }, 1000);
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
        
        // Pause timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
      }
    }
  };

  // Play recorded audio
  const playRecording = () => {
    if (audioBlob && !isPlaying) {
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.play();
      setIsPlaying(true);
    } else if (audioRef.current && isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [audioStream]);

  return (
    <RecorderContainer className={className}>
      <RecordButton
        isRecording={isRecording}
        onClick={isRecording ? stopRecording : startRecording}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        disabled={isPaused}
      >
        {isRecording ? <FaStop /> : <FaMicrophone />}
        
        {isRecording && (
          <RecordingIndicator
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </RecordButton>

      {isRecording && (
        <AudioVisualizer isRecording={isRecording} audioStream={audioStream} />
      )}

      <TimerDisplay>
        {formatTime(recordingTime)}
        {maxDuration && ` / ${formatTime(maxDuration)}`}
      </TimerDisplay>

      {isRecording && (
        <ControlsContainer>
          <ControlButton
            onClick={togglePause}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isPaused ? <FaPlay /> : <FaPause />}
          </ControlButton>
        </ControlsContainer>
      )}

      {audioBlob && !isRecording && (
        <ControlsContainer>
          <ControlButton
            onClick={playRecording}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isPlaying ? <FaPause /> : <FaPlay />}
          </ControlButton>
        </ControlsContainer>
      )}

      <StatusText>
        {isRecording 
          ? isPaused 
            ? 'Recording paused - Click to resume'
            : 'Recording... Click to stop'
          : audioBlob 
            ? 'Recording complete - Click play to review'
            : 'Click microphone to start recording'
        }
      </StatusText>
    </RecorderContainer>
  );
};

export default Recorder;
