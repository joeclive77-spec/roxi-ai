// Backend base URL. Change to your deployed API (e.g. https://api.example.com).
export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export const SSE_CHAT_PATH = `${API_BASE_URL}/api/chat`;