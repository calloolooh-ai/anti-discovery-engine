import React, { useState } from "react";

const STORAGE_KEY = "ade_onboarding_done";

const STEPS = [
  {
    title: "This is the map of science",
    body: "Each dot is a scientific concept. Lines connect concepts that have been studied together. Dense clusters are established fields.",
    highlight: "graph",
  },
  {
    title: "Amber lines are gaps nobody has crossed",
    body: "These dashed amber connections link concepts that are structurally related but have never been studied together. Every major scientific breakthrough started as one of these gaps.",
    highlight: "gap",
  },
  {
    title: "Click a gap to see the question nobody has asked",
    body: "The engine ranks each gap by how many other problems answering it would unlock. Click any amber edge or gap in the list to see the AI-generated research question.",
    highlight: "panel",
  },
];

interface Props {
  onDone: () => void;
}

export const Onboarding: React.FC<Props> = ({ onDone }) => {
  const [step, setStep] = useState(0);

  const advance = () => {
    if (step < STEPS.length - 1) {
      setStep(step + 1);
    } else {
      localStorage.setItem(STORAGE_KEY, "1");
      onDone();
    }
  };

  const skip = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    onDone();
  };

  const current = STEPS[step];

  return (
    <div style={styles.backdrop}>
      <div style={styles.card}>
        <div style={styles.stepIndicator}>
          {STEPS.map((_, i) => (
            <div
              key={i}
              style={{
                ...styles.dot,
                background: i === step ? "#f59e0b" : "#2d2d2d",
              }}
            />
          ))}
        </div>

        <div style={styles.stepNum}>
          Step {step + 1} of {STEPS.length}
        </div>
        <h2 style={styles.title}>{current.title}</h2>
        <p style={styles.body}>{current.body}</p>

        <div style={styles.actions}>
          <button style={styles.skipBtn} onClick={skip}>
            Skip
          </button>
          <button style={styles.nextBtn} onClick={advance}>
            {step < STEPS.length - 1 ? "Next →" : "Got it"}
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
  stepIndicator: {
    display: "flex",
    gap: 6,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    transition: "background 0.2s",
  },
  stepNum: {
    fontSize: 11,
    color: "#4b5563",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  title: {
    fontSize: 20,
    fontWeight: 700,
    color: "#e5e7eb",
    margin: 0,
    lineHeight: 1.3,
  },
  body: {
    fontSize: 14,
    color: "#9ca3af",
    lineHeight: 1.7,
    margin: 0,
  },
  actions: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 8,
  },
  skipBtn: {
    fontSize: 13,
    color: "#4b5563",
    background: "transparent",
    border: "none",
    cursor: "pointer",
    padding: "8px 0",
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
