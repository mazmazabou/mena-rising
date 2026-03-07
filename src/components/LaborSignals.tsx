import { useBriefContext } from "@/context/BriefDataContext";
import OrnamentalDivider from "./OrnamentalDivider";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const LaborSignals = () => {
  const { ref, isVisible } = useScrollReveal();
  const briefData = useBriefContext();
  const { youthUnemployment, aiAdoption, techJobs } = briefData.laborSignals;
  const maxUnemp = Math.max(...youthUnemployment.map((d) => d.value));

  return (
    <section ref={ref} className="px-6 py-4 md:px-12 lg:px-24">
      <OrnamentalDivider title="Labor & AI Signals" />
      <div
        className="mx-auto grid max-w-6xl grid-cols-1 gap-4 transition-all duration-700 md:grid-cols-3"
        style={{ opacity: isVisible ? 1 : 0, transform: isVisible ? "none" : "translateY(20px)" }}
      >
        {/* Youth Unemployment */}
        <div className="card-ottoman rounded bg-card p-5">
          <p className="mb-4 font-display text-sm font-semibold uppercase tracking-widest text-primary">
            Youth Unemployment
          </p>
          <div className="space-y-2">
            {youthUnemployment.map((d) => (
              <div key={d.country} className="flex items-center gap-2">
                <span className="w-20 font-body text-xs text-muted-foreground">{d.country}</span>
                <div className="flex-1">
                  <div
                    className="h-3 rounded-sm bg-primary/60 transition-all duration-700"
                    style={{ width: `${(d.value / maxUnemp) * 100}%` }}
                  />
                </div>
                <span className="font-mono-data text-xs text-foreground">{d.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Adoption */}
        <div className="card-ottoman rounded bg-card p-5">
          <p className="mb-4 font-display text-sm font-semibold uppercase tracking-widest text-primary">
            AI Adoption Index
          </p>
          <div className="space-y-2">
            {aiAdoption.map((d) => (
              <div key={d.country} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-mono-data text-xs text-primary/70">#{d.rank}</span>
                  <span className="font-body text-sm text-foreground">{d.country}</span>
                </div>
                <span className="font-mono-data text-sm font-bold text-foreground">{d.score}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Jobs */}
        <div className="card-ottoman rounded bg-card p-5">
          <p className="mb-4 font-display text-sm font-semibold uppercase tracking-widest text-primary">
            Tech Sector Postings
          </p>
          <div className="mb-3 flex items-center gap-2">
            <span className="text-3xl text-green-accent">▲</span>
            <span className="font-mono-data text-3xl font-bold text-foreground">{techJobs.change}%</span>
          </div>
          <p className="font-body text-sm leading-relaxed text-muted-foreground">{techJobs.context}</p>
        </div>
      </div>
    </section>
  );
};

export default LaborSignals;
