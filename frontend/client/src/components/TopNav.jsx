import { Brain, Settings, Download, ChevronDown } from 'lucide-react';
import { useState } from 'react';

export function TopNav({ modelConfig, onExport }) {
  const [showControls, setShowControls] = useState(false);

  return (
    <header className="border-b border-neurolens-border bg-neurolens-surface/50 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4 flex-wrap">
          {/* Left: Title */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <Brain className="w-6 h-6 text-neurolens-textPrimary" aria-hidden="true" />
            <div>
              <h1 className="font-mono text-headline font-bold text-neurolens-textPrimary tracking-tight">
                NEUROLENS
              </h1>
              <p className="font-mono text-tiny text-neurolens-textSecondary">
                BDH Model Internals & Behavioral Investigator
              </p>
            </div>
          </div>

          {/* Center: Status */}
          <div className="hidden md:flex items-center gap-4 text-small text-neurolens-textSecondary font-mono flex-1 justify-center">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-neurolens-textPrimary" aria-hidden="true" />
              Model Checkpoint: bdh_small_v1 (10M params)
            </span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-neurolens-textPrimary animate-pulse" aria-hidden="true" />
              Status: Instrumented
            </span>
          </div>

          {/* Right: Global Controls */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="hidden sm:flex items-center gap-3 text-small text-neurolens-textSecondary font-mono">
              <span>Control Baseline: Randomized Graph</span>
              <span className="px-2 py-0.5 bg-neurolens-badgeMeasured text-neurolens-badgeMeasuredText rounded-badge text-tiny">
                Active
              </span>
            </div>
            <div className="hidden lg:flex items-center gap-2 text-small text-neurolens-textSecondary font-mono">
              <span>Seed:</span>
              <span className="px-2 py-0.5 bg-neurolens-border rounded-panel">42</span>
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
          <div id="mobile-controls" className="sm:hidden py-3 border-t border-neurolens-border animate-slide-up">
            <div className="flex flex-col gap-3 text-small font-mono">
              <div className="flex items-center justify-between">
                <span className="text-neurolens-textSecondary">Control Baseline</span>
                <span className="px-2 py-0.5 bg-neurolens-badgeMeasured text-neurolens-badgeMeasuredText rounded-badge text-tiny">
                  Randomized Graph (Active)
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-neurolens-textSecondary">Seed</span>
                <span className="px-2 py-0.5 bg-neurolens-border rounded-panel">42</span>
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