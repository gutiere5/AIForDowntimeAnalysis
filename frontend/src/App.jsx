import { useState, useEffect, useCallback } from 'react';
import Chatbot from '@/components/ui/Chatbot';
import SidePanel from '@/components/ui/SidePanel';
import api from '@/api';
import "./App.css";

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    let session_id = localStorage.getItem('session_id');
    if (!session_id) {
      session_id = crypto.randomUUID();
      localStorage.setItem('session_id', session_id);
    }
    setSessionId(session_id);

    api.getConversations(session_id).then(data => {
      setConversations(data.conversations);
      if (data.conversations.length > 0) {
        setActiveConversationId(data.conversations[0].conversation_id);
      }
    });
  }, []);

  const handleNewConversation = useCallback((newConvo) => {
    if (!conversations.find(c => c.conversation_id === newConvo.conversation_id)) {
      setConversations(prev => [newConvo, ...prev]);
    }
    setActiveConversationId(newConvo.conversation_id);
  }, [conversations]);

  return (
    <div className='app-container'>
      <div className='sidebar-wrapper'>
        <SidePanel
          conversations={conversations}
          activeConversationId={activeConversationId}
          setActiveConversationId={setActiveConversationId}
          sessionId={sessionId}
          setConversations={setConversations}
        />
      </div>
      <div className='chatbot-wrapper'>
        <Chatbot
          sessionId={sessionId}
          activeConversationId={activeConversationId}
          onNewConversation={handleNewConversation}
        />
      </div>
    </div>
  );
}