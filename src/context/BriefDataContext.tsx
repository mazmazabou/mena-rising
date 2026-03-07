import { createContext, useContext } from "react";
import { briefData } from "@/data/briefData";
import { useBriefData } from "@/hooks/useBriefData";

type BriefData = typeof briefData;

const BriefDataContext = createContext<BriefData>(briefData);

export function BriefDataProvider({ children }: { children: React.ReactNode }) {
  const { data } = useBriefData();
  return (
    <BriefDataContext.Provider value={data}>
      {children}
    </BriefDataContext.Provider>
  );
}

export function useBriefContext(): BriefData {
  return useContext(BriefDataContext);
}
