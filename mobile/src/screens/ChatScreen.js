import React, { useRef, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import Markdown from 'react-native-markdown-display';

import { streamChat } from '../services/sseClient';

const SYSTEM_BUBBLE = '#e8eaf6';
const USER_BUBBLE = '#b3e5fc';

export default function ChatScreen() {
  const [messages, setMessages] = useState([]); // {id, role, text, sources?}
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [assistantId, setAssistantId] = useState(null);
  const listRef = useRef(null);

  const send = async () => {
    const text = input.trim();
    if (!text || busy) return;
    setInput('');
    const userMsg = { id: `u${Date.now()}`, role: 'user', text };
    const aid = `a${Date.now()}`;
    setAssistantId(aid);
    setMessages((m) => [...m, userMsg, { id: aid, role: 'assistant', text: '' }]);
    setBusy(true);

    streamChat(
      {
        messages: [...messages, userMsg].map((m) => ({ role: m.role, content: m.text })),
        search: true,
      },
      {
        onSources: (sources) =>
          setMessages((m) =>
            m.map((mm) => (mm.id === aid ? { ...mm, sources } : mm))
          ),
        onToken: (d) =>
          setMessages((m) =>
            m.map((mm) => (mm.id === aid ? { ...mm, text: mm.text + d } : mm))
          ),
        onDone: (t) =>
          setMessages((m) => m.map((mm) => (mm.id === aid ? { ...mm, text: t } : mm))),
        onError: (e) =>
          setMessages((m) =>
            m.map((mm) => (mm.id === aid ? { ...mm, text: `Error: ${e}` } : mm))
          ),
        onEnd: () => {
          setBusy(false);
          setAssistantId(null);
        },
      }
    );
  };

  const renderItem = ({ item }) => (
    <View
      style={[
        styles.bubble,
        item.role === 'user' ? styles.userBubble : styles.botBubble,
      ]}
    >
      {item.role === 'assistant' && item.sources?.length > 0 && (
        <Text style={styles.sourceText}>Grounding: {item.sources.length} sources</Text>
      )}
      <Markdown>{item.text || (item.role === 'assistant' && busy ? '▎' : '')}</Markdown>
    </View>
  );

  return (
    <KeyboardAvoidingView style={styles.flex} behavior="padding">
      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(m) => m.id}
        renderItem={renderItem}
        style={styles.list}
        contentContainerStyle={styles.listContent}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
      />
      <View style={styles.inputBar}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Ask AI anything…"
          multiline
          editable={!busy}
        />
        <TouchableOpacity
          style={[styles.send, (!input || busy) && styles.sendDisabled]}
          onPress={send}
          disabled={!input || busy}
        >
          {busy ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.sendText}>Send</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  list: { flex: 1 },
  listContent: { padding: 12 },
  bubble: {
    maxWidth: '85%',
    borderRadius: 14,
    padding: 12,
    marginVertical: 4,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: USER_BUBBLE,
  },
  botBubble: {
    alignSelf: 'flex-start',
    backgroundColor: SYSTEM_BUBBLE,
  },
  sourceText: {
    fontSize: 11,
    color: '#555',
    marginBottom: 4,
    fontWeight: '600',
  },
  inputBar: {
    flexDirection: 'row',
    padding: 8,
    borderTopWidth: 1,
    borderTopColor: '#ddd',
    gap: 8,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 10,
    maxHeight: 120,
  },
  send: {
    backgroundColor: '#1a73e8',
    borderRadius: 20,
    paddingHorizontal: 18,
    justifyContent: 'center',
  },
  sendDisabled: { opacity: 0.5 },
  sendText: { color: '#fff', fontWeight: '600' },
});