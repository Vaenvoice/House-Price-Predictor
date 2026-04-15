import { motion } from "framer-motion";
import { cn } from "@/utils/cn";

export function Card({ className, children, delay = 0, hover = false }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.23, 1, 0.32, 1] }}
      className={cn(
        "card-flat p-6 relative overflow-hidden transition-all duration-300",
        hover && "hover:border-[var(--muted-foreground)]/30 hover:shadow-sm",
        className
      )}
    >
      {children}
    </motion.div>
  );
}
