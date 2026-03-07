import { useBriefContext } from "@/context/BriefDataContext";
import OrnamentalDivider from "./OrnamentalDivider";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const riskColors: Record<string, { bg: string; text: string }> = {
  LOW: { bg: "bg-green-accent/20", text: "text-green-accent" },
  MEDIUM: { bg: "bg-amber/20", text: "text-amber" },
  HIGH: { bg: "bg-terracotta/20", text: "text-terracotta" },
  CRITICAL: { bg: "bg-red-accent/20", text: "text-red-accent" },
};

const RiskRadar = () => {
  const { ref, isVisible } = useScrollReveal();
  const briefData = useBriefContext();

  return (
    <section ref={ref} className="bg-navy/50 px-6 py-8 md:px-12 lg:px-24">
      <OrnamentalDivider title="Risk Radar" />
      <div
        className="mx-auto grid max-w-6xl grid-cols-1 gap-4 transition-all duration-700 md:grid-cols-3"
        style={{ opacity: isVisible ? 1 : 0, transform: isVisible ? "none" : "translateY(20px)" }}
      >
        {briefData.risks.map((risk, i) => {
          const colors = riskColors[risk.level] || riskColors.MEDIUM;
          return (
            <div key={i} className="card-ottoman rounded bg-card p-5">
              <span className={`inline-block rounded-sm px-2 py-0.5 font-mono-data text-xs font-bold ${colors.bg} ${colors.text}`}>
                {risk.level}
              </span>
              <h4 className="mt-3 font-display text-lg font-semibold text-foreground">{risk.title}</h4>
              <p className="mt-2 font-body text-sm leading-relaxed text-muted-foreground">{risk.description}</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {risk.countries.map((c) => (
                  <span key={c} className="rounded-sm border border-primary/20 px-2 py-0.5 font-mono-data text-xs text-primary/70">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default RiskRadar;
