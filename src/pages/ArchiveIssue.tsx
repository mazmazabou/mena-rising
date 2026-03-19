import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { briefData } from "@/data/briefData";
import { BriefDataProvider } from "@/context/BriefDataContext";
import Masthead from "@/components/Masthead";
import BottomLine from "@/components/BottomLine";
import MacroPulse from "@/components/MacroPulse";
import TradeCapital from "@/components/TradeCapital";
import LaborSignals from "@/components/LaborSignals";
import RiskRadar from "@/components/RiskRadar";
import Footer from "@/components/Footer";

type BriefData = typeof briefData;

const ArchiveIssue = () => {
  const { issueNumber } = useParams<{ issueNumber: string }>();
  const [data, setData] = useState<BriefData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    const padded = String(issueNumber).padStart(3, "0");
    fetch(`/data/archive/issue-${padded}.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: BriefData) => {
        setData(json);
      })
      .catch(() => {
        setNotFound(true);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [issueNumber]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background zellige-bg">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <p className="font-body text-sm text-muted-foreground">Loading issue...</p>
        </div>
      </div>
    );
  }

  if (notFound || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background zellige-bg">
        <div className="text-center">
          <h1 className="font-display text-3xl font-bold text-primary">Issue Not Found</h1>
          <p className="mt-3 font-body text-muted-foreground">
            Issue #{issueNumber} doesn't exist in the archive.
          </p>
          <div className="mt-6 flex justify-center gap-4">
            <Link
              to="/archive"
              className="font-mono-data text-sm text-primary/70 transition-colors hover:text-primary"
            >
              &larr; Back to Archive
            </Link>
            <Link
              to="/"
              className="font-mono-data text-sm text-primary/70 transition-colors hover:text-primary"
            >
              &larr; Current Issue
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const headline = data.headline || "";
  const description = (typeof data.bottomLine === "string" ? data.bottomLine : "").slice(0, 155);
  const ogTitle = `MENA Rising Issue #${issueNumber} — ${headline}`;

  return (
    <BriefDataProvider data={data}>
      <Helmet>
        <title>{ogTitle}</title>
        <meta property="og:title" content={ogTitle} />
        <meta property="og:description" content={description} />
        <meta property="og:url" content={`https://mena-rising.com/archive/${issueNumber}`} />
        <meta property="og:image" content="https://mena-rising.com/og-default.png" />
        <meta name="twitter:title" content={ogTitle} />
        <meta name="twitter:description" content={description} />
        <meta name="twitter:image" content="https://mena-rising.com/og-default.png" />
      </Helmet>
      <div className="min-h-screen bg-background zellige-bg">
        <div className="flex items-center justify-between border-b border-primary/20 bg-deep-teal/30 px-6 py-2">
          <Link
            to="/archive"
            className="font-mono-data text-xs text-primary/60 transition-colors hover:text-primary"
          >
            &larr; Back to Archive
          </Link>
          <Link
            to="/"
            className="font-mono-data text-xs text-primary/60 transition-colors hover:text-primary"
          >
            &larr; Current Issue
          </Link>
        </div>
        <Masthead />
        <main>
          <BottomLine />
          <MacroPulse />
          <TradeCapital />
          <LaborSignals />
          <RiskRadar />
        </main>
        <Footer />
      </div>
    </BriefDataProvider>
  );
};

export default ArchiveIssue;
