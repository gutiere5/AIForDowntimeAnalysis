import { useState, useEffect, useCallback } from 'react'; // Merged imports
import Chatbot from '@/components/ui/Chatbot';
import SidePanel from '@/components/ui/SidePanel';
import { AboutModal } from './components/AboutModal'; // Your import
import api from '@/api'; // 'main' branch's import

function App() {
  // Your 'About Modal' state
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  // State from the 'main' branch
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  // Effect from the 'main' branch
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

  // Handler from the 'main' branch
  const handleNewConversation = useCallback((newConvo) => {
    if (!conversations.find(c => c.conversation_id === newConvo.conversation_id)) {
      setConversations(prev => [newConvo, ...prev]);
    }
    setActiveConversationId(newConvo.conversation_id);
  }, [conversations]);

  return (
    <div className='flex flex-col h-screen w-screen overflow-hidden'>
      {/* Your header with the 'About' button */}
      <header className='z-20 bg-white border-b flex items-center justify-between px-6 py-4'>
        {/* An empty div to help center the title */}
        <div className='w-20'></div>

        <h1 className='font-urbanist text-[1.65rem] font-semibold text-center'>
          AI DownTime Chatbot
        </h1>

        {/* Your trigger button */}
        <button
          onClick={() => setIsAboutModalOpen(true)}
          className='w-20 rounded-md bg-gray-200 px-3 py-1 text-sm font-medium text-gray-800 hover:bg-gray-300'
        >
          About
        </button>
      </header>

      {/* Merged body, using the props from 'main' */}
      <div className='flex flex-1 min-h-0'>
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

      {/* Your modal component */}
      <AboutModal
        isOpen={isAboutModalOpen}
        onClose={() => setIsAboutModalOpen(false)}
      />
    </div>
  );
}

export default App;