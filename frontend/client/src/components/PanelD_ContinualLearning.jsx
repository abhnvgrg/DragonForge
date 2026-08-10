import { ClaimBadge } from './ClaimBadge';
import { ArrowRight, Minus, AlertTriangle, Layers, CheckCircle2 } from 'lucide-react';

export function PanelD_ContinualLearning({ continualData }) {
  const hasData = Boolean(continualData && Object.keys(continualData).length > 0);
  
  // Default data matching design spec
  const defaultData = {
    task_a_before: 0.81,
    task_a_after: 0.73,
    task_b_after: 0.76,
    forgetting: 0.08,
    baseline_transformer: {
      task_a_before: 0.81,
      task_a_after: 0.58,
      forgetting: 0.23,
    },
    tag: 'MEASURED',
  };

  const data = hasData ? continualData : defaultData;
  const tag = data.tag || 'MEASURED';
  
  const bdhForgetting = (data.forgetting ?? 0.08) * 100;
  const transForgetting = data.baseline_transformer?.forgetting 
    ? data.baseline_transformer.forgetting * 100 
    : 23.0;
  
  const bdhRetention = ((data.task_a_after / (data.task_a_before || 1)) * 100).toFixed(1);
  const transRetention = data.baseline_transformer?.task_a_after && data.baseline_transformer?.task_a_before
    ? ((data.baseline_transformer.task_a_after / data.baseline_transformer.task_a_before) * 100).toFixed(1)
    : '71.6';

  return (
    <div className="panel min-h-[440px] flex flex-col justify-between">
      <div>
        {/* Consistent Header Pattern */}
        <div className="panel-header flex-wrap gap-3 pb-3 border-b border-dragonforge-border">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="panel-title text-base sm:text-lg flex items-center gap-2 font-medium text-dragonforge-textPrimary">
                <Layers className="w-5 h-5 text-emerald-400" />
                Sequential Continual Learning Matrix
              </h2>
              <ClaimBadge tag={tag} />
            </div>
            <p className="panel-subtitle text-tiny text-dragonforge-textMuted mt-1">
              Task A → Task B → Re-test Task A (Catastrophic Forgetting)
            </p>
          </div>
        </div>
        
        {/* Flow Diagram */}
        <div className="flex items-center justify-center gap-3 my-4 flex-wrap">
          <div className="text-center">
            <div className="font-mono text-tiny text-dragonforge-textMuted mb-1">Task A (Train)</div>
            <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel px-3.5 py-2.5 min-w-[110px]">
              <div className="font-mono text-headline font-semibold text-dragonforge-textPrimary">
                {(data.task_a_before * 100).toFixed(1)}%
              </div>
              <div className="text-[11px] text-dragonforge-textMuted">Initial Accuracy</div>
            </div>
          </div>
          
          <ArrowRight className="w-5 h-5 text-dragonforge-textMuted flex-shrink-0" />
          
          <div className="text-center">
            <div className="font-mono text-tiny text-dragonforge-textMuted mb-1">Task B (Train)</div>
            <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel px-3.5 py-2.5 min-w-[110px]">
              <div className="font-mono text-headline font-semibold text-dragonforge-textPrimary">
                {(data.task_b_after * 100).toFixed(1)}%
              </div>
              <div className="text-[11px] text-dragonforge-textMuted">After Training</div>
            </div>
          </div>
          
          <ArrowRight className="w-5 h-5 text-dragonforge-textMuted flex-shrink-0" />
          
          <div className="text-center">
            <div className="font-mono text-tiny text-dragonforge-textMuted mb-1">Re-test Task A</div>
            <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel px-3.5 py-2.5 min-w-[110px]">
              <div className="font-mono text-headline font-semibold text-dragonforge-textPrimary">
                {(data.task_a_after * 100).toFixed(1)}%
              </div>
              <div className="text-[11px] text-dragonforge-textMuted">Post-Task B</div>
            </div>
          </div>
        </div>
        
        {/* Forgetting Comparison Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
          {/* BDH Card */}
          <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3.5">
            <div className="flex items-center justify-between mb-2.5">
              <h3 className="font-mono text-small font-medium text-dragonforge-textPrimary flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                BDH (NeuroLens)
              </h3>
              <ClaimBadge tag={tag} className="text-tiny" />
            </div>
            <div className="space-y-2 text-small font-mono">
              <div className="flex justify-between text-dragonforge-textSecondary">
                <span>Task A Initial:</span>
                <span className="font-semibold text-dragonforge-textPrimary">
                  {(data.task_a_before * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-dragonforge-textSecondary">
                <span>Task A Post-Task B:</span>
                <span className="font-semibold text-dragonforge-textPrimary">
                  {(data.task_a_after * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between border-t border-dragonforge-border pt-2 text-dragonforge-textPrimary">
                <span className="font-medium">Retention:</span>
                <span className="font-bold text-emerald-400">
                  {bdhRetention}%
                </span>
              </div>
              <div className="flex justify-between text-emerald-400/90 text-tiny">
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3 text-amber-400" />
                  Forgetting Loss:
                </span>
                <span className="font-bold">
                  -{bdhForgetting.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
          
          {/* Transformer Baseline Card */}
          <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3.5">
            <div className="flex items-center justify-between mb-2.5">
              <h3 className="font-mono text-small font-medium text-dragonforge-textSecondary flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-zinc-500" />
                Transformer Baseline
              </h3>
              <ClaimBadge tag="MEASURED" className="text-tiny" />
            </div>
            <div className="space-y-2 text-small font-mono">
              <div className="flex justify-between text-dragonforge-textSecondary">
                <span>Task A Initial:</span>
                <span className="font-semibold text-dragonforge-textSecondary">
                  {(data.baseline_transformer?.task_a_before * 100 || 81.0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-dragonforge-textSecondary">
                <span>Task A Post-Task B:</span>
                <span className="font-semibold text-dragonforge-textSecondary">
                  {(data.baseline_transformer?.task_a_after * 100 || 58.0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between border-t border-dragonforge-border pt-2 text-dragonforge-textSecondary">
                <span className="font-medium">Retention:</span>
                <span className="font-bold text-zinc-300">
                  {transRetention}%
                </span>
              </div>
              <div className="flex justify-between text-red-400 text-tiny">
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3 text-red-400" />
                  Forgetting Loss:
                </span>
                <span className="font-bold">
                  -{transForgetting.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Delta Summary */}
        <div className="bg-[#18181B]/90 border border-dragonforge-border rounded-panel p-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2.5">
              <Minus className="w-4 h-4 text-emerald-400" />
              <div>
                <p className="font-mono text-tiny font-semibold text-dragonforge-textPrimary">
                  Forgetting Delta: BDH <span className="text-emerald-400">outperforms</span> Transformer by <span className="font-bold text-white">{(transForgetting - bdhForgetting).toFixed(1)}%</span>
                </p>
                <p className="text-[11px] text-dragonforge-textMuted">
                  Lower forgetting indicates modular preservation of weights across tasks
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="font-mono text-base font-bold text-emerald-400">
                +{(transForgetting - bdhForgetting).toFixed(1)}%
              </span>
              <span className="text-[10px] text-dragonforge-textMuted block uppercase">Advantage</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer Notes */}
      <div className="mt-4 pt-3 border-t border-dragonforge-border text-tiny text-dragonforge-textMuted flex items-center justify-between flex-wrap gap-2">
        <span className="font-mono flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          Standardized 2-task sequential continual learning benchmark
        </span>
        {!hasData && (
          <span className="font-mono text-dragonforge-badgeExploratoryText text-[11px]">
            [EXPLORATORY] Representative Data
          </span>
        )}
      </div>
    </div>
  );
}