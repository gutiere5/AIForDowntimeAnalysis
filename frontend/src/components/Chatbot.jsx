import {useRef, useState} from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
const [messages, setMessages] = useImmer([]);
const [newMessage, setNewMessage] = useState('');
const conversationIdRef = useRef(null);
const firstTokenRef = useRef(false);
const isLoading = messages.length > 0 && messages[messages.length - 1].loading;

async function submitNewMessage() {
  const trimmedMessage = newMessage.trim();
  if (!trimmedMessage || isLoading) return;

  setMessages(draft => {
    draft.push(
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', sources: [], loading: true }
    );
  });
  setNewMessage('');
  firstTokenRef.current = true;

  try {
      const stream = await api.sendChatMessage(trimmedMessage, conversationIdRef.current);
      for await (const evt of parseSSEStream(stream)) {
        if (evt.type === 'conversation_id') {
          conversationIdRef.current = evt.id;
        } else if (evt.type === 'chunk') {
          let token = evt.content;
          if (firstTokenRef.current) {
            token = token.replace(/^\s+/, '');
            firstTokenRef.current = false;
          }
          setMessages(d => { d[d.length - 1].content += token; });
        } else if (evt.type === 'error') {
          setMessages(d => {
            const last = d[d.length - 1];
            last.loading = false;
            last.error = true;
            last.content += (last.content ? '\n\n' : '') + evt.message;
          });
          break;
        } else if (evt.type === 'done') {
          setMessages(d => { d[d.length - 1].loading = false; });
          break;
        }
      }
    } catch (err) {
      console.error('Stream error:', err);
      setMessages(d => {
        const last = d[d.length - 1];
        last.loading = false;
        last.error = true;
      });
      alert(`Error: ${err.message}`);
    }
  }


return (
  <div className='flex flex-col flex-1 min-h-0 w-full border-8 border-gray-200 rounded-lg'>

    <div className='flex-1 min-h-0 overflow-y-auto px-8 py-6 space-y-6'>
      {messages.length === 0 && (
        <div className='flex flex-col items-center justify-center rounded-lg bg-gray-50 border border-gray-200 px-10 py-10 text-center font-urbanist text-gray-800'>
          <p className='text-2xl font-semibold mb-2'>Welcome to \[Chatbot Name]\!</p>
          <p className=''>Here to analyze any downtime request</p>
        </div>
      )}
      <ChatMessages messages={messages} isLoading={isLoading} />
    </div>

    <div className='border-t bg-white px-6 py-4'>
      <ChatInput
        className={"w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"}
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  </div>
 );
}

export default Chatbot;