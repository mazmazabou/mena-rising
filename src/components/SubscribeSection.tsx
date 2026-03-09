import { useState } from "react";
import { toast } from "sonner";
import OrnamentalDivider from "./OrnamentalDivider";
import { useScrollReveal } from "@/hooks/useScrollReveal";
import { useBriefContext } from "@/context/BriefDataContext";

const features = [
  { name: "Macro Pulse", desc: "key indicators across 8 MENA economies" },
  { name: "Risk Radar", desc: "geopolitical and economic threat signals" },
  { name: "Trade & Capital", desc: "notable flows and deals to watch" },
];

const SubscribeSection = () => {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { ref, isVisible } = useScrollReveal();
  const briefData = useBriefContext();

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) {
        toast.error(data.error || "Subscription failed");
        return;
      }
      if (data.already) {
        toast.info("You're already subscribed — see you Monday!");
      } else {
        toast.success("You're subscribed! Check your inbox for a welcome email.");
        setEmail("");
      }
    } catch {
      toast.error("Network error — please try again");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="bg-navy/50 px-6 py-12 md:px-12 lg:px-24">
      <OrnamentalDivider title="Stay Informed" />

      <div
        ref={ref}
        className={`mx-auto max-w-3xl text-center transition-all duration-700 ${
          isVisible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
        }`}
      >
        <h2 className="font-display text-2xl text-foreground md:text-3xl">
          Weekly economic intelligence. Straight from the data.
        </h2>

        <p className="mx-auto mt-4 max-w-2xl font-body text-sm leading-relaxed text-muted-foreground md:text-base">
          Every Monday, MENA Rising distills macro data, risk signals, and capital flows across the
          region into one concise briefing — so you start the week informed.
        </p>

        <div className="mx-auto mt-6 grid max-w-lg gap-2 text-left sm:grid-cols-3 sm:text-center">
          {features.map((f) => (
            <div key={f.name} className="font-body text-sm text-muted-foreground">
              <span className="text-primary">&#10022;</span>{" "}
              <span className="font-semibold text-foreground">{f.name}</span> — {f.desc}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubscribe} className="mx-auto mt-8 flex max-w-md gap-2">
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
            className="flex-1 rounded border border-primary/30 bg-input px-4 py-2 font-body text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="rounded bg-primary px-5 py-2 font-display text-sm font-semibold text-primary-foreground transition-colors hover:bg-amber disabled:opacity-50"
          >
            {isLoading ? "..." : "Subscribe"}
          </button>
        </form>

        <p className="mt-6 font-mono-data text-xs text-muted-foreground/60">
          Join readers of Issue #{briefData.issue.number} and counting.
        </p>
      </div>
    </section>
  );
};

export default SubscribeSection;
