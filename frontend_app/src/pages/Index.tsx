import { useState, useEffect } from "react";
import ResumeCommandCenter from "@/components/ResumeCommandCenter";
import JobCard from "@/components/JobCard";
import JobCardSkeleton from "@/components/JobCardSkeleton";
import AIInsightsPanel from "@/components/AIInsightsPanel";
import { useMatching } from "@/hooks/use-matching";
import { useAuth } from "@/context/AuthContext";
import { Job } from "@/types/job";

const RESUME_KEY = "jobmatch_resume_uploaded";

const Index = () => {
  const { user } = useAuth();
  const USER_ID = user?.id ?? "";
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const {
    jobs,
    queueSize,
    loading,
    error,
    resumeName,
    runMatching,
    removeJob
  } = useMatching(USER_ID);

  const [resumeUploaded, setResumeUploaded] = useState(() => {
    return localStorage.getItem(RESUME_KEY) === "true";
  });

  const handleResumeReady = () => {
    localStorage.setItem(RESUME_KEY, "true");
    setResumeUploaded(true);
    runMatching();
  };

  const handleApply = (jobId: number) => {
    // Save to applied list
    const existing = JSON.parse(
      localStorage.getItem("jobmatch_applied_jobs") || "[]"
    );
    if (!existing.includes(jobId)) {
      localStorage.setItem(
        "jobmatch_applied_jobs",
        JSON.stringify([...existing, jobId])
      );
    }
    // Remove from visible and pull next from queue
    removeJob(jobId);
    // Close panel if the applied job was selected
    if (selectedJob?.id === jobId) {
      setSelectedJob(null);
    }
  };

  useEffect(() => {
    if (resumeUploaded && USER_ID && jobs.length === 0) {
      runMatching();
    }
  }, [USER_ID]);

  return (
    <div className="p-6 flex gap-6">
      <div className="w-72 shrink-0">
        <ResumeCommandCenter
          userId={USER_ID}
          onResumeReady={handleResumeReady}
          resumeUploaded={resumeUploaded}
        />

        {/* Queue indicator */}
        {queueSize > 0 && (
          <div className="mt-4 glass-panel p-3 text-center">
            <p className="text-xs text-muted-foreground">
              <span className="text-primary font-medium">{queueSize}</span> more matches ready
            </p>
          </div>
        )}
      </div>

      <div className="flex-1">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-sm font-semibold text-foreground tracking-wide uppercase">
              Match Results
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              {loading
                ? "Agent is analyzing your profile..."
                : error
                ? error
                : jobs.length > 0
                ? `${jobs.length} positions · ${queueSize} more in queue`
                : resumeUploaded
                ? "No matches found — try refreshing"
                : "Upload your resume to see matches"}
            </p>
          </div>

          {!loading && resumeUploaded && (
            <button
              onClick={runMatching}
              className="text-xs text-primary hover:text-primary/80 transition-colors font-medium"
            >
              Refresh Matches
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => <JobCardSkeleton key={i} />)
            : jobs.length === 0 && resumeUploaded
            ? (
              <div className="col-span-3 glass-panel p-12 text-center">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🎉</span>
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">
                  You've applied to all matches!
                </p>
                <p className="text-xs text-muted-foreground mb-4">
                  Great job! Click below to find more opportunities.
                </p>
                <button
                  onClick={runMatching}
                  className="px-4 py-2 rounded-xl text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                  Find More Jobs
                </button>
              </div>
            )
            : jobs.map((job, i) => (
                <JobCard
                  key={job.id}
                  job={job}
                  index={i}
                  onSelect={setSelectedJob}
                  onApply={handleApply}
                  isApplied={false}
                />
              ))
          }
        </div>
      </div>

      <AIInsightsPanel
        job={selectedJob}
        userId={USER_ID}
        onClose={() => setSelectedJob(null)}
        onApply={handleApply}
      />
    </div>
  );
};

export default Index;