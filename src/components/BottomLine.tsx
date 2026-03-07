import { briefData } from "@/data/briefData";

const BottomLine = () => (
  <section className="animate-fade-up px-6 py-10 md:px-12 lg:px-24" style={{ animationDelay: "0.2s" }}>
    <div className="parchment mx-auto max-w-4xl rounded border-l-4 border-l-primary p-8 md:p-10">
      <p className="mb-4 font-display text-xs font-semibold tracking-[0.3em] uppercase text-primary">
        This Week's Analysis
      </p>
      <p className="font-body text-lg italic leading-relaxed text-foreground/90 md:text-xl">
        {briefData.bottomLine}
      </p>
    </div>
  </section>
);

export default BottomLine;
