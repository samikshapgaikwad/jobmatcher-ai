import { useState } from "react";
import { cn } from "@/lib/utils";
import AppSidebar from "@/components/AppSidebar";
import DashboardHeader from "@/components/DashboardHeader";
import ResumeCommandCenter from "@/components/ResumeCommandCenter";
import JobCard from "@/components/JobCard";
import JobCardSkeleton from "@/components/JobCardSkeleton";
import AIInsightsPanel from "@/components/AIInsightsPanel";
import { useMatching } from "@/hooks/use-matching";
import { useAuth } from "@/context/AuthContext";
import { Job } from "@/types/job";

const Index = () => {
  const { user } = useAuth();                          // ← inside component
  const USER_ID = user?.id ?? "";

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const { jobs, loading, error, resumeName, runMatching } = useMatching(USER_ID);

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div className={cn("transition-all duration-300", sidebarCollapsed ? "ml-16" : "ml-56")}>
        <DashboardHeader />

        <div className="p-6 flex gap-6">
          <div className="w-72 shrink-0">
            <ResumeCommandCenter
              userId={USER_ID}
              onResumeReady={runMatching}
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
                    ? `${jobs.length} positions found for ${resumeName}`
                    : "Upload your resume to see matches"}
                </p>
              </div>

              {jobs.length > 0 && !loading && (
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
                : jobs.map((job, i) => (
                    <JobCard
                      key={job.id}
                      job={job}
                      index={i}
                      onSelect={setSelectedJob}
                    />
                  ))}
            </div>
          </div>
        </div>
      </div>

      <AIInsightsPanel
        job={selectedJob}
        userId={USER_ID}
        onClose={() => setSelectedJob(null)}
      />
    </div>
  );
};

export default Index;