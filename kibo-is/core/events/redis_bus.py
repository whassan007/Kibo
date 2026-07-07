import json
import asyncio
from datetime import datetime
from typing import Callable, List, Any
from core.events.domain_events import DomainEvent
from core.events.event_bus import EventBus

class RedisEventBus(EventBus):
    def __init__(self, redis_client, stream_name: str = 'compliance_events'):
        self.redis = redis_client
        self.stream_name = stream_name
        self.handlers: dict[str, List[Callable]] = {}
        self.consumer_group = 'event_processors'
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish event to Redis Stream"""
        event_data = {
            'event_id': event.event_id,
            'event_type': event.event_type,
            'tenant_id': event.tenant_id,
            'aggregate_id': str(event.aggregate_id) if event.aggregate_id else "",
            'aggregate_type': event.aggregate_type,
            'timestamp': event.timestamp.isoformat(),
            'user_id': event.user_id if event.user_id else "",
            'payload': json.dumps(event.__dict__, default=str)
        }
        
        # Add to Redis Stream
        await self.redis.xadd(
            self.stream_name,
            event_data,
            maxlen=1000000  # Keep last 1M events
        )
        
        # Also publish to pub/sub for real-time subscribers
        await self.redis.publish(
            f'events:{event.tenant_id}',
            json.dumps(event_data)
        )
    
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Any], None]
    ) -> None:
        """Subscribe to event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def process_events(self) -> None:
        """Main event loop - process events from stream"""
        # Create consumer group if not exists
        try:
            await self.redis.xgroup_create(
                self.stream_name,
                self.consumer_group,
                id='0',
                mkstream=True
            )
        except Exception:
            pass  # Group already exists
        
        while True:
            try:
                # Read events from stream
                events = await self.redis.xreadgroup(
                    self.consumer_group,
                    'consumer_1',
                    {self.stream_name: '>'},
                    count=10,
                    block=1000  # 1 second timeout
                )
                
                if not events:
                    await asyncio.sleep(0.1)
                    continue
                    
                for stream, messages in events:
                    for message_id, data in messages:
                        try:
                            # Parse data
                            decoded_data = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}
                            event_type = decoded_data.get('event_type')
                            payload_str = decoded_data.get('payload')
                            payload = json.loads(payload_str) if payload_str else decoded_data
                            
                            # Call handlers for this event type
                            handlers = self.handlers.get(event_type, [])
                            for handler in handlers:
                                await handler(payload)
                            
                            # Acknowledge message
                            await self.redis.xack(
                                self.stream_name,
                                self.consumer_group,
                                message_id
                            )
                        except Exception as e:
                            print(f"[RedisEventBus] Error processing event: {e}")
                            # Move to dead-letter queue
                            try:
                                error_data = {
                                    'error': str(e),
                                    'message_id': str(message_id),
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                                await self.redis.xadd(
                                    f'{self.stream_name}:dlq',
                                    error_data
                                )
                            except:
                                pass
            except Exception as e:
                print(f"[RedisEventBus] Stream read error: {e}")
                await asyncio.sleep(1)
