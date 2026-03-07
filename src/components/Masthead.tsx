import { Link } from "react-router-dom";
import { useBriefContext } from "@/context/BriefDataContext";

const Masthead = () => {
  const briefData = useBriefContext();
  return (
    <header className="relative zellige-bg">
      {/* Ticker Strip */}
      <div className="overflow-hidden border-b border-primary/20 bg-deep-teal/50">
        <div className="ticker-animate flex whitespace-nowrap py-1.5">
          {[...briefData.ticker, ...briefData.ticker].map((item, i) => (
            <span key={i} className="mx-6 font-mono-data text-xs">
              <span className="text-muted-foreground">{item.label}:</span>{" "}
              <span className="text-foreground">{item.value}</span>{" "}
              {item.change !== null && item.change !== 0 && (
                <span className={item.change > 0 ? "text-green-accent" : "text-red-accent"}>
                  {item.change > 0 ? "▲" : "▼"}
                  {Math.abs(item.change)}%
                </span>
              )}
              {item.change === 0 && <span className="text-muted-foreground">—</span>}
              <span className="ml-6 text-primary/30">·</span>
            </span>
          ))}
        </div>
      </div>

      {/* Main Masthead */}
      <div className="px-6 py-12 text-center md:py-16">
        {/* Calligraphic flourishes */}
        <div className="mb-4 flex items-center justify-center gap-4">
          <svg width="60" height="20" viewBox="0 0 60 20" className="text-primary opacity-50">
            <path d="M0,10 Q15,0 30,10 Q45,20 60,10" fill="none" stroke="currentColor" strokeWidth="1"/>
            <path d="M5,10 Q15,3 25,10" fill="none" stroke="currentColor" strokeWidth="0.5"/>
          </svg>
          <h1 className="font-display text-5xl font-bold tracking-[0.15em] text-primary md:text-7xl">
            MENA RISING
          </h1>
          <svg width="60" height="20" viewBox="0 0 60 20" className="text-primary opacity-50">
            <path d="M0,10 Q15,20 30,10 Q45,0 60,10" fill="none" stroke="currentColor" strokeWidth="1"/>
            <path d="M35,10 Q45,17 55,10" fill="none" stroke="currentColor" strokeWidth="0.5"/>
          </svg>
        </div>

        <p className="font-body text-lg tracking-wide text-muted-foreground md:text-xl">
          Economic Intelligence for the Middle East &amp; North Africa
        </p>
        <p className="mt-3 font-mono-data text-xs tracking-widest text-primary/70">
          Issue #{briefData.issue.number} · Week of {briefData.issue.weekOf}
        </p>
        <Link
          to="/archive"
          className="mt-2 inline-block font-mono-data text-xs text-primary/40 transition-colors hover:text-primary"
        >
          Past Issues &rarr;
        </Link>
      </div>

      {/* Muqarnas Strip */}
      <div className="muqarnas-strip" />
    </header>
  );
};

export default Masthead;
