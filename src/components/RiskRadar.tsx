import { useBriefContext } from "@/context/BriefDataContext";
import OrnamentalDivider from "./OrnamentalDivider";

const riskColors: Record<string, { rule: string; text: string }> = {
  LOW: { rule: "border-l-green-accent", text: "text-green-accent" },
  MEDIUM: { rule: "border-l-amber", text: "text-amber" },
  HIGH: { rule: "border-l-terracotta", text: "text-terracotta" },
  CRITICAL: { rule: "border-l-red-accent", text: "text-red-accent" },
};

const RiskRadar = () => {
  const briefData = useBriefContext();

  return (
    <section id="risk-radar" className="scroll-mt-6 px-5 pb-6 md:px-10">
      <OrnamentalDivider title="Risk radar" />
      <div
        className="mx-auto grid max-w-6xl grid-cols-1 gap-4 md:grid-cols-3"
      >
        {briefData.risks.map((risk, i) => {
          const colors = riskColors[risk.level] || riskColors.MEDIUM;
          return (
            <article key={i} className={`border-l-[3px] bg-card/70 p-5 ${colors.rule}`}>
              <p className={`font-display text-base font-semibold italic ${colors.text}`}>
                {risk.level.charAt(0) + risk.level.slice(1).toLowerCase()} risk
              </p>
              <h3 className="mt-1 font-display text-xl font-semibold leading-snug text-foreground">{risk.title}</h3>
              <p className="mt-2 font-body text-base leading-relaxed text-muted-foreground">{risk.description}</p>
              <p className="mt-3 font-body text-sm text-primary/80">{risk.countries.join(", ")}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
};

export default RiskRadar;
