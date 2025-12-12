import { useEffect, useRef, useState } from 'react';
import api from '@/assets/api';
import { parseSSEStream } from '@/assets/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';
import "./Chatbot.css";

export default function Chatbot({ sessionId, activeConversationId, onNewConversation }) {
  const [messages, setMessages] = useState([]);
  const firstTokenRef = useRef(false);

  useEffect(() => {
    if (activeConversationId) {
      api.getConversation(activeConversationId, sessionId).then(history => {
        setMessages(history.messages);
      });
    } else {
        setMessages([]);
    }
  }, [activeConversationId, sessionId]);

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
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            const updatedContent = lastMessage.content + token;
            const formattedContent = updatedContent.replace(/([^\n]) ?•/g, '$1\n •');

            const updatedMessage = {
              ...lastMessage,
              content: formattedContent,
            };
            newMessages[newMessages.length - 1] = updatedMessage;
            return newMessages;
          });
        } else if (evt.type === 'error') {
          setMessages(prev => {
            const updated = [...prev];
            const lastMessage = updated[updated.length - 1];
            lastMessage.loading = false;
            lastMessage.error = true;
            lastMessage.content = evt.message;
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

  const handleFeedback = async (rating) => {
      try {
          await api.sendFeedback(activeConversationId, sessionId, rating);
          console.log(`Feedback submitted: ${rating}`);
      } catch (error) {
          console.error("Error submitting feedback:", error);
      }
  };

  return (
    <div className="chat-content" data-name="Content">
      <div className="chat-content-inner">
        {!hasMessages ? (
          <div className="welcome-message-container">
            {/* Title Group */}
            <div className="title-group" data-name="Title group">
              <div className="title" data-name="Title">
                <p className="title-text">Welcome to ChatBot</p>
              </div>
            </div>
            <div className="input-wrapper-centered">
              <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
            </div>
          </div>
        ) : (
          <>
            {/* Messages Display */}
            <ChatMessages messages={messages} onFeedback={handleFeedback} />

            {/* Chat Input */}
            <div className="input-wrapper-fixed">
              <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
