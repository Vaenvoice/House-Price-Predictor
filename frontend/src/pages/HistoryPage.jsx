import { useEffect, useState } from "react";
import apiClient from "@/api/client";
import { Card } from "@/components/ui/Card";
import { FileDown, Calendar, Trash2 } from "lucide-react";
import jsPDF from "jspdf";
import 'jspdf-autotable';

export default function HistoryPage() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = () => {
    apiClient.get('/predictions/history').then(res => setHistory(res.data)).catch(console.error);
  };

  const clearHistory = () => {
    if(confirm("Are you sure you want to clear all prediction history?")) {
      apiClient.delete('/predictions/history').then(() => setHistory([])).catch(console.error);
    }
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    
    doc.setFontSize(18);
    doc.text("VaenEstate Prediction Report", 14, 22);
    
    doc.setFontSize(11);
    doc.setTextColor(100);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);

    const tableColumn = ["Date", "Area (sqft)", "Rooms", "Location", "Age", "Predicted Price", "Model"];
    const tableRows = [];

    history.forEach(item => {
      const date = new Date(item.created_at).toLocaleDateString();
      const price = `Rs. ${(item.predicted_price/100000).toFixed(2)}L`;
      tableRows.push([
        date, item.area, item.rooms, item.location, item.age, price, item.model_used
      ]);
    });

    doc.autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 40,
      theme: 'grid',
      styles: { fontSize: 9 },
      headStyles: { fillColor: [59, 130, 246] } // Primary blue
    });

    doc.save("vaenestate-predictions.pdf");
  };

  return (
    <div className="space-y-8 h-full flex flex-col">
      <div className="flex justify-between items-end shrink-0">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold tracking-tight">Prediction Log</h1>
          <p className="text-muted-foreground text-sm">Review your past property valuations.</p>
        </div>

        <div className="flex gap-2">
          <button onClick={clearHistory} className="px-4 py-2 text-rose-500 hover:bg-rose-500/5 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
            <Trash2 className="w-3.5 h-3.5" /> Clear All
          </button>
          <button onClick={exportPDF} className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors flex items-center gap-2">
            <FileDown className="w-3.5 h-3.5" /> Export Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pb-6">
        {history.length === 0 && (
          <div className="col-span-full h-40 flex items-center justify-center text-slate-500">
            No past predictions found. Try making one first!
          </div>
        )}
        
        {history.map((record, i) => (
          <Card key={i} delay={i * 0.05} className="p-6 flex flex-col relative group">
            <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
              <Calendar className="w-3 h-3" /> {new Date(record.created_at).toLocaleString()}
            </div>
            
            <div className="text-2xl font-bold text-foreground mb-4">
              ₹{(record.predicted_price/100000).toFixed(2)}L
            </div>
            
            <div className="grid grid-cols-2 gap-y-3 text-xs">
              <div className="text-muted-foreground font-medium uppercase tracking-tighter">Area</div><div className="text-right font-bold">{record.area} sqft</div>
              <div className="text-muted-foreground font-medium uppercase tracking-tighter">Rooms</div><div className="text-right font-bold">{record.rooms}</div>
              <div className="text-muted-foreground font-medium uppercase tracking-tighter">Location</div><div className="text-right font-bold truncate">{record.location}</div>
              <div className="text-muted-foreground font-medium uppercase tracking-tighter">Age</div><div className="text-right font-bold">{record.age} years</div>
            </div>

            <div className="mt-6 pt-4 border-t border-border flex justify-between items-center text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
               <span>Algorithm</span>
               <span className="text-foreground">{record.model_used}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
