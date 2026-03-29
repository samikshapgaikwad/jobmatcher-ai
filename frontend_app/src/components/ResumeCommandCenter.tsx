import { Upload, Check, Loader2, AlertCircle } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { uploadResume } from "@/lib/api";

const steps = [
  { label: "Extracting Text" },
  { label: "Segmenting Sections" },
  { label: "Generating Embeddings" },
];

interface ResumeCommandCenterProps {
  userId: string;
  onResumeReady: () => void;
  resumeUploaded?: boolean;
}

const ResumeCommandCenter = ({
  userId,
  onResumeReady,
  resumeUploaded = false,
}: ResumeCommandCenterProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [currentStep, setCurrentStep] = useState(resumeUploaded ? 3 : -1);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const timeoutsRef = useRef<NodeJS.Timeout[]>([]);

  const isDone = currentStep >= 3 || resumeUploaded;
  const isProcessing = currentStep >= 0 && currentStep < 3;

  // Cleanup timeouts (prevents memory leaks)
  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach(clearTimeout);
    };
  }, []);

  const handleFile = async (selectedFile: File) => {
    // Validate file type using MIME (more reliable)
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (!validTypes.includes(selectedFile.type)) {
      setError("Only PDF or DOCX files are allowed.");
      return;
    }

    setFile(selectedFile);
    setError(null);
    setCurrentStep(0);

    try {
      const t1 = setTimeout(() => setCurrentStep(1), 1500);
      const t2 = setTimeout(() => setCurrentStep(2), 3000);

      timeoutsRef.current.push(t1, t2);

      await uploadResume(selectedFile, userId);

      timeoutsRef.current.forEach(clearTimeout);
      setCurrentStep(3);
      onResumeReady();
    } catch (e) {
      setError("Upload failed. Check that the embedding service is running.");
      setCurrentStep(-1);
      setFile(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  };

  const handleClick = () => {
    if (!isProcessing && !isDone) {
      fileInputRef.current?.click();
    }
  };

  const handleReupload = () => {
    localStorage.removeItem("jobmatch_resume_uploaded");
    setCurrentStep(-1);
    setFile(null);
    setError(null);
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-foreground tracking-wide uppercase">
        Resume Command Center
      </h2>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        onChange={(e) =>
          e.target.files?.[0] && handleFile(e.target.files[0])
        }
      />

      <motion.div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className={`drop-zone p-8 ${
          isProcessing ? "animate-pulse-glow border-primary/50" : ""
        } ${isDone ? "border-secondary/40" : ""} ${
          !isProcessing && !isDone ? "cursor-pointer" : ""
        }`}
        whileHover={{ scale: !isProcessing && !isDone ? 1.02 : 1 }}
        whileTap={{ scale: !isProcessing && !isDone ? 0.98 : 1 }}
      >
        {isDone ? (
          <>
            <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center">
              <Check size={20} className="text-secondary" />
            </div>
            <p className="text-sm text-secondary font-medium">
              Resume Analyzed
            </p>
            <p className="text-xs text-muted-foreground">
              {file?.name || "Previously uploaded resume"}
            </p>
          </>
        ) : isProcessing ? (
          <>
            <Loader2 size={28} className="text-primary animate-spin" />
            <p className="text-sm text-foreground font-medium">
              Processing...
            </p>
          </>
        ) : (
          <>
            <Upload size={28} className="text-primary" />
            <p className="text-sm text-muted-foreground">
              Drop your resume (PDF or DOCX)
            </p>
            <p className="text-xs text-muted-foreground/60">
              or click to browse
            </p>
          </>
        )}
      </motion.div>

      {isDone && (
        <button
          onClick={handleReupload}
          className="w-full text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
        >
          Upload a different resume
        </button>
      )}

      {error && (
        <div className="flex items-center gap-2 text-destructive text-xs glass-panel p-3">
          <AlertCircle size={14} />
          <span>{error}</span>
        </div>
      )}

      <AnimatePresence>
        {(file || isProcessing) && !error && !resumeUploaded && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="glass-panel p-4 space-y-3"
          >
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Parsing Status
            </p>

            {steps.map((step, i) => {
              const isActive = i === currentStep;
              const isComplete = i < currentStep;

              return (
                <div key={step.label} className="flex items-center gap-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 transition-all duration-300 ${
                      isComplete
                        ? "bg-secondary/20 text-secondary"
                        : isActive
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {isComplete ? (
                      <Check size={12} />
                    ) : isActive ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      i + 1
                    )}
                  </div>

                  <span
                    className={`text-xs transition-colors ${
                      isComplete
                        ? "text-secondary"
                        : isActive
                        ? "text-foreground font-medium"
                        : "text-muted-foreground"
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ResumeCommandCenter;