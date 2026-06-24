import React, { useState, useEffect, useCallback } from "react";
import type { GraphExport, Inversion } from "../types";
import { getInversions } from "../api/inversions";

interface Props {
  graphData: GraphExport | null;
}

/**
 * Type-C "Antimatter Query" surface. For studied directional claims
 * (A → B) where the inverse (B → A) has never been tested, it lists the
 * systematically-unstudied inversions. Self-contained floating panel.
 */
export const InversionPanel: React.FC<Props> = ({ graphData }) => {
  const [open, setOpen] = useState(false);
  const [inversions, setInversions] = useState<Inversion[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const jobId = graphData?.job_id;
  const isReal = !!jobId && jobId !== "demo";

  const load = useCallback(async () => {
    if (!isReal || !jobId) return;
    setStatus("loading");
    setError(null);
    try {
      const res = await getInversions(jobId);
      setInversions(res.inversions);
      setStatus("done");
    } catch (e) {
      setError((e as Error).message);
      setStatus("error");
    }
  }, [isReal, jobId]);

  // Auto-load when the panel opens against a freshly-built graph.
  useEffect(() => {
    if (open && isReal && status === "idle") load();
  }, [open, isReal, status, load]);

  // Reset when a new graph is built.
  useEffect(() => {
    setInversions([]);
    setStatus("idle");
    setError(null);
  }, [jobId]);

  return (
    <>
      {/* Launcher */}
      <button
        style={styles.launcher}
        onClick={() => setOpen((o) => !o)}
        title="Antimatter Query — unstudied inverse relationships"
      >
        ⇄ Antimatter
      </button>

      {open && (
        <div style={styles.panel}>
          <div style={styles.header}>
            <div>
              <div style={styles.title}>Antimatter Query</div>
              <div style={styles.subtitle}>Studied A→B · untested B→A</div>
            </div>
            <button style={styles.close} onClick={() => setOpen(false)}>
              ×
            </button>
          </div>

          <div style={styles.body}>
            {!isReal && (
              <div style={styles.hint}>
                Build a live graph to mine directional claims and surface their
                untested inverses.
              </div>
            )}
            {isReal && status === "loading" && (
              <div style={styles.hint}>Scanning the corpus for one-way claims…</div>
            )}
            {isReal && status === "error" && (
              <div style={styles.hint}>Couldn’t load inversions: {error}</div>
            )}
            {isReal && status === "done" && inversions.length === 0 && (
              <div style={styles.hint}>
                No clean one-directional claims found in this corpus. Try larger /
                more causal fields (e.g. medicine, climate).
              </div>
            )}
            {inversions.map((inv) => (
              <div key={inv.inversion_id} style={styles.card}>
                <div style={styles.statement}>
                  <span style={styles.cause}>{inv.cause}</span>
                  <span style={styles.verb}> {inv.verb} </span>
                  <span style={styles.effect}>{inv.effect}</span>
                </div>
                <div style={styles.antimatter}>
                  <span style={styles.qmark}>?</span>
                  <span style={styles.effect}>{inv.effect}</span>
                  <span style={styles.verbGhost}> {inv.verb} </span>
                  <span style={styles.cause}>{inv.cause}</span>
                  <span style={styles.zero}>0 papers</span>
                </div>
                <div style={styles.meta}>
                  {inv.forward_count} paper{inv.forward_count === 1 ? "" : "s"} study
                  the forward direction · inverse untested
                </div>
                {inv.example_titles[0] && (
                  <div style={styles.example}>“{inv.example_titles[0]}”</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

const styles: Record<string, React.CSSProperties> = {
  launcher: {
    position: "fixed",
    bottom: 18,
    left: 18,
    zIndex: 60,
    background: "#1a1a1a",
    border: "1px solid rgba(167,139,250,0.4)",
    color: "#c4b5fd",
    fontSize: 13,
    fontWeight: 600,
    borderRadius: 20,
    padding: "8px 16px",
    cursor: "pointer",
    boxShadow: "0 4px 16px rgba(0,0,0,0.5)",
  },
  panel: {
    position: "fixed",
    bottom: 64,
    left: 18,
    width: 340,
    maxHeight: "70vh",
    zIndex: 60,
    background: "#141414",
    border: "1px solid #2d2d2d",
    borderRadius: 12,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 14px",
    borderBottom: "1px solid #2d2d2d",
    background: "rgba(139,92,246,0.08)",
  },
  title: { fontSize: 14, fontWeight: 700, color: "#e5e7eb" },
  subtitle: { fontSize: 11, color: "#8b5cf6", marginTop: 2 },
  close: {
    background: "transparent",
    border: "none",
    color: "#6b7280",
    fontSize: 20,
    cursor: "pointer",
    lineHeight: 1,
  },
  body: {
    padding: 12,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  hint: { fontSize: 12.5, color: "#6b7280", lineHeight: 1.6, padding: "8px 2px" },
  card: {
    background: "#1a1a1a",
    border: "1px solid #2d2d2d",
    borderRadius: 8,
    padding: "10px 12px",
  },
  statement: { fontSize: 13, lineHeight: 1.5 },
  cause: { color: "#e5e7eb", fontWeight: 600 },
  effect: { color: "#e5e7eb", fontWeight: 600 },
  verb: { color: "#10b981", fontStyle: "italic" },
  antimatter: {
    fontSize: 13,
    lineHeight: 1.5,
    marginTop: 4,
    opacity: 0.85,
    display: "flex",
    alignItems: "center",
    gap: 4,
    flexWrap: "wrap",
  },
  qmark: {
    color: "#a78bfa",
    fontWeight: 800,
    fontSize: 14,
  },
  verbGhost: { color: "#a78bfa", fontStyle: "italic" },
  zero: {
    marginLeft: "auto",
    fontSize: 10.5,
    color: "#ef4444",
    fontWeight: 700,
    border: "1px solid rgba(239,68,68,0.3)",
    borderRadius: 4,
    padding: "1px 6px",
  },
  meta: { fontSize: 11, color: "#6b7280", marginTop: 6 },
  example: {
    fontSize: 11,
    color: "#4b5563",
    marginTop: 4,
    fontStyle: "italic",
    lineHeight: 1.4,
  },
};
