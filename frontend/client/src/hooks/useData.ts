// Custom hooks for data fetching with loading/error states
import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../utils/api';
import type {
  StructureCheckpoint,
  StructureMetrics,
  InteractionGraph,
  ContinualLearningResult,
  ReasoningResult,
  SummaryResult,
  ModelConfig,
  InstrumentationConfig,
} from '../types';

interface UseDataResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

function useFetch<T>(fetchFn: () => Promise<T>, deps: unknown[] = []): UseDataResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Keep a ref to the latest fetchFn so inline functions don't trigger re-fetch loops
  const fetchFnRef = useRef(fetchFn);
  useEffect(() => {
    fetchFnRef.current = fetchFn;
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFnRef.current();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;

    const execute = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchFnRef.current();
        if (!isCancelled) {
          setData(result);
        }
      } catch (err) {
        if (!isCancelled) {
          setError(err instanceof Error ? err : new Error('Unknown error'));
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    execute();

    return () => {
      isCancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, loading, error, refetch: fetchData };
}

// Structure hooks
export function useStructureCheckpoints() {
  return useFetch(() => api.structure.all());
}

export function useLatestStructureCheckpoint() {
  return useFetch(() => api.structure.latest());
}

export function useStructureComparison() {
  return useFetch(() => api.structure.comparison());
}

export function useStructureGraph(model: 'bdh' | 'transformer') {
  return useFetch(() => api.structure.graph(model), [model]);
}

// Continual Learning hooks
export function useContinualLearning() {
  return useFetch(() => api.continual.all());
}

export function useBdhContinual() {
  return useFetch(() => api.continual.bdh());
}

export function useTransformerContinual() {
  return useFetch(() => api.continual.transformer());
}

// Reasoning hooks
export function useReasoning() {
  return useFetch(() => api.reasoning.all());
}

export function useReasoningComparison() {
  return useFetch(() => api.reasoning.comparison());
}

// Summary hooks
export function useSummary() {
  return useFetch(() => api.summary.all());
}

export function useHeadline() {
  return useFetch(() => api.summary.headline());
}

// Config hooks
export function useModelConfig() {
  return useFetch(() => api.config.model());
}

export function useInstrumentationConfig() {
  return useFetch(() => api.config.instrumentation());
}