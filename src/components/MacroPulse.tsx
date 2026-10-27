import { useBriefContext } from "@/context/BriefDataContext";
import OrnamentalDivider from "./OrnamentalDivider";
import Sparkline from "./Sparkline";
import { useRef, useEffect, useState } from "react";
import { briefData } from "@/data/briefData";

const MetricCard = ({ item }: { item: typeof briefData.macroPulse[0] }) => {
  const ref = useRef<HTMLDivElement>(null);
  const reduceMotion = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [displayValue, setDisplayValue] = useState(reduceMotion ? item.value : 0);

  useEffect(() => {
    if (reduceMotion) {
      setDisplayValue(item.value);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          observer.disconnect();
          const start = performance.now();
          const animate = (now: number) => {
            const progress = Math.min((now - start) / 600, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplayValue(eased * item.value);
            if (progress < 1) requestAnimationFrame(animate);
          };
          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [item.value, reduceMotion]);

  const formatValue = (v: number) => {
    if (item.unit === "$B") return `$${v.toFixed(1)}B`;
    if (item.unit === "% GDP") return `${v.toFixed(1)}%`;
    if (item.unit === "%") return `${v.toFixed(1)}%`;
    return v.toFixed(2);
  };

  return (
    <div
      ref={ref}
      className="card-ottoman rounded-sm bg-card p-5"
    >
      <div className="mb-1 flex items-center gap-2">
        <span className="text-lg">{item.flag}</span>
        <span className="font-body text-sm text-muted-foreground">{item.country}</span>
      </div>
      <p className="mb-2 font-display text-lg font-semibold leading-snug text-foreground">{item.metric}</p>
      <div className="flex items-end justify-between">
        <div>
          <span className="font-mono-data text-2xl font-bold text-foreground">
            {formatValue(displayValue)}
          </span>
          {item.change !== 0 && (
            <span className={`ml-2 font-mono-data text-xs ${item.change > 0 ? "text-green-accent" : "text-red-accent"}`}>
              {item.change > 0 ? "▲" : "▼"}{Math.abs(item.change)}%
            </span>
          )}
          {item.change === 0 && (
            <span className="ml-2 font-mono-data text-xs text-muted-foreground">—</span>
          )}
        </div>
        <Sparkline data={item.sparkline} />
      </div>
    </div>
  );
};

const MacroPulse = () => {
  const data = useBriefContext();

  return (
    <section id="macro-pulse" className="scroll-mt-6 px-5 md:px-10">
      <OrnamentalDivider title="Macro pulse" />
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.macroPulse.map((item) => (
          <MetricCard key={`${item.country}-${item.metric}`} item={item} />
        ))}
      </div>
    </section>
  );
};

export default MacroPulse;
