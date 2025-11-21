import { useRef, useState } from 'react';
import api from '@/api';
import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ui/ChatMessages';
import ChatInput from '@/components/ui/ChatInput';
import "./Chatbot.css";

export default function Chatbot({ sessionId, activeConversationId, onNewConversation }) {
  const [messages, setMessages] = useState([]);
  const firstTokenRef = useRef(false);

  const isLoading = messages.length > 0 && messages[messages.length - 1].loading;
  const hasMessages = messages.length > 0;

  const handleSendMessage = async (messageText) => {
    const trimmedMessage = messageText.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(prev => [
      ...prev,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', loading: true }
    ]);

    firstTokenRef.current = true;

    try {
      const stream = await api.sendChatMessage(
        trimmedMessage,
        activeConversationId,
        sessionId
      );

      let newConvoId = null;

      for await (const evt of parseSSEStream(stream)) {
        if (evt.type === 'conversation_id') {
          newConvoId = evt.id;
          if (!activeConversationId && onNewConversation) {
            onNewConversation({
              conversation_id: newConvoId,
              title: trimmedMessage
            });
          }
        } else if (evt.type === 'chunk') {
          let token = evt.content;

          if (firstTokenRef.current) {
            token = token.replace(/^\s+/, '');
            firstTokenRef.current = false;
          }

          setMessages(prev => {
            const updated = [...prev];
            const lastMessage = updated[updated.length - 1];
            lastMessage.content += token;
            return updated;
          });
        } else if (evt.type === 'error') {
          setMessages(prev => {
            const updated = [...prev];
            const lastMessage = updated[updated.length - 1];
            lastMessage.loading = false;
            lastMessage.error = true;
            lastMessage.content += (lastMessage.content ? '\n\n' : '') + evt.message;
            return updated;
          });
          break;
        } else if (evt.type === 'done') {
          setMessages(prev => {
            const updated = [...prev];
            const lastMessage = updated[updated.length - 1];
            lastMessage.loading = false;
            return updated;
          });
          break;
        }
      }
    } catch (err) {
      console.error('Stream error:', err);
      setMessages(prev => {
        const updated = [...prev];
        const lastMessage = updated[updated.length - 1];
        lastMessage.loading = false;
        lastMessage.error = true;
        lastMessage.content = `Error: ${err.message}`;
        return updated;
      });
    }
  };

  return (
    <div className="chat-content" data-name="Content">
      <div className="chat-content-inner">
        {!hasMessages ? (
          <>
            {/* Title Group - Only show when no messages */}
            <div className="title-group" data-name="Title group">
              <div className="title" data-name="Title">
                <p className="title-text">Welcome to ChatBot</p>
              </div>
            </div>

            {/* Chat Input - Centered when no messages */}
            <div className="input-wrapper-centered">
              <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
            </div>
          </>
        ) : (
          <>
            {/* Messages Display */}
            <ChatMessages messages={messages} />

            {/* Chat Input */}
            <div className="input-wrapper-bottom">
              <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}