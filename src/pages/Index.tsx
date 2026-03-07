import Masthead from "@/components/Masthead";
import BottomLine from "@/components/BottomLine";
import MacroPulse from "@/components/MacroPulse";
import TradeCapital from "@/components/TradeCapital";
import LaborSignals from "@/components/LaborSignals";
import RiskRadar from "@/components/RiskRadar";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background zellige-bg">
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
};

export default Index;
