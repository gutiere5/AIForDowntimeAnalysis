const BASE_URL = "http://localhost:8000";

async function sendChatMessage(user_message, conversation_id = null, session_id = null) {
  const payload = { query: user_message };
  if (conversation_id) {
    payload.conversation_id = conversation_id;
  }
  if (session_id) {
    payload.session_id = session_id;
  }

  const response = await fetch(BASE_URL + `/agent_query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  return response.body;
}

async function getHistory(conversationId, sessionId) {
  const response = await fetch(`${BASE_URL}/get_history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      conversation_id: conversationId,
      session_id: sessionId,
    }),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

async function getConversations(sessionId) {
  const response = await fetch(`${BASE_URL}/conversations/${sessionId}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

async function deleteConversation(conversationId, sessionId) {
    const response = await fetch(`${BASE_URL}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

async function updateConversationTitle(conversationId, sessionId, newTitle) {
    const response = await fetch(`${BASE_URL}/conversations/${conversationId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            new_title: newTitle,
        }),
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

export default { sendChatMessage, getHistory, getConversations, deleteConversation, updateConversationTitle };