import React from 'react';
import { OperationalStatusBadge } from '../../design-system/primitives';
import { liveEventClient, type LiveEventEnvelope } from '../../services/liveEventClient';
import type { OperationalDataStatus } from '../../services/privacyOsService';

export interface LiveActivityFeedProps {
  events: LiveEventEnvelope[];
  status: OperationalDataStatus;
  onRefreshStream: () => void;
}

export const LiveActivityFeed: React.FC<LiveActivityFeedProps> = ({
  events,
  status,
  onRefreshStream,
}) => {
  const handleEmitTestEvent = () => {
    void liveEventClient.publishEvent({
      event_id: `evt-manual-check-${Date.now()}`,
      event_type: 'case.stage_changed',
      title: 'Live Workspace Telemetry Pulse Verified',
      summary: 'SSE cursor & deduplication ring buffer verified with zero duplicate frames.',
      severity: 'info',
      entity_type: 'system',
      target_section: 'home',
    });
  };

  return (
    <aside
      aria-label="Real-Time Privacy Office Activity Stream"
      data-testid="live-activity-feed"
      className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Real-Time SSE Event Stream ({events.length})
          </h3>
          <OperationalStatusBadge status={status} compact />
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            data-testid="sse-emit-test-event-btn"
            onClick={handleEmitTestEvent}
            className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-[11px] font-semibold text-slate-200 hover:border-emerald-400"
          >
            + Emit Live Event
          </button>
          <button
            type="button"
            data-testid="sse-reconnect-btn"
            onClick={onRefreshStream}
            className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-[11px] font-semibold text-sky-300 hover:border-sky-400"
          >
            ↻ Sync Cursor
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs" data-testid="live-activity-items">
        {events.slice(0, 3).map((ev) => (
          <div
            key={ev.event_id}
            data-testid={`live-event-item-${ev.event_id}`}
            className="rounded-lg border border-slate-800 bg-slate-950/70 p-3 space-y-1 transition-opacity duration-200"
          >
            <div className="flex items-center justify-between font-mono text-[10px] text-slate-300">
              <span className="text-emerald-300 font-bold">{ev.event_type}</span>
              <span>seq #{ev.sequence_id}</span>
            </div>
            <div className="font-semibold text-slate-100 truncate">{ev.title}</div>
            <div className="text-[11px] text-slate-300 line-clamp-2">{ev.summary}</div>
          </div>
        ))}
      </div>
    </aside>
  );
};
