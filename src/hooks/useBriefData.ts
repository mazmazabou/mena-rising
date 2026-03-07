import { useState, useEffect } from "react";
import { briefData } from "@/data/briefData";

type BriefData = typeof briefData;

export function useBriefData(): { data: BriefData; isLoading: boolean } {
  const [data, setData] = useState<BriefData>(briefData);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch("/data/latest_brief.json")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: BriefData) => {
        setData(json);
      })
      .catch(() => {
        // Fall back to hardcoded briefData — already set as default
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return { data, isLoading };
}
