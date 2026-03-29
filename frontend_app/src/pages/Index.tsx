import { useState, useEffect } from "react";
import ResumeCommandCenter from "@/components/ResumeCommandCenter";
import JobCard from "@/components/JobCard";
import JobCardSkeleton from "@/components/JobCardSkeleton";
import AIInsightsPanel from "@/components/AIInsightsPanel";
import { useMatching } from "@/hooks/use-matching";
import { useAuth } from "@/context/AuthContext";
import { useAppliedJobs } from "@/hooks/use-appliedjobs";
import { Job } from "@/types/job";

const RESUME_KEY = "jobmatch_resume_uploaded";

const Index = () => {
  const { user } = useAuth();
  const USER_ID = user?.id ?? "";
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const { jobs, loading, error, resumeName, runMatching } = useMatching(USER_ID);
  const { markApplied, isApplied } = useAppliedJobs();
  const [showApplied, setShowApplied] = useState(false);

  const [resumeUploaded, setResumeUploaded] = useState(() => {
    return localStorage.getItem(RESUME_KEY) === "true";
  });

  const handleResumeReady = () => {
    localStorage.setItem(RESUME_KEY, "true");
    setResumeUploaded(true);
    runMatching();
  };

  useEffect(() => {
    if (resumeUploaded && USER_ID && jobs.length === 0) {
      runMatching();
    }
  }, [USER_ID]);

  // Filter out applied jobs unless user wants to see them
  const visibleJobs = showApplied
    ? jobs
    : jobs.filter(job => !isApplied(job.id));

  const appliedCount = jobs.filter(job => isApplied(job.id)).length;

  return (
    <div className="p-6 flex gap-6">
      <div className="w-72 shrink-0">
        <ResumeCommandCenter
          userId={USER_ID}
          onResumeReady={handleResumeReady}
          resumeUploaded={resumeUploaded}
        />
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
                ? `${visibleJobs.length} positions found for ${resumeName}`
                : "Upload your resume to see matches"}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {appliedCount > 0 && (
              <button
                onClick={() => setShowApplied(!showApplied)}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                {showApplied ? "Hide" : "Show"} {appliedCount} applied
              </button>
            )}
            {jobs.length > 0 && !loading && (
              <button
                onClick={runMatching}
                className="text-xs text-primary hover:text-primary/80 transition-colors font-medium"
              >
                Refresh Matches
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => <JobCardSkeleton key={i} />)
            : visibleJobs.map((job, i) => (
                <JobCard
                  key={job.id}
                  job={job}
                  index={i}
                  onSelect={setSelectedJob}
                  onApply={markApplied}
                  isApplied={isApplied(job.id)}
                />
              ))}
        </div>
      </div>

      <AIInsightsPanel
        job={selectedJob}
        userId={USER_ID}
        onClose={() => setSelectedJob(null)}
        onApply={markApplied}
      />
    </div>
  );
};

export default Index;