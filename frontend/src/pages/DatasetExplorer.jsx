import { useEffect, useState } from "react";
import apiClient from "@/api/client";
import { Card } from "@/components/ui/Card";
import { Upload, FileSpreadsheet, ArrowUpDown, ChevronLeft, ChevronRight } from "lucide-react";

export default function DatasetExplorer() {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortBy, setSortBy] = useState('price');
  const [sortOrder, setSortOrder] = useState('desc');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchData();
    apiClient.get('/dataset/stats').then(res => setStats(res.data)).catch(console.error);
  }, [page, sortBy, sortOrder]);

  const fetchData = () => {
    apiClient.get(`/dataset?page=${page}&page_size=20&sort_by=${sortBy}&sort_order=${sortOrder}`)
      .then(res => {
        setData(res.data.data);
        setTotalPages(res.data.total_pages);
      }).catch(console.error);
  };

  const handleSort = (col) => {
    if (sortBy === col) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortOrder('desc');
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      await apiClient.post("/dataset/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      alert("Dataset uploaded successfully! Models retrained in the background.");
      fetchData();
      apiClient.get('/dataset/stats').then(res => setStats(res.data));
    } catch (err) {
      alert("Error uploading dataset: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 h-full flex flex-col">
      <div className="flex justify-between items-end shrink-0">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold tracking-tight">Dataset Explorer</h1>
          <p className="text-muted-foreground text-sm">Review and manage underlying training data assets.</p>
        </div>

        <div className="flex gap-2">
          <label className="cursor-pointer bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
            <Upload className="w-3.5 h-3.5" />
            {uploading ? "Uploading..." : "Import CSV"}
            <input type="file" accept=".csv" className="hidden" disabled={uploading} onChange={handleUpload} />
          </label>
        </div>
      </div>

      <Card className="flex-1 flex flex-col min-h-0 overflow-hidden p-0" delay={0.1}>
        <div className="overflow-auto flex-1">
          <table className="w-full text-left text-xs whitespace-nowrap">
            <thead className="sticky top-0 bg-muted border-b border-border z-10">
              <tr>
                {['area', 'rooms', 'location', 'age', 'price'].map(col => (
                  <th key={col} className="px-6 py-3 font-bold text-muted-foreground uppercase tracking-wider cursor-pointer hover:bg-border transition-colors"
                      onClick={() => handleSort(col)}>
                    <div className="flex items-center gap-2">
                      {col} {sortBy === col && <ArrowUpDown className="w-3 h-3 text-primary" />}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.map((row, i) => (
                <tr key={i} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4 font-medium">{row.area} sqft</td>
                  <td className="px-6 py-4 font-medium">{row.rooms}</td>
                  <td className="px-6 py-4 font-medium">{row.location}</td>
                  <td className="px-6 py-4 font-medium">{row.age} yrs</td>
                  <td className="px-6 py-4 font-bold text-foreground">₹{(row.price/100000).toFixed(2)}L</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="border-t border-border p-4 flex justify-between items-center bg-card shrink-0 shadow-sm">
          <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">
            Total Records: {stats?.total_rows?.toLocaleString() || "..." || "0"}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="p-2 border border-border rounded-lg disabled:opacity-30 hover:bg-muted transition-colors"><ChevronLeft className="w-3.5 h-3.5" /></button>
            <span className="text-[10px] font-bold uppercase tracking-widest px-4">Page {page} of {totalPages}</span>
            <button onClick={() => setPage(p => p + 1)} disabled={page >= totalPages} className="p-2 border border-border rounded-lg disabled:opacity-30 hover:bg-muted transition-colors"><ChevronRight className="w-3.5 h-3.5" /></button>
          </div>
        </div>
      </Card>
    </div>
  );
}
