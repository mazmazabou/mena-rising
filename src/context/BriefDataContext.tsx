import { createContext, useContext } from "react";
import { briefData } from "@/data/briefData";
import { useBriefData } from "@/hooks/useBriefData";

type BriefData = typeof briefData;

const BriefDataContext = createContext<BriefData>(briefData);
const BriefLoadingContext = createContext<{
  isLoading: boolean;
  error: boolean;
  retry: () => void;
}>({ isLoading: false, error: false, retry: () => {} });

export function BriefDataProvider({
  children,
  data: overrideData,
}: {
  children: React.ReactNode;
  data?: BriefData;
}) {
  const { data: fetchedData, isLoading, error, retry } = useBriefData();
  return (
    <BriefLoadingContext.Provider value={{ isLoading, error, retry }}>
      <BriefDataContext.Provider value={overrideData ?? fetchedData}>
        {children}
      </BriefDataContext.Provider>
    </BriefLoadingContext.Provider>
  );
}

export function useBriefContext(): BriefData {
  return useContext(BriefDataContext);
}

export function useBriefLoading() {
  return useContext(BriefLoadingContext);
}
