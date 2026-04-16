import { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Analytics = lazy(() => import("./pages/Analytics"));
const LocationIntel = lazy(() => import("./pages/LocationIntel"));
const DatasetExplorer = lazy(() => import("./pages/DatasetExplorer"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));

export default function App() {
  return (
    <BrowserRouter>
      <Suspense
        fallback={
          <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground font-medium animate-pulse">
            VaenEstate Intelligence Module Loading...
          </div>
        }
      >
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="location" element={<LocationIntel />} />
            <Route path="dataset" element={<DatasetExplorer />} />
            <Route path="history" element={<HistoryPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
