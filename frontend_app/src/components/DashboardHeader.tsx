import { ChevronDown, Bell, LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const DashboardHeader = () => {
  const { user, signOut } = useAuth();

  const initials = user?.user_metadata?.full_name
    ?.split(" ")
    .map((n: string) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "U";

  const displayName = user?.user_metadata?.full_name?.split(" ")[0] || "User";

  return (
    <header className="h-16 border-b border-border/50 flex items-center justify-between px-6 bg-card/40 backdrop-blur-xl">
      <div>
        <h1 className="text-lg font-semibold text-foreground">AI Job Matching</h1>
        <p className="text-xs text-muted-foreground">Intelligent career recommendations</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="glass-panel px-3 py-1.5 flex items-center gap-2 text-xs">
          <span className="status-dot" />
          <span className="text-secondary font-medium font-mono">Vector Engine Active</span>
        </div>

        <button className="relative p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-primary" />
        </button>

        {/* User — now shows real Google account */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 glass-panel px-3 py-1.5">
            {user?.user_metadata?.avatar_url ? (
              <img
                src={user.user_metadata.avatar_url}
                className="w-7 h-7 rounded-lg object-cover"
                alt={displayName}
              />
            ) : (
              <div className="w-7 h-7 rounded-lg bg-primary/20 flex items-center justify-center">
                <span className="text-primary text-xs font-semibold">{initials}</span>
              </div>
            )}
            <span className="text-sm text-foreground">{displayName}</span>
          </div>

          <button
            onClick={signOut}
            className="p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;