import { useState, useEffect } from "react";
import apiClient from "@/api/client";
import { Card } from "@/components/ui/Card";
import { Settings2, Play, CheckCircle2 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function ModelLab() {
  const [params, setParams] = useState({
    test_size: 0.2,
    rf_n_estimators: 100,
    xgb_n_estimators: 100,
    xgb_learning_rate: 0.1,
  });
  const [models, setModels] = useState([]);
  const [training, setTraining] = useState(false);
  const [bestModel, setBestModel] = useState("");

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = () => {
    apiClient.get('/models/comparison').then(res => {
      setModels(res.data);
      const best = res.data.find(m => m.is_best);
      if (best) setBestModel(best.name);
    });
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      const res = await apiClient.post('/models/train', params);
      setModels(res.data.metrics.sort((a,b) => b.r2_score - a.r2_score));
      setBestModel(res.data.best_model);
      alert(`Model retraining completed successfully! Best Model: ${res.data.best_model}`);
    } catch (err) {
      alert("Error training models");
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="space-y-10 pb-20">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight">Architectural Lab</h1>
        <p className="text-muted-foreground text-sm">Automated hyperparameter optimization and training cycles.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        
        {/* Tuning Controls */}
        <Card className="p-8 space-y-8" delay={0.1}>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-muted rounded-lg border border-border">
              <Settings2 className="w-4 h-4 text-muted-foreground" />
            </div>
            <h2 className="font-bold">Hyperparameters</h2>
          </div>

          <div className="space-y-8">
            <div className="space-y-4">
              <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex justify-between mb-2">
                Test Split Size <span>{params.test_size}</span>
              </label>
              <input type="range" min="0.1" max="0.5" step="0.05"
                     value={params.test_size} onChange={e => setParams({...params, test_size: e.target.value})}
                     className="range-slider w-full" />
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex justify-between mb-2">
                RF Estimators <span>{params.rf_n_estimators}</span>
              </label>
              <input type="range" min="10" max="500" step="10"
                     value={params.rf_n_estimators} onChange={e => setParams({...params, rf_n_estimators: e.target.value})}
                     className="range-slider w-full" />
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex justify-between mb-2">
                XGB Estimators <span>{params.xgb_n_estimators}</span>
              </label>
              <input type="range" min="10" max="500" step="10"
                     value={params.xgb_n_estimators} onChange={e => setParams({...params, xgb_n_estimators: e.target.value})}
                     className="range-slider w-full" />
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex justify-between mb-2">
                XGB LR <span>{params.xgb_learning_rate}</span>
              </label>
              <input type="range" min="0.01" max="1.0" step="0.05"
                     value={params.xgb_learning_rate} onChange={e => setParams({...params, xgb_learning_rate: e.target.value})}
                     className="range-slider w-full" />
            </div>
          </div>

          <button
            onClick={handleTrain} disabled={training}
            className="w-full mt-6 py-3 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-bold uppercase tracking-[0.2em] text-[10px] flex items-center justify-center gap-3 transition-all duration-300 disabled:opacity-50 active:scale-95"
          >
            {training ? <span className="animate-pulse">Retraining System...</span> : <><Play className="w-3.5 h-3.5 fill-current" /> Initiate Pipeline</>}
          </button>
        </Card>

        {/* Results Matrix */}
        <Card className="lg:col-span-2 p-8 flex flex-col" delay={0.2}>
          <div className="flex justify-between items-center mb-8">
            <h2 className="font-bold">Leaderboard</h2>
            {bestModel && (
              <div className="text-[10px] font-bold uppercase tracking-widest bg-primary text-primary-foreground px-3 py-1.5 rounded-md flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5" /> Optimal: {bestModel}
              </div>
            )}
          </div>

          <div className="flex-1 min-h-[400px]">
             <ResponsiveContainer width="100%" height="100%">
              <BarChart data={models} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                <XAxis type="number" domain={[0, 1]} hide />
                <YAxis dataKey="name" type="category" tick={{ fill: 'var(--muted-foreground)', fontSize: 10, fontWeight: 700 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: 'var(--muted)'}} contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--foreground)', fontSize: '10px' }} />
                <Bar dataKey="r2_score" name="R² Score" fill="var(--foreground)" radius={[0, 4, 4, 0]}>
                   {models.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.is_best ? 'var(--foreground)' : 'var(--muted-foreground)'} opacity={entry.is_best ? 1 : 0.4} />
                    ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
