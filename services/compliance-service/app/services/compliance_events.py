"""
Compliance event publishing utilities.
Handles async Kafka event publishing for compliance-related events such as violations, alerts, and check completions.
"""

from typing import Optional
from datetime import datetime
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

async def publish_compliance_event(
    event_type_str: str,
    compliance_id: int,
    employee_id: Optional[int] = None,
    description: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> bool:
    """Publish a compliance event to Kafka.

    Args:
        event_type_str: Event type string (e.g., "violation", "alert", "check_completed").
        compliance_id: Identifier of the compliance record.
        employee_id: Optional employee identifier related to the event.
        description: Optional human‑readable description.
        timestamp: Optional timestamp; defaults to ``datetime.utcnow()``.

    Returns:
        ``True`` if the event was successfully sent, ``False`` otherwise.
    """
    if not settings.KAFKA_ENABLE_PRODUCER:
        logger.debug("Kafka producer disabled (KAFKA_ENABLE_PRODUCER=False), skipping compliance event")
        return False

    try:
        # Dynamically import shared kafka to avoid circular imports
        from shared.kafka import get_producer, create_compliance_event, EventType

        # Map string to EventType enum – extend as needed
        event_type_map = {
            "violation": EventType.COMPLIANCE_VIOLATION,
            "alert": EventType.COMPLIANCE_ALERT,
            "check_completed": EventType.COMPLIANCE_CHECK_COMPLETED,
        }
        event_type = event_type_map.get(event_type_str)
        if not event_type:
            logger.warning(f"Unknown compliance event type: {event_type_str}")
            return False

        producer = await get_producer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID,
        )
        if not producer or not producer.is_started:
            logger.warning("Kafka producer not started, skipping compliance event")
            return False

        # Build the event payload using the shared factory
        event = create_compliance_event(
            source_service=settings.APP_NAME,
            event_type=event_type,
            compliance_id=compliance_id,
            employee_id=employee_id,
            description=description,
            timestamp=timestamp or datetime.utcnow(),
        )
        success = await producer.send_event(settings.KAFKA_COMPLIANCE_TOPIC, event)
        if success:
            logger.info(f"Compliance event sent via Kafka: {event_type_str} for id {compliance_id}")
        else:
            logger.warning(f"Failed to send compliance event via Kafka: {event_type_str} for id {compliance_id}")
        return success
    except Exception as e:
        logger.error(f"Error publishing compliance event: {e}")
        return False
