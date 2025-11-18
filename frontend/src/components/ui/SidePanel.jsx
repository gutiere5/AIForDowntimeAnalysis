import { useState } from "react";
import { Plus, MessageSquare, Trash2, FileText, ExternalLink, Power, Sun, Moon } from "lucide-react";
import './SidePanel.css';


export default function SidePanel({ conversations, activeConversationId, setActiveConversationId }) {
    const [theme, setTheme] = useState('dark');
    const [chats, setChats] = useState([
        { id: 1, text: "What were major downtime issues?", isActive: true },
        { id: 2, text: "How to fix a machine that is..." },
        { id: 3, text: "What are some trends this..." },
        { id: 4, text: "Create graphs based on..." },
    ]);

    const handleDeleteChat = (id) => {
        setChats(chats.filter(chat => chat.id !== id));
    };

    const handleClearAll = () => {
        setChats([]);
    };

    return (
        <div className="sidebar-container">
            {/* Top Section */}
            <div className="sidebar-top-section">
                {/* User Profile */}
                <div className="user-profile">
                    <div className="user-profile-content">
                        <div className="user-avatar">
                            <span className="user_avatar-text">EG</span>
                        </div>
                        <div className="user-info">
                            <p className="user-info-welcome">Welcome</p>
                            <p className="user-info-name">Elber Gutierrez</p>
                        </div>
                    </div>
                </div>

                {/* Theme Toggle */}
                <div className="theme-toggle-container">
                    <div className="theme-toggle-group">
                        <button
                            onClick={() => setTheme('light')}
                            className={`theme-btn theme-btn-light ${theme === "light" ? "active" : ""}`}
                        >
                            <Sun className="theme-btn-icon" />
                            <span className="theme-btn-text">Light</span>
                        </button>

                        <button
                            onClick={() => setTheme('dark')}
                            className={`theme-btn theme-btn-dark ${theme === "dark" ? "active" : ""}`}
                        >
                            <Moon className="theme-btn-icon" />
                            <span className="theme-btn-text">Dark</span>
                        </button>
                    </div>
                </div>

                {/* New Chat Button */}
                <button className="new-chat-btn">
                    <Plus className="new-chat-icon" />
                    <span className="new-chat-text">Start New Chat</span>
                </button>

                {/* Chat List */}
                <div className="chat-list">
                    {chats.map((chat) => (
                        <div
                            key={chat.id}
                            className={`chat-item ${chat.isActive ? "active" : "inactive"}`}
                        >
                            <MessageSquare className="chat-item-icon" />
                            <p className="chat-item-text">
                                {chat.text}
                            </p>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteChat(chat.id);
                                }}
                                className="chat-delete-btn"
                            >
                                <Trash2 className="chat-delete-icon" />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Bottom Section */}
            <div className="sidebar-bottom-section">
                <button
                    onClick={handleClearAll}
                    className="bottom-btn"
                >
                    <Trash2 className="bottom-btn-icon" />
                    <span>Clear All Chats</span>
                </button>

                <button className="bottom-btn">
                    <FileText className="bottom-btn-icon" />
                    <span>Report An Issue</span>
                </button>

                <button className="bottom-btn">
                    <ExternalLink className="bottom-btn-icon" />
                    <span>Updates</span>
                </button>

                <button className="bottom-btn">
                    <Power className="bottom-btn-icon" />
                    <span>Log Out</span>
                </button>
            </div>
        </div>);
}