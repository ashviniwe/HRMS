"""
Kafka consumer for audit events.
Processes audit events from the audit-queue topic with batch processing.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path to import shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.kafka import KafkaConsumer
from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import get_session
from app.models.employee import AuditLog

logger = get_logger(__name__)


class AuditConsumer:
    """
    Kafka consumer for processing audit events.
    Listens to audit-queue and stores audit logs in batch for better performance.
    """
    
    def __init__(self):
        """Initialize the audit consumer."""
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Start the Kafka consumer."""
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP_ID,
                topics=[settings.KAFKA_AUDIT_TOPIC],
                client_id=f"{settings.APP_NAME}-consumer",
                auto_offset_reset="earliest",
                enable_auto_commit=False,  # Manual commit for reliability
                max_poll_records=500,  # Higher for batch processing
            )
            
            await self.consumer.start()
            logger.info(
                f"Audit consumer started: "
                f"topic={settings.KAFKA_AUDIT_TOPIC}, "
                f"group={settings.KAFKA_CONSUMER_GROUP_ID}"
            )
            
            # Start consuming in background with batch processing
            self.running = True
            asyncio.create_task(self._consume_loop())
            
        except Exception as e:
            logger.error(f"Failed to start audit consumer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka consumer."""
        try:
            self.running = False
            if self.consumer:
                await self.consumer.stop()
                logger.info("Audit consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping audit consumer: {e}")
    
    async def _consume_loop(self):
        """Main consumption loop with batch processing."""
        try:
            await self.consumer.consume_batch(
                handler=self._handle_audit_batch,
                batch_size=settings.KAFKA_BATCH_SIZE,
                dlq_handler=self._handle_failed_batch,
            )
        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
            # Restart consumer after error
            if self.running:
                logger.info("Restarting consumer in 5 seconds...")
                await asyncio.sleep(5)
                await self._consume_loop()
    
    async def _handle_audit_batch(self, events: List[Dict[str, Any]]):
        """
        Handle a batch of audit events from Kafka.
        Performs bulk insert for better performance.
        
        Args:
            events: List of audit event dictionaries
        """
        if not events:
            return
        
        try:
            logger.info(f"Processing batch of {len(events)} audit events")
            
            # Convert events to AuditLog models
            audit_logs = []
            for event in events:
                try:
                    audit_log = self._event_to_audit_log(event)
                    if audit_log:
                        audit_logs.append(audit_log)
                except Exception as e:
                    logger.error(
                        f"Error converting event to audit log: {e}, "
                        f"event_id={event.get('event_id')}"
                    )
                    # Continue processing other events
            
            if not audit_logs:
                logger.warning("No valid audit logs in batch")
                return
            
            # Bulk insert to database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                session.add_all(audit_logs)
                session.commit()
                logger.info(
                    f"Successfully inserted {len(audit_logs)} audit logs "
                    f"(batch size: {len(events)})"
                )
            except Exception as db_error:
                session.rollback()
                logger.error(f"Database error during batch insert: {db_error}")
                raise
            finally:
                session.close()
        
        except Exception as e:
            logger.error(f"Error handling audit batch: {e}")
            raise
    
    def _event_to_audit_log(self, event: Dict[str, Any]) -> AuditLog:
        """
        Convert a Kafka event to an AuditLog model.
        
        Args:
            event: Audit event dictionary
        
        Returns:
            AuditLog model instance
        """
        try:
            data = event.get("data", {})
            
            # Create AuditLog instance
            audit_log = AuditLog(
                user_id=data.get("user_id"),
                action=data.get("action"),
                resource_type=data.get("resource_type"),
                resource_id=data.get("resource_id"),
                description=data.get("description"),
                ip_address=data.get("ip_address"),
                user_agent=data.get("user_agent"),
                old_value=data.get("old_value"),
                new_value=data.get("new_value"),
                timestamp=datetime.fromisoformat(event.get("timestamp").replace("Z", "+00:00")),
                event_id=event.get("event_id"),
                source_service=event.get("source_service"),
            )
            
            return audit_log
        
        except Exception as e:
            logger.error(
                f"Error creating AuditLog from event: {e}, "
                f"event_id={event.get('event_id')}"
            )
            raise
    
    async def _handle_failed_batch(self, events: List[Dict[str, Any]], error: Exception):
        """
        Handle failed audit event batches by sending to DLQ.
        
        Args:
            events: Failed audit events
            error: Exception that caused the failure
        """
        try:
            from shared.kafka import KafkaProducer
            
            logger.warning(
                f"Sending failed audit batch to DLQ: "
                f"batch_size={len(events)}, "
                f"error={str(error)}"
            )
            
            # Send to DLQ
            dlq_producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=f"{settings.APP_NAME}-dlq-producer",
            )
            await dlq_producer.start()
            
            # Send each event individually to DLQ
            for event in events:
                await dlq_producer.send_raw(
                    topic="audit-dlq",
                    value={
                        "original_event": event,
                        "error": str(error),
                        "error_type": type(error).__name__,
                        "timestamp": datetime.utcnow().isoformat(),
                        "service": settings.APP_NAME,
                    },
                )
            
            await dlq_producer.stop()
            
            logger.info(f"Batch of {len(events)} events sent to DLQ")
        
        except Exception as dlq_error:
            logger.error(f"Failed to send batch to DLQ: {dlq_error}")


# Global consumer instance
_consumer_instance: AuditConsumer = None


async def start_consumer():
    """Start the global audit consumer."""
    global _consumer_instance
    
    if _consumer_instance is None:
        _consumer_instance = AuditConsumer()
        await _consumer_instance.start()
    
    return _consumer_instance


async def stop_consumer():
    """Stop the global audit consumer."""
    global _consumer_instance
    
    if _consumer_instance:
        await _consumer_instance.stop()
        _consumer_instance = None
