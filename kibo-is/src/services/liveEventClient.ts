import { VITE_API_BASE } from './api';
import { getPrivacyOsTenantContext } from './privacyOsService';

export type LiveEventType =
  | 'case.created'
  | 'case.assigned'
  | 'case.stage_changed'
  | 'assessment.saved'
  | 'assessment.submitted'
  | 'assessment.approved'
  | 'incident.created'
  | 'incident.severity_changed'
  | 'incident.deadline_updated'
  | 'dsar.deadline_approaching'
  | 'approval.requested'
  | 'approval.completed'
  | 'regulation.discovered'
  | 'regulation.verified'
  | 'regulation.impact_detected'
  | 'agent.started'
  | 'agent.progress'
  | 'agent.completed'
  | 'agent.failed'
  | 'integration.status_changed';

export const ALL_GOVERNED_EVENT_TYPES: LiveEventType[] = [
  'case.created',
  'case.assigned',
  'case.stage_changed',
  'assessment.saved',
  'assessment.submitted',
  'assessment.approved',
  'incident.created',
  'incident.severity_changed',
  'incident.deadline_updated',
  'dsar.deadline_approaching',
  'approval.requested',
  'approval.completed',
  'regulation.discovered',
  'regulation.verified',
  'regulation.impact_detected',
  'agent.started',
  'agent.progress',
  'agent.completed',
  'agent.failed',
  'integration.status_changed',
];

export type LiveConnectionState = 'live' | 'updating' | 'stale' | 'offline' | 'demo' | 'error';

export interface LiveEventEnvelope {
  event_id: string;
  sequence_id: number;
  tenant_id: string;
  event_type: LiveEventType;
  title: string;
  summary: string;
  severity: 'info' | 'success' | 'warning' | 'critical';
  actor_id: string;
  actor_role: string;
  entity_type?: string | null;
  entity_id?: string | null;
  target_section?: string | null;
  requires_human_review: boolean;
  provenance_status: 'verified' | 'pending_review' | 'operational';
  created_at: string;
  payload: Record<string, unknown>;
}

export type LiveEventSubscriber = (events: LiveEventEnvelope[], state: LiveConnectionState) => void;

export class LiveEventClient {
  private events: LiveEventEnvelope[] = [];
  private seenIds: Set<string> = new Set();
  private lastSequenceId = 0;
  private state: LiveConnectionState = 'updating';
  private subscribers: Set<LiveEventSubscriber> = new Set();
  private eventSource: EventSource | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private activeTenantId: string = 'tnt-enterprise-global-001';
  private isPaused = false;
  private visibilityListenerBound = false;

  constructor() {
    this.bindVisibilityHandler();
  }

  private bindVisibilityHandler(): void {
    if (this.visibilityListenerBound || typeof document === 'undefined') return;
    this.visibilityListenerBound = true;
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.pause();
      } else {
        this.resume();
      }
    });
  }

  public getEvents(): LiveEventEnvelope[] {
    return [...this.events];
  }

  public getConnectionState(): LiveConnectionState {
    return this.state;
  }

  public getLastSequenceId(): number {
    return this.lastSequenceId;
  }

  /**
   * Deterministic deduplication by `event_id` and tenant isolation guard (UX-11).
   */
  public ingestEvents(incoming: LiveEventEnvelope[], nextState?: LiveConnectionState): number {
    let added = 0;
    for (const ev of incoming) {
      if (!ev || !ev.event_id) continue;
      if (ev.tenant_id && ev.tenant_id !== this.activeTenantId) continue;
      if (this.seenIds.has(ev.event_id)) continue;

      this.seenIds.add(ev.event_id);
      this.events.unshift(ev);
      if (ev.sequence_id > this.lastSequenceId) {
        this.lastSequenceId = ev.sequence_id;
      }
      added += 1;
    }

    if (this.events.length > 200) {
      const removed = this.events.splice(200);
      for (const r of removed) {
        this.seenIds.delete(r.event_id);
      }
    }

    // Keep descending sequence order
    this.events.sort((a, b) => b.sequence_id - a.sequence_id);

    if (nextState) {
      this.state = nextState;
    }
    this.notify();
    return added;
  }

  public switchTenant(tenantId: string): void {
    if (tenantId === this.activeTenantId) return;
    this.activeTenantId = tenantId;
    this.events = [];
    this.seenIds.clear();
    this.lastSequenceId = 0;
    this.disconnect();
    void this.connect(tenantId);
  }

  public subscribe(fn: LiveEventSubscriber): () => void {
    this.subscribers.add(fn);
    fn(this.getEvents(), this.state);
    return () => {
      this.subscribers.delete(fn);
    };
  }

  private notify(): void {
    const snapshot = this.getEvents();
    for (const sub of this.subscribers) {
      sub(snapshot, this.state);
    }
  }

  public async fetchRecent(tenantId?: string): Promise<{ events: LiveEventEnvelope[]; live: boolean }> {
    const ctx = getPrivacyOsTenantContext();
    const targetTenant = tenantId || ctx.tenantId || this.activeTenantId;
    if (targetTenant !== this.activeTenantId) {
      this.activeTenantId = targetTenant;
      this.events = [];
      this.seenIds.clear();
      this.lastSequenceId = 0;
    }

    const baseUrl = VITE_API_BASE.replace(/\/api\/?$/, '');
    const url = `${baseUrl}/api/v1/events/recent?since_sequence_id=${this.lastSequenceId}&limit=50`;
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': targetTenant,
          'X-User-ID': ctx.userId,
          Authorization: `Bearer ${ctx.bearerToken}`,
        },
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const json = (await res.json()) as { events?: LiveEventEnvelope[] };
      const incoming = json.events || [];
      this.ingestEvents(incoming, 'live');
      return { events: this.getEvents(), live: true };
    } catch {
      const fallbackState: LiveConnectionState = this.events.length > 0 ? 'stale' : 'offline';
      this.state = fallbackState;
      this.notify();
      return { events: this.getEvents(), live: false };
    }
  }

  public async publishEvent(input: {
    event_id?: string;
    event_type: LiveEventType;
    title: string;
    summary: string;
    severity?: 'info' | 'success' | 'warning' | 'critical';
    entity_type?: string;
    entity_id?: string;
    target_section?: string;
    requires_human_review?: boolean;
    provenance_status?: 'verified' | 'pending_review' | 'operational';
    payload?: Record<string, unknown>;
  }): Promise<{ event: LiveEventEnvelope; live: boolean }> {
    const ctx = getPrivacyOsTenantContext();
    const baseUrl = VITE_API_BASE.replace(/\/api\/?$/, '');
    const url = `${baseUrl}/api/v1/events/publish`;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-ID': ctx.tenantId,
          'X-User-ID': ctx.userId,
          Authorization: `Bearer ${ctx.bearerToken}`,
        },
        body: JSON.stringify(input),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = (await res.json()) as { event: LiveEventEnvelope };
      this.ingestEvents([data.event], 'live');
      return { event: data.event, live: true };
    } catch {
      const localEvent: LiveEventEnvelope = {
        event_id: input.event_id || `evt-local-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        sequence_id: this.lastSequenceId + 1,
        tenant_id: ctx.tenantId,
        event_type: input.event_type,
        title: input.title,
        summary: input.summary,
        severity: input.severity || 'info',
        actor_id: ctx.userId,
        actor_role: 'USER',
        entity_type: input.entity_type || null,
        entity_id: input.entity_id || null,
        target_section: input.target_section || null,
        requires_human_review: Boolean(input.requires_human_review),
        provenance_status: input.provenance_status || 'operational',
        created_at: new Date().toISOString(),
        payload: input.payload || {},
      };
      this.ingestEvents([localEvent], this.state === 'live' ? 'live' : 'offline');
      return { event: localEvent, live: false };
    }
  }

  public async connect(tenantId?: string): Promise<void> {
    const ctx = getPrivacyOsTenantContext();
    this.activeTenantId = tenantId || ctx.tenantId || this.activeTenantId;
    this.isPaused = false;

    const recent = await this.fetchRecent(this.activeTenantId);
    if (!recent.live || typeof EventSource === 'undefined') {
      return;
    }

    this.disconnectStreamOnly();
    const baseUrl = VITE_API_BASE.replace(/\/api\/?$/, '');
    const streamUrl = `${baseUrl}/api/v1/events/stream?tenant_id=${encodeURIComponent(
      this.activeTenantId
    )}&last_event_id=${this.lastSequenceId}`;

    try {
      const es = new EventSource(streamUrl);
      this.eventSource = es;

      es.onopen = () => {
        this.state = 'live';
        this.notify();
      };

      const handler = (msg: MessageEvent) => {
        try {
          const parsed = JSON.parse(msg.data) as LiveEventEnvelope;
          this.ingestEvents([parsed], 'live');
        } catch {
          // ignore malformed frame
        }
      };

      es.onmessage = handler;
      for (const evtType of ALL_GOVERNED_EVENT_TYPES) {
        es.addEventListener(evtType, handler as EventListener);
      }

      es.onerror = () => {
        this.disconnectStreamOnly();
        this.state = this.events.length > 0 ? 'stale' : 'offline';
        this.notify();
        if (!this.isPaused) {
          this.scheduleReconnect();
        }
      };
    } catch {
      this.state = this.events.length > 0 ? 'stale' : 'offline';
      this.notify();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      if (!this.isPaused) {
        void this.connect(this.activeTenantId);
      }
    }, 5000);
  }

  public pause(): void {
    this.isPaused = true;
    this.disconnectStreamOnly();
  }

  public resume(): void {
    if (!this.isPaused) return;
    this.isPaused = false;
    void this.connect(this.activeTenantId);
  }

  private disconnectStreamOnly(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  public disconnect(): void {
    this.isPaused = true;
    this.disconnectStreamOnly();
  }
}

export const liveEventClient = new LiveEventClient();
