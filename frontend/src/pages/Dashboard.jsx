import { useState, useEffect } from "react";
import apiClient from "@/api/client";
import { Card } from "@/components/ui/Card";
import { motion, AnimatePresence } from "framer-motion";
import { Home, MapPin, Ruler, Grid2X2, Sparkles, TrendingUp, TrendingDown, History, Star, Activity, Info, Pin, Calculator, ArrowRight, ShieldAlert } from "lucide-react";
import clsx from "clsx";

export default function Dashboard() {
  const [locations, setLocations] = useState([]);
  const [formData, setFormData] = useState({
    area: 1200,
    rooms: 2,
    location: "Mumbai",
    age: 5,
  });
  const [prediction, setPrediction] = useState(null);
  const [pinnedPrediction, setPinnedPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const maxAttempts = 12;

    const fetchLocations = () => {
      apiClient
        .get("/locations")
        .then((res) => {
          if (cancelled) return;
          setLocations(res.data);
          setApiError("");
        })
        .catch((err) => {
          if (cancelled) return;
          attempts += 1;
          if (attempts < maxAttempts) {
            setTimeout(fetchLocations, 1500);
          } else {
            setApiError("Backend is unreachable. Ensure API is running on port 8000.");
            console.error(err);
          }
        });
    };

    fetchLocations();
    return () => {
      cancelled = true;
    };
  }, []);

  // Use debounce for live prediction
  useEffect(() => {
    if (!locations.length) return;
    
    const delayDebounceFn = setTimeout(() => {
      setLoading(true);
      apiClient.post('/predict', formData)
        .then(res => {
          setPrediction(res.data);
          setApiError("");
        })
        .catch((err) => {
          setPrediction(null);
          setApiError("Live prediction failed. Check backend connection.");
          console.error(err);
        })
        .finally(() => setLoading(false));
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [formData, locations]);

  const handleSliderChange = (e) => {
    setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
  };

  return (
    <div className="space-y-10 pb-20">
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="h-1 w-12 bg-slate-900 dark:bg-slate-100 rounded-full" />
          <span className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Intelligence Unit</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white lg:text-5xl">
          VaenEstate Predictor
        </h1>
        <p className="text-lg text-slate-500 dark:text-slate-400 max-w-2xl leading-relaxed">
          Estimate property values with clinical precision using our state-of-the-art ensemble learning architecture.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Controls Panel */}
        <Card className="lg:col-span-5 p-8" delay={0.1}>
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2 bg-muted rounded-lg border border-border">
              <Grid2X2 className="w-4 h-4 text-muted-foreground" />
            </div>
            <h2 className="text-lg font-bold">Property Parameters</h2>
          </div>

          <div className="space-y-10">
            {/* Area */}
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <label className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                  <Ruler className="w-3.5 h-3.5" /> Total Area
                </label>
                <span className="text-base font-bold text-foreground">{formData.area.toLocaleString()} <span className="text-xs font-medium text-muted-foreground">sq ft</span></span>
              </div>
              <input 
                type="range" name="area" min="500" max="5000" step="50"
                value={formData.area} onChange={handleSliderChange}
                className="range-slider w-full"
              />
            </div>

            {/* Rooms */}
            <div className="space-y-4">
              <label className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                <Home className="w-3.5 h-3.5" /> Bedrooms
              </label>
              <div className="grid grid-cols-6 gap-2">
                {[1, 2, 3, 4, 5, 6].map(num => (
                  <button
                    key={num}
                    onClick={() => setFormData({...formData, rooms: num})}
                    className={clsx(
                      "aspect-square flex items-center justify-center text-xs font-bold rounded-lg transition-all duration-200 border",
                      formData.rooms === num 
                        ? "bg-primary text-primary-foreground border-primary shadow-sm" 
                        : "bg-muted text-muted-foreground border-transparent hover:border-border"
                    )}
                  >
                    {num}
                  </button>
                ))}
              </div>
            </div>

            {/* Age */}
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <label className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                  <History className="w-3.5 h-3.5" /> Construction Age
                </label>
                <span className="text-base font-bold text-foreground">{formData.age} <span className="text-xs font-medium text-muted-foreground">Years</span></span>
              </div>
              <input 
                type="range" name="age" min="0" max="50" step="1"
                value={formData.age} onChange={handleSliderChange}
                className="range-slider w-full"
              />
            </div>

            {/* Location */}
            <div className="space-y-4">
              <label className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5" /> Target Location
              </label>
              <select
                name="location"
                value={formData.location}
                onChange={(e) => setFormData({...formData, location: e.target.value})}
                className="w-full bg-muted border border-border rounded-lg px-4 py-3 text-sm font-medium focus:outline-none focus:ring-1 focus:ring-primary transition-all cursor-pointer"
              >
                {locations.map(loc => (
                  <option key={loc.name} value={loc.name} className="dark:bg-background">
                    {loc.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card>

        <div className="lg:col-span-7 space-y-8">
          <Card className="p-10 flex flex-col justify-center items-center relative min-h-[300px]" delay={0.2} hover>
            
            {loading && (
              <div className="absolute top-4 right-4 flex items-center gap-2 text-muted-foreground text-[10px] font-bold uppercase tracking-widest">
                <Activity className="w-3 h-3 animate-pulse" /> Modeling
              </div>
            )}

            <div className="absolute top-4 left-4">
               <button 
                 onClick={() => setPinnedPrediction(prediction)}
                 disabled={!prediction}
                 className={clsx(
                   "p-2 rounded-md border transition-all duration-200",
                   pinnedPrediction?.predicted_price === prediction?.predicted_price 
                    ? "bg-primary text-primary-foreground border-primary" 
                    : "bg-muted text-muted-foreground border-border hover:bg-muted/80"
                 )}
               >
                 <Pin className="w-4 h-4" />
               </button>
            </div>

            <div className="text-muted-foreground text-[10px] font-bold uppercase tracking-[0.2em] mb-6">
              Predictive Valuation
            </div>
            {apiError && (
              <div className="mb-4 rounded-md border border-rose-300 bg-rose-50 px-3 py-2 text-[11px] font-medium text-rose-700 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-300">
                {apiError}
              </div>
            )}
            
            <AnimatePresence mode="wait">
              <motion.div
                key={prediction?.formatted_price || "empty"}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="text-7xl font-bold tracking-tighter text-foreground"
              >
                {prediction ? prediction.formatted_price : "---"}
              </motion.div>
            </AnimatePresence>

            {prediction?.is_outlier && (
              <div className="mt-4 flex items-center gap-2 text-rose-500 text-[11px] font-bold uppercase tracking-wider">
                <ShieldAlert className="w-3.5 h-3.5" /> High Variance Data Detected
              </div>
            )}

            {prediction && (
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="mt-8 flex flex-wrap gap-2 justify-center"
              >
                <div className="px-4 py-1.5 rounded-md bg-muted text-[10px] font-bold text-muted-foreground border border-border uppercase tracking-widest">
                  Est. Range: ₹{(prediction.confidence_low/100000).toFixed(1)}L - ₹{(prediction.confidence_high/100000).toFixed(1)}L
                </div>
                <div className="px-4 py-1.5 rounded-md bg-primary text-primary-foreground text-[10px] font-bold uppercase tracking-widest">
                   {prediction.model_used}
                </div>
              </motion.div>
            )}
          </Card>

          {/* New Comparison Mode Layout */}
          <AnimatePresence>
            {pinnedPrediction && prediction && pinnedPrediction.predicted_price !== prediction.predicted_price && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <Card className="p-6 bg-muted/40 border-dashed">
                   <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        <History className="w-3 h-3" /> Comparison Benchmarking
                      </div>
                      <button onClick={() => setPinnedPrediction(null)} className="text-[10px] font-bold text-rose-500 hover:underline">Clear</button>
                   </div>
                   <div className="grid grid-cols-2 gap-8">
                      <div>
                        <div className="text-xs font-medium text-muted-foreground mb-1">Pinned Valuation</div>
                        <div className="text-xl font-bold">{pinnedPrediction.formatted_price}</div>
                      </div>
                      <div className="border-l border-border pl-8">
                         <div className="text-xs font-medium text-muted-foreground mb-1">Impact Difference</div>
                         <div className={clsx(
                           "text-xl font-bold flex items-center gap-2",
                           prediction.predicted_price > pinnedPrediction.predicted_price ? "text-green-600" : "text-rose-600"
                         )}>
                            {prediction.predicted_price > pinnedPrediction.predicted_price ? "+" : "-"}
                            ₹{Math.abs((prediction.predicted_price - pinnedPrediction.predicted_price) / 100000).toFixed(1)}L
                            {prediction.predicted_price > pinnedPrediction.predicted_price ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                         </div>
                      </div>
                   </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
             {/* Financial Insights */}
             <Card className="p-8" delay={0.3}>
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-muted rounded-lg">
                    <Calculator className="w-4 h-4" />
                  </div>
                  <h3 className="font-bold">Affordability</h3>
                </div>
                {prediction ? (
                  <div className="space-y-4">
                    <div className="flex justify-between items-end">
                      <span className="text-xs text-muted-foreground font-medium">Est. Monthly EMI</span>
                      <span className="text-lg font-bold">₹{prediction.emi_estimate?.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                       <motion.div 
                        initial={{ width: 0 }} 
                        animate={{ width: "65%" }} 
                        className="h-full bg-primary"
                       />
                    </div>
                    <p className="text-[10px] text-muted-foreground leading-relaxed">
                      Based on 80% LTV at 8.5% interest over 20 years. Individual eligibility may vary.
                    </p>
                  </div>
                ) : (
                  <div className="py-8 text-center text-xs text-muted-foreground font-medium italic">Awaiting predictive data...</div>
                )}
             </Card>

             {/* Better Value Finder */}
             <Card className="p-8" delay={0.4}>
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-muted rounded-lg">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <h3 className="font-bold">Value Finder</h3>
                </div>
                <div className="space-y-4">
                   {prediction?.alternatives?.map((alt, i) => (
                     <div key={i} className="flex items-center justify-between group cursor-default">
                        <div>
                           <div className="text-xs font-bold">{alt.location}</div>
                           <div className="text-[10px] text-green-600 font-bold">Save {alt.savings}%</div>
                        </div>
                        <div className="text-right">
                           <div className="text-xs font-bold">₹{(alt.price/100000).toFixed(1)}L</div>
                           <ArrowRight className="w-3 h-3 inline-block ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                     </div>
                   ))}
                   {!prediction?.alternatives && (
                     <div className="py-8 text-center text-xs text-muted-foreground font-medium italic">Scanning market alternatives...</div>
                   )}
                </div>
             </Card>
          </div>

          {/* AI Insights & Optimization */}
          <div className="space-y-6">
            <Card className="p-8 overflow-hidden" delay={0.5}>
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary rounded-lg">
                    <Sparkles className="w-4 h-4 text-primary-foreground" />
                  </div>
                  <h3 className="font-bold">Market Intelligence</h3>
                </div>
              </div>
              
              <AnimatePresence mode="wait">
                {prediction?.insights ? (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-10"
                  >
                    {/* Score & Rating */}
                    <div className="space-y-6">
                      <div className="space-y-2">
                        <div className="flex justify-between items-end">
                          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Market Score</span>
                          <span className="text-xl font-bold">{prediction.insights.market_score}%</span>
                        </div>
                        <div className="w-full h-1 bg-muted rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }} animate={{ width: `${prediction.insights.market_score}%` }}
                            className="h-full bg-primary"
                          />
                        </div>
                        <p className="text-[10px] text-muted-foreground font-medium">
                          Analysis vs {prediction.insights.market_comparison}
                        </p>
                      </div>

                      <div className="space-y-2">
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest block">Investment Grade</span>
                        <div className="flex items-center gap-1">
                          {[1, 2, 3, 4, 5].map(star => (
                            <Star 
                              key={star} 
                              className={clsx(
                                "w-4 h-4",
                                star <= Math.round(prediction.insights.investment_rating) 
                                  ? "fill-primary text-primary" 
                                  : "text-muted"
                              )} 
                            />
                          ))}
                          <span className="ml-2 text-base font-bold text-foreground">
                            {prediction.insights.investment_rating.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Feature Impact */}
                    <div className="space-y-4">
                      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Contribution Analysis</span>
                      <div className="space-y-3">
                        {Object.entries(prediction.insights.feature_impact).map(([key, val], i) => (
                          <div key={key} className="space-y-1">
                            <div className="flex justify-between text-[10px] uppercase font-bold tracking-widest">
                              <span className="text-muted-foreground">{key}</span>
                              <span className="text-foreground">{(val * 100).toFixed(1)}%</span>
                            </div>
                            <div className="w-full h-1 bg-muted rounded-full overflow-hidden">
                              <motion.div 
                                initial={{ width: 0 }} animate={{ width: `${Math.abs(val) * 100}%` }}
                                className={clsx(
                                  "h-full rounded-full",
                                  val >= 0 ? "bg-primary" : "bg-muted-foreground/30"
                                )}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Narrative */}
                    <div className="md:col-span-2 p-6 bg-muted border border-border rounded-xl relative overflow-hidden">
                      <p className="text-xs text-foreground leading-relaxed font-medium italic">
                        "{prediction.insights.narrative}"
                      </p>
                    </div>
                  </motion.div>
                ) : (
                  <div className="py-12 flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                    <div className="w-12 h-12 rounded-full border border-dashed border-muted-foreground flex items-center justify-center">
                      <Info className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                      Awaiting Data Scan
                    </p>
                  </div>
                )}
              </AnimatePresence>
            </Card>

            {/* Simple Optimization Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-12">
              {prediction?.suggestions?.map((sug, i) => (
                <motion.div 
                  initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + (i*0.1) }}
                  key={i} className="p-5 rounded-xl bg-card border border-border group hover:border-muted-foreground/50 transition-all duration-300"
                >
                  <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-2 transition-colors">{sug.type}</div>
                  <div className="text-xs font-bold mb-3 leading-snug">{sug.text}</div>
                  <div className={clsx(
                    "inline-flex items-center gap-2 text-xs font-bold",
                    sug.direction === 'up' ? "text-primary" : "text-muted-foreground"
                  )}>
                    {sug.direction === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    Impact: ₹{Math.abs(sug.impact / 100000).toFixed(1)}L
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
}
