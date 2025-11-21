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
            continue;
          } else if (evt.type === 'done') {
            yield { type: 'done' };
            return;
          } else if (evt.type === 'error' && typeof evt.message === 'string') {
            yield { type: 'error', message: evt.message };
            continue;
          } else if (evt.type === 'conversation_id' && typeof evt.id === 'string') {
            yield { type: 'conversation_id', id: evt.id };
            continue;
          }
        } catch {
          // Not a valid JSON, fall through to treat as a raw chunk
        }
      }

      // If we reach here, it's either not JSON, or it's a JSON shape we
      // don't recognize. In either case, we'll treat it as a raw text chunk.
      yield { type: 'chunk', content: raw };
    }
  } finally {
    reader.releaseLock();
  }
}