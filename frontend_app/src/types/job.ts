export interface Job {
  id: number;        // changed from string — DB returns bigint
  title: string;
  company: string;
  location: string;
  link: string;      // added — needed for Apply button
  match_score: number;
  skills_match_pct: number;
  experience_match_pct: number;
  missing_skills: string[];
  strengths: string[];
  weaknesses: string[];
}