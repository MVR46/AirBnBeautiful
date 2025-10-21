import { useState, KeyboardEvent } from "react";
import { Send, Mic } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  onSubmit: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

const ChatInput = ({ onSubmit, placeholder, disabled, className }: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSubmit(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={className}>
      <div className="relative flex items-end gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "Type your message..."}
          disabled={disabled}
          className="min-h-[80px] resize-none pr-20"
        />
        <div className="absolute bottom-2 right-2 flex gap-2">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            disabled={disabled}
          >
            <Mic className="h-4 w-4" />
          </Button>
          <Button
            type="button"
            size="icon"
            className="h-8 w-8"
            onClick={handleSubmit}
            disabled={disabled || !message.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
