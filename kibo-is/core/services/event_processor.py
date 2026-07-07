import asyncio
from core.events.event_bus import EventBus
from core.handlers.assessment_handlers import register_assessment_handlers
from core.handlers.risk_handlers import register_risk_handlers

class EventProcessor:
    def __init__(self, event_bus: EventBus, db_session_factory):
        self.event_bus = event_bus
        self.db_session_factory = db_session_factory
        self._register_handlers()
        
    def _register_handlers(self):
        """Register all event handlers"""
        register_assessment_handlers(self.event_bus, self.db_session_factory)
        register_risk_handlers(self.event_bus, self.db_session_factory)
        
    async def start(self):
        """Start the event processing loop"""
        print("[EventProcessor] Event processor started")
        await self.event_bus.process_events()
