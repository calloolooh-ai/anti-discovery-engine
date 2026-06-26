import React, { useState } from "react";
import type { Gap, ResearchQuestion } from "../types";
import { generateQuestions } from "../api/gaps";
import { TopGapsLeaderboard } from "./TopGapsLeaderboard";
import { QuestionCard } from "./QuestionCard";

interface Props {
  gaps: Gap[];
  selectedGapId: string | null;
  onSelectGap: (gapId: string) => void;
}

export const GapPanel: React.FC<Props> = ({
  gaps,
  selectedGapId,
  onSelectGap,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [localGaps, setLocalGaps] = useState<Gap[]>(gaps);

  // Keep localGaps in sync when parent updates
  React.useEffect(() => {
    setLocalGaps(gaps);
  }, [gaps]);

  const selectedGap = localGaps.find((g) => g.gap_id === selectedGapId) ?? null;

  const handleGenerate = async (gapId: string) => {
    setIsGenerating(true);
    try {
      const gap = localGaps.find((g) => g.gap_id === gapId);
      const questions: ResearchQuestion[] = await generateQuestions({
        gap_ids: [gapId],
        gaps: gap ? [gap] : [],
        use_high_quality: false,
      });
      if (questions.length > 0) {
        setLocalGaps((prev) =>
          prev.map((g) =>
            g.gap_id === gapId ? { ...g, question: questions[0] } : g
          )
        );
      }
    } catch (e) {
      console.error("Failed to generate question:", e);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <aside style={styles.panel}>
      <TopGapsLeaderboard
        gaps={localGaps}
        selectedGapId={selectedGapId}
        onSelect={onSelectGap}
        expandedContent={
          selectedGap ? (
            <QuestionCard
              gap={selectedGap}
              isGenerating={isGenerating}
              onGenerate={handleGenerate}
            />
          ) : null
        }
      />

      {!selectedGap && (
        <div style={styles.placeholder}>
          <div style={styles.placeholderIcon}>⬡</div>
          <p style={styles.placeholderText}>
            Select a gap from the list or click an amber edge in the graph
          </p>
        </div>
      )}
    </aside>
  );
};

const styles: Record<string, React.CSSProperties> = {
  panel: {
    width: 320,
    flexShrink: 0,
    background: "#1a1a1a",
    borderLeft: "1px solid #2d2d2d",
    display: "flex",
    flexDirection: "column",
    overflowY: "auto",
  },
  placeholder: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    padding: "32px 20px",
    color: "#4b5563",
  },
  placeholderIcon: {
    fontSize: 32,
    color: "#2d2d2d",
  },
  placeholderText: {
    fontSize: 13,
    textAlign: "center",
    lineHeight: 1.6,
    color: "#4b5563",
  },
};
