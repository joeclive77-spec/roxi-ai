// Standalone Node demo: POSTs to the chat endpoint and prints tokens as they
// stream in. Requires the backend to be running:
//   cd backend && uvicorn app.main:app
//   node examples/consume_sse.js
const { streamChat } = require('../src/services/sseClient');

streamChat(
  { messages: [{ role: 'user', content: 'What can you help me with?' }], search: true },
  {
    onSources: (s) => console.log(`\n[SOURCES] ${s.length} references\n`),
    onToken: (d) => process.stdout.write(d),
    onDone: (t) => console.log('\n[DONE]'),
    onError: (e) => console.error('\n[ERROR]', e),
  }
);