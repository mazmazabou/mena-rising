import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

interface ManifestEntry {
  issue: number;
  date: string;
  headline: string;
  filename: string;
}

const Archive = () => {
  const [entries, setEntries] = useState<ManifestEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch("/data/archive/manifest.json")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: ManifestEntry[]) => {
        setEntries(data);
      })
      .catch(() => {
        setError(true);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-background zellige-bg">
      <div className="mx-auto max-w-3xl px-6 py-12 md:px-12">
        <Link
          to="/"
          className="font-mono-data text-xs text-primary/50 transition-colors hover:text-primary"
        >
          &larr; Current Issue
        </Link>

        <h1 className="mt-6 font-display text-4xl font-bold tracking-wide text-primary md:text-5xl">
          Past Issues
        </h1>
        <div className="ornamental-divider mt-4" />

        {isLoading && (
          <div className="mt-12 text-center">
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <p className="font-body text-sm text-muted-foreground">Loading archive...</p>
          </div>
        )}

        {error && (
          <div className="mt-12 text-center">
            <p className="font-body text-muted-foreground">Unable to load archive.</p>
          </div>
        )}

        {!isLoading && !error && entries.length === 0 && (
          <p className="mt-12 font-body text-center text-muted-foreground">
            No archived issues yet.
          </p>
        )}

        {!isLoading && !error && entries.length > 0 && (
          <div className="mt-8 space-y-4">
            {entries.map((entry) => (
              <Link
                key={entry.issue}
                to={`/archive/${entry.issue}`}
                className="card-ottoman block rounded border border-primary/10 px-6 py-5 transition-colors hover:border-primary/30"
              >
                <div className="flex items-baseline justify-between gap-4">
                  <span className="font-mono-data text-xs text-primary/60">
                    #{String(entry.issue).padStart(3, "0")}
                  </span>
                  <span className="font-mono-data text-xs text-muted-foreground">
                    {entry.date}
                  </span>
                </div>
                <p className="mt-2 font-body text-base text-foreground">{entry.headline}</p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Archive;
