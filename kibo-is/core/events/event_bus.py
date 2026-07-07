import asyncio
from abc import ABC, abstractmethod
from typing import Callable, List, Type, Any
from core.events.domain_events import DomainEvent

class EventBus(ABC):
    """Abstract event bus interface"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to the event stream"""
        pass
    
    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Any], None]
    ) -> None:
        """Subscribe to events of a specific type"""
        pass
    
    @abstractmethod
    async def process_events(self) -> None:
        """Main event loop - continuously process events"""
        pass

# In-memory event bus (for testing and local runs)
class InMemoryEventBus(EventBus):
    def __init__(self):
        self.events: List[DomainEvent] = []
        self.handlers: dict[str, List[Callable]] = {}
    
    async def publish(self, event: DomainEvent) -> None:
        self.events.append(event)
        
        event_type = event.event_type or event.__class__.__name__
        handlers = self.handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"[InMemoryEventBus] Error in handler for {event_type}: {e}")
    
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Any], None]
    ) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def process_events(self) -> None:
        # In-memory bus executes publish synchronously, process_events is just a sleep loop
        while True:
            await asyncio.sleep(3600)
