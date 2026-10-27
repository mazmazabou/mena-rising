import { useBriefContext } from "@/context/BriefDataContext";
import OrnamentalDivider from "./OrnamentalDivider";

const BottomLine = () => {
  const briefData = useBriefContext();
  return (
    <section id="bottom-line" className="scroll-mt-6 px-5 md:px-10">
      <OrnamentalDivider title="The bottom line" />
      <div className="mx-auto max-w-6xl">
        <p className="lede max-w-[68ch] font-body text-xl leading-[1.7] text-foreground/90 md:text-[1.35rem]">
          {briefData.bottomLine}
        </p>
      </div>
    </section>
  );
};

export default BottomLine;
