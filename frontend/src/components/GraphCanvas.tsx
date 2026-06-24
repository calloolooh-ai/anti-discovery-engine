import React, { useRef, useCallback, useMemo, useState, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphExport, GraphNode } from "../types";
import {
  getCommunityColor,
  gapColor,
  regularEdgeColor,
  backgroundColor,
} from "../styles/theme";

interface Props {
  graphData: GraphExport;
  selectedGapId: string | null;
  onGapClick: (gapId: string) => void;
}

interface FGNode extends GraphNode {
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number;
  fy?: number;
}

interface FGEdge {
  source: string | FGNode;
  target: string | FGNode;
  weight: number;
  is_gap: boolean;
  gap_id?: string;
  gap_type?: "structural" | "cross_domain";
}

// Map paper_count to node radius
function nodeRadius(paperCount: number, min = 4, max = 20): number {
  const counts = [76, 231]; // rough min/max in mock — will self-adjust
  const t = Math.min(
    1,
    Math.max(0, (paperCount - counts[0]) / (counts[1] - counts[0]))
  );
  return min + t * (max - min);
}

const legendStyles: Record<string, React.CSSProperties> = {
  container: {
    position: "absolute",
    top: 12,
    left: 12,
    background: "rgba(26,26,26,0.88)",
    border: "1px solid #2d2d2d",
    borderRadius: 8,
    padding: "10px 14px",
    display: "flex",
    flexDirection: "column",
    gap: 7,
    pointerEvents: "none",
    zIndex: 10,
  },
  item: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: "50%",
    flexShrink: 0,
  },
  gapLine: {
    width: 24,
    height: 2,
    background: "#f59e0b",
    borderRadius: 1,
    flexShrink: 0,
    backgroundImage: "repeating-linear-gradient(90deg, #f59e0b 0, #f59e0b 4px, transparent 4px, transparent 8px)",
  },
  edgeLine: {
    width: 24,
    height: 2,
    background: "#374151",
    borderRadius: 1,
    flexShrink: 0,
  },
  label: {
    fontSize: 11,
    color: "#9ca3af",
    fontWeight: 500,
  },
  sub: {
    fontSize: 10,
    color: "#4b5563",
  },
};

interface LinkLabel {
  x: number;
  y: number;
  source: string;
  target: string;
  isGap: boolean;
  weight: number;
}

function endpointId(end: string | FGNode): string {
  return typeof end === "object" ? end.id : end;
}

