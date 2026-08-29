// Minimal SSE (Server-Sent Events) streaming client for the chat endpoint.
//
// Takes a POST body and streams `sources`, `token`, `error`, and `done`
// events to the provided handlers. Works in React Native via fetch + reader,
// and in plain Node (run `node examples/consume_sse.js`).
import { SSE_CHAT_PATH } from './config';

const decoder = new TextDecoder('utf-8');

/**
 * @param {object} body           Chat request payload (messages, search, ...)
 * @param {object} handlers
 * @param {(src:object[])=>void} handlers.onSources source citations
 * @param {(delta:string)=>void} handlers.onToken  incremental text
 * @param {(usage:object)=>void} handlers.onDone   full built message
 * @param {(err:string)=>void}   handlers.onError  stream error
 */
export async function streamChat(body, handlers) {
  const controller = new AbortController();
  try {
    const res = await fetch(SSE_CHAT_PATH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!res.ok) {
      handlers.onError?.(`HTTP ${res.status} ${await res.text()}`);
      return;
    }

    const reader = res.body.getReader();
    let buf = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      // Split on blank-line boundaries.
      const lines = buf.split('\n\n');
      buf = lines.pop();
      for (const frame of lines) {
        dispatchFrame(frame, handlers);
      }
    }
    if (buf.trim()) dispatchFrame(buf, handlers);
    handlers.onEnd?.();
  } catch (err) {
    handlers.onError?.(err.message || String(err));
  }
}

function dispatchFrame(frame, h) {
  let event = 'message';
  const dataLines = [];
  for (const line of frame.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
  }
  const data = dataLines.join('\n');
  if (!data) return;

  let parsed;
  try {
    parsed = JSON.parse(data);
  } catch {
    parsed = data;
  }

  switch (event) {
    case 'sources':
      h.onSources?.(Array.isArray(parsed) ? parsed : []);
      break;
    case 'token':
      h.onToken?.(parsed && parsed.delta ? parsed.delta : '');
      break;
    case 'done':
      h.onDone?.(parsed && parsed.text ? parsed.text : '');
      break;
    case 'error':
      h.onError?.(parsed && parsed.message ? parsed.message : String(parsed));
      break;
    default:
      h.onMessage?.(parsed);
  }
}