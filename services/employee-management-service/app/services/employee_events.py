"""
Employee event publishing utilities.
Handles async Kafka event publishing for employee lifecycle events.
"""

from typing import Optional
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


async def publish_employee_event(
    event_type_str: str,
    employee_id: int,
    name: str,
    age: Optional[int] = None,
) -> bool:
    """
    Publish employee lifecycle event to Kafka.
    
    Tries Kafka first if enabled, logs appropriately if disabled or fails.
    This is a fire-and-forget operation that doesn't block the main request.
    
    Args:
        event_type_str: Event type string ('created', 'updated', 'deleted')
        employee_id: Employee ID
        name: Employee name
        age: Employee age (optional)
    
    Returns:
        True if published successfully, False otherwise
    """
    if not settings.KAFKA_ENABLE_PRODUCER:
        logger.debug("Kafka producer disabled (KAFKA_ENABLE_PRODUCER=False), skipping employee event")
        return False
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
        
        from shared.kafka import get_producer, create_employee_event, EventType
        
        # Map string to EventType
        event_type_map = {
            "created": EventType.EMPLOYEE_CREATED,
            "updated": EventType.EMPLOYEE_UPDATED,
            "deleted": EventType.EMPLOYEE_TERMINATED,
        }
        
        event_type = event_type_map.get(event_type_str)
        if not event_type:
            logger.warning(f"Unknown employee event type: {event_type_str}")
            return False
        
        producer = await get_producer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID
        )
        
        if not producer or not producer.is_started:
            logger.warning("Kafka producer not started, skipping employee event")
            return False
        
        # Parse name into first/last (simple split for now)
        name_parts = name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        event = create_employee_event(
            source_service=settings.APP_NAME,
            event_type=event_type,
            employee_id=employee_id,
            email=f"employee{employee_id}@company.com",  # Placeholder
            first_name=first_name,
            last_name=last_name,
            status="active" if event_type_str != "deleted" else "terminated",
        )
        
        success = await producer.send_event(settings.KAFKA_EMPLOYEE_TOPIC, event)
        if success:
            logger.info(f"Employee event sent via Kafka: {event_type_str} for employee {employee_id}")
            return True
        else:
            logger.warning(f"Failed to send employee event via Kafka: {event_type_str} for employee {employee_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error publishing employee event: {e}")
        return False
