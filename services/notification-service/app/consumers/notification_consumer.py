"""
Kafka consumer for notification events.
Processes notification events from the notification-queue topic.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.kafka import KafkaConsumer, EventType
from app.core.config import settings
from app.core.logging import get_logger
from app.services.email_service import send_email

logger = get_logger(__name__)


class NotificationConsumer:
    """
    Kafka consumer for processing notification events.
    Listens to notification-queue and sends emails based on events.
    """
    
    def __init__(self):
        """Initialize the notification consumer."""
        self.consumer = None
        self.running = False
    
    async def start(self):
        """Start the Kafka consumer."""
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP_ID,
                topics=[settings.KAFKA_NOTIFICATION_TOPIC],
                client_id=f"{settings.APP_NAME}-consumer",
                auto_offset_reset="earliest",
                enable_auto_commit=False,  # Manual commit for reliability
                max_poll_records=100,
            )
            
            await self.consumer.start()
            logger.info(
                f"Notification consumer started: "
                f"topic={settings.KAFKA_NOTIFICATION_TOPIC}, "
                f"group={settings.KAFKA_CONSUMER_GROUP_ID}"
            )
            
            # Start consuming in background
            self.running = True
            asyncio.create_task(self._consume_loop())
            
        except Exception as e:
            logger.error(f"Failed to start notification consumer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka consumer."""
        try:
            self.running = False
            if self.consumer:
                await self.consumer.stop()
                logger.info("Notification consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping notification consumer: {e}")
    
    async def _consume_loop(self):
        """Main consumption loop."""
        try:
            await self.consumer.consume(
                handler=self._handle_notification_event,
                dlq_handler=self._handle_failed_event,
            )
        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
            # Restart consumer after error
            if self.running:
                logger.info("Restarting consumer in 5 seconds...")
                await asyncio.sleep(5)
                await self._consume_loop()
    
    async def _handle_notification_event(self, event: dict):
        """
        Handle a notification event from Kafka.
        
        Args:
            event: Notification event dictionary
        """
        try:
            event_type = event.get("event_type")
            event_id = event.get("event_id")
            data = event.get("data", {})
            
            logger.info(
                f"Processing notification event: "
                f"event_id={event_id}, "
                f"event_type={event_type}"
            )
            
            # Extract notification data
            recipient_email = data.get("recipient_email")
            subject = data.get("subject")
            template_name = data.get("template_name")
            template_data = data.get("template_data", {})
            
            if not recipient_email or not subject or not template_name:
                logger.error(
                    f"Invalid notification event: missing required fields, "
                    f"event_id={event_id}"
                )
                return
            
            # Send email using existing email service
            success = await send_email(
                to_email=recipient_email,
                subject=subject,
                template_name=template_name,
                template_data=template_data,
            )
            
            if success:
                logger.info(
                    f"Notification sent successfully: "
                    f"event_id={event_id}, "
                    f"recipient={recipient_email}"
                )
            else:
                logger.error(
                    f"Failed to send notification: "
                    f"event_id={event_id}, "
                    f"recipient={recipient_email}"
                )
                # This will trigger DLQ handler
                raise Exception("Email sending failed")
        
        except Exception as e:
            logger.error(
                f"Error handling notification event: {e}, "
                f"event_id={event.get('event_id')}"
            )
            raise
    
    async def _handle_failed_event(self, event: dict, error: Exception):
        """
        Handle failed notification events by sending to DLQ.
        
        Args:
            event: Failed notification event
            error: Exception that caused the failure
        """
        try:
            from shared.kafka import KafkaProducer
            from datetime import datetime
            
            logger.warning(
                f"Sending failed notification to DLQ: "
                f"event_id={event.get('event_id')}, "
                f"error={str(error)}"
            )
            
            # Send to DLQ
            dlq_producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                client_id=f"{settings.APP_NAME}-dlq-producer",
            )
            await dlq_producer.start()
            
            await dlq_producer.send_raw(
                topic="notification-dlq",
                value={
                    "original_event": event,
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "timestamp": datetime.utcnow().isoformat(),
                    "service": settings.APP_NAME,
                },
            )
            
            await dlq_producer.stop()
            
            logger.info(f"Event sent to DLQ: event_id={event.get('event_id')}")
        
        except Exception as dlq_error:
            logger.error(f"Failed to send event to DLQ: {dlq_error}")


# Global consumer instance
_consumer_instance: NotificationConsumer = None


async def start_consumer():
    """Start the global notification consumer."""
    global _consumer_instance
    
    if _consumer_instance is None:
        _consumer_instance = NotificationConsumer()
        await _consumer_instance.start()
    
    return _consumer_instance


async def stop_consumer():
    """Stop the global notification consumer."""
    global _consumer_instance
    
    if _consumer_instance:
        await _consumer_instance.stop()
        _consumer_instance = None
