import { useState, KeyboardEvent, useEffect } from "react";
import { Send, Mic, MicOff, Loader2, Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";

interface ChatInputProps {
  onSubmit: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  clearOnSubmit?: boolean;
}

const ChatInput = ({ onSubmit, placeholder, disabled, className, clearOnSubmit = true }: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const [language, setLanguage] = useState<'en-US' | 'es-ES'>('en-US');
  const { toast } = useToast();
  
  const {
    isRecording,
    isProcessing,
    transcript,
    error,
    isSupported,
    startRecording,
    stopRecording,
    resetTranscript,
  } = useSpeechRecognition({ language, continuous: false, interimResults: true });

  // Update message with transcript
  useEffect(() => {
    if (transcript) {
      setMessage(transcript);
    }
  }, [transcript]);

  // Show error toast
  useEffect(() => {
    if (error) {
      toast({
        title: "Speech Recognition Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  const handleSubmit = () => {
    if (message.trim() && !disabled && !isRecording) {
      onSubmit(message.trim());
      if (clearOnSubmit) {
        setMessage("");
      }
      resetTranscript();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleRecording = () => {
    if (!isSupported) {
      toast({
        title: "Not Supported",
        description: "Speech recognition is not supported in your browser. Try Chrome or Edge.",
        variant: "destructive",
      });
      return;
    }

    if (isRecording) {
      stopRecording();
    } else {
      resetTranscript();
      setMessage("");
      startRecording();
    }
  };

  return (
    <div className={className}>
      <div className="relative flex items-end gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isRecording 
              ? `Listening... (${language === 'en-US' ? 'English' : 'Spanish'})`
              : placeholder || "Type your message..."
          }
          disabled={disabled || isRecording}
          className="min-h-[80px] resize-none pr-24"
        />
        <div className="absolute bottom-2 right-2 flex gap-1">
          {/* Language Selector */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                disabled={disabled || isRecording}
                title="Select language"
              >
                <Languages className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setLanguage('en-US')}>
                🇬🇧 English
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setLanguage('es-ES')}>
                🇪🇸 Spanish
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Microphone Button */}
          <Button
            type="button"
            variant={isRecording ? "destructive" : "ghost"}
            size="icon"
            className={`h-8 w-8 ${isRecording ? 'animate-pulse' : ''}`}
            onClick={toggleRecording}
            disabled={disabled}
            title={isRecording ? "Stop recording" : "Start voice input"}
          >
            {isProcessing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : isRecording ? (
              <MicOff className="h-4 w-4" />
            ) : (
              <Mic className="h-4 w-4" />
            )}
          </Button>

          {/* Send Button */}
          <Button
            type="button"
            size="icon"
            className="h-8 w-8"
            onClick={handleSubmit}
            disabled={disabled || !message.trim() || isRecording}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
