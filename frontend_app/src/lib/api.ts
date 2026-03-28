const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function fetchMatches(userId: string): Promise<{
  jobs: Job[];
  resume_name: string;
  total_found: number;
}> {
  const res = await fetch(`${API_BASE}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, top_k: 10 }),
  });
  if (!res.ok) throw new Error("Failed to fetch matches");
  return res.json();
}

export async function fetchExplanation(jobId: number, userId: string) {
  const res = await fetch(`${API_BASE}/explain/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) throw new Error("Failed to fetch explanation");
  return res.json();
}

export async function fetchCoverLetter(jobId: number, userId: string) {
  const res = await fetch(`${API_BASE}/cover-letter/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!res.ok) throw new Error("Failed to generate cover letter");
  return res.json();
}

export async function uploadResume(file: File, userId: string) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", userId);
  const res = await fetch(
    `${import.meta.env.VITE_EMBEDDING_URL || "http://localhost:8001"}/upload-resume`,
    { method: "POST", body: formData }
  );
  if (!res.ok) throw new Error("Resume upload failed");
  return res.json();
}
export async function sendChatMessage(
  jobId: number,
  userId: string,
  message: string,
  matchScore: number,
  missingSkills: string[],
  history: { role: string; content: string }[]
) {
  const res = await fetch(`${API_BASE}/chat/${jobId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      job_id: jobId,
      message,
      match_score: matchScore,
      missing_skills: missingSkills,
      history
    }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

import { Job } from "@/types/job";