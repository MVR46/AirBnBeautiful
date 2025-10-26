import { useState, useEffect, useRef, useCallback } from 'react';

// Extend Window interface for browser compatibility
interface SpeechRecognitionWindow extends Window {
  SpeechRecognition?: typeof SpeechRecognition;
  webkitSpeechRecognition?: typeof SpeechRecognition;
}

type Language = 'en-US' | 'es-ES';

interface UseSpeechRecognitionProps {
  language?: Language;
  continuous?: boolean;
  interimResults?: boolean;
}

interface UseSpeechRecognitionReturn {
  isRecording: boolean;
  isProcessing: boolean;
  transcript: string;
  error: string | null;
  isSupported: boolean;
  startRecording: () => void;
  stopRecording: () => void;
  resetTranscript: () => void;
}

export const useSpeechRecognition = ({
  language = 'en-US',
  continuous = false,
  interimResults = true,
}: UseSpeechRecognitionProps = {}): UseSpeechRecognitionReturn => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Check browser support
  const isSupported = useCallback(() => {
    const win = window as SpeechRecognitionWindow;
    return !!(win.SpeechRecognition || win.webkitSpeechRecognition);
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    if (!isSupported()) return;

    const win = window as SpeechRecognitionWindow;
    const SpeechRecognitionAPI = win.SpeechRecognition || win.webkitSpeechRecognition;
    
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = continuous;
    recognition.interimResults = interimResults;
    recognition.lang = language;

    recognition.onstart = () => {
      setIsRecording(true);
      setIsProcessing(false);
      setError(null);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPart + ' ';
        } else {
          interimTranscript += transcriptPart;
        }
      }

      if (finalTranscript) {
        setTranscript((prev) => prev + finalTranscript);
        setIsProcessing(false);
      } else if (interimTranscript) {
        setTranscript((prev) => prev + interimTranscript);
        setIsProcessing(true);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setIsRecording(false);
      setIsProcessing(false);
      
      switch (event.error) {
        case 'no-speech':
          setError('No speech detected. Please try again.');
          break;
        case 'audio-capture':
          setError('Microphone not detected. Please check your device.');
          break;
        case 'not-allowed':
          setError('Microphone access denied. Please enable permissions.');
          break;
        case 'network':
          setError('Network error. Please check your connection.');
          break;
        default:
          setError(`Error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsRecording(false);
      setIsProcessing(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [language, continuous, interimResults, isSupported]);

  const startRecording = useCallback(() => {
    if (!isSupported()) {
      setError('Speech recognition is not supported in your browser.');
      return;
    }

    if (recognitionRef.current && !isRecording) {
      try {
        setTranscript('');
        setError(null);
        recognitionRef.current.start();
      } catch (err) {
        setError('Failed to start recording. Please try again.');
        console.error(err);
      }
    }
  }, [isRecording, isSupported]);

  const stopRecording = useCallback(() => {
    if (recognitionRef.current && isRecording) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error(err);
      }
    }
  }, [isRecording]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setError(null);
  }, []);

  return {
    isRecording,
    isProcessing,
    transcript,
    error,
    isSupported: isSupported(),
    startRecording,
    stopRecording,
    resetTranscript,
  };
};

