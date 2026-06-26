import { useState, useCallback } from "react";
import type { GraphExport, BuildRequest, JobStatus, Gap } from "../types";
import { buildGraphSync } from "../api/graph";
import { mockGraphExport } from "../api/mockData";

type Stage = JobStatus["stage"] | "idle";

interface GraphDataState {
  graphData: GraphExport | null;
  isBuilding: boolean;
  progress: number;
  stage: Stage;
  error: string | null;
  startBuild: (req: BuildRequest, onComplete?: (jobId: string, gaps?: Gap[]) => void) => void;
  loadDemo: () => void;
}

export function useGraphData(): GraphDataState {
  const [graphData, setGraphData] = useState<GraphExport | null>(null);
  const [isBuilding, setIsBuilding] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);

  const startBuild = useCallback(
    async (req: BuildRequest, onComplete?: (jobId: string, gaps?: Gap[]) => void) => {
      setIsBuilding(true);
      setStage("fetching");
      setProgress(0);
      setError(null);

      // Animate progress while the sync request is in flight
      let done = false;
      (async () => {
        const steps: Array<[Stage, number, number]> = [
          ["fetching", 25, 5000],
          ["building", 50, 6000],
          ["detecting_gaps", 72, 5000],
          ["scoring", 88, 4000],
        ];
        for (const [s, p, delay] of steps) {
          if (done) return;
          setStage(s);
          setProgress(p);
          await new Promise<void>((r) => setTimeout(r, delay));
        }
      })();

      try {
        const res = await buildGraphSync(req);
        done = true;
        setGraphData(res.graph);
        setStage("complete");
        setProgress(100);
        setIsBuilding(false);
        onComplete?.(res.job_id, res.gaps);
      } catch (e) {
        done = true;
        setError((e as Error).message);
        setIsBuilding(false);
        setStage("error");
      }
    },
    []
  );

  const loadDemo = useCallback(() => {
    setGraphData(mockGraphExport);
    setStage("complete");
    setProgress(100);
    setError(null);
  }, []);

  return { graphData, isBuilding, progress, stage, error, startBuild, loadDemo };
}
