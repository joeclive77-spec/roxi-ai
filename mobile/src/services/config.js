// Backend base URL. EXPO_PUBLIC_API_URL (from .env, for local dev) overrides
// the production default. The default is hardcoded so EAS cloud builds (which
// can't see the gitignored .env) always bake in the live backend.
export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'https://roxi-ai-backend.onrender.com';

export const SSE_CHAT_PATH = `${API_BASE_URL}/api/chat`;