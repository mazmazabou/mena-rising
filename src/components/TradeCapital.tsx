import { briefData } from "@/data/briefData";
import OrnamentalDivider from "./OrnamentalDivider";
import { useScrollReveal } from "@/hooks/useScrollReveal";

const TradeCapital = () => {
  const { ref, isVisible } = useScrollReveal();

  return (
    <section ref={ref} className="px-6 py-4 md:px-12 lg:px-24">
      <OrnamentalDivider title="Trade & Capital" />
      <div
        className="mx-auto grid max-w-6xl grid-cols-1 gap-8 transition-all duration-700 lg:grid-cols-2"
        style={{ opacity: isVisible ? 1 : 0, transform: isVisible ? "none" : "translateY(20px)" }}
      >
        {/* Notable Flows */}
        <div>
          <h3 className="mb-4 font-display text-xl font-semibold text-primary">Notable Flows</h3>
          <ul className="space-y-3">
            {briefData.notableFlows.map((flow, i) => (
              <li key={i} className="flex items-start gap-3 font-body text-base text-foreground/90">
                <span className="mt-2 block h-2 w-2 shrink-0 rotate-45 bg-primary" />
                {flow}
              </li>
            ))}
          </ul>
        </div>

        {/* Deals to Watch */}
        <div>
          <h3 className="mb-4 font-display text-xl font-semibold text-primary">Deals to Watch</h3>
          <div className="space-y-3">
            {briefData.dealsToWatch.map((deal, i) => (
              <div key={i} className="rounded border border-terracotta/40 bg-card p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-display text-base font-semibold text-foreground">{deal.name}</p>
                    <p className="font-body text-sm text-muted-foreground">{deal.parties}</p>
                  </div>
                  <span className="font-mono-data text-sm font-bold text-primary">{deal.value}</span>
                </div>
                <div className="mt-2">
                  <span className="rounded-sm bg-terracotta/20 px-2 py-0.5 font-mono-data text-xs text-terracotta">
                    {deal.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TradeCapital;
