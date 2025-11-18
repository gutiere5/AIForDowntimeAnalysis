
import Chatbot from '@/components/Chatbot';
import SidePanel from '@/components/SidePanel';
// 1. IMPORT useState from React and your new AboutModal
import  { useState } from 'react';
import { AboutModal } from './components/AboutModal'; // Make sure this path is correct

function App() {
  // 2. ADD state to control the modal's visibility
  const [isAboutModalOpen, setIsAboutModalOpen] = useState(false);

  return (
    <div className='flex flex-col h-screen w-screen overflow-hidden'>
      {/* I've added flex layout to the header to position 
        the title and the new button.
      */}
      <header className='z-20 bg-white border-b flex items-center justify-between px-6 py-4'>
        {/* An empty div to help center the title */}
        <div className='w-20'></div> 
        
        <h1 className='font-urbanist text-[1.65rem] font-semibold text-center'>
          AI DownTime Chatbot
        </h1>

        {/* 3. ADD the trigger button */}
        <button 
          onClick={() => setIsAboutModalOpen(true)}
          className='w-20 rounded-md bg-gray-200 px-3 py-1 text-sm font-medium text-gray-800 hover:bg-gray-300'
        >
          About
        </button>
      </header>

      <div className='flex flex-1 min-h-0'>
        <SidePanel />
        <main className='flex flex-col flex-1 min-h-0'>
          <Chatbot />
        </main>
      </div>

      {/* 4. ADD the modal component itself. 
        It will be hidden until `isAboutModalOpen` is true.
      */}
      <AboutModal 
        isOpen={isAboutModalOpen} 
        onClose={() => setIsAboutModalOpen(false)} 
      />
    </div>
  );
}

export default App;