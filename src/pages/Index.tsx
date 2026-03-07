import { BriefDataProvider, useBriefLoading } from "@/context/BriefDataContext";
import Masthead from "@/components/Masthead";
import BottomLine from "@/components/BottomLine";
import MacroPulse from "@/components/MacroPulse";
import TradeCapital from "@/components/TradeCapital";
import LaborSignals from "@/components/LaborSignals";
import RiskRadar from "@/components/RiskRadar";
import Footer from "@/components/Footer";

function BriefContent() {
  const { isLoading, error, retry } = useBriefLoading();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background zellige-bg">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <p className="font-body text-sm text-muted-foreground">Loading briefing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background zellige-bg">
      {error && (
        <div className="border-b border-primary/20 bg-deep-teal/30 px-4 py-2 text-center">
          <span className="font-body text-xs text-muted-foreground">
            Showing cached data.{" "}
            <button onClick={retry} className="text-primary underline hover:text-amber">
              Retry
            </button>
          </span>
        </div>
      )}
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
  );
}

const Index = () => {
  return (
    <BriefDataProvider>
      <BriefContent />
    </BriefDataProvider>
  );
};

export default Index;
