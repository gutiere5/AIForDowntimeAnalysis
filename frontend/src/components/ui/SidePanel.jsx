import { useState } from "react";
import { Plus, MessageSquare, Trash2, FileText, ExternalLink, Power, Sun, Moon } from "lucide-react";
import AboutModal from "./AboutModal";
import "./SidePanel.css";

export default function SidePanel() {
    const [theme, setTheme] = useState("dark");
    const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);
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
        <>
            <div className="sidebar">
                {/* Top Section */}
                <div className="sidebar-top">
                    {/* User Profile */}
                    <div className="user-profile">
                        <div className="user-avatar">
                            <span className="user-initials">EG</span>
                        </div>
                        <div className="user-info">
                            <p className="user-greeting">Welcome!</p>
                            <p className="user-name">Elber Gutierrez</p>
                        </div>
                    </div>

                    {/* Theme Toggle */}
                    <div className="theme-toggle-wrapper">
                        <div className="theme-toggle">
                            <button
                                onClick={() => setTheme("light")}
                                className={`theme-button ${theme === "light" ? "active" : ""}`}
                            >
                                <Sun className="theme-icon" />
                                <span className="theme-label">Light</span>
                            </button>
                            <button
                                onClick={() => setTheme("dark")}
                                className={`theme-button ${theme === "dark" ? "active" : ""}`}
                            >
                                <Moon className="theme-icon" />
                                <span className="theme-label">Dark</span>
                            </button>
                        </div>
                    </div>

                    {/* Chat List */}
                    <div className="chat-list">
                        {chats.map((chat) => (
                            <div
                                key={chat.id}
                                className={`chat-item ${chat.isActive ? "active" : ""}`}
                            >
                                <MessageSquare className={`chat-icon ${chat.isActive ? "active" : ""}`} />
                                <p className={`chat-text ${chat.isActive ? "active" : ""}`}>
                                    {chat.text}
                                </p>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteChat(chat.id);
                                    }}
                                    className="delete-button"
                                >
                                    <Trash2 className="delete-icon" />
                                </button>
                            </div>
                        ))}
                    </div>

                    {/* New Chat Button */}
                    <button className="new-chat-button">
                        <Plus className="new-chat-icon" />
                        <span className="new-chat-text">Start a new chat</span>
                    </button>
                </div>

                {/* Bottom Section */}
                <div className="sidebar-bottom">
                    <button
                        onClick={handleClearAll}
                        className="bottom-button"
                    >
                        <Trash2 className="bottom-icon" />
                        <span>Clear All Conversations</span>
                    </button>

                    <button className="bottom-button">
                        <FileText className="bottom-icon" />
                        <span>Report An Issue</span>
                    </button>

                    <button
                        onClick={() => setIsAboutModalOpen(true)}
                        className="bottom-button"
                    >
                        <ExternalLink className="bottom-icon" />
                        <span>Updates</span>
                    </button>

                    <button className="bottom-button logout">
                        <Power className="bottom-icon" />
                        <span>Log out</span>
                    </button>
                </div>
            </div>
            <AboutModal isOpen={isAboutModalOpen} onClose={() => setIsAboutModalOpen(false)} />
        </>
    );
}