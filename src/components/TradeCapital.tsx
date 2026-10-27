import { useBriefContext } from "@/context/BriefDataContext";
import OrnamentalDivider from "./OrnamentalDivider";

const TradeCapital = () => {
  const briefData = useBriefContext();

  return (
    <section id="trade-capital" className="scroll-mt-6 px-5 md:px-10">
      <OrnamentalDivider title="Trade & capital" />
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-10 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:gap-14">
        <div>
          <h3 className="mb-3 font-display text-xl font-semibold text-primary">Notable flows</h3>
          <ul className="divide-y divide-primary/15">
            {briefData.notableFlows.map((flow, i) => (
              <li key={i} className="flex items-start gap-3 py-3 font-body text-lg leading-relaxed text-foreground/90">
                <span className="mt-[0.7em] block h-1.5 w-1.5 shrink-0 rotate-45 bg-primary" aria-hidden="true" />
                {flow}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="mb-3 font-display text-xl font-semibold text-primary">Deals to watch</h3>
          <ul className="border-t border-primary/40">
            {briefData.dealsToWatch.map((deal, i) => (
              <li key={i} className="grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 border-b border-primary/20 py-4">
                <p className="font-display text-lg font-semibold leading-snug text-foreground">{deal.name}</p>
                <p className="row-span-2 self-start font-mono-data text-xl text-primary">{deal.value}</p>
                <p className="font-body text-base text-muted-foreground">
                  {deal.parties.split(" · ").join(", ")}
                  <span className="italic text-terracotta"> ({deal.status})</span>
                </p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
};

export default TradeCapital;
