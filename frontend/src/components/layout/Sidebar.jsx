import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BarChart3,
  MapPin,
  Database,
  History,
  Home,
} from "lucide-react";
import { cn } from "@/utils/cn";

const navigation = [
  { name: "Prediction", href: "/", icon: LayoutDashboard },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Location", href: "/location", icon: MapPin },
  { name: "Dataset Explorer", href: "/dataset", icon: Database },
  { name: "History", href: "/history", icon: History },
];

export default function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col border-r border-border bg-card">
      <div className="flex h-16 items-center gap-2 px-6 border-b border-border">
        <Home className="h-6 w-6 text-foreground" />
        <span className="text-xl font-bold text-foreground">
          VaenEstate
        </span>
      </div>

      <nav className="flex-1 space-y-1 px-4 py-6">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary-500/10 text-primary-600 dark:text-primary-400"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white"
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={cn(
                      "h-5 w-5 flex-shrink-0 transition-colors",
                      isActive
                        ? "text-primary-600 dark:text-primary-400"
                        : "text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300"
                    )}
                  />
                  {item.name}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border/50 text-xs text-center text-slate-500 dark:text-slate-400">
        &copy; 2026 VaenEstate Platform
      </div>
    </div>
  );
}
