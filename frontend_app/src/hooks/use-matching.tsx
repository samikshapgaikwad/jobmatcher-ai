import { useState, useCallback } from "react";
import { Job } from "@/types/job";
import { fetchMatches, fetchExplanation, fetchCoverLetter } from "@/lib/api";

export function useMatching(userId: string) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resumeName, setResumeName] = useState<string>("");

  const runMatching = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMatches(userId);
      setJobs(data.jobs);
      setResumeName(data.resume_name);
    } catch (e) {
      setError("Matching failed. Is the API running?");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const getExplanation = useCallback(async (jobId: number) => {
    return fetchExplanation(jobId, userId);
  }, [userId]);

  const getCoverLetter = useCallback(async (jobId: number) => {
    return fetchCoverLetter(jobId, userId);
  }, [userId]);

  return { jobs, loading, error, resumeName, runMatching, getExplanation, getCoverLetter };
}