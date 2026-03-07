import { useState, useEffect, useCallback } from "react";
import { briefData } from "@/data/briefData";

type BriefData = typeof briefData;

export function useBriefData(): {
  data: BriefData;
  isLoading: boolean;
  error: boolean;
  retry: () => void;
} {
  const [data, setData] = useState<BriefData>(briefData);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);

  const retry = useCallback(() => {
    setError(false);
    setIsLoading(true);
    setAttempt((n) => n + 1);
  }, []);

  useEffect(() => {
    fetch("/data/latest_brief.json")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json: BriefData) => {
        setData(json);
        setError(false);
      })
      .catch(() => {
        setError(true);
        // Fall back to hardcoded briefData — already set as default
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [attempt]);

  return { data, isLoading, error, retry };
}
