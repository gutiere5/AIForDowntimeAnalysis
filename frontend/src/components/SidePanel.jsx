import { useState } from "react";
import { Plus, MessageSquare, Trash2, FileText, ExternalLink, Power, Sun, Moon, Pencil, BookOpen } from "lucide-react";
import AboutModal from "./AboutModal";
import KnownIssuesModal from "./KnownIssuesModal"
import api from "@/assets/api";
import "./SidePanel.css";

export default function SidePanel({ conversations, activeConversationId, setActiveConversationId, sessionId, setConversations, onNewConversation }) {
    const [theme, setTheme] = useState("dark");
    const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);
    const [isKnownIssuesModalOpen, setIsKnownIssuesModalOpen] = useState(false);
    const [editingConversationId, setEditingConversationId] = useState(null);
    const [editingTitle, setEditingTitle] = useState("");

    const handleClearAll = () => {
        // This should ideally trigger a backend call to delete all conversations
        // and then update the state in the parent component.
        // For now, we'll just clear the frontend state via the passed-in setter.
        // setConversations([]);
        console.log("Clearing all conversations is not implemented yet.");
    };

    const handleDelete = async (conversationId) => {
        try {
            await api.deleteConversation(conversationId, sessionId);
            setConversations(prev => prev.filter(c => c.conversation_id !== conversationId));
        } catch (error) {
            console.error("Failed to delete conversation:", error);
        }
    };

    const handleUpdateTitle = async (conversationId) => {
        try {
            await api.updateConversationTitle(conversationId, sessionId, editingTitle);
            setConversations(prev => prev.map(c =>
                c.conversation_id === conversationId ? { ...c, title: editingTitle } : c
            ));
            setEditingConversationId(null);
        } catch (error) {
            console.error("Failed to update conversation title:", error);
        }
    };

    const handleNewChat = async () => {
        try {
            const newConvo = await api.createConversation(sessionId);
            onNewConversation(newConvo);
        } catch (error) {
            console.error("Failed to create new conversation:", error);
        }
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
                        {conversations.map((chat) => (
                            <div
                                key={chat.conversation_id}
                                className={`chat-item ${chat.conversation_id === activeConversationId ? "active" : ""}`}
                                onClick={() => setActiveConversationId(chat.conversation_id)}
                            >
                                <MessageSquare className={`chat-icon ${chat.conversation_id === activeConversationId ? "active" : ""}`} />
                                {editingConversationId === chat.conversation_id ? (
                                    <input
                                        type="text"
                                        value={editingTitle}
                                        onChange={(e) => setEditingTitle(e.target.value)}
                                        onBlur={() => handleUpdateTitle(chat.conversation_id)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') {
                                                handleUpdateTitle(chat.conversation_id);
                                            } else if (e.key === 'Escape') {
                                                setEditingConversationId(null);
                                            }
                                        }}
                                        autoFocus
                                        className="edit-input"
                                    />
                                ) : (
                                    <p className={`chat-text ${chat.conversation_id === activeConversationId ? "active" : ""}`}>
                                        {chat.title}
                                    </p>
                                )}
                                <div className="chat-actions">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setEditingConversationId(chat.conversation_id);
                                            setEditingTitle(chat.title);
                                        }}
                                        className="edit-button"
                                    >
                                        <Pencil className="edit-icon" />
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDelete(chat.conversation_id);
                                        }}
                                        className="delete-button"
                                    >
                                        <Trash2 className="delete-icon" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* New Chat Button */}
                    <button className="new-chat-button" onClick={handleNewChat}>
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
                        onClick={() => setIsKnownIssuesModalOpen(true)}
                        className="bottom-button"
                    >
                        <BookOpen className="bottom-icon" />
                        <span>Manage Known Issues</span>
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
            <KnownIssuesModal isOpen={isKnownIssuesModalOpen} onClose={() => setIsKnownIssuesModalOpen(false)} />
        </>
    );
}