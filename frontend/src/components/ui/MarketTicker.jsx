import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";

const trends = [
  { city: "Mumbai", trend: "+1.2%", direction: "up" },
  { city: "Bangalore", trend: "+0.8%", direction: "up" },
  { city: "Delhi", trend: "-0.3%", direction: "down" },
  { city: "Hyderabad", trend: "+2.1%", direction: "up" },
  { city: "Pune", trend: "+0.5%", direction: "up" },
  { city: "Chennai", trend: "+0.2%", direction: "up" },
  { city: "Kolkata", trend: "-0.1%", direction: "down" },
];

export default function MarketTicker() {
  return (
    <div className="bg-muted border-b border-border overflow-hidden py-2 select-none">
      <motion.div
        animate={{ x: [0, -1000] }}
        transition={{ repeat: Infinity, duration: 30, ease: "linear" }}
        className="flex whitespace-nowrap gap-12 items-center"
      >
        {[...trends, ...trends].map((item, i) => (
          <div key={i} className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider">
            <span className="text-muted-foreground">{item.city}</span>
            <span className={item.direction === "up" ? "text-green-600" : "text-rose-600"}>
              {item.trend}
            </span>
            {item.direction === "up" ? (
              <TrendingUp className="w-3 h-3 text-green-600" />
            ) : (
              <TrendingDown className="w-3 h-3 text-rose-600" />
            )}
          </div>
        ))}
      </motion.div>
    </div>
  );
}
