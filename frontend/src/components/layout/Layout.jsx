import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import MarketTicker from "../ui/MarketTicker";

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[var(--background)]">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Topbar />
        <MarketTicker />
        
        <main className="flex-1 overflow-y-auto p-4 md:p-8 z-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
