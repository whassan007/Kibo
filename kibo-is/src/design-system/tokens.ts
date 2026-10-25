/**
 * KIBO Privacy OS — Enterprise Design System Tokens (Agent G12)
 * Implements Section 8 (Visual Design, Typography, Density & Accessibility)
 * WCAG 2.2 AA contrast validated across Light Mode and Dark Mode.
 */

export type ThemeMode = 'dark' | 'light';

export interface ThemePalette {
  bgPrimary: string;
  bgElevated: string;
  bgSurface: string;
  borderSubtle: string;
  borderFocus: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  brandAccent: string;
}

export const DESIGN_TOKENS: Record<ThemeMode, ThemePalette> = {
  dark: {
    bgPrimary: '#0B1120',
    bgElevated: '#111827',
    bgSurface: '#1E293B',
    borderSubtle: '#334155',
    borderFocus: '#38BDF8',
    textPrimary: '#F8FAFC',
    textSecondary: '#CBD5E1',
    textMuted: '#94A3B8',
    brandAccent: '#10B981',
  },
  light: {
    bgPrimary: '#F8FAFC',
    bgElevated: '#FFFFFF',
    bgSurface: '#F1F5F9',
    borderSubtle: '#CBD5E1',
    borderFocus: '#0284C7',
    textPrimary: '#0F172A',
    textSecondary: '#334155',
    textMuted: '#475569',
    brandAccent: '#047857',
  },
};

export const SEMANTIC_BADGE_STYLES = {
  live: {
    label: 'LIVE',
    icon: '●',
    className: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40',
    description: 'Verified backend connection and active SSE stream',
  },
  updating: {
    label: 'UPDATING',
    icon: '↻',
    className: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
    description: 'Request or workflow calculation in flight',
  },
  stale: {
    label: 'STALE',
    icon: '◷',
    className: 'bg-amber-950/80 text-amber-300 border-amber-500/40',
    description: 'Showing cached snapshot while reconnecting',
  },
  offline: {
    label: 'OFFLINE',
    icon: '✕',
    className: 'bg-rose-950/80 text-rose-300 border-rose-500/40',
    description: 'Backend unreachable; read-only cached/reference view',
  },
  demo: {
    label: 'DEMO',
    icon: '◈',
    className: 'bg-purple-950/80 text-purple-300 border-purple-500/40',
    description: 'Explicitly selected demonstration sandbox',
  },
  error: {
    label: 'ERROR',
    icon: '⚠',
    className: 'bg-rose-950/90 text-rose-200 border-rose-500/60',
    description: 'Operation failed; see recovery guidance',
  },
  unverified: {
    label: 'UNVERIFIED',
    icon: '⚑',
    className: 'bg-amber-950/90 text-amber-200 border-amber-500/60',
    description: 'Pending human legal counsel verification',
  },
} as const;
