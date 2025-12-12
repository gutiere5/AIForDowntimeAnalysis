import { User, Bot, AlertCircle, ThumbsUp, ThumbsDown, CheckCircle } from "lucide-react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import "./Message.css";

export default function Message({ role, content, loading, error, onFeedback }) {
    const isUser = role === "user";
    const isAssistant = role === "assistant";
    const [feedbackGiven, setFeedbackGiven] = useState(false);

    const handleFeedbackClick = (rating) => {
        if (!feedbackGiven && onFeedback) {
            onFeedback(rating);
            setFeedbackGiven(true);
        }
    };

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
                                <Markdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        h1: ({node, ...props}) => <h1 className="markdown-h1" {...props} />,
                                        h2: ({node, ...props}) => <h2 className="markdown-h2" {...props} />,
                                        h3: ({node, ...props}) => <h3 className="markdown-h3" {...props} />,
                                        h4: ({node, ...props}) => <h4 className="markdown-h4" {...props} />,
                                        h5: ({node, ...props}) => <h5 className="markdown-h5" {...props} />,
                                        h6: ({node, ...props}) => <h6 className="markdown-h6" {...props} />,
                                        ul: ({node, ...props}) => <ul className="markdown-ul" {...props} />,
                                        ol: ({node, ...props}) => <ol className="markdown-ol" {...props} />,
                                        li: ({node, ...props}) => <li className="markdown-li" {...props} />,
                                        p: ({node, ...props}) => <p className="markdown-p" {...props} />,
                                        blockquote: ({node, ...props}) => <blockquote className="markdown-blockquote" {...props} />,
                                        code: ({node, inline, ...props}) =>
                                            inline ?
                                            <code className="markdown-code-inline" {...props} /> :
                                            <code className="markdown-code-block" {...props} />,
                                        pre: ({node, ...props}) => <pre className="markdown-pre" {...props} />,
                                        a: ({node, ...props}) => <a className="markdown-link" target="_blank" rel="noopener noreferrer" {...props} />,
                                        table: ({node, ...props}) => <table className="markdown-table" {...props} />,
                                        thead: ({node, ...props}) => <thead className="markdown-thead" {...props} />,
                                        tbody: ({node, ...props}) => <tbody className="markdown-tbody" {...props} />,
                                        tr: ({node, ...props}) => <tr className="markdown-tr" {...props} />,
                                        th: ({node, ...props}) => <th className="markdown-th" {...props} />,
                                        td: ({node, ...props}) => <td className="markdown-td" {...props} />,
                                        hr: ({node, ...props}) => <hr className="markdown-hr" {...props} />,
                                        strong: ({node, ...props}) => <strong className="markdown-strong" {...props} />,
                                        em: ({node, ...props}) => <em className="markdown-em" {...props} />,
                                    }}
                                >
                                    {content}
                                </Markdown>
                            </div>
                        )}

                        {error && (
                            <div className="message-error">
                                <AlertCircle className="error-icon" />
                                <span>Error generating response</span>
                            </div>
                        )}
                    </div>
                    
                    {/* Feedback Buttons */}
                    {isAssistant && !loading && !error && (
                        <div className="feedback-container">
                            {!feedbackGiven ? (
                                <>
                                    <button 
                                        className="feedback-button" 
                                        onClick={() => handleFeedbackClick("Helpful")}
                                        title="Helpful"
                                    >
                                        <ThumbsUp className="feedback-icon" size={16} />
                                        <span>Helpful</span>
                                    </button>
                                    <button 
                                        className="feedback-button" 
                                        onClick={() => handleFeedbackClick("Not Helpful")}
                                        title="Not Helpful"
                                    >
                                        <ThumbsDown className="feedback-icon" size={16} />
                                        <span>Not Helpful</span>
                                    </button>
                                    <button 
                                        className="feedback-button" 
                                        onClick={() => handleFeedbackClick("Resolved Issue")}
                                        title="Resolved Issue"
                                    >
                                        <CheckCircle className="feedback-icon" size={16} />
                                        <span>Resolved Issue</span>
                                    </button>
                                </>
                            ) : (
                                <div className="feedback-thank-you">
                                    <span>Thank you for your feedback!</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