export const GraphCanvas: React.FC<Props> = ({
  graphData,
  selectedGapId,
  onGapClick,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [linkLabel, setLinkLabel] = useState<LinkLabel | null>(null);

  // Clear a stale clicked-link label when the graph is rebuilt
  useEffect(() => {
    setLinkLabel(null);
  }, [graphData]);

  // Build FG-compatible data
  const fgData = useMemo(() => {
    const nodes: FGNode[] = graphData.nodes.map((n) => ({ ...n }));
    const links: FGEdge[] = graphData.edges.map((e) => ({ ...e }));
    return { nodes, links };
  }, [graphData]);

  // Tooltip state via canvas overlay
  const tooltipRef = useRef<HTMLDivElement>(null);

  const handleNodeHover = useCallback(
    (node: FGNode | null) => {
      const tooltip = tooltipRef.current;
      if (!tooltip) return;
      if (!node) {
        tooltip.style.display = "none";
        return;
      }
      tooltip.style.display = "block";
      tooltip.innerHTML = `
        <div style="font-weight:600;margin-bottom:4px;">${node.label}</div>
        <div style="color:#9ca3af;font-size:12px;">${node.field.join(", ")}</div>
        <div style="color:#f59e0b;font-size:12px;margin-top:2px;">${node.paper_count} papers</div>
      `;
    },
    []
  );

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const tooltip = tooltipRef.current;
    if (!tooltip || tooltip.style.display === "none") return;
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    tooltip.style.left = `${x + 14}px`;
    tooltip.style.top = `${y - 10}px`;
  }, []);

  const handleLinkClick = useCallback(
    (link: FGEdge, event: MouseEvent) => {
      const rect = containerRef.current?.getBoundingClientRect();
      setLinkLabel({
        x: rect ? event.clientX - rect.left : 0,
        y: rect ? event.clientY - rect.top : 0,
        source: endpointId(link.source),
        target: endpointId(link.target),
        isGap: link.is_gap,
        weight: link.weight,
      });
      if (link.is_gap && link.gap_id) {
        onGapClick(link.gap_id);
      }
    },
    [onGapClick]
  );

  const handleBackgroundClick = useCallback(() => {
    setLinkLabel(null);
  }, []);

  const handleLinkHover = useCallback((link: FGEdge | null) => {
    const el = containerRef.current;
    if (!el) return;
    el.style.cursor = link && link.is_gap ? "pointer" : "default";
  }, []);

  const paintNode = useCallback(
    (node: FGNode, ctx: CanvasRenderingContext2D) => {
      const x = node.x ?? 0;
      const y = node.y ?? 0;
      const r = nodeRadius(node.paper_count);
      const color = getCommunityColor(node.community_id);

      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();

      // Subtle border
      ctx.strokeStyle = "rgba(255,255,255,0.15)";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Label for larger nodes
      if (r > 8) {
        ctx.font = `${Math.max(8, r * 0.7)}px Inter, sans-serif`;
        ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(
          node.label.length > 14 ? node.label.slice(0, 13) + "…" : node.label,
          x,
          y + r + 8
        );
      }
    },
    []
  );

  const linkColor = useCallback(
    (link: FGEdge) => {
      if (link.is_gap) {
        return link.gap_id === selectedGapId ? "#fbbf24" : gapColor;
      }
      return regularEdgeColor;
    },
    [selectedGapId]
  );

  const linkWidth = useCallback(
    (link: FGEdge) => {
      if (link.is_gap) return link.gap_id === selectedGapId ? 3 : 2;
      return Math.max(0.5, link.weight * 2);
    },
    [selectedGapId]
  );

  const linkDirectionalParticles = useCallback(
    (link: FGEdge) => (link.is_gap ? 4 : 0),
    []
  );

  const linkDirectionalParticleSpeed = useCallback(
    (_link: FGEdge) => 0.006,
    []
  );

  const linkDirectionalParticleColor = useCallback(
    (_link: FGEdge) => gapColor,
    []
  );

  const linkLineDash = useCallback(
    (link: FGEdge) => (link.is_gap ? [4, 4] : null),
    []
  );

  return (
    <div
      ref={containerRef}
      style={{ position: "relative", width: "100%", height: "100%" }}
      onMouseMove={handleMouseMove}
    >
      <ForceGraph2D
        graphData={fgData}
        backgroundColor={backgroundColor}
        nodeCanvasObject={paintNode as never}
        nodeCanvasObjectMode={() => "replace"}
        nodePointerAreaPaint={(node: FGNode, color, ctx) => {
          const x = node.x ?? 0;
          const y = node.y ?? 0;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(x, y, nodeRadius(node.paper_count) + 4, 0, 2 * Math.PI);
          ctx.fill();
        }}
        onNodeHover={handleNodeHover as never}
        linkColor={linkColor as never}
        linkWidth={linkWidth as never}
        linkLineDash={linkLineDash as never}
        linkDirectionalParticles={linkDirectionalParticles as never}
        linkDirectionalParticleSpeed={linkDirectionalParticleSpeed as never}
        linkDirectionalParticleColor={linkDirectionalParticleColor as never}
        onLinkClick={handleLinkClick as never}
        onLinkHover={handleLinkHover as never}
        onBackgroundClick={handleBackgroundClick}
        linkHoverPrecision={12}
        warmupTicks={100}
        cooldownTicks={50}
        width={containerRef.current?.clientWidth ?? 800}
        height={containerRef.current?.clientHeight ?? 600}
      />
      {/* Hover tooltip */}
      <div
        ref={tooltipRef}
        style={{
          display: "none",
          position: "absolute",
          pointerEvents: "none",
          background: "#1a1a1a",
          border: "1px solid #2d2d2d",
          borderRadius: "6px",
          padding: "8px 12px",
          fontSize: "13px",
          color: "#e5e7eb",
          zIndex: 100,
          maxWidth: "220px",
          boxShadow: "0 4px 16px rgba(0,0,0,0.5)",
        }}
      />
      {/* Clicked-link label */}
      {linkLabel && (
        <div
          style={{
            position: "absolute",
            left: linkLabel.x,
            top: linkLabel.y,
            transform: "translate(-50%, calc(-100% - 10px))",
            pointerEvents: "none",
            background: "#1a1a1a",
            border: `1px solid ${linkLabel.isGap ? "rgba(245,158,11,0.5)" : "#2d2d2d"}`,
            borderRadius: 6,
            padding: "7px 11px",
            fontSize: 12.5,
            color: "#e5e7eb",
            zIndex: 100,
            maxWidth: 260,
            whiteSpace: "nowrap",
            boxShadow: "0 4px 16px rgba(0,0,0,0.5)",
          }}
        >
          <span style={{ color: "#e5e7eb", fontWeight: 600 }}>
            {linkLabel.source.replace(/_/g, " ")}
          </span>
          <span style={{ color: linkLabel.isGap ? "#f59e0b" : "#6b7280", margin: "0 6px" }}>
            {linkLabel.isGap ? "⇢" : "—"}
          </span>
          <span style={{ color: "#e5e7eb", fontWeight: 600 }}>
            {linkLabel.target.replace(/_/g, " ")}
          </span>
          <div style={{ fontSize: 11, color: linkLabel.isGap ? "#f59e0b" : "#6b7280", marginTop: 3 }}>
            {linkLabel.isGap
              ? "Unexplored research gap"
              : `Known connection · ${linkLabel.weight} co-occurrence${linkLabel.weight === 1 ? "" : "s"}`}
          </div>
        </div>
      )}
      {/* Legend */}
      <div style={legendStyles.container}>
        <div style={legendStyles.item}>
          <div style={{ ...legendStyles.dot, background: "#4e79a7" }} />
          <span style={legendStyles.label}>Concept node</span>
          <span style={legendStyles.sub}>(size = citations)</span>
        </div>
        <div style={legendStyles.item}>
          <div style={legendStyles.gapLine} />
          <span style={legendStyles.label}>Unexplored gap</span>
        </div>
        <div style={legendStyles.item}>
          <div style={legendStyles.edgeLine} />
          <span style={legendStyles.label}>Known connection</span>
        </div>
      </div>

      {/* Gap hint */}
      <div
        style={{
          position: "absolute",
          bottom: 12,
          left: "50%",
          transform: "translateX(-50%)",
          background: "rgba(26,26,26,0.85)",
          border: "1px solid #2d2d2d",
          borderRadius: "4px",
          padding: "4px 12px",
          fontSize: "12px",
          color: "#9ca3af",
          pointerEvents: "none",
        }}
      >
        Click an amber edge to explore a research gap
      </div>
    </div>
  );
};
