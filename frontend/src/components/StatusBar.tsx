import React from "react";

interface Props {
  stage: string;
  progress: number;
  visible: boolean;
  etaSeconds?: number | null;
}

const STAGE_LABELS: Record<string, string> = {
  fetching: "Reading papers from Semantic Scholar…",
  building: "Mapping the knowledge graph…",
  detecting_gaps: "Finding unexplored connections…",
  scoring: "Ranking gaps by impact potential…",
  complete: "Graph ready",
  error: "Something went wrong",
};

export const StatusBar: React.FC<Props> = ({
  stage,
  progress,
  visible,
  etaSeconds,
}) => {
  if (!visible) return null;

  const label = STAGE_LABELS[stage] ?? stage;
  const isError = stage === "error";
  const barColor = isError ? "#ef4444" : "#f59e0b";

  return (
    <div style={styles.bar}>
      <div
        style={{
          ...styles.fill,
          width: `${progress}%`,
          background: barColor,
          transition: "width 0.4s ease, background 0.2s",
        }}
      />
      <div style={styles.content}>
        <span style={styles.stageLabel}>{label}</span>
        <span style={styles.progress}>{Math.round(progress)}%</span>
        {etaSeconds != null && etaSeconds > 0 && (
          <span style={styles.eta}>~{Math.round(etaSeconds)}s remaining</span>
        )}
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  bar: {
    position: "relative",
    height: 28,
    background: "#111",
    borderBottom: "1px solid #2d2d2d",
    flexShrink: 0,
    overflow: "hidden",
  },
  fill: {
    position: "absolute",
    top: 0,
    left: 0,
    height: "100%",
    opacity: 0.25,
  },
  content: {
    position: "relative",
    height: "100%",
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "0 16px",
  },
  stageLabel: {
    fontSize: 12,
    fontWeight: 600,
    color: "#e5e7eb",
  },
  progress: {
    fontSize: 12,
    color: "#f59e0b",
    fontWeight: 700,
    fontFamily: "monospace",
  },
  eta: {
    fontSize: 11,
    color: "#6b7280",
  },
};
