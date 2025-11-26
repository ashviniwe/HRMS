"""
Shared Kafka producer for HRMS microservices.
Provides a reusable async Kafka producer with error handling and retry logic.
"""

import json
import logging
from typing import Optional, Dict, Any
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from .schemas import BaseEvent

logger = logging.getLogger(__name__)


class KafkaProducer:
    """
    Async Kafka producer wrapper with error handling and retry logic.
    
    Usage:
        producer = KafkaProducer(bootstrap_servers="kafka:9092")
        await producer.start()
        await producer.send_event("notification-queue", event)
        await producer.stop()
    """
    
    def __init__(
        self,
        bootstrap_servers: str,
        client_id: Optional[str] = None,
        acks: str = "1",  # 0=none, 1=leader, all=all replicas
        retries: int = 3,
        compression_type: str = "lz4",
        max_request_size: int = 1048576,  # 1MB
    ):
        """
        Initialize Kafka producer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers (comma-separated)
            client_id: Client identifier for the producer
            acks: Number of acknowledgments the producer requires
            retries: Number of retries on transient errors
            compression_type: Compression algorithm (none, gzip, snappy, lz4, zstd)
            max_request_size: Maximum size of a request in bytes
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id or "hrms-producer"
        self.acks = acks
        self.retries = retries
        self.compression_type = compression_type
        self.max_request_size = max_request_size
        self._producer: Optional[AIOKafkaProducer] = None
        self._started = False
    
    async def start(self):
        """Start the Kafka producer."""
        if self._started:
            logger.warning("Producer already started")
            return
        
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                acks=self.acks,
                retries=self.retries,
                compression_type=self.compression_type,
                max_request_size=self.max_request_size,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            self._started = True
            logger.info(
                f"Kafka producer started: {self.bootstrap_servers} (client_id={self.client_id})"
            )
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka producer."""
        if not self._started or not self._producer:
            return
        
        try:
            await self._producer.stop()
            self._started = False
            logger.info("Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}")
    
    async def send_event(
        self,
        topic: str,
        event: BaseEvent,
        key: Optional[str] = None,
        partition: Optional[int] = None,
    ) -> bool:
        """
        Send an event to a Kafka topic.
        
        Args:
            topic: Kafka topic name
            event: Event object (must inherit from BaseEvent)
            key: Optional message key for partitioning
            partition: Optional specific partition to send to
        
        Returns:
            True if successful, False otherwise
        """
        if not self._started or not self._producer:
            logger.error("Producer not started. Call start() first.")
            return False
        
        try:
            # Convert Pydantic model to dict
            event_dict = event.model_dump(mode="json")
            
            # Send to Kafka
            future = await self._producer.send(
                topic=topic,
                value=event_dict,
                key=key,
                partition=partition,
            )
            
            # Wait for acknowledgment
            record_metadata = await future
            
            logger.info(
                f"Event sent successfully: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}, "
                f"event_id={event.event_id}, "
                f"event_type={event.event_type}"
            )
            return True
            
        except KafkaError as e:
            logger.error(
                f"Kafka error sending event: {e}, "
                f"event_id={event.event_id}, "
                f"event_type={event.event_type}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error sending event: {e}, "
                f"event_id={event.event_id}, "
                f"event_type={event.event_type}"
            )
            return False
    
    async def send_raw(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        partition: Optional[int] = None,
    ) -> bool:
        """
        Send a raw dictionary to a Kafka topic (without event schema validation).
        
        Args:
            topic: Kafka topic name
            value: Dictionary to send
            key: Optional message key for partitioning
            partition: Optional specific partition to send to
        
        Returns:
            True if successful, False otherwise
        """
        if not self._started or not self._producer:
            logger.error("Producer not started. Call start() first.")
            return False
        
        try:
            future = await self._producer.send(
                topic=topic,
                value=value,
                key=key,
                partition=partition,
            )
            
            record_metadata = await future
            
            logger.info(
                f"Raw message sent: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error sending raw message: {e}")
            return False
    
    async def flush(self):
        """Flush pending messages."""
        if self._started and self._producer:
            await self._producer.flush()
    
    @property
    def is_started(self) -> bool:
        """Check if producer is started."""
        return self._started


# Singleton producer instance (optional)
_producer_instance: Optional[KafkaProducer] = None


async def get_producer(bootstrap_servers: str, client_id: str) -> KafkaProducer:
    """
    Get or create a singleton Kafka producer instance.
    
    Args:
        bootstrap_servers: Kafka bootstrap servers
        client_id: Client identifier
    
    Returns:
        KafkaProducer instance
    """
    global _producer_instance
    
    if _producer_instance is None:
        _producer_instance = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
        )
        await _producer_instance.start()
    
    return _producer_instance


async def close_producer():
    """Close the singleton producer instance."""
    global _producer_instance
    
    if _producer_instance:
        await _producer_instance.stop()
        _producer_instance = None
