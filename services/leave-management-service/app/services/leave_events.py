"""
Leave event publishing utilities.
Handles async Kafka event publishing for leave lifecycle events.
"""

from typing import Optional
from datetime import date
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


async def publish_leave_event(
    event_type_str: str,
    leave_id: int,
    employee_id: int,
    leave_type: str,
    start_date: date,
    end_date: date,
    status: str,
    reason: Optional[str] = None,
    approved_by: Optional[int] = None,
    rejection_reason: Optional[str] = None,
) -> bool:
    """
    Publish leave lifecycle event to Kafka.
    
    Tries Kafka first if enabled, logs appropriately if disabled or fails.
    This is a fire-and-forget operation that doesn't block the main request.
    
    Args:
        event_type_str: Event type string ('created', 'approved', 'rejected', 'cancelled')
        leave_id: Leave request ID
        employee_id: Employee ID
        leave_type: Type of leave
        start_date: Leave start date
        end_date: Leave end date
        status: Current status
        reason: Leave reason (optional)
        approved_by: Approver user ID (optional)
        rejection_reason: Rejection reason (optional)
    
    Returns:
        True if published successfully, False otherwise
    """
    if not settings.KAFKA_ENABLE_PRODUCER:
        logger.debug("Kafka producer disabled (KAFKA_ENABLE_PRODUCER=False), skipping leave event")
        return False
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
        
        from shared.kafka import get_producer, create_leave_event, EventType
        
        # Map string to EventType
        event_type_map = {
            "created": EventType.LEAVE_REQUESTED,
            "approved": EventType.LEAVE_APPROVED,
            "rejected": EventType.LEAVE_REJECTED,
            "cancelled": EventType.LEAVE_CANCELLED,
        }
        
        event_type = event_type_map.get(event_type_str)
        if not event_type:
            logger.warning(f"Unknown leave event type: {event_type_str}")
            return False
        
        producer = await get_producer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID
        )
        
        if not producer or not producer.is_started:
            logger.warning("Kafka producer not started, skipping leave event")
            return False
        
        # Convert dates to ISO format strings
        start_date_str = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
        end_date_str = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
        
        # Calculate days (simple calculation)
        days = (end_date - start_date).days + 1 if hasattr(start_date, '__sub__') else 0
        
        event = create_leave_event(
            source_service=settings.APP_NAME,
            event_type=event_type,
            leave_id=leave_id,
            employee_id=employee_id,
            employee_email=f"employee{employee_id}@company.com",  # Placeholder
            leave_type=leave_type,
            start_date=start_date_str,
            end_date=end_date_str,
            status=status,
            days=days,
            reason=reason,
            approved_by=str(approved_by) if approved_by else None,
            rejection_reason=rejection_reason,
        )
        
        success = await producer.send_event(settings.KAFKA_LEAVE_TOPIC, event)
        if success:
            logger.info(f"Leave event sent via Kafka: {event_type_str} for leave {leave_id}")
            return True
        else:
            logger.warning(f"Failed to send leave event via Kafka: {event_type_str} for leave {leave_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error publishing leave event: {e}")
        return False
