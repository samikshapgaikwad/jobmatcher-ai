import { useState, useCallback, useRef } from "react";
import { Job } from "@/types/job";
import { fetchMatches } from "@/lib/api";

const VISIBLE_COUNT = 10; // always show this many

export function useMatching(userId: string) {
  const [visibleJobs, setVisibleJobs] = useState<Job[]>([]);
  const [queue, setQueue] = useState<Job[]>([]); // buffer of next jobs
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resumeName, setResumeName] = useState<string>("");
  const appliedIds = useRef<Set<number>>(new Set(
    JSON.parse(localStorage.getItem("jobmatch_applied_jobs") || "[]")
  ));

  const runMatching = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMatches(userId, 30); // fetch 30 at once
      const allJobs: Job[] = data.jobs;
      setResumeName(data.resume_name);

      // Filter already applied jobs
      const unapplied = allJobs.filter(j => !appliedIds.current.has(j.id));

      // First 10 visible, rest in queue
      setVisibleJobs(unapplied.slice(0, VISIBLE_COUNT));
      setQueue(unapplied.slice(VISIBLE_COUNT));
    } catch (e) {
      setError("Matching failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Called when user applies to a job
  const removeJob = useCallback((jobId: number) => {
    appliedIds.current.add(jobId);

    setVisibleJobs(prev => {
      const remaining = prev.filter(j => j.id !== jobId);

      // Pull next job from queue if available
      setQueue(q => {
        if (q.length > 0) {
          const [next, ...rest] = q;
          // Small delay for smooth animation
          setTimeout(() => {
            setVisibleJobs([...remaining, next]);
          }, 300);
          return rest;
        } else {
          setVisibleJobs(remaining);
          return q;
        }
      });

      return remaining; // temporary — updated above
    });
  }, []);

  return {
    jobs: visibleJobs,
    queueSize: queue.length,
    loading,
    error,
    resumeName,
    runMatching,
    removeJob
  };
}