import React from "react";

const STORAGE_KEY = "ade_onboarding_done";

const POINTS = [
  {
    icon: "◉",
    title: "The map of science",
    body: "Each dot is a concept; lines connect concepts studied together. Dense clusters are established fields.",
  },
  {
    icon: "⤳",
    title: "Amber lines are uncrossed gaps",
    body: "Dashed amber edges link concepts that are structurally related but have never been studied together. Most breakthroughs began as one of these.",
  },
  {
    icon: "★",
    title: "Click a gap for the unasked question",
    body: "Gaps are ranked by how much answering them would unlock. Click any amber edge to see the AI-generated research question.",
  },
];

interface Props {
  onDone: () => void;
}

export const Onboarding: React.FC<Props> = ({ onDone }) => {
  const dismiss = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    onDone();
  };

  return (
    <div style={styles.backdrop}>
      <div style={styles.card}>
        <h2 style={styles.title}>How to read the map</h2>
        <div style={styles.points}>
          {POINTS.map((p) => (
            <div key={p.title} style={styles.point}>
              <span style={styles.icon}>{p.icon}</span>
              <div>
                <div style={styles.pointTitle}>{p.title}</div>
                <p style={styles.body}>{p.body}</p>
              </div>
            </div>
          ))}
        </div>
        <div style={styles.actions}>
          <button style={styles.nextBtn} onClick={dismiss}>
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};

export function shouldShowOnboarding(): boolean {
  return !localStorage.getItem(STORAGE_KEY);
}

const styles: Record<string, React.CSSProperties> = {
  backdrop: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.7)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    backdropFilter: "blur(4px)",
  },
  card: {
    background: "#1a1a1a",
    border: "1px solid #2d2d2d",
    borderRadius: 14,
    padding: "36px 40px",
    maxWidth: 460,
    width: "90%",
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 700,
    color: "#e5e7eb",
    margin: 0,
    lineHeight: 1.3,
  },
  points: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  point: {
    display: "flex",
    gap: 12,
    alignItems: "flex-start",
  },
  icon: {
    fontSize: 18,
    color: "#f59e0b",
    flexShrink: 0,
    width: 22,
    textAlign: "center",
    lineHeight: 1.4,
  },
  pointTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#e5e7eb",
    marginBottom: 3,
  },
  body: {
    fontSize: 13,
    color: "#9ca3af",
    lineHeight: 1.6,
    margin: 0,
  },
  actions: {
    display: "flex",
    justifyContent: "flex-end",
    alignItems: "center",
    marginTop: 8,
  },
  nextBtn: {
    fontSize: 14,
    fontWeight: 700,
    color: "#0f0f0f",
    background: "#f59e0b",
    border: "none",
    borderRadius: 8,
    padding: "10px 24px",
    cursor: "pointer",
  },
};
