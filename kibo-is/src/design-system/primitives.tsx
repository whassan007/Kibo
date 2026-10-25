import React, { Component, ErrorInfo, ReactNode } from 'react';
import { SEMANTIC_BADGE_STYLES } from './tokens';
import type { OperationalDataStatus } from '../services/privacyOsService';

export interface StatusBadgeProps {
  status: OperationalDataStatus;
  cachedAt?: string;
  compact?: boolean;
}

export const OperationalStatusBadge: React.FC<StatusBadgeProps> = ({ status, cachedAt, compact }) => {
  const cfg = SEMANTIC_BADGE_STYLES[status] || SEMANTIC_BADGE_STYLES.offline;
  return (
    <span
      role="status"
      aria-live="polite"
      title={cachedAt ? `${cfg.description} (Last synced: ${cachedAt})` : cfg.description}
      data-testid="operational-status-badge"
      data-status={status}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold tracking-wide ${cfg.className}`}
    >
      <span aria-hidden="true">{cfg.icon}</span>
      <span>{cfg.label}</span>
      {!compact && status === 'stale' && cachedAt && (
        <span className="opacity-75 font-normal">({new Date(cachedAt).toLocaleTimeString()})</span>
      )}
    </span>
  );
};

export interface SlaCountdownBadgeProps {
  label: string;
  hoursRemaining?: number | null;
  daysRemaining?: number | null;
  overdue?: boolean;
}

export const SlaCountdownBadge: React.FC<SlaCountdownBadgeProps> = ({
  label,
  hoursRemaining,
  daysRemaining,
  overdue,
}) => {
  const isUrgent = Boolean(overdue) || (typeof hoursRemaining === 'number' && hoursRemaining <= 24) || (typeof daysRemaining === 'number' && daysRemaining <= 5);
  const tone = overdue
    ? 'bg-rose-950/90 text-rose-200 border-rose-500/50'
    : isUrgent
    ? 'bg-amber-950/90 text-amber-200 border-amber-500/50'
    : 'bg-slate-800/90 text-slate-200 border-slate-600/50';
  const icon = overdue ? '⚠' : isUrgent ? '⏱' : '✓';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded border px-2 py-0.5 text-xs font-mono font-medium ${tone}`}>
      <span aria-hidden="true">{icon}</span>
      <span>{label}</span>
    </span>
  );
};

export interface StageStepperProps {
  stages: string[];
  currentIndex: number;
  onSelectStage?: (index: number) => void;
}

export const StageStepper: React.FC<StageStepperProps> = ({ stages, currentIndex, onSelectStage }) => {
  return (
    <nav aria-label="Workflow Progress" className="w-full overflow-x-auto py-2">
      <ol className="flex items-center gap-2 min-w-max">
        {stages.map((stage, idx) => {
          const isCompleted = idx < currentIndex;
          const isCurrent = idx === currentIndex;
          const tone = isCurrent
            ? 'bg-emerald-500/20 border-emerald-400 text-emerald-200 font-semibold'
            : isCompleted
            ? 'bg-slate-800/90 border-emerald-500/40 text-emerald-300'
            : 'bg-slate-900/60 border-slate-700 text-slate-400';
          return (
            <li key={stage} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => onSelectStage && onSelectStage(idx)}
                aria-current={isCurrent ? 'step' : undefined}
                className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition-colors focus:outline-none focus:ring-2 focus:ring-sky-400 ${tone}`}
              >
                <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-slate-950/60 text-[11px] font-mono">
                  {isCompleted ? '✓' : idx + 1}
                </span>
                <span>{stage}</span>
              </button>
              {idx < stages.length - 1 && (
                <span aria-hidden="true" className="text-slate-600">
                  →
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export interface MetricSummaryCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  tone?: 'critical' | 'warning' | 'success' | 'info';
  icon?: string;
  onClick?: () => void;
  testId?: string;
}

export const MetricSummaryCard: React.FC<MetricSummaryCardProps> = ({
  title,
  value,
  subtitle,
  tone = 'info',
  icon = '●',
  onClick,
  testId,
}) => {
  const borderMap = {
    critical: 'border-rose-500/40 hover:border-rose-400 bg-rose-950/20',
    warning: 'border-amber-500/40 hover:border-amber-400 bg-amber-950/20',
    success: 'border-emerald-500/40 hover:border-emerald-400 bg-emerald-950/20',
    info: 'border-sky-500/40 hover:border-sky-400 bg-slate-900/70',
  };
  const badgeMap = {
    critical: 'text-rose-300',
    warning: 'text-amber-300',
    success: 'text-emerald-300',
    info: 'text-sky-300',
  };

  return (
    <button
      type="button"
      onClick={onClick}
      data-testid={testId}
      className={`text-left w-full rounded-xl border p-4 transition-all focus:outline-none focus:ring-2 focus:ring-sky-400 ${borderMap[tone]}`}
    >
      <div className="flex items-center justify-between text-xs uppercase tracking-wider text-slate-300">
        <span>{title}</span>
        <span aria-hidden="true" className={badgeMap[tone]}>
          {icon}
        </span>
      </div>
      <div className={`mt-2 text-2xl font-bold font-mono ${badgeMap[tone]}`}>{value}</div>
      <div className="mt-1 text-xs text-slate-300">{subtitle}</div>
    </button>
  );
};

export interface EmptyStateCardProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyStateCard: React.FC<EmptyStateCardProps> = ({
  title,
  description,
  actionLabel,
  onAction,
}) => (
  <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/50 p-8 text-center">
    <h3 className="text-base font-semibold text-slate-100">{title}</h3>
    <p className="mx-auto mt-2 max-w-lg text-sm text-slate-300">{description}</p>
    {actionLabel && onAction && (
      <button
        type="button"
        onClick={onAction}
        className="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-sky-400"
      >
        {actionLabel}
      </button>
    )}
  </div>
);

interface ErrorBoundaryState {
  hasError: boolean;
  errorMessage: string;
}

export class WorkspaceErrorBoundary extends Component<
  { children: ReactNode; sectionName?: string },
  ErrorBoundaryState
> {
  constructor(props: { children: ReactNode; sectionName?: string }) {
    super(props);
    this.state = { hasError: false, errorMessage: '' };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, errorMessage: error.message || 'Unexpected rendering error' };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('[WorkspaceErrorBoundary]', error, info);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          className="rounded-xl border border-rose-500/40 bg-rose-950/30 p-6 text-slate-100"
        >
          <h3 className="text-base font-semibold text-rose-200">
            ⚠ {this.props.sectionName || 'Workspace Module'} encountered a recoverable error
          </h3>
          <p className="mt-2 text-xs text-slate-300">{this.state.errorMessage}</p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false, errorMessage: '' })}
            className="mt-4 rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-500"
          >
            Retry Module
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
