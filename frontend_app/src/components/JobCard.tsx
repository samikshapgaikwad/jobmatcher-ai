import { MapPin, ExternalLink, Bookmark, BookmarkCheck, CheckCircle } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import MatchScoreRing from "./MatchScoreRing";
import { Job } from "@/types/job";
import { useSavedJobs } from "@/pages/SavedJobs";

interface JobCardProps {
  job: Job;
  index: number;
  onSelect: (job: Job) => void;
  onApply?: (jobId: number) => void;
  isApplied?: boolean;
}

const JobCard = ({ job, index, onSelect, onApply, isApplied = false }: JobCardProps) => {
  const { saveJob, removeJob, isSaved } = useSavedJobs();
  const saved = isSaved(job.id);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: "easeOut" }}
      className={cn(
        "glass-panel-hover p-5 cursor-pointer",
        isApplied && "opacity-60"
      )}
      onClick={() => onSelect(job)}
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

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-3">
            <MapPin size={12} />
            <span>{job.location}</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            <span className="tag-teal">Skills: {job.skills_match_pct}%</span>
            <span className="tag-skill">Exp: {job.experience_match_pct}%</span>
            {job.missing_skills.length > 0 && (
              <span className="tag-danger">{job.missing_skills.length} gaps</span>
            )}
            {isApplied && (
              <span className="tag-teal flex items-center gap-1">
                <CheckCircle size={10} /> Applied
              </span>
            )}
          </div>
        </div>

        <MatchScoreRing score={job.match_score} />
      </div>

      <div className="flex gap-2 mt-4 pt-3 border-t border-border/50">
        <button
          onClick={(e) => { e.stopPropagation(); onSelect(job); }}
          className="flex-1 px-3 py-2 rounded-xl text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          View Analysis
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            saved ? removeJob(job.id) : saveJob(job);
          }}
          className={cn(
            "flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium border transition-colors",
            saved
              ? "border-primary/30 text-primary bg-primary/10"
              : "border-border text-muted-foreground hover:text-foreground hover:border-primary/30"
          )}
        >
          {saved ? <BookmarkCheck size={12} /> : <Bookmark size={12} />}
          {saved ? "Saved" : "Save"}
        </button>
        {job.link && (
        <a
          href={job.link}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => {
            e.stopPropagation();
            onApply?.(job.id); // mark as applied when clicking Apply
          }}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium border border-border text-muted-foreground hover:text-foreground hover:border-primary/30 transition-colors"
        >
          Apply <ExternalLink size={11} />
        </a>
      )}
      </div>
    </motion.div>
  );
};

export default JobCard;