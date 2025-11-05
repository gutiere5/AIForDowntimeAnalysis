import { EventSourceParserStream } from 'eventsource-parser/stream';

export async function* parseSSEStream(stream) {
  const reader = stream
    .pipeThrough(new TextDecoderStream())
    .pipeThrough(new EventSourceParserStream())
    .getReader();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const raw = (value?.data ?? '').trim();
      if (!raw) continue;
      if (raw === '[DONE]') {
        yield { type: 'done' };
        return;
      }
      if (raw.startsWith('{') && raw.endsWith('}')) {
        try {
          const evt = JSON.parse(raw);
            if (evt.type === 'chunk' && typeof evt.content === 'string') {
              yield { type: 'chunk', content: evt.content };
            } else if (evt.type === 'done') {
              yield { type: 'done' };
              return;
            } else if (evt.type === 'conversation_id' && typeof evt.id === 'string') {
              yield { type: 'conversation_id', id: evt.id };
            } else {
              // Unknown JSON -> treat as text chunk
              yield { type: 'chunk', content: raw };
            }
          continue;
        } catch {
          // Fall through to treat as text
        }
      }
      if (raw.startsWith('Error:')) {
        yield { type: 'error', message: raw };
        continue;
      }
      yield { type: 'chunk', content: raw };
    }
  } finally {
    reader.releaseLock();
  }
}