import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

const Footer = () => {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
    <footer className="border-t border-primary/20 px-6 py-10 md:px-12 lg:px-24">
      <div className="mx-auto max-w-4xl text-center">
        <p className="font-body text-sm leading-relaxed text-muted-foreground">
          MENA Rising publishes every Monday. Data sourced from World Bank, FRED, IMF, and regional central banks.
        </p>

        {/* Email Subscription */}
        <form onSubmit={handleSubscribe} className="mx-auto mt-6 flex max-w-md gap-2">
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
          Built with Python · Claude API · GitHub Actions
        </p>
        <Link
          to="/archive"
          className="mt-2 inline-block font-mono-data text-xs text-muted-foreground/40 transition-colors hover:text-primary"
        >
          Browse Past Issues
        </Link>
      </div>

      {/* Geometric border strip */}
      <div className="geometric-border-bottom mt-8" />
    </footer>
  );
};

export default Footer;
