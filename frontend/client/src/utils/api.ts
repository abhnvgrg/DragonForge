// API Client for NeuroLens Backend

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

const API_BASE = '/api';

async function fetchJson<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  // Health
  health: () => fetchJson<{ status: string; timestamp: string }>('/health'),
  
  // Structure
  structure: {
    all: () => fetchJson<{ checkpoints: StructureCheckpoint[]; count: number }>('/structure'),
    latest: () => fetchJson<StructureCheckpoint>('/structure/latest'),
    comparison: () => fetchJson<{ bdh: StructureMetrics | null; transformer: StructureMetrics | null }>('/structure/comparison'),
    graph: (model: 'bdh' | 'transformer') => fetchJson<InteractionGraph>(`/structure/graph?model=${model}`),
  },
  
  // Continual Learning
  continual: {
    all: () => fetchJson<ContinualLearningResult>('/continual'),
    bdh: () => fetchJson<Partial<ContinualLearningResult>>('/continual/bdh'),
    transformer: () => fetchJson<Partial<ContinualLearningResult>>('/continual/transformer'),
  },
  
  // Long-Context Reasoning
  reasoning: {
    all: () => fetchJson<ReasoningResult>('/reasoning'),
    comparison: () => fetchJson<{ tasks: Array<{ name: string; bdh: { mean: number; std: number }; transformer: { mean: number; std: number }; seeds: number[]; tag: string }> }>('/reasoning/comparison'),
  },
  
  // Summary
  summary: {
    all: () => fetchJson<SummaryResult>('/summary'),
    headline: () => fetchJson<{ headline: string }>('/summary/headline'),
  },
  
  // Config
  config: {
    all: () => fetchJson<any>('/config'),
    model: () => fetchJson<ModelConfig>('/config/model'),
    instrumentation: () => fetchJson<InstrumentationConfig>('/config/instrumentation'),
  },
};
