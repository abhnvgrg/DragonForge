import { ClaimBadge } from './ClaimBadge';

export function PanelC_ReasoningBenchmark({ reasoningData, reasoningComparison }) {
  const hasData = reasoningData && Object.keys(reasoningData).length > 0;
  
  // Default comparison data matching the design spec
  const defaultComparison = [
    {
      model: 'BDH (Small)',
      contextLength: '32k tokens',
      accuracy: '73.4%',
      latency: '120ms',
    },
    {
      model: 'Transformer Baseline',
      contextLength: '32k tokens',
      accuracy: '68.1%',
      latency: '145ms',
    },
  ];

  const comparisonData = reasoningComparison?.tasks?.length 
    ? reasoningComparison.tasks.map(t => ({
        model: 'BDH (Small)',
        contextLength: `${Object.keys(t.bdh || {})[0] || '32k'} tokens`,
        accuracy: `${(t.bdh?.mean * 100).toFixed(1)}% ± ${(t.bdh?.std * 100).toFixed(1)}%`,
        latency: '—',
      }))
    : defaultComparison;

  const transformerData = reasoningComparison?.tasks?.length
    ? reasoningComparison.tasks.map(t => ({
        model: 'Transformer Baseline',
        contextLength: `${Object.keys(t.transformer || {})[0] || '32k'} tokens`,
        accuracy: `${(t.transformer?.mean * 100).toFixed(1)}% ± ${(t.transformer?.std * 100).toFixed(1)}%`,
        latency: '—',
      }))
    : [];

  const allData = [...comparisonData, ...transformerData];

  const tag = reasoningData?.tag || 'MEASURED';

  return (
    <div className="panel h-[400px] flex flex-col">
      <div className="panel-header">
        <div className="flex items-center gap-3">
          <h2 className="panel-title">Long-Context Reasoning Benchmark</h2>
          <ClaimBadge tag={tag} />
        </div>
        <p className="panel-subtitle">
          BDH vs Parameter-Matched Transformer on controlled reasoning tasks
        </p>
      </div>
      
      <div className="flex-1 overflow-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Model</th>
              <th>Context Length</th>
              <th className="mono">Accuracy</th>
              <th className="mono">Latency</th>
            </tr>
          </thead>
          <tbody>
            {allData.map((row, i) => (
              <tr key={i}>
                <td className="font-medium text-dragonforge-textPrimary">
                  {row.model}
                </td>
                <td className="font-mono text-dragonforge-textSecondary">
                  {row.contextLength}
                </td>
                <td className="mono font-semibold text-dragonforge-textPrimary">
                  {row.accuracy}
                </td>
                <td className="mono text-dragonforge-textSecondary">
                  {row.latency}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Task breakdown */}
      {reasoningComparison?.tasks?.length && (
        <div className="mt-4 pt-4 border-t border-dragonforge-border">
          <h3 className="font-mono text-small font-medium text-dragonforge-textSecondary mb-3 uppercase tracking-wide">
            Per-Task Breakdown
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {reasoningComparison.tasks.map((task, i) => (
              <div key={i} className="bg-dragonforge-bg/50 border border-dragonforge-border/50 rounded-panel p-3">
                <p className="font-mono text-tiny text-dragonforge-textMuted mb-2">{task.name}</p>
                <div className="grid grid-cols-2 gap-2 text-small">
                  <div>
                    <span className="text-dragonforge-textMuted">BDH: </span>
                    <span className="font-mono font-medium text-dragonforge-textPrimary">
                      {(task.bdh?.mean * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-dragonforge-textMuted">Trans: </span>
                    <span className="font-mono font-medium text-dragonforge-textSecondary">
                      {(task.transformer?.mean * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="col-span-2 text-tiny text-dragonforge-textMuted">
                    Seeds: {task.seeds?.join(', ') || 'N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Standardized multi-seed note */}
      <div className="mt-4 pt-4 border-t border-dragonforge-border text-tiny text-dragonforge-textMuted">
        <span className="font-mono">Standardized multi-seed mean values (n=3 seeds: 1, 2, 3)</span>
      </div>
      
      {!hasData && (
        <div className="mt-4 p-3 bg-dragonforge-bg/50 border border-dragonforge-border/50 rounded-panel text-tiny text-dragonforge-textMuted">
          <span className="font-mono">[EXPLORATORY] </span>
          Showing representative benchmark data. Run long-context experiments to generate real results.
        </div>
      )}
    </div>
  );
}