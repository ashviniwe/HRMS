"""
Attendance event publishing utilities.
Handles async Kafka event publishing for attendance tracking events.
"""

from typing import Optional
from datetime import date, datetime
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


async def publish_attendance_event(
    event_type_str: str,
    attendance_id: int,
    employee_id: int,
    attendance_date: date,
    status: str,
    check_in_time: Optional[datetime] = None,
    check_out_time: Optional[datetime] = None,
    hours_worked: Optional[float] = None,
    notes: Optional[str] = None,
) -> bool:
    """
    Publish attendance tracking event to Kafka.
    
    Tries Kafka first if enabled, logs appropriately if disabled or fails.
    This is a fire-and-forget operation that doesn't block the main request.
    
    Args:
        event_type_str: Event type string ('logged', 'updated')
        attendance_id: Attendance record ID
        employee_id: Employee ID
        attendance_date: Attendance date
        status: Attendance status
        check_in_time: Check-in time (optional)
        check_out_time: Check-out time (optional)
        hours_worked: Hours worked (optional)
        notes: Additional notes (optional)
    
    Returns:
        True if published successfully, False otherwise
    """
    if not settings.KAFKA_ENABLE_PRODUCER:
        logger.debug("Kafka producer disabled (KAFKA_ENABLE_PRODUCER=False), skipping attendance event")
        return False
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
        
        from shared.kafka import get_producer, create_attendance_event, EventType
        
        # Map string to EventType
        event_type_map = {
            "logged": EventType.ATTENDANCE_MARKED,
            "updated": EventType.ATTENDANCE_UPDATED,
        }
        
        event_type = event_type_map.get(event_type_str)
        if not event_type:
            logger.warning(f"Unknown attendance event type: {event_type_str}")
            return False
        
        producer = await get_producer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID
        )
        
        if not producer or not producer.is_started:
            logger.warning("Kafka producer not started, skipping attendance event")
            return False
        
        # Convert dates/times to ISO format strings
        date_str = attendance_date.isoformat() if hasattr(attendance_date, 'isoformat') else str(attendance_date)
        check_in_str = check_in_time.isoformat() if check_in_time and hasattr(check_in_time, 'isoformat') else None
        check_out_str = check_out_time.isoformat() if check_out_time and hasattr(check_out_time, 'isoformat') else None
        
        event = create_attendance_event(
            source_service=settings.APP_NAME,
            event_type=event_type,
            attendance_id=attendance_id,
            employee_id=employee_id,
            employee_email=f"employee{employee_id}@company.com",  # Placeholder
            date=date_str,
            status=status,
            check_in=check_in_str,
            check_out=check_out_str,
            hours_worked=hours_worked,
            notes=notes,
        )
        
        success = await producer.send_event(settings.KAFKA_ATTENDANCE_TOPIC, event)
        if success:
            logger.info(f"Attendance event sent via Kafka: {event_type_str} for attendance {attendance_id}")
            return True
        else:
            logger.warning(f"Failed to send attendance event via Kafka: {event_type_str} for attendance {attendance_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error publishing attendance event: {e}")
        return False
