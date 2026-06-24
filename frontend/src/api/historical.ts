import type { HistoricalValidationResult } from "../types";
import { apiFetch } from "./client";

export function runHistorical(): Promise<{ job_id: string }> {
  return apiFetch<{ job_id: string }>("/historical/run", {
    method: "POST",
  });
}

export function getHistoricalResult(
  job_id: string
): Promise<HistoricalValidationResult> {
  return apiFetch<HistoricalValidationResult>(`/historical/result/${job_id}`);
}
