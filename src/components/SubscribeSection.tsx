import { useState } from "react";
import { toast } from "sonner";
import { useBriefContext } from "@/context/BriefDataContext";

const SubscribeSection = () => {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
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
    <section id="subscribe" className="mt-16 border-y border-primary/25 bg-deep-teal/40 px-5 py-14 md:px-10">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:items-end">
        <div>
          <h2 className="font-display text-3xl font-medium leading-tight text-foreground md:text-4xl [text-wrap:balance]">
            Get the brief in your inbox every Monday
          </h2>
          <p className="mt-4 max-w-[60ch] font-body text-lg leading-relaxed text-muted-foreground">
            Macro data, capital flows and risk signals across the region, distilled into one read
            before the week starts.
          </p>
        </div>

        <div>
          <form onSubmit={handleSubscribe} className="flex gap-2">
            <input
              type="email"
              placeholder="you@company.com"
              aria-label="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
              className="min-w-0 flex-1 rounded-sm border border-primary/40 bg-navy px-4 py-2.5 font-body text-base text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="rounded-sm bg-primary px-5 py-2.5 font-display text-base font-semibold text-primary-foreground transition-colors hover:bg-amber disabled:opacity-50"
            >
              {isLoading ? "Subscribing…" : "Subscribe"}
            </button>
          </form>

          <p className="mt-3 font-body text-sm text-muted-foreground">
            Issue {briefData.issue.number} is out now. The next one lands Monday.
          </p>
        </div>
      </div>
    </section>
  );
};

export default SubscribeSection;
