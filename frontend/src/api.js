const BASE_URL = "http://localhost:8000";

    async function sendChatMessage(user_message) {
      const response = await fetch(BASE_URL + `/agent_query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: user_message })
      });
      if (!response.ok) {
        return Promise.reject({ status: response.status, data: await response.json() });
      }

      const data = await response.json();
      console.log("API Response:", data);

      // Check if we have a response
      if (!data || !data.response) {
        console.warn("Empty or invalid response received");
      }

      return data;
    }

    export default {
      sendChatMessage
    };