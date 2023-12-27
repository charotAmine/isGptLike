import axios from "axios";

export async function sendPrompt(message: string,sessionId: string, indexValue: string) {
  try {
    const response = await axios.post('http://localhost:5000/generateAnswer', { prompt: message, sessionId: sessionId, indexValue: indexValue });
    return response.data.Answer;
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return "I'm sorry, but I cannot answer that.";
    }
  }
}

export async function clearChat(sessionId: string) {
  try {
    const response = await axios.delete('http://localhost:5000/clearChat', {data:{ sessionId: sessionId }} );
    return response.data.Answer;
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return "I'm sorry, but I cannot delete";
    }
  }
}

export async function getChat() {
  try {
    const response = await axios.get('http://localhost:5000/getChatHistory');
    return response.data.messages;
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return error;
    }
  }
}

export async function createIndex(formData: FormData) {
  try {
    const response = await axios.post('http://localhost:5000/createIndex', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    } );
    return response.data.message;
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return "I'm sorry, but I cannot answer that.";
    }
  }
}
export async function importPlugin(formData: FormData) {
  try {
    const response = await axios.post('http://localhost:5000/importPlugin', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    } );
    return response.data.message;
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return "I'm sorry, but I cannot answer that.";
    }
  }
}

export async function listIndexes() {
  try {
    const response = await axios.get('http://localhost:5000/list_indexes');
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 500) {
      return "I'm sorry, but I cannot answer that.";
    }
  }
}