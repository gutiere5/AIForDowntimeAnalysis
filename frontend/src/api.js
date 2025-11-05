const BASE_URL = "http://localhost:8000";

    async function sendChatMessage(user_message, conversation_id = null) {
      const payload = { query: user_message };
      if (conversation_id) {
        payload.conversation_id = conversation_id;
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

    export default { sendChatMessage };