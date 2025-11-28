import { Send, Paperclip } from 'lucide-react';
import { useState } from 'react';
import './ChatInput.css';

export default function ChatInput({ onSendMessage, disabled }) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  return (
    <div className='chat-input-container'>
      <form onSubmit={handleSubmit} className='chat-input-form'>
        <div className='chat-input-wrapper'>
          <div className='chat-input-actions'>
            {/* Left Actions */}
            <div className="chat-input-actions">
              <button
                type="button"
                className="action-button"
                title="Attach file"
                disabled={disabled}
              >
                <Paperclip className="action-icon" />
              </button>
            </div>
          </div>

          {/* Input Field */}
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Ask me anything... e.g., "Summarize the downtime records from this month"'
            className='chat-input'
            rows="1"
            disabled={disabled}
          />

          {/* Right Actions */}
          <div className='chat-input-actions'>
            <button
              type='submit'
              className={`send-button ${message.trim() && !disabled ? "active" : ""}`}
              disabledåå={!message.trim() || disabled}
              title='Send Message'
            >
              <Send className='send-icon' />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
