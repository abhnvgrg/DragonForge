import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { ClaimBadge } from './ClaimBadge';

export function PanelB_TrainingEvolution({ structureCheckpoints }) {
  // Generate training evolution data from checkpoints
  const chartData = structureCheckpoints?.checkpoints?.map((cp, i) => ({
    step: cp.step,
    modularity: cp.modularity,
    modularityControl: cp.modularity_random_control,
    sparsity: cp.sparsity,
    clustering: cp.clustering_coefficient,
  })) || [];

  // If no real data, show placeholder
  const hasData = chartData.length > 0;

  const placeholderData = Array.from({ length: 11 }, (_, i) => ({
    step: i * 1000,
    modularity: 0.15 + i * 0.04 + Math.random() * 0.02,
    modularityControl: 0.12 + Math.random() * 0.03,
    sparsity: 0.75 + i * 0.01 + Math.random() * 0.02,
    clustering: 0.25 + i * 0.01 + Math.random() * 0.02,
  }));

  const displayData = hasData ? chartData : placeholderData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dragonforge-surface border border-dragonforge-border rounded-panel p-3 shadow-panel">
          <p className="font-mono text-tiny text-dragonforge-textMuted mb-1">Step: {label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="font-mono text-small text-dragonforge-textPrimary flex items-center gap-2">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(4) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="panel h-[400px] flex flex-col">
      <div className="panel-header">
        <div className="flex items-center gap-3">
          <h2 className="panel-title">Training Evolution Timeline</h2>
          <ClaimBadge tag={hasData ? 'MEASURED' : 'EXPLORATORY'} />
        </div>
        <p className="panel-subtitle">
          Modularity vs Downstream Accuracy across training steps
        </p>
      </div>
      
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={displayData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
            <CartesianGrid 
              strokeDasharray="4 4" 
              stroke="#27272A" 
              vertical={false}
              horizontal={true}
            />
            <XAxis
              dataKey="step"
              tick={{ fill: '#71717A', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              axisLine={{ stroke: '#27272A' }}
              tickLine={{ stroke: '#27272A' }}
              label={{ value: 'Training Steps', position: 'insideBottom', offset: -20, fill: '#A1A1AA', fontSize: 11 }}
            />
            <YAxis
              tick={{ fill: '#71717A', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              axisLine={{ stroke: '#27272A' }}
              tickLine={{ stroke: '#27272A' }}
              label={{ value: 'Score', angle: -90, position: 'insideLeft', offset: 20, fill: '#A1A1AA', fontSize: 11 }}
              domain={[0, 1]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: 20 }}
              formatter={(value) => value}
            />
            <ReferenceLine y={0.5} stroke="#27272A" strokeDasharray="4 4" />
            
            {/* Modularity Control (dashed) */}
            <Line
              type="monotone"
              dataKey="modularityControl"
              stroke="#3F3F46"
              strokeWidth={1.5}
              strokeDasharray="6 4"
              dot={false}
              name="Modularity (Control)"
              animationDuration={300}
            />
            
            {/* Modularity BDH */}
            <Line
              type="monotone"
              dataKey="modularity"
              stroke="#FAFAFA"
              strokeWidth={2}
              dot={false}
              name="Modularity (BDH)"
              animationDuration={300}
            />
            
            {/* Sparsity */}
            <Line
              type="monotone"
              dataKey="sparsity"
              stroke="#A1A1AA"
              strokeWidth={1.5}
              dot={false}
              name="Sparsity"
              animationDuration={300}
            />
            
            {/* Clustering */}
            <Line
              type="monotone"
              dataKey="clustering"
              stroke="#71717A"
              strokeWidth={1.5}
              strokeDasharray="2 2"
              dot={false}
              name="Clustering"
              animationDuration={300}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Legend / Key Metrics */}
      <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-dragonforge-border text-tiny">
        <div className="flex items-center gap-2 text-dragonforge-textSecondary">
          <span className="w-6 h-0.5 bg-white" />
          <span>Modularity (BDH)</span>
        </div>
        <div className="flex items-center gap-2 text-dragonforge-textMuted">
          <span className="w-6 h-0.5 bg-dragonforge-border" style={{ borderTop: '2px dashed #3F3F46' }} />
          <span>Modularity (Control)</span>
        </div>
        <div className="flex items-center gap-2 text-dragonforge-textMuted">
          <span className="w-6 h-0.5 bg-dragonforge-textSecondary" />
          <span>Sparsity</span>
        </div>
        <div className="flex items-center gap-2 text-dragonforge-textMuted">
          <span className="w-6 h-0.5 bg-dragonforge-textMuted" style={{ borderTop: '1px dashed #71717A' }} />
          <span>Clustering</span>
        </div>
      </div>
      
      {!hasData && (
        <div className="mt-4 p-3 bg-dragonforge-bg/50 border border-dragonforge-border/50 rounded-panel text-tiny text-dragonforge-textMuted">
          <span className="font-mono">[EXPLORATORY] </span>
          Showing synthetic training evolution data. Run the full pipeline to generate real checkpoint metrics.
        </div>
      )}
    </div>
  );
}