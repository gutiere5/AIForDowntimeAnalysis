
import { useState, useEffect, useCallback } from 'react';
import Chatbot from '@/components/Chatbot';
import SidePanel from '@/components/SidePanel';
import api from '@/api';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    let sid = localStorage.getItem('session_id');
    if (!sid) {
      sid = crypto.randomUUID();
      localStorage.setItem('session_id', sid);
    }
    setSessionId(sid);

    api.getConversations(sid).then(data => {
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
    <div className='flex flex-col h-screen w-screen overflow-hidden'>
      <header className='z-20bg-white border-b'>
         <h1 className='font-urbanist text-[1.65rem] font-semibold text-center py-4'>AI DownTime Chatbot</h1>
      </header>
        <div className= 'flex flex-1 min-h-0'>
            <SidePanel 
              conversations={conversations} 
              activeConversationId={activeConversationId} 
              setActiveConversationId={setActiveConversationId} 
            />
            <main className='flex flex-col flex-1 min-h-0'>
               <Chatbot 
                sessionId={sessionId} 
                activeConversationId={activeConversationId} 
                onNewConversation={handleNewConversation}
               />
            </main>
        </div>
    </div>
  );
}

export default App;