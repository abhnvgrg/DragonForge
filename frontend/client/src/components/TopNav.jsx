import { Brain, Settings, Download } from 'lucide-react';
import { useState } from 'react';

export function TopNav({ modelConfig, onExport }) {
  const [showControls, setShowControls] = useState(false);

  return (
    <header className="border-b border-dragonforge-border bg-dragonforge-bg/95 backdrop-blur-md sticky top-0 z-40 shadow-sm">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4 flex-wrap">
          {/* Left: Title */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <Brain className="w-6 h-6 text-dragonforge-textPrimary" aria-hidden="true" />
            <div>
              <h1 className="font-mono text-headline font-bold text-dragonforge-textPrimary tracking-tight">
                NEUROLENS
              </h1>
              <p className="font-mono text-tiny text-dragonforge-textSecondary">
                BDH Model Internals & Behavioral Investigator
              </p>
            </div>
          </div>

          {/* Center: Status */}
          <div className="hidden md:flex items-center gap-4 text-small text-dragonforge-textSecondary font-mono flex-1 justify-center">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-dragonforge-textPrimary" aria-hidden="true" />
              Model Checkpoint: bdh_small_v1 (10M params)
            </span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
              Status: Instrumented
            </span>
          </div>

          {/* Right: Global Controls */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="hidden sm:flex items-center gap-3 text-small text-dragonforge-textSecondary font-mono">
              <span>Control Baseline: Randomized Graph</span>
              <span className="px-2 py-0.5 bg-dragonforge-badgeMeasured text-dragonforge-badgeMeasuredText rounded-badge text-tiny">
                Active
              </span>
            </div>
            <div className="hidden lg:flex items-center gap-2 text-small text-dragonforge-textSecondary font-mono">
              <span>Seed:</span>
              <span className="px-2 py-0.5 bg-dragonforge-border rounded-panel">42</span>
            </div>
            
            <button
              onClick={onExport}
              className="btn-secondary hidden sm:inline-flex"
              title="Export all data as JSON"
            >
              <Download className="w-4 h-4" aria-hidden="true" />
              Export Data
            </button>
            
            <button
              onClick={() => setShowControls(!showControls)}
              className="btn-ghost sm:hidden p-2"
              aria-expanded={showControls}
              aria-controls="mobile-controls"
            >
              <Settings className="w-5 h-5" aria-hidden="true" />
            </button>
          </div>
        </div>

        {/* Mobile controls dropdown */}
        {showControls && (
          <div id="mobile-controls" className="sm:hidden py-3 border-t border-dragonforge-border bg-dragonforge-bg/95 animate-slide-up">
            <div className="flex flex-col gap-3 text-small font-mono">
              <div className="flex items-center justify-between">
                <span className="text-dragonforge-textSecondary">Control Baseline</span>
                <span className="px-2 py-0.5 bg-dragonforge-badgeMeasured text-dragonforge-badgeMeasuredText rounded-badge text-tiny">
                  Randomized Graph (Active)
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-dragonforge-textSecondary">Seed</span>
                <span className="px-2 py-0.5 bg-dragonforge-border rounded-panel">42</span>
              </div>
              <button onClick={onExport} className="btn-secondary w-full justify-center">
                <Download className="w-4 h-4" aria-hidden="true" />
                Export Data (JSON)
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}