import type { Gap, QuestionRequest, ResearchQuestion } from "../types";
import { apiFetch } from "./client";

export function scoreGaps(job_id: string): Promise<Gap[]> {
  return apiFetch<Gap[]>(`/gaps/score/${job_id}`);
}

export function getDemoGaps(): Promise<Gap[]> {
  return apiFetch<Gap[]>("/gaps/demo");
}

export function generateQuestions(
  req: QuestionRequest
): Promise<ResearchQuestion[]> {
  return apiFetch<ResearchQuestion[]>("/gaps/questions", {
    method: "POST",
    body: JSON.stringify(req),
  });
}
