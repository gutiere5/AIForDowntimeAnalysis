const BASE_URL = "http://localhost:8000";

    async function sendChatMessage(user_message) {
      const response = await fetch(BASE_URL + `/agent_query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: user_message })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      return response.body;
    }

    export default {
      sendChatMessage
    };