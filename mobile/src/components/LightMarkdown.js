import React from 'react';
import { Text } from 'react-native';

/**
 * Minimal markdown renderer using only core RN primitives.
 * Supports: **bold**, _italic_, `inline code`, newline paragraphs.
 * Replaces react-native-markdown-display (whose transitive dependency
 * react-native-fit-image@1.6.0 crashes on RN >= 0.71).
 */

function splitInline(text) {
  // Split into tokens, keeping the inline markers so they can be styled.
  const parts = text.split(/(\*\*[^*]+\*\*|_[^_]+_|`[^`]+`)/g).filter(Boolean);
  return parts.map((p, i) => {
    if (p.startsWith('**') && p.endsWith('**')) {
      return <Text key={i} style={{ fontWeight: '700' }}>{p.slice(2, -2)}</Text>;
    }
    if (p.startsWith('_') && p.endsWith('_')) {
      return <Text key={i} style={{ fontStyle: 'italic' }}>{p.slice(1, -1)}</Text>;
    }
    if (p.startsWith('`') && p.endsWith('`')) {
      return <Text key={i} style={{ fontFamily: 'monospace' }}>{p.slice(1, -1)}</Text>;
    }
    return p;
  });
}

export default function LightMarkdown({ children }) {
  if (typeof children !== 'string') return null;
  const paragraphs = children.split('\n\n');
  return (
    <Text>
      {paragraphs.map((para, i) => (
        <Text key={i}>{splitInline(para)}
          {i < paragraphs.length - 1 ? '\n\n' : null}
        </Text>
      ))}
    </Text>
  );
}