import { useState } from 'react';
import { ChevronUp, ChevronDown, Cpu, ShieldAlert, Layers } from 'lucide-react';

export function BottomBanner() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <footer className="border-t border-neurolens-border bg-neurolens-surface sticky bottom-0 z-30">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-6 py-4 font-mono text-small text-neurolens-textSecondary hover:text-neurolens-textPrimary focus:outline-none"
        aria-expanded={isOpen}
      >
        <span className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-white animate-pulse" />
          SCALE HORIZON PROTOCOL: IF WE HAD ACCESS TO A LARGER BDH MODEL
        </span>
        {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="px-6 pb-6 pt-2 border-t border-neurolens-border/30 bg-neurolens-bg/90 animate-slide-up">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
            {/* Column 1: 100M+ Scale */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-neurolens-textPrimary">
                <Cpu className="w-4 h-4 text-neurolens-textPrimary" />
                <h4 className="font-mono text-small font-medium">100M+ Parameter Scaling</h4>
              </div>
              <p className="text-small text-neurolens-textSecondary leading-relaxed">
                Hypothesize that modularity gains will grow non-linearly with scale. Larger model extraction 
                will target sparse activation patterns to verify if sub-graph structures self-assemble 
                into distinct expert networks.
              </p>
            </div>

            {/* Column 2: Zero Forgetting */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-neurolens-textPrimary">
                <ShieldAlert className="w-4 h-4 text-neurolens-textPrimary" />
                <h4 className="font-mono text-small font-medium">Zero-Forgetting Boundaries</h4>
              </div>
              <p className="text-small text-neurolens-textSecondary leading-relaxed">
                We intend to test whether orthogonal weight projections in 100M+ parameter matrices 
                can achieve a strict mathematical limit of 0% catastrophic forgetting without any replay data, 
                relying purely on Hebbian routing pathways.
              </p>
            </div>

            {/* Column 3: 100k+ Retention */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-neurolens-textPrimary">
                <Layers className="w-4 h-4 text-neurolens-textPrimary" />
                <h4 className="font-mono text-small font-medium">100k+ Token Scaling</h4>
              </div>
              <p className="text-small text-neurolens-textSecondary leading-relaxed">
                We plan to benchmark linear state-space scan retrieval properties beyond 32k contexts. 
                Sparsity metrics should predict if long-context retrieval latency scales O(N) 
                while keeping memory consumption flat.
              </p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-neurolens-border/30 flex justify-between items-center text-tiny text-neurolens-textMuted font-mono">
            <span>Protocol: SCALE_HORIZON_v1.0</span>
            <span>Unpublished Theoretical Framework</span>
          </div>
        </div>
      )}
    </footer>
  );
}
