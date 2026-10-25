import React, { useState, useEffect, useRef } from 'react';
import type { PrimarySectionId } from '../navigation/WorkspaceNavigation';

export interface CommandPaletteAction {
  id: string;
  label: string;
  category: string;
  shortcut?: string;
  targetSection: PrimarySectionId;
}

const DEFAULT_ACTIONS: CommandPaletteAction[] = [
  { id: 'cmd-home', label: 'Go to Executive Home Dashboard', category: 'Navigation', shortcut: 'G H', targetSection: 'home' },
  { id: 'cmd-inbox', label: 'Open Unified Privacy Inbox & Approval Queue', category: 'Navigation', shortcut: 'G I', targetSection: 'inbox' },
  { id: 'cmd-dpia', label: 'Start or Resume Guided Assessment (DPIA / Law 25 EFVP / PHIPA TRA)', category: 'Workflow', shortcut: 'C A', targetSection: 'assessments' },
  { id: 'cmd-breach', label: 'Triage Multi-Jurisdiction Breach Incident (72h GDPR / RROSH)', category: 'Workflow', shortcut: 'C B', targetSection: 'incidents' },
  { id: 'cmd-dsar', label: 'Evaluate DSAR Privacy Rights Request & Statutory Exemptions', category: 'Workflow', shortcut: 'C D', targetSection: 'rights' },
  { id: 'cmd-ropa', label: 'Inspect Records of Processing Activities (RoPA) & Vendors', category: 'Inventory', targetSection: 'data_vendors' },
  { id: 'cmd-reg', label: 'Inspect Verified Regulatory Intelligence & Legal Review Queue', category: 'Intelligence', targetSection: 'regulatory' },
  { id: 'cmd-jrae', label: 'Open JRAE Applicability Engine & 113-Jurisdiction Matrix', category: 'Intelligence', targetSection: 'applicability' },
  { id: 'cmd-assistant', label: 'Query Governed Multi-Jurisdictional Privacy Assistant', category: 'AI Assistant', targetSection: 'assistant' },
  { id: 'cmd-reports', label: 'Export SHA-256 Sealed Regulator Audit Pack', category: 'Reporting', targetSection: 'reports' },
  { id: 'cmd-admin', label: 'Open Enterprise Administration & Connector Health', category: 'Admin', targetSection: 'admin' },
];

export interface CommandPaletteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSection: (section: PrimarySectionId) => void;
}

export const CommandPaletteModal: React.FC<CommandPaletteModalProps> = ({
  isOpen,
  onClose,
  onSelectSection,
}) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const filtered = DEFAULT_ACTIONS.filter((a) => {
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    return a.label.toLowerCase().includes(q) || a.category.toLowerCase().includes(q);
  });

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 20);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleGlobalKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        }
      } else if (isOpen && e.key === 'Escape') {
        e.preventDefault();
        onClose();
      } else if (isOpen && e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, Math.max(0, filtered.length - 1)));
      } else if (isOpen && e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(0, prev - 1));
      } else if (isOpen && e.key === 'Enter' && filtered[selectedIndex]) {
        e.preventDefault();
        onSelectSection(filtered[selectedIndex].targetSection);
        onClose();
      }
    };
    window.addEventListener('keydown', handleGlobalKey);
    return () => window.removeEventListener('keydown', handleGlobalKey);
  }, [isOpen, filtered, selectedIndex, onClose, onSelectSection]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Global Command Palette"
      data-testid="command-palette-modal"
      className="fixed inset-0 z-50 flex items-start justify-center bg-slate-950/80 backdrop-blur-sm pt-20 px-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="border-b border-slate-800 p-3.5 flex items-center gap-2">
          <span className="text-slate-300 font-mono">⌕</span>
          <input
            ref={inputRef}
            type="search"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Type a command, workflow, statute, or section..."
            aria-label="Command palette search"
            data-testid="command-palette-input"
            className="w-full bg-transparent text-sm text-slate-100 focus:outline-none"
          />
          <button
            type="button"
            onClick={onClose}
            className="rounded bg-slate-800 px-2 py-0.5 text-xs font-mono text-slate-300"
          >
            ESC
          </button>
        </div>

        <ul className="max-h-80 overflow-y-auto divide-y divide-slate-800/70 p-2 text-xs">
          {filtered.map((item, idx) => (
            <li key={item.id}>
              <button
                type="button"
                data-testid={`command-item-${item.id}`}
                onClick={() => {
                  onSelectSection(item.targetSection);
                  onClose();
                }}
                className={`w-full text-left rounded-lg px-3 py-2.5 flex items-center justify-between ${
                  idx === selectedIndex
                    ? 'bg-emerald-500/20 text-emerald-200 font-semibold'
                    : 'text-slate-200 hover:bg-slate-800'
                }`}
              >
                <div>
                  <span className="font-mono text-[10px] uppercase text-sky-300 mr-2">
                    [{item.category}]
                  </span>
                  <span>{item.label}</span>
                </div>
                {item.shortcut && (
                  <kbd className="rounded bg-slate-950 px-1.5 py-0.5 font-mono text-[10px] text-slate-300">
                    {item.shortcut}
                  </kbd>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
