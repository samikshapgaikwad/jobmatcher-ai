import { useState } from "react";

const APPLIED_KEY = "jobmatch_applied_jobs";

export function useAppliedJobs() {
  const [appliedIds, setAppliedIds] = useState<number[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(APPLIED_KEY) || "[]");
    } catch { return []; }
  });

  const markApplied = (jobId: number) => {
    setAppliedIds(prev => {
      if (prev.includes(jobId)) return prev;
      const updated = [...prev, jobId];
      localStorage.setItem(APPLIED_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const isApplied = (jobId: number) => appliedIds.includes(jobId);

  return { appliedIds, markApplied, isApplied };
}