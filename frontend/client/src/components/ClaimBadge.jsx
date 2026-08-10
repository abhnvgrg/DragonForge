import { ShieldCheck, Percent, HelpCircle } from 'lucide-react';

export function ClaimBadge({ tag, className = '' }) {
  const badgeConfig = {
    ESTABLISHED: {
      className: 'badge badge-established',
      icon: ShieldCheck,
      label: 'ESTABLISHED',
      title: 'Prior published result, reproduced or cited',
    },
    MEASURED: {
      className: 'badge badge-measured',
      icon: Percent,
      label: 'MEASURED',
      title: 'New result from our experiments (p < 0.05, n ≥ 3 seeds)',
    },
    EXPLORATORY: {
      className: 'badge badge-exploratory',
      icon: HelpCircle,
      label: 'EXPLORATORY',
      title: 'Hypothesis, not yet tested',
    },
    PARTIALLY_SUPPORTED: {
      className: 'badge badge-exploratory',
      icon: HelpCircle,
      label: 'PARTIALLY SUPPORTED',
      title: 'Mixed evidence - some metrics support, others contradict',
    },
  };

  const config = badgeConfig[tag] || badgeConfig.EXPLORATORY;
  const Icon = config.icon;

  return (
    <span
      className={`${config.className} ${className}`}
      title={config.title}
    >
      <Icon className="w-3 h-3 mr-1.5" aria-hidden="true" />
      {config.label}
    </span>
  );
}