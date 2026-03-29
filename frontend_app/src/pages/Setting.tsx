import { useState } from "react";
import { motion } from "framer-motion";
import { Bell, Shield, Trash2, LogOut, Moon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const Settings = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const { signOut, user } = useAuth();

  const Toggle = ({ value, onChange }: { value: boolean; onChange: () => void }) => (
    <button
      onClick={onChange}
      className={cn(
        "relative w-10 h-5 rounded-full transition-colors",
        value ? "bg-primary" : "bg-muted"
      )}
    >
      <div className={cn(
        "absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform",
        value ? "translate-x-5" : "translate-x-0.5"
      )} />
    </button>
  );

  return (
    <div className="p-6 max-w-2xl space-y-4">
      <h2 className="text-sm font-semibold text-foreground tracking-wide uppercase mb-5">
        Settings
      </h2>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel p-5">
        <h3 className="text-sm font-semibold text-foreground mb-4">Preferences</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell size={16} className="text-muted-foreground" />
              <div>
                <p className="text-sm text-foreground">Job Notifications</p>
                <p className="text-xs text-muted-foreground">Get notified about new matches</p>
              </div>
            </div>
            <Toggle value={notifications} onChange={() => setNotifications(!notifications)} />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Moon size={16} className="text-muted-foreground" />
              <div>
                <p className="text-sm text-foreground">Dark Mode</p>
                <p className="text-xs text-muted-foreground">Toggle dark/light theme</p>
              </div>
            </div>
            <Toggle value={darkMode} onChange={() => setDarkMode(!darkMode)} />
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-panel p-5"
      >
        <h3 className="text-sm font-semibold text-foreground mb-4">Account</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-muted/30">
            <Shield size={16} className="text-secondary" />
            <div>
              <p className="text-sm text-foreground">Signed in with Google</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={signOut}
            className="w-full flex items-center gap-3 p-3 rounded-xl text-sm text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
          >
            <LogOut size={16} /> Sign Out
          </button>
          <button className="w-full flex items-center gap-3 p-3 rounded-xl text-sm text-destructive hover:bg-destructive/10 transition-colors">
            <Trash2 size={16} /> Delete Account
          </button>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-panel p-5"
      >
        <h3 className="text-sm font-semibold text-foreground mb-3">About</h3>
        <div className="space-y-1.5 text-xs text-muted-foreground">
          <p>JobMatch AI v1.0.0</p>
          <p>Powered by LangGraph + Groq + pgvector</p>
          <p>Built with React + FastAPI + Supabase</p>
        </div>
      </motion.div>
    </div>
  );
};

export default Settings;