import React from "react";

interface Props {
  isHistorical: boolean;
  isRunning: boolean;
  onChange: (historical: boolean) => void;
}

export const ModeToggle: React.FC<Props> = ({
  isHistorical,
  isRunning,
  onChange,
}) => {
  return (
    <div style={styles.container}>
      <div style={styles.label}>Mode</div>
      <div style={styles.toggleGroup}>
        <button
          style={{
            ...styles.option,
            ...(isHistorical ? {} : styles.optionActive),
          }}
          onClick={() => onChange(false)}
          disabled={isRunning}
        >
          Live
        </button>
        <button
          style={{
            ...styles.option,
            ...(isHistorical ? styles.optionActiveHistorical : {}),
          }}
          onClick={() => onChange(true)}
          disabled={isRunning}
        >
          Historical
          <span style={styles.year}>2005</span>
        </button>
      </div>
      {isHistorical && (
        <p style={styles.hint}>
          Validating against a known gap discovered in 2001 using 2005 literature
        </p>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: "12px 16px",
    borderTop: "1px solid #2d2d2d",
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  label: {
    fontSize: 11,
    fontWeight: 700,
    color: "#6b7280",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
  },
  toggleGroup: {
    display: "flex",
    background: "#111",
    borderRadius: 6,
    border: "1px solid #2d2d2d",
    overflow: "hidden",
  },
  option: {
    flex: 1,
    padding: "6px 4px",
    background: "transparent",
    color: "#6b7280",
    fontSize: 12,
    fontWeight: 600,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    border: "none",
    cursor: "pointer",
    transition: "background 0.15s, color 0.15s",
  },
  optionActive: {
    background: "#f59e0b",
    color: "#0f0f0f",
    borderRadius: 4,
  },
  optionActiveHistorical: {
    background: "#7c3aed",
    color: "#fff",
    borderRadius: 4,
  },
  year: {
    fontSize: 10,
    background: "rgba(255,255,255,0.15)",
    borderRadius: 3,
    padding: "1px 4px",
  },
  hint: {
    fontSize: 11,
    color: "#6b7280",
    lineHeight: 1.4,
  },
};
