import { User, Bot, AlertCircle } from "lucide-react";
import Markdown from "react-markdown";
import "./Message.css";

export default function Message({ role, content, loading, error }) {
    const isUser = role === "user";
    const isAssistant = role === "assistant";

    return (
        <div className={`message ${isUser ? "message-user" : "message-assistant"}`}>
            <div className="message-container">
                {/* Avatar */}
                <div className={`message-avatar ${isUser ? "avatar-user" : "avatar-assistant"}`}>
                    {isUser ? (
                        <User className="avatar-icon" />
                    ) : (
                        <Bot className="avatar-icon" />
                    )}
                </div>

                {/* Content */}
                <div className="message-content-wrapper">
                    <div className={`message-bubble ${isUser ? "bubble-user" : "bubble-assistant"} ${error ? "bubble-error" : ""}`}>
                        {loading && !content ? (
                            <div className="message-loading">
                                <div className="loading-dots">
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                    <span className="dot"></span>
                                </div>
                            </div>
                        ) : (
                            <div className="message-text">
                                <Markdown>{content}</Markdown>
                            </div>
                        )}

                        {error && (
                            <div className="message-error">
                                <AlertCircle className="error-icon" />
                                <span>Error generating response</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
