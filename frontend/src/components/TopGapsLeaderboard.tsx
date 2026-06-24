import React, { useEffect, useRef } from "react";
import type { Gap } from "../types";

interface Props {
  gaps: Gap[];
  selectedGapId: string | null;
  onSelect: (gapId: string) => void;
  /** Rendered inline directly beneath the selected gap row. */
  expandedContent?: React.ReactNode;
}

export const TopGapsLeaderboard: React.FC<Props> = ({
  gaps,
  selectedGapId,
  onSelect,
  expandedContent,
}) => {
  const sorted = [...gaps].sort((a, b) => b.leverage_score - a.leverage_score);

  const selectedRowRef = useRef<HTMLButtonElement>(null);

  // Scroll the selected gap to the top so its inline detail card is visible
  useEffect(() => {
    selectedRowRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }, [selectedGapId]);

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.title}>Top Gaps</span>
        <span style={styles.count}>{gaps.length} detected</span>
      </div>
      {gaps.length === 0 ? (
        <div style={styles.empty}>No gaps scored yet</div>
      ) : (
        <div style={styles.list}>
          {sorted.map((gap, i) => {
            const isSelected = selectedGapId === gap.gap_id;
            return (
              <React.Fragment key={gap.gap_id}>
                <button
                  ref={isSelected ? selectedRowRef : undefined}
                  style={{
                    ...styles.row,
                    ...(isSelected ? styles.rowSelected : {}),
                  }}
                  onClick={() => onSelect(gap.gap_id)}
                >
                  <span style={styles.rank}>{i + 1}</span>
                  <div style={styles.info}>
                    <div style={styles.nodes}>
                      <span style={styles.nodeA}>{gap.node_a.replace(/_/g, " ")}</span>
                      <span style={styles.arrow}>→</span>
                      <span style={styles.nodeB}>{gap.node_b.replace(/_/g, " ")}</span>
                    </div>
                    <div style={styles.meta}>
                      <span
                        className={`badge badge--${gap.type === "cross_domain" ? "cross-domain" : "structural"}`}
                      >
                        {gap.type === "cross_domain" ? "Cross-Domain" : "Structural"}
                      </span>
                    </div>
                  </div>
                  <div style={styles.scoreCol}>
                    <div style={styles.scoreNum}>{gap.leverage_score}</div>
                    <div
                      style={{
                        ...styles.scoreBar,
                        width: `${gap.leverage_score}%`,
                      }}
                    />
                  </div>
                </button>
                {isSelected && expandedContent && (
                  <div style={styles.expanded}>{expandedContent}</div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      )}
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 16px 10px",
    borderBottom: "1px solid #2d2d2d",
  },
  title: {
    fontSize: 12,
    fontWeight: 700,
    color: "#e5e7eb",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
  },
  count: {
    fontSize: 11,
    color: "#6b7280",
    background: "#242424",
    padding: "2px 7px",
    borderRadius: 4,
  },
  empty: {
    padding: "20px 16px",
    fontSize: 13,
    color: "#4b5563",
    textAlign: "center",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: 0,
  },
  expanded: {
    borderBottom: "1px solid #2d2d2d",
    background: "#161616",
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 16px",
    background: "transparent",
    border: "none",
    borderBottom: "1px solid #1f1f1f",
    cursor: "pointer",
    textAlign: "left",
    transition: "background 0.12s",
    width: "100%",
  },
  rowSelected: {
    background: "rgba(245,158,11,0.08)",
    borderLeft: "2px solid #f59e0b",
    paddingLeft: 14,
  },
  rank: {
    fontSize: 12,
    fontWeight: 700,
    color: "#4b5563",
    width: 16,
    flexShrink: 0,
  },
  info: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: 4,
    minWidth: 0,
  },
  nodes: {
    display: "flex",
    alignItems: "center",
    gap: 4,
    flexWrap: "wrap",
  },
  nodeA: {
    fontSize: 12,
    color: "#e5e7eb",
    fontWeight: 500,
  },
  arrow: {
    fontSize: 11,
    color: "#f59e0b",
  },
  nodeB: {
    fontSize: 12,
    color: "#e5e7eb",
    fontWeight: 500,
  },
  meta: {
    display: "flex",
    gap: 6,
  },
  scoreCol: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end",
    gap: 4,
    flexShrink: 0,
  },
  scoreNum: {
    fontSize: 14,
    fontWeight: 700,
    color: "#f59e0b",
  },
  scoreBar: {
    height: 3,
    background: "#f59e0b",
    borderRadius: 2,
    maxWidth: 40,
  },
};
