import { X, CheckCircle2, AlertCircle, ExternalLink, FileText, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { Job } from "@/types/job";
import MatchScoreRing from "./MatchScoreRing";
import { fetchCoverLetter } from "@/lib/api";
import JobChat from "./JobChat";

interface AIInsightsPanelProps {
  job: Job | null;
  userId: string;
  onClose: () => void;
  onApply?: (jobId: number) => void;
}

const AIInsightsPanel = ({ job, userId, onClose, onApply }: AIInsightsPanelProps) => {
  const [coverLetter, setCoverLetter] = useState<string | null>(null);
  const [loadingCover, setLoadingCover] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCoverLetter = async () => {
    if (!job) return;
    setLoadingCover(true);
    try {
      const data = await fetchCoverLetter(job.id, userId);
      setCoverLetter(data.cover_letter);
    } catch {
      setCoverLetter("Failed to generate cover letter. Please try again.");
    } finally {
      setLoadingCover(false);
    }
  };

  const handleCopy = () => {
    if (coverLetter) {
      navigator.clipboard.writeText(coverLetter);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleClose = () => {
    setCoverLetter(null);
    onClose();
  };

  return (
    <AnimatePresence>
      {job && (
        <>
          {/* Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/60 backdrop-blur-sm z-50"
            onClick={handleClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-screen w-full max-w-md z-50 border-l border-border/50 bg-card/95 backdrop-blur-xl overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-card/90 backdrop-blur-xl border-b border-border/50 p-5 flex items-start justify-between">
              <div>
                <p className="text-xs text-primary font-mono font-medium uppercase tracking-wider mb-1">
                  AI Analysis
                </p>
                <h2 className="text-lg font-semibold text-foreground">{job.title}</h2>
                <p className="text-sm text-muted-foreground">
                  {job.company} · {job.location}
                </p>
              </div>
              <button
                onClick={handleClose}
                className="p-2 rounded-xl hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-5 space-y-6">
              {/* Score */}
              <div className="glass-panel p-5 flex items-center gap-5">
                <MatchScoreRing score={job.match_score} size={80} />
                <div>
                  <p className="text-sm font-semibold text-foreground">Overall Match</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Based on skills, experience, and role requirements
                  </p>
                  <div className="flex gap-2 mt-2">
                    <span className="tag-teal">Skills: {job.skills_match_pct}%</span>
                    <span className="tag-skill">Exp: {job.experience_match_pct}%</span>
                  </div>
                </div>
              </div>

              {/* Strengths */}
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                  <CheckCircle2 size={16} className="text-secondary" />
                  Why You Match
                </h3>
                <div className="space-y-2">
                  {job.strengths.map((s, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-start gap-2.5 glass-panel p-3"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5 shrink-0" />
                      <span className="text-sm text-foreground/90">{s}</span>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Weaknesses */}
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                  <AlertCircle size={16} className="text-destructive" />
                  Areas to Improve
                </h3>
                <div className="space-y-2">
                  {job.weaknesses.map((w, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 + 0.3 }}
                      className="flex items-start gap-2.5 glass-panel p-3"
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-destructive mt-1.5 shrink-0" />
                      <span className="text-sm text-foreground/90">{w}</span>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Missing Skills */}
              {job.missing_skills.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-3">
                    Missing Skills
                  </h3>
                  <div className="space-y-2">
                    {job.missing_skills.map((skill, i) => (
                      <div
                        key={i}
                        className="glass-panel p-3 flex items-center justify-between"
                      >
                        <span className="text-sm text-foreground">{skill}</span>

                        {/* FIXED LINK */}
                        <a
                          href={`https://www.google.com/search?q=learn+${encodeURIComponent(skill)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors font-medium"
                        >
                          Learn Now <ExternalLink size={11} />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cover Letter */}
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
                  <FileText size={16} className="text-primary" />
                  Cover Letter
                </h3>

                {!coverLetter ? (
                  <button
                    onClick={handleCoverLetter}
                    disabled={loadingCover}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium border border-primary/30 text-primary hover:bg-primary/10 transition-colors disabled:opacity-50"
                  >
                    {loadingCover ? (
                      <>
                        <Loader2 size={14} className="animate-spin" /> Generating...
                      </>
                    ) : (
                      <>
                        <FileText size={14} /> Generate Cover Letter
                      </>
                    )}
                  </button>
                ) : (
                  <div className="glass-panel p-4 space-y-3">
                    <p className="text-xs text-foreground/80 whitespace-pre-line leading-relaxed">
                      {coverLetter}
                    </p>
                    <button
                      onClick={handleCopy}
                      className="w-full px-3 py-2 rounded-xl text-xs font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                    >
                      {copied ? "Copied!" : "Copy to Clipboard"}
                    </button>
                  </div>
                )}
              </div>

              {/* Apply Button */}
              {job.link && (
                <a
                  href={job.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => onApply?.(job.id)}
                  className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                >
                  Apply Now <ExternalLink size={14} />
                </a>
              )}

              {/* Chat */}
              <JobChat job={job} userId={userId} />
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default AIInsightsPanel;