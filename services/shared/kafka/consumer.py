"""
Shared Kafka consumer for HRMS microservices.
Provides a reusable async Kafka consumer with error handling and dead letter queue support.
"""

import json
import logging
from typing import Optional, Callable, Awaitable, Dict, Any
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """
    Async Kafka consumer wrapper with error handling and DLQ support.
    
    Usage:
        async def handle_message(message):
            print(f"Received: {message}")
        
        consumer = KafkaConsumer(
            bootstrap_servers="kafka:9092",
            group_id="notification-service-group",
            topics=["notification-queue"]
        )
        await consumer.start()
        await consumer.consume(handle_message)
    """
    
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topics: list[str],
        client_id: Optional[str] = None,
        auto_offset_reset: str = "earliest",
        enable_auto_commit: bool = False,
        max_poll_records: int = 100,
        session_timeout_ms: int = 30000,
        heartbeat_interval_ms: int = 10000,
    ):
        """
        Initialize Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers (comma-separated)
            group_id: Consumer group ID
            topics: List of topics to subscribe to
            client_id: Client identifier for the consumer
            auto_offset_reset: Where to start reading (earliest, latest)
            enable_auto_commit: Whether to auto-commit offsets
            max_poll_records: Maximum records to fetch in one poll
            session_timeout_ms: Session timeout in milliseconds
            heartbeat_interval_ms: Heartbeat interval in milliseconds
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.client_id = client_id or f"{group_id}-client"
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.max_poll_records = max_poll_records
        self.session_timeout_ms = session_timeout_ms
        self.heartbeat_interval_ms = heartbeat_interval_ms
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._started = False
        self._running = False
    
    async def start(self):
        """Start the Kafka consumer."""
        if self._started:
            logger.warning("Consumer already started")
            return
        
        try:
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                client_id=self.client_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=self.enable_auto_commit,
                max_poll_records=self.max_poll_records,
                session_timeout_ms=self.session_timeout_ms,
                heartbeat_interval_ms=self.heartbeat_interval_ms,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
            )
            await self._consumer.start()
            self._started = True
            logger.info(
                f"Kafka consumer started: group_id={self.group_id}, "
                f"topics={self.topics}, "
                f"bootstrap_servers={self.bootstrap_servers}"
            )
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka consumer."""
        if not self._started or not self._consumer:
            return
        
        try:
            self._running = False
            await self._consumer.stop()
            self._started = False
            logger.info("Kafka consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping Kafka consumer: {e}")
    
    async def consume(
        self,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        dlq_handler: Optional[Callable[[Dict[str, Any], Exception], Awaitable[None]]] = None,
    ):
        """
        Start consuming messages and process them with the handler.
        
        Args:
            handler: Async function to process each message
            dlq_handler: Optional async function to handle failed messages (DLQ)
        """
        if not self._started or not self._consumer:
            logger.error("Consumer not started. Call start() first.")
            return
        
        self._running = True
        logger.info(f"Starting to consume messages from {self.topics}")
        
        try:
            async for message in self._consumer:
                if not self._running:
                    break
                
                try:
                    logger.debug(
                        f"Received message: topic={message.topic}, "
                        f"partition={message.partition}, "
                        f"offset={message.offset}, "
                        f"key={message.key}"
                    )
                    
                    # Process the message
                    await handler(message.value)
                    
                    # Manually commit offset if auto-commit is disabled
                    if not self.enable_auto_commit:
                        await self._consumer.commit()
                    
                    logger.debug(
                        f"Message processed successfully: "
                        f"topic={message.topic}, offset={message.offset}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Error processing message: {e}, "
                        f"topic={message.topic}, "
                        f"partition={message.partition}, "
                        f"offset={message.offset}"
                    )
                    
                    # Send to DLQ if handler is provided
                    if dlq_handler:
                        try:
                            await dlq_handler(message.value, e)
                        except Exception as dlq_error:
                            logger.error(f"Error sending to DLQ: {dlq_error}")
                    
                    # Commit offset even on error to avoid reprocessing
                    if not self.enable_auto_commit:
                        await self._consumer.commit()
        
        except KafkaError as e:
            logger.error(f"Kafka error while consuming: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while consuming: {e}")
            raise
        finally:
            logger.info("Stopped consuming messages")
    
    async def consume_batch(
        self,
        handler: Callable[[list[Dict[str, Any]]], Awaitable[None]],
        batch_size: int = 100,
        dlq_handler: Optional[Callable[[list[Dict[str, Any]], Exception], Awaitable[None]]] = None,
    ):
        """
        Consume messages in batches for better performance.
        
        Args:
            handler: Async function to process a batch of messages
            batch_size: Number of messages to batch together
            dlq_handler: Optional async function to handle failed batches
        """
        if not self._started or not self._consumer:
            logger.error("Consumer not started. Call start() first.")
            return
        
        self._running = True
        logger.info(f"Starting batch consumption from {self.topics} (batch_size={batch_size})")
        
        batch = []
        
        try:
            async for message in self._consumer:
                if not self._running:
                    break
                
                batch.append(message.value)
                
                if len(batch) >= batch_size:
                    try:
                        logger.debug(f"Processing batch of {len(batch)} messages")
                        await handler(batch)
                        
                        if not self.enable_auto_commit:
                            await self._consumer.commit()
                        
                        logger.debug(f"Batch processed successfully: {len(batch)} messages")
                        batch = []
                        
                    except Exception as e:
                        logger.error(f"Error processing batch: {e}")
                        
                        if dlq_handler:
                            try:
                                await dlq_handler(batch, e)
                            except Exception as dlq_error:
                                logger.error(f"Error sending batch to DLQ: {dlq_error}")
                        
                        if not self.enable_auto_commit:
                            await self._consumer.commit()
                        
                        batch = []
            
            # Process remaining messages in batch
            if batch:
                try:
                    logger.debug(f"Processing final batch of {len(batch)} messages")
                    await handler(batch)
                    
                    if not self.enable_auto_commit:
                        await self._consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing final batch: {e}")
                    
                    if dlq_handler:
                        try:
                            await dlq_handler(batch, e)
                        except Exception as dlq_error:
                            logger.error(f"Error sending final batch to DLQ: {dlq_error}")
        
        except KafkaError as e:
            logger.error(f"Kafka error while batch consuming: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while batch consuming: {e}")
            raise
        finally:
            logger.info("Stopped batch consumption")
    
    @property
    def is_started(self) -> bool:
        """Check if consumer is started."""
        return self._started
    
    @property
    def is_running(self) -> bool:
        """Check if consumer is actively consuming."""
        return self._running
