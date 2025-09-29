
import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');

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

    try {
        const stream = await api.sendChatMessage(trimmedMessage);

        for await (const textChunk of parseSSEStream(stream)) {
            setMessages(draft => {
                const lastMessage = draft[draft.length - 1];
                lastMessage.content += textChunk;
            });
        }

        setMessages(draft => {
            draft[draft.length - 1].loading = false;
        });
    } catch (err) {
        console.error("Error:", err);
        setMessages(draft => {
          draft[draft.length - 1].loading = false;
          draft[draft.length - 1].error = true;
        });

        alert(`Error sending message: ${err.message}`);
    }
  }

  return (
    <div className='relative grow flex flex-col gap-6 pt-6'>
      {messages.length === 0 && (
        <div className='mt-3 font-urbanist text-primary-blue text-xl font-light space-y-2'>
          <p>👋 Welcome!</p>
          <p>I can summarize and analyze downtime records</p>
          <p>Ask me anything relating to downtime.</p>
        </div>
      )}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;
