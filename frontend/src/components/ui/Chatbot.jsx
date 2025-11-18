import { useState } from "react";
import "./Chatbot.css";

export default function ChatContent() {
  const [message, setMessage] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      console.log("Sending message:", message);
      setMessage("");
    }
  };

  return (
    <div className="chat-content-container" data-name="Content">
      <div className="chat-content-wrapper">
        {/* Title Group */}
        <div className="title-group" data-name="Title Group">
          <div className="title" data_name="Title">
            <p className="title-welcome">{`Welcome to `}</p>
            <div className="title-chatbot-wrapper">
              <p className="title-chatbot">ChatBot</p>
            </div>
          </div>
          <p className="subtitle">
            Here to analyze your downtime requests and provide insights.
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSubmit} className="chat-form">
          <div className="form-input-container">
            <div className="form-input-wrapper">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder='Example : "Summarize all downtime records from this month..."'
                className="chat-input"
              />
              <button type="submit" className="submit-button">
                <div className="submit-icon-wrapper" data-name="send">
                </div>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
