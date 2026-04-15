import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

export default function Topbar() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    // Add dark class strictly since we enforce dark mode primarily
    document.documentElement.classList.add('dark');
  }, []);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-8 sticky top-0 z-10">
      <div className="text-sm font-medium text-slate-500 dark:text-slate-400 flex items-center gap-2">
        {/* Status items removed */}
      </div>
      
      <div className="flex items-center gap-4">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-white/10 transition-colors text-slate-600 dark:text-slate-300"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        <div className="h-8 w-8 rounded-full bg-muted border border-border"></div>
      </div>
    </header>
  );
}
