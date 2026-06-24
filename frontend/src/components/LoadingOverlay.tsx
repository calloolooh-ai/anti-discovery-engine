import React from "react";

interface Props {
  stage: string;
  progress: number;
  etaSeconds?: number | null;
  visible: boolean;
}

const STAGE_LABELS: Record<string, string> = {
  fetching: "Fetching papers from arXiv…",
  building: "Building knowledge graph…",
  detecting_gaps: "Detecting structural gaps…",
  scoring: "Scoring gap leverage…",
  complete: "Done!",
  error: "Something went wrong",
};

export const LoadingOverlay: React.FC<Props> = ({
  stage,
  progress,
  etaSeconds,
  visible,
}) => {
  if (!visible) return null;

  const label = STAGE_LABELS[stage] ?? stage;

  return (
    <div style={styles.overlay}>
      <div style={styles.card}>
        {/* Animated hexagon spinner */}
        <div style={styles.spinner}>
          <div style={styles.spinnerRing} />
        </div>

        <div style={styles.stageLabel}>{label}</div>

        {/* Progress bar */}
        <div style={styles.barTrack}>
          <div
            style={{
              ...styles.barFill,
              width: `${progress}%`,
            }}
          />
        </div>

        <div style={styles.meta}>
          <span style={styles.pct}>{Math.round(progress)}%</span>
          {etaSeconds != null && etaSeconds > 0 && (
            <span style={styles.eta}>
              ~{Math.round(etaSeconds)}s remaining
            </span>
          )}
        </div>

        <p style={styles.hint}>
          The engine is mapping the knowledge graph and hunting for structural
          gaps that no one has explored yet.
        </p>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "absolute",
    inset: 0,
    background: "rgba(15,15,15,0.88)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 200,
    backdropFilter: "blur(4px)",
  },
  card: {
    background: "#1a1a1a",
    border: "1px solid #2d2d2d",
    borderRadius: 12,
    padding: "40px 48px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 18,
    maxWidth: 400,
    width: "90%",
  },
  spinner: {
    width: 48,
    height: 48,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  spinnerRing: {
    width: 40,
    height: 40,
    border: "3px solid #2d2d2d",
    borderTopColor: "#f59e0b",
    borderRadius: "50%",
    animation: "spin 0.9s linear infinite",
  },
  stageLabel: {
    fontSize: 15,
    fontWeight: 600,
    color: "#e5e7eb",
    textAlign: "center",
  },
  barTrack: {
    width: "100%",
    height: 6,
    background: "#2d2d2d",
    borderRadius: 3,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    background: "#f59e0b",
    borderRadius: 3,
    transition: "width 0.4s ease",
  },
  meta: {
    display: "flex",
    gap: 16,
    alignItems: "center",
  },
  pct: {
    fontSize: 20,
    fontWeight: 700,
    color: "#f59e0b",
    fontFamily: "monospace",
  },
  eta: {
    fontSize: 13,
    color: "#6b7280",
  },
  hint: {
    fontSize: 12,
    color: "#4b5563",
    textAlign: "center",
    lineHeight: 1.6,
  },
};

// Inject keyframes once
const styleTag = document.createElement("style");
styleTag.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`;
if (!document.head.querySelector("[data-spin]")) {
  styleTag.setAttribute("data-spin", "1");
  document.head.appendChild(styleTag);
}
