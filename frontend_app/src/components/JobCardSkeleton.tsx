const JobCardSkeleton = () => (
  <div className="glass-panel p-5 space-y-4">
    <div className="flex items-start gap-4">
      <div className="flex-1 space-y-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl skeleton-shimmer" />
          <div className="space-y-1.5 flex-1">
            <div className="h-4 w-3/4 rounded-md skeleton-shimmer" />
            <div className="h-3 w-1/2 rounded-md skeleton-shimmer" />
          </div>
        </div>
        <div className="h-3 w-1/3 rounded-md skeleton-shimmer" />
        <div className="flex gap-2">
          <div className="h-6 w-20 rounded-lg skeleton-shimmer" />
          <div className="h-6 w-16 rounded-lg skeleton-shimmer" />
        </div>
      </div>
      <div className="w-16 h-16 rounded-full skeleton-shimmer" />
    </div>
    <div className="flex gap-2 pt-3 border-t border-border/50">
      <div className="flex-1 h-9 rounded-xl skeleton-shimmer" />
      <div className="w-20 h-9 rounded-xl skeleton-shimmer" />
    </div>
  </div>
);

export default JobCardSkeleton;
