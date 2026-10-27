import { Link } from "react-router-dom";
import { useBriefContext } from "@/context/BriefDataContext";

// Eight-point khatam star: two squares turned 45° against each other, ringed.
// pathLength=1 lets the CSS draw each stroke in from 0 to 1.
const Rosette = () => (
  <svg viewBox="0 0 48 48" className="rosette h-12 w-12 text-primary md:h-14 md:w-14" aria-hidden="true">
    <rect x="10" y="10" width="28" height="28" pathLength={1} />
    <rect x="10" y="10" width="28" height="28" pathLength={1} transform="rotate(45 24 24)" />
    <circle cx="24" cy="24" r="7" pathLength={1} />
    <circle cx="24" cy="24" r="22" pathLength={1} className="rosette-ring" />
  </svg>
);

const firstSentence = (text: string) => {
  const match = text.match(/^.+?[.!?](\s|$)/);
  return (match ? match[0] : text).trim();
};

const Masthead = () => {
  const briefData = useBriefContext();
  const { issue, ticker, risks, dealsToWatch, macroPulse } = briefData;
  const lead = briefData.headline?.trim() || firstSentence(briefData.bottomLine);
  const topRisk = [...risks].sort(
    (a, b) => ["CRITICAL", "HIGH", "MEDIUM", "LOW"].indexOf(a.level) - ["CRITICAL", "HIGH", "MEDIUM", "LOW"].indexOf(b.level),
  )[0];
  const countries = new Set(macroPulse.map((m) => m.country)).size;

  const contents = [
    { href: "#bottom-line", name: "The bottom line", teaser: "This week's analysis" },
    { href: "#macro-pulse", name: "Macro pulse", teaser: `${macroPulse.length} indicators across ${countries} economies` },
    dealsToWatch[0] && { href: "#trade-capital", name: "Trade & capital", teaser: dealsToWatch[0].name },
    { href: "#labor-signals", name: "Labor & AI", teaser: "Youth jobs, AI adoption, tech hiring" },
    topRisk && { href: "#risk-radar", name: "Risk radar", teaser: `${topRisk.title} (${topRisk.level.toLowerCase()})` },
  ].filter(Boolean) as { href: string; name: string; teaser: string }[];

  return (
    <header className="relative">
      {/* Ticker strip */}
      <div className="ticker group overflow-hidden border-b border-primary/20 bg-deep-teal/60">
        <div className="ticker-animate flex whitespace-nowrap py-1.5 group-hover:[animation-play-state:paused]">
          {[...ticker, ...ticker].map((item, i) => (
            <span key={i} className="mx-6 text-sm" aria-hidden={i >= ticker.length || undefined}>
              <span className="font-body text-muted-foreground">{item.label}</span>{" "}
              <span className="font-mono-data text-xs text-foreground">{item.value}</span>{" "}
              {item.change !== null && item.change !== 0 && (
                <span className={`font-mono-data text-xs ${item.change > 0 ? "text-green-accent" : "text-red-accent"}`}>
                  {item.change > 0 ? "▲" : "▼"}
                  {Math.abs(item.change)}%
                </span>
              )}
            </span>
          ))}
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-5 pt-8 md:px-10 md:pt-10">
        {/* Dateline */}
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 font-body text-sm text-muted-foreground md:text-base">
          <span>No. {issue.number}</span>
          <Rosette />
          <span className="text-right">
            <span className="hidden sm:inline">Week of </span>
            {issue.weekOf}
          </span>
        </div>

        <div className="rule-draw mt-4 border-t-[3px] border-double border-primary/70" />

        {/* Nameplate */}
        <h1 className="nameplate py-4 text-center font-display text-[clamp(3rem,11vw,7.5rem)] font-semibold leading-none text-primary md:py-5">
          MENA Rising
        </h1>

        <div className="rule-draw geometric-border-bottom" />
        <div className="mt-2 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 font-body text-sm text-muted-foreground md:text-base">
          <span className="italic">Economic intelligence for the Middle East &amp; North Africa, every Monday</span>
          <Link to="/archive" className="text-primary/80 underline-offset-4 hover:text-primary hover:underline">
            Past issues
          </Link>
        </div>

        {/* Front page: lead story + contents */}
        <div className="mt-10 grid gap-10 border-t border-primary/25 pt-8 pb-4 md:mt-12 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)] lg:gap-14">
          <h2 className="lead-headline font-display text-[clamp(2.1rem,5.2vw,4.1rem)] font-medium leading-[1.05] text-foreground [text-wrap:balance]">
            {lead}
          </h2>

          <nav aria-label="In this issue" className="lead-contents border-primary/25 lg:border-l lg:pl-8">
            <p className="font-display text-lg italic text-primary">In this issue</p>
            <ol className="mt-3 divide-y divide-primary/15">
              {contents.map((c) => (
                <li key={c.href}>
                  <a href={c.href} className="group block py-2.5 focus-visible:outline-none">
                    <span className="font-display text-lg font-semibold text-foreground group-hover:text-primary group-focus-visible:text-primary group-focus-visible:underline">
                      {c.name}
                    </span>
                    <span className="block font-body text-sm leading-snug text-muted-foreground">{c.teaser}</span>
                  </a>
                </li>
              ))}
            </ol>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Masthead;
