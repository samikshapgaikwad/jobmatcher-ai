import { useState } from "react";
import { motion } from "framer-motion";
import { User, Mail, Phone, Briefcase, GraduationCap, Award, Edit3, Check } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import AppSidebar from "@/components/AppSidebar";
import DashboardHeader from "@/components/DashboardHeader";
import { cn } from "@/lib/utils";

const Profile = () => {
  const { user } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const avatar = user?.user_metadata?.avatar_url;
  const name = user?.user_metadata?.full_name || "User";
  const email = user?.email || "";

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <div className={cn("transition-all duration-300", sidebarCollapsed ? "ml-16" : "ml-56")}>
        <DashboardHeader />
        <div className="p-6 max-w-3xl">
          <h2 className="text-sm font-semibold text-foreground tracking-wide uppercase mb-5">
            My Profile
          </h2>

          {/* Avatar + Name */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel p-6 flex items-center gap-5 mb-4"
          >
            {avatar ? (
              <img src={avatar} className="w-16 h-16 rounded-2xl object-cover" alt={name} />
            ) : (
              <div className="w-16 h-16 rounded-2xl bg-primary/20 flex items-center justify-center">
                <User size={28} className="text-primary" />
              </div>
            )}
            <div>
              <h3 className="text-lg font-semibold text-foreground">{name}</h3>
              <p className="text-sm text-muted-foreground flex items-center gap-1.5 mt-0.5">
                <Mail size={13} /> {email}
              </p>
              <div className="flex items-center gap-1.5 mt-2">
                <span className="tag-teal">Google Account</span>
                <span className="tag-skill">Active</span>
              </div>
            </div>
          </motion.div>

          {/* Info Cards */}
          {[
            { icon: Briefcase, label: "Experience", value: "Parsed from your resume" },
            { icon: GraduationCap, label: "Education", value: "Parsed from your resume" },
            { icon: Award, label: "Skills", value: "Extracted via NLP pipeline" },
            { icon: Phone, label: "Phone", value: "Parsed from your resume" },
          ].map(({ icon: Icon, label, value }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-panel p-4 flex items-center gap-4 mb-3"
            >
              <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                <Icon size={16} className="text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="text-sm text-foreground font-medium">{value}</p>
              </div>
            </motion.div>
          ))}

          <p className="text-xs text-muted-foreground mt-4 glass-panel p-3">
            💡 Upload a new resume from the dashboard to update your profile data automatically.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Profile;