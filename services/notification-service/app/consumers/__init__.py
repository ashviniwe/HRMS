"""Consumers package for Kafka event processing."""

from .notification_consumer import start_consumer, stop_consumer

__all__ = ["start_consumer", "stop_consumer"]
