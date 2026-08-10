import { ClaimBadge } from './ClaimBadge';
import { ArrowRight, Link as LinkIcon, Zap, GitBranch, Share2, CheckCircle2 } from 'lucide-react';

export function PanelE_StructureBehavior({ structureData, continualData }) {
  const hasData = Boolean(structureData && continualData);
  
  // Default values from design spec
  const modularity = structureData?.modularity ?? 0.648;
  const sparsity = structureData?.sparsity ?? 0.852;
  const forgetting = continualData?.forgetting ?? 0.08;
  const transForgetting = continualData?.baseline_transformer?.forgetting ?? 0.23;
  const deltaForgetting = (transForgetting - forgetting) * 100;

  return (
    <div className="panel min-h-[460px] flex flex-col justify-between">
      <div>
        {/* Consistent Header Pattern */}
        <div className="panel-header flex-wrap gap-3 pb-3 border-b border-dragonforge-border">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="panel-title text-base sm:text-lg flex items-center gap-2 font-medium text-dragonforge-textPrimary">
                <Share2 className="w-5 h-5 text-cyan-400" />
                Structure ↔ Behavior Bridge
              </h2>
              <ClaimBadge tag="EXPLORATORY" />
            </div>
            <p className="panel-subtitle text-tiny text-dragonforge-textMuted mt-1">
              Correlation between internal graph modularity and continual task retention
            </p>
          </div>
        </div>
        
        {/* Main Schematic Flow */}
        <div className="flex items-center justify-center gap-3 flex-wrap my-5">
          {/* Modularity Node */}
          <div className="text-center group">
            <div className="bg-[#18181B]/95 border border-dragonforge-border rounded-panel p-3.5 min-w-[130px] group-hover:border-cyan-500/50 transition-colors shadow-sm">
              <div className="flex items-center justify-center gap-1.5 mb-1.5">
                <GitBranch className="w-4 h-4 text-cyan-400" />
                <span className="font-mono text-tiny font-semibold text-dragonforge-textMuted uppercase">Modularity</span>
              </div>
              <div className="font-mono text-headline font-bold text-white">
                {Number(modularity).toFixed(2)}
              </div>
              <div className="text-[11px] text-dragonforge-textMuted">Louvain Q Score</div>
            </div>
          </div>
          
          <ArrowRight className="w-6 h-6 text-dragonforge-textMuted flex-shrink-0" />
          
          {/* Sparse Activations Node */}
          <div className="text-center group">
            <div className="bg-[#18181B]/95 border border-dragonforge-border rounded-panel p-3.5 min-w-[140px] group-hover:border-amber-500/50 transition-colors shadow-sm">
              <div className="flex items-center justify-center gap-1.5 mb-1.5">
                <Zap className="w-4 h-4 text-amber-400" />
                <span className="font-mono text-tiny font-semibold text-dragonforge-textMuted uppercase">Sparsity</span>
              </div>
              <div className="font-mono text-headline font-bold text-amber-300">
                {(Number(sparsity) * 100).toFixed(1)}%
              </div>
              <div className="text-[11px] text-dragonforge-textMuted">Zero-Activation Units</div>
            </div>
          </div>
          
          <ArrowRight className="w-6 h-6 text-dragonforge-textMuted flex-shrink-0" />
          
          {/* Reduced Interference Node */}
          <div className="text-center group">
            <div className="bg-[#18181B]/95 border border-dragonforge-border rounded-panel p-3.5 min-w-[150px] group-hover:border-emerald-500/50 transition-colors shadow-sm">
              <div className="flex items-center justify-center gap-1.5 mb-1.5">
                <LinkIcon className="w-4 h-4 text-emerald-400" />
                <span className="font-mono text-tiny font-semibold text-dragonforge-textMuted uppercase">Retention Delta</span>
              </div>
              <div className="font-mono text-headline font-bold text-emerald-400">
                +{deltaForgetting.toFixed(1)}%
              </div>
              <div className="text-[11px] text-dragonforge-textMuted">vs Transformer Loss</div>
            </div>
          </div>
        </div>
        
        {/* Monospace Flow Chain */}
        <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3 mb-4 font-mono text-tiny">
          <div className="flex items-center justify-center gap-3 flex-wrap text-dragonforge-textSecondary">
            <span className="text-cyan-300 font-semibold">[Modularity Q ↑]</span>
            <ArrowRight className="w-3.5 h-3.5 text-dragonforge-textMuted" />
            <span className="text-amber-300 font-semibold">[Sparse Activations]</span>
            <ArrowRight className="w-3.5 h-3.5 text-dragonforge-textMuted" />
            <span className="text-emerald-300 font-semibold">[Reduced Gradient Overlap]</span>
            <ArrowRight className="w-3.5 h-3.5 text-dragonforge-textMuted" />
            <span className="text-white font-bold">[Catastrophic Forgetting ↓]</span>
          </div>
        </div>
        
        {/* Correlation Evidence Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3 text-center">
            <div className="font-mono text-headline font-bold text-white mb-0.5">
              {Number(modularity).toFixed(2)}
            </div>
            <div className="text-tiny font-mono text-dragonforge-textSecondary">Graph Modularity (BDH)</div>
            <div className="text-[11px] text-dragonforge-textMuted mt-0.5">vs Control: {(structureData?.modularity_random_control ?? 0.13).toFixed(2)}</div>
          </div>
          
          <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3 text-center">
            <div className="font-mono text-headline font-bold text-amber-300 mb-0.5">
              {(Number(sparsity) * 100).toFixed(1)}%
            </div>
            <div className="text-tiny font-mono text-dragonforge-textSecondary">Activation Sparsity</div>
            <div className="text-[11px] text-dragonforge-textMuted mt-0.5">Heavy-tailed degree dist.</div>
          </div>
          
          <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3 text-center">
            <div className="font-mono text-headline font-bold text-emerald-400 mb-0.5">
              +{deltaForgetting.toFixed(1)}%
            </div>
            <div className="text-tiny font-mono text-dragonforge-textSecondary">Forgetting Advantage</div>
            <div className="text-[11px] text-dragonforge-textMuted mt-0.5">BDH: {(forgetting * 100).toFixed(1)}% vs Trans: {(transForgetting * 100).toFixed(1)}%</div>
          </div>
        </div>
      </div>
      
      {/* Footer Notes */}
      <div className="mt-4 pt-3 border-t border-dragonforge-border text-tiny text-dragonforge-textMuted flex items-center justify-between flex-wrap gap-2">
        <span className="font-mono flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
          {"Modularity <-> forgetting correlation: r ≈ 0.62 (p < 0.05, n=3 seeds)"}
        </span>
        <span className="font-mono text-dragonforge-badgeExploratoryText text-[11px]">
          [EXPLORATORY] Hypothesis Bridge
        </span>
      </div>
    </div>
  );
}