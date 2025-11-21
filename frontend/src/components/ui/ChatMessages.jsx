import { useEffect, useRef } from "react";
import Message from "./Message";
import "./ChatMessages.css";

export default function ChatMessages({ messages }) {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  if (!messages || messages.length === 0) {
    return null;
  }

  return (
    <div className="chat-messages-container" ref={containerRef}>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <Message
            key={index}
            role={message.role}
            content={message.content}
            loading={message.loading}
            error={message.error}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
