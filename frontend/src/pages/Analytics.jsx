import { useEffect, useState } from "react";
import apiClient from "@/api/client";
import { Card } from "@/components/ui/Card";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [models, setModels] = useState([]);
  const [importance, setImportance] = useState(null);

  useEffect(() => {
    apiClient.get('/analytics/summary').then(res => setSummary(res.data)).catch(console.error);
    apiClient.get('/models/comparison').then(res => setModels(res.data)).catch(console.error);
    apiClient.get('/models/feature-importance').then(res => {
      if(res.data?.importances) {
        const arr = Object.entries(res.data.importances)
          .map(([name, val]) => ({ name, value: Number(val) }))
          .sort((a,b) => b.value - a.value)
          .slice(0, 8); // Top 8 features (prevents unreadable charts with hot-encoding)
        setImportance(arr);
      }
    }).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight">VaenEstate Analytics</h1>
        <p className="text-muted-foreground text-sm">Engine performance and market feature distributions.</p>
      </div>

      {/* KPI Stats */}
      {summary && summary.status !== 'not_trained' ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total Samples", value: summary.total_samples?.toLocaleString() || "0" },
            { label: "Avg Price", value: summary.avg_price ? `₹${(summary.avg_price/100000).toFixed(1)}L` : "N/A" },
            { label: "Best Model", value: summary.best_model || "N/A" },
            { label: "Top Accuracy", value: summary.best_r2 ? `${(summary.best_r2 * 100).toFixed(1)}%` : "N/A" },
          ].map((stat, i) => (
            <Card key={i} className="p-5" delay={i * 0.1}>
              <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">{stat.label}</div>
              <div className="text-xl font-bold">{stat.value}</div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-8 text-center bg-muted/30 border-dashed">
          <p className="text-sm font-medium text-muted-foreground italic">
            Models are not yet trained. Please visit the Model Lab to initiate the AI Pipeline.
          </p>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Comparison */}
        <Card className="p-6 h-[400px]" delay={0.3}>
          <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-8">System R² Benchmark</h3>
          <ResponsiveContainer width="100%" height="80%">
            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={models}>
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis dataKey="name" tick={{ fill: 'var(--muted-foreground)', fontSize: 10, fontWeight: 600 }} />
              <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
              <Radar name="Accuracy" dataKey="r2_score" stroke="var(--foreground)" fill="var(--foreground)" fillOpacity={0.1} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '8px', fontSize: '10px' }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        {/* Feature Importance */}
        <Card className="p-6 h-[400px]" delay={0.4}>
          <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-8">Feature Contribution</h3>
          {importance ? (
            <ResponsiveContainer width="100%" height="80%">
              <BarChart data={importance} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" tick={{ fill: 'var(--muted-foreground)', fontSize: 10, fontWeight: 600 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: 'var(--muted)'}} contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '8px', fontSize: '10px' }} />
                <Bar dataKey="value" fill="var(--foreground)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
             <div className="h-full flex items-center justify-center text-muted-foreground text-xs">Computing importance...</div>
          )}
        </Card>
      </div>
    </div>
  );
}
