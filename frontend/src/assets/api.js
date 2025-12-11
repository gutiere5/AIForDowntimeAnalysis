import axios from 'axios';

const BASE_URL = "http://localhost:8000";

async function sendChatMessage(user_query, conversation_id = null, session_id = null) {
    const response = await fetch(`${BASE_URL}/agent/query?query=${user_query}&session_id=${session_id}&conversation_id=${conversation_id}`);
    return response.body;
}

async function getConversation(conversationId, sessionId) {
    const response = await axios.get(`${BASE_URL}/conversations?conversation_id=${conversationId}&session_id=${sessionId}`);
    return response.data;
}

async function getConversations(sessionId) {
    const response = await axios.get(`${BASE_URL}/conversations/${sessionId}`);
    return response.data;
}

async function createConversation(sessionId, title = "New Conversation") {
    const response = await axios.post(`${BASE_URL}/conversations/create?session_id=${sessionId}&title=${title}`);
    return response.data;
}

async function deleteConversation(conversationId, sessionId) {
    try {
        const response = await axios.delete(`${BASE_URL}/conversations/${sessionId}/${conversationId}`);
        return response.data;
    } catch (error) {
        throw new Error(`HTTP error! status: ${error.response.status}`);
    }
}

async function deleteAllConversations(sessionId) {
    try {
        const response = await axios.delete(`${BASE_URL}/conversations/${sessionId}`);
        return response.data;
    } catch (error) {
        throw new Error(`HTTP error! status: ${error.response.status}`);
    }
}

async function updateConversationTitle(conversationId, sessionId, newTitle) {
    try {
        const response = await axios.put(`${BASE_URL}/conversations`, null, {
            params: {
                session_id: sessionId,
                conversation_id: conversationId,
                title: newTitle,
            }
        });
        return response.data
    } catch (error) {
        throw new Error(`HTTP error! status: ${error.response.status}`);
    }
}

async function getKnownIssues() {
    try {
        const response = await axios.get(`${BASE_URL}/known_issues/`);
        return response.data.known_issues;
    } catch (error) {
        throw new Error(`Failed to fetch known issues: ${error.response?.status || error.message}`);
    }
}

async function addKnownIssue(issueData) {
    try {
        const response = await axios.post(`${BASE_URL}/known_issues/`, null, {
            params: {
                title: issueData.title,
                description: issueData.description,
                solution: issueData.solution,
                author: issueData.author
            }
        });
        return response.data;
    } catch (error) {
        throw new Error(`Failed to add known issue: ${error.response?.status || error.message}`);
    }
}

async function updateKnownIssue(issueId, issueData) {
    try {
        const response = await axios.put(`${BASE_URL}/known_issues/${issueId}`, null, {
            params: {
                title: issueData.title,
                description: issueData.description,
                solution: issueData.solution,
                author: issueData.author
            }
        });
        return response.data;
    } catch (error) {
        throw new Error(`Failed to update known issue: ${error.response?.status || error.message}`);
    }
}

async function deleteKnownIssue(issueId) {
    try {
        const response = await axios.delete(`${BASE_URL}/known_issues/${issueId}`);
        return response.data;
    } catch (error) {
        throw new Error(`Failed to delete known issue: ${error.response?.status || error.message}`);
    }
}

export default {
    sendChatMessage,
    getConversation,
    getConversations,
    deleteConversation,
    updateConversationTitle,
    createConversation,
    getKnownIssues,
    addKnownIssue,
    updateKnownIssue,
    deleteKnownIssue,
    deleteAllConversations
};