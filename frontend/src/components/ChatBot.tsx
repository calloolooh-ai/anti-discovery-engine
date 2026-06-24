import React, { useState, useRef, useEffect } from "react";
import type { Gap, GraphExport } from "../types";
import { sendChatMessage, type ChatMessage } from "../api/chat";

interface Props {
  graphData: GraphExport | null;
  gaps: Gap[];
}

const SUGGESTIONS = [
  "What's the most important gap?",
  "Explain the top gap simply",
  "Which field should I study to close gap 1?",
  "Why hasn't this gap been explored before?",
];

export const ChatBot: React.FC<Props> = ({ graphData, gaps }) => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([
        {
          role: "assistant",
          content: graphData
            ? `I can see your knowledge graph — ${graphData.node_count} concepts, ${graphData.gap_count} unexplored gaps. Ask me anything about the gaps or what they mean.`
            : "Load a graph first, then ask me anything about the research gaps it finds.",
        },
      ]);
    }
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || isLoading) return;
    const userMsg: ChatMessage = { role: "user", content: text };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setIsLoading(true);
    try {
      const reply = await sendChatMessage(updated, graphData, gaps);
      setMessages([...updated, { role: "assistant", content: reply }]);
    } catch {
      setMessages([
        ...updated,
        { role: "assistant", content: "Sorry, I couldn't reach the server. Check that the backend is running." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating button */}
      <button style={styles.fab} onClick={() => setOpen(!open)} title="Ask about the graph">
        {open ? "✕" : "💬"}
      </button>

      {/* Chat panel */}
      {open && (
        <div style={styles.panel}>
          <div style={styles.header}>
            <span style={styles.headerTitle}>Ask the Engine</span>
            <span style={styles.headerSub}>Graph-aware AI assistant</span>
          </div>

          <div style={styles.messages}>
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  ...styles.bubble,
                  ...(m.role === "user" ? styles.userBubble : styles.aiBubble),
                }}
              >
                {m.content}
              </div>
            ))}
            {isLoading && (
              <div style={{ ...styles.bubble, ...styles.aiBubble, color: "#4b5563" }}>
                Thinking…
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Suggestions */}
          {messages.length <= 1 && (
            <div style={styles.suggestions}>
              {SUGGESTIONS.map((s) => (
                <button key={s} style={styles.suggestion} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}

          <div style={styles.inputRow}>
            <input
              style={styles.input}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send(input)}
              placeholder="Ask about gaps, fields, research…"
              disabled={isLoading}
            />
            <button
              style={styles.sendBtn}
              onClick={() => send(input)}
              disabled={isLoading || !input.trim()}
            >
              →
            </button>
          </div>
        </div>
      )}
    </>
  );
};

const styles: Record<string, React.CSSProperties> = {
  fab: {
    position: "fixed",
    bottom: 24,
    right: 24,
    width: 52,
    height: 52,
    borderRadius: "50%",
    background: "#f59e0b",
    border: "none",
    fontSize: 22,
    cursor: "pointer",
    zIndex: 500,
    boxShadow: "0 4px 16px rgba(245,158,11,0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  panel: {
    position: "fixed",
    bottom: 88,
    right: 24,
    width: 360,
    maxHeight: 520,
    background: "#1a1a1a",
    border: "1px solid #2d2d2d",
    borderRadius: 12,
    display: "flex",
    flexDirection: "column",
    zIndex: 499,
    boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
    overflow: "hidden",
  },
  header: {
    padding: "12px 16px",
    borderBottom: "1px solid #2d2d2d",
    display: "flex",
    flexDirection: "column",
    gap: 2,
  },
  headerTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#e5e7eb",
  },
  headerSub: {
    fontSize: 11,
    color: "#4b5563",
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "12px 14px",
    display: "flex",
    flexDirection: "column",
    gap: 10,
    minHeight: 0,
    maxHeight: 300,
  },
  bubble: {
    fontSize: 13,
    lineHeight: 1.6,
    padding: "8px 12px",
    borderRadius: 8,
    maxWidth: "90%",
    wordBreak: "break-word",
  },
  userBubble: {
    alignSelf: "flex-end",
    background: "#f59e0b",
    color: "#0f0f0f",
    fontWeight: 500,
  },
  aiBubble: {
    alignSelf: "flex-start",
    background: "#242424",
    color: "#e5e7eb",
    border: "1px solid #2d2d2d",
  },
  suggestions: {
    padding: "8px 12px",
    display: "flex",
    flexDirection: "column",
    gap: 5,
    borderTop: "1px solid #1f1f1f",
  },
  suggestion: {
    fontSize: 12,
    color: "#9ca3af",
    background: "#242424",
    border: "1px solid #2d2d2d",
    borderRadius: 6,
    padding: "6px 10px",
    textAlign: "left",
    cursor: "pointer",
  },
  inputRow: {
    display: "flex",
    gap: 8,
    padding: "10px 12px",
    borderTop: "1px solid #2d2d2d",
  },
  input: {
    flex: 1,
    background: "#242424",
    border: "1px solid #2d2d2d",
    borderRadius: 6,
    color: "#e5e7eb",
    fontSize: 13,
    padding: "8px 10px",
    outline: "none",
  },
  sendBtn: {
    background: "#f59e0b",
    border: "none",
    borderRadius: 6,
    color: "#0f0f0f",
    fontWeight: 700,
    fontSize: 16,
    padding: "8px 14px",
    cursor: "pointer",
  },
};
