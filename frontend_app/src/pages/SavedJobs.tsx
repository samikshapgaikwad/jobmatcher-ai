import { useState } from "react";
import { motion } from "framer-motion";
import { Bookmark, ExternalLink, Trash2 } from "lucide-react";
import MatchScoreRing from "@/components/MatchScoreRing";
import { Job } from "@/types/job";

const STORAGE_KEY = "jobmatch_saved_jobs";

export function useSavedJobs() {
  const [savedJobs, setSavedJobs] = useState<Job[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch { return []; }
  });

  const saveJob = (job: Job) => {
    setSavedJobs(prev => {
      if (prev.find(j => j.id === job.id)) return prev;
      const updated = [...prev, job];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const removeJob = (jobId: number) => {
    setSavedJobs(prev => {
      const updated = prev.filter(j => j.id !== jobId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  };

  const isSaved = (jobId: number) => savedJobs.some(j => j.id === jobId);
  return { savedJobs, saveJob, removeJob, isSaved };
}

const SavedJobs = () => {
  const { savedJobs, removeJob } = useSavedJobs();

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-sm font-semibold text-foreground tracking-wide uppercase">
            Saved Jobs
          </h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            {savedJobs.length} job{savedJobs.length !== 1 ? "s" : ""} saved
          </p>
        </div>
      </div>

      {savedJobs.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-panel p-12 text-center"
        >
          <Bookmark size={32} className="text-muted-foreground mx-auto mb-3" />
          <p className="text-sm font-medium text-foreground">No saved jobs yet</p>
          <p className="text-xs text-muted-foreground mt-1">
            Save jobs from the dashboard to review them later
          </p>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {savedJobs.map((job, i) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-panel p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-muted flex items-center justify-center shrink-0">
                      <span className="text-xs font-bold text-muted-foreground">
                        {job.company.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-sm font-semibold text-foreground truncate">{job.title}</h3>
                      <p className="text-xs text-muted-foreground">{job.company}</p>
                    </div>
                  </div>
                  <div className="flex gap-1.5 mt-2">
                    <span className="tag-teal">Skills: {job.skills_match_pct}%</span>
                    <span className="tag-skill">Exp: {job.experience_match_pct}%</span>
                  </div>
                </div>
                <MatchScoreRing score={job.match_score} />
              </div>

              <div className="flex gap-2 mt-4 pt-3 border-t border-border/50">
                {job.link && (
                  <a
                    href={job.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                  >
                    Apply <ExternalLink size={11} />
                  </a>
                )}
                <button
                  onClick={() => removeJob(job.id)}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium border border-border text-muted-foreground hover:text-destructive hover:border-destructive/30 transition-colors"
                >
                  <Trash2 size={12} /> Remove
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SavedJobs;