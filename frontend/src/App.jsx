
import Chatbot from '@/components/Chatbot';
import SidePanel from '@/components/SidePanel';
import React from 'react';

function App() {
  return (
    <div className='flex flex-col h-screen w-screen overflow-hidden'>
      <header className='z-20bg-white border-b'>
         <h1 className='font-urbanist text-[1.65rem] font-semibold text-center py-4'>AI DownTime Chatbot</h1>
      </header>
        <div className= 'flex flex-1 min-h-0'>
            <SidePanel />
            <main className='flex flex-col flex-1 min-h-0'>
               <Chatbot/>
            </main>
        </div>
    </div>
  );
}

export default App;