import type { BuildRequest, JobStatus, GraphExport } from "../types";
import { apiFetch } from "./client";

export function buildGraph(req: BuildRequest): Promise<{ job_id: string }> {
  return apiFetch<{ job_id: string }>("/graph/build", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export function getStatus(job_id: string): Promise<JobStatus> {
  return apiFetch<JobStatus>(`/graph/status/${job_id}`);
}

export function getExport(job_id: string): Promise<GraphExport> {
  return apiFetch<GraphExport>(`/graph/export/${job_id}`);
}

export function getDemoExport(): Promise<GraphExport> {
  return apiFetch<GraphExport>("/graph/export/demo");
}
