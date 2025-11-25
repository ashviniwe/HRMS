# Shared Kafka Library for HRMS

This directory contains shared Kafka utilities for all HRMS microservices.

## Structure

```
shared/kafka/
├── __init__.py          # Package exports
├── schemas.py           # Event schemas (Pydantic models)
├── producer.py          # Kafka producer wrapper
├── consumer.py          # Kafka consumer wrapper
└── README.md            # This file
```

## Installation

Add `aiokafka` to your service's `pyproject.toml`:

```toml
[tool.poetry.dependencies]
aiokafka = "^0.11.0"
pydantic = "^2.0.0"
```

Then install:

```bash
uv sync
```

## Usage

### Producer Example

```python
from shared.kafka import KafkaProducer, create_notification_event, EventType

# Initialize producer
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    client_id="user-service"
)
await producer.start()

# Create and send an event
event = create_notification_event(
    source_service="user-management-service",
    recipient_email="user@example.com",
    subject="Welcome to HRMS!",
    template_name="welcome_email",
    template_data={"name": "John Doe"},
    event_type=EventType.USER_CREATED
)

await producer.send_event("notification-queue", event)

# Clean up
await producer.stop()
```

### Consumer Example

```python
from shared.kafka import KafkaConsumer

# Define message handler
async def handle_notification(message: dict):
    print(f"Processing notification: {message}")
    # Your processing logic here

# Initialize consumer
consumer = KafkaConsumer(
    bootstrap_servers="kafka:9092",
    group_id="notification-service-group",
    topics=["notification-queue"]
)
await consumer.start()

# Start consuming
await consumer.consume(handle_notification)
```

### Batch Consumer Example

```python
async def handle_batch(messages: list[dict]):
    print(f"Processing {len(messages)} audit events")
    # Batch insert to database
    await db.bulk_insert(messages)

consumer = KafkaConsumer(
    bootstrap_servers="kafka:9092",
    group_id="audit-service-group",
    topics=["audit-queue"]
)
await consumer.start()
await consumer.consume_batch(handle_batch, batch_size=500)
```

## Event Types

All available event types:

### User Events
- `USER_CREATED`
- `USER_UPDATED`
- `USER_DELETED`
- `USER_SUSPENDED`
- `USER_ACTIVATED`
- `USER_PASSWORD_CHANGED`

### Employee Events
- `EMPLOYEE_CREATED`
- `EMPLOYEE_UPDATED`
- `EMPLOYEE_TERMINATED`
- `EMPLOYEE_STATUS_CHANGED`

### Leave Events
- `LEAVE_REQUESTED`
- `LEAVE_APPROVED`
- `LEAVE_REJECTED`
- `LEAVE_CANCELLED`
- `LEAVE_UPDATED`

### Attendance Events
- `ATTENDANCE_MARKED`
- `ATTENDANCE_UPDATED`
- `ATTENDANCE_DELETED`

### Compliance Events
- `COMPLIANCE_VIOLATION`
- `COMPLIANCE_ALERT`
- `COMPLIANCE_CHECK_COMPLETED`

### Audit Events
- `AUDIT_USER_ACTION`
- `AUDIT_EMPLOYEE_ACTION`
- `AUDIT_LEAVE_ACTION`
- `AUDIT_ATTENDANCE_ACTION`
- `AUDIT_COMPLIANCE_ACTION`

## Event Schemas

### NotificationEvent

```python
{
    "event_id": "uuid",
    "event_type": "user.created",
    "timestamp": "2025-11-25T18:00:00Z",
    "source_service": "user-management-service",
    "correlation_id": "optional-uuid",
    "data": {
        "recipient_email": "user@example.com",
        "recipient_name": "John Doe",
        "subject": "Welcome!",
        "template_name": "welcome_email",
        "template_data": {"key": "value"},
        "priority": "normal"
    }
}
```

### AuditEvent

```python
{
    "event_id": "uuid",
    "event_type": "audit.user.action",
    "timestamp": "2025-11-25T18:00:00Z",
    "source_service": "user-management-service",
    "data": {
        "user_id": 123,
        "action": "CREATE",
        "resource_type": "user",
        "resource_id": 456,
        "description": "Created new user",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "changes": {"email": "new@example.com"}
    }
}
```

## Configuration

### Environment Variables

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_NOTIFICATION_TOPIC=notification-queue
KAFKA_AUDIT_TOPIC=audit-queue

# Producer Configuration
KAFKA_PRODUCER_ACKS=1
KAFKA_PRODUCER_RETRIES=3
KAFKA_PRODUCER_COMPRESSION=lz4

# Consumer Configuration
KAFKA_CONSUMER_GROUP_ID=my-service-group
KAFKA_CONSUMER_AUTO_OFFSET_RESET=earliest
KAFKA_CONSUMER_MAX_POLL_RECORDS=100
```

## Integration with FastAPI

### Lifespan Management

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.kafka import KafkaProducer

producer: KafkaProducer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global producer
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        client_id=settings.APP_NAME
    )
    await producer.start()
    
    yield
    
    # Shutdown
    await producer.stop()

app = FastAPI(lifespan=lifespan)
```

### Using in Routes

```python
from fastapi import APIRouter
from shared.kafka import create_notification_event, EventType

router = APIRouter()

@router.post("/users")
async def create_user(user_data: UserCreate):
    # Create user in database
    user = await db.create_user(user_data)
    
    # Send notification event
    event = create_notification_event(
        source_service="user-management-service",
        recipient_email=user.email,
        subject="Welcome!",
        template_name="welcome_email",
        template_data={"name": user.first_name},
        event_type=EventType.USER_CREATED
    )
    
    await producer.send_event(
        topic=settings.KAFKA_NOTIFICATION_TOPIC,
        event=event
    )
    
    return user
```

## Error Handling

### Producer Error Handling

The producer automatically handles transient errors with retries. For permanent failures:

```python
success = await producer.send_event(topic, event)
if not success:
    logger.error(f"Failed to send event: {event.event_id}")
    # Fallback logic (e.g., HTTP call, store in DB for retry)
```

### Consumer Error Handling with DLQ

```python
from shared.kafka import KafkaProducer

# DLQ producer
dlq_producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    client_id="dlq-producer"
)
await dlq_producer.start()

async def dlq_handler(message: dict, error: Exception):
    """Send failed messages to dead letter queue."""
    logger.error(f"Sending to DLQ: {error}")
    await dlq_producer.send_raw(
        topic="notification-dlq",
        value={
            "original_message": message,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Use DLQ handler in consumer
await consumer.consume(handle_message, dlq_handler=dlq_handler)
```

## Testing

### Unit Tests

```python
import pytest
from shared.kafka import create_notification_event, EventType

def test_create_notification_event():
    event = create_notification_event(
        source_service="test-service",
        recipient_email="test@example.com",
        subject="Test",
        template_name="test_template",
        template_data={"key": "value"},
        event_type=EventType.USER_CREATED
    )
    
    assert event.event_type == EventType.USER_CREATED
    assert event.source_service == "test-service"
    assert event.data.recipient_email == "test@example.com"
```

### Integration Tests

Use `testcontainers` for integration testing with real Kafka:

```python
import pytest
from testcontainers.kafka import KafkaContainer
from shared.kafka import KafkaProducer, KafkaConsumer

@pytest.fixture
async def kafka_container():
    with KafkaContainer() as kafka:
        yield kafka.get_bootstrap_server()

@pytest.mark.asyncio
async def test_producer_consumer(kafka_container):
    # Test producer and consumer integration
    pass
```

## Best Practices

1. **Use Event Schemas**: Always use the provided Pydantic models for type safety
2. **Correlation IDs**: Use correlation IDs to track related events across services
3. **Idempotency**: Design consumers to be idempotent (handle duplicate messages)
4. **Error Handling**: Always implement DLQ handling for critical events
5. **Monitoring**: Log event IDs and types for debugging
6. **Partitioning**: Use message keys for ordered processing (e.g., user_id, employee_id)

## Troubleshooting

### Producer Not Sending Messages

```python
# Check if producer is started
if not producer.is_started:
    await producer.start()

# Enable debug logging
import logging
logging.getLogger("aiokafka").setLevel(logging.DEBUG)
```

### Consumer Not Receiving Messages

```python
# Check consumer group lag
# kubectl exec -it kafka-0 -n kafka -- kafka-consumer-groups.sh \
#   --bootstrap-server localhost:9092 \
#   --describe --group notification-service-group

# Reset consumer offset (CAUTION!)
# kubectl exec -it kafka-0 -n kafka -- kafka-consumer-groups.sh \
#   --bootstrap-server localhost:9092 \
#   --group notification-service-group \
#   --reset-offsets --to-earliest --topic notification-queue --execute
```

## Migration from HTTP

When migrating from HTTP to Kafka:

1. **Dual-Write Pattern**: Send to both Kafka and HTTP initially
2. **Monitor**: Watch Kafka success rate for 1-2 weeks
3. **Remove HTTP**: Once stable, remove HTTP fallback
4. **Rollback Plan**: Keep HTTP code commented for quick rollback

Example:

```python
# Send to Kafka
kafka_success = await producer.send_event(topic, event)

# Fallback to HTTP (temporary during migration)
if not kafka_success:
    logger.warning("Kafka failed, falling back to HTTP")
    await http_client.post(url, json=event.model_dump())
```

## Support

For issues or questions:
1. Check logs for error messages
2. Verify Kafka cluster is healthy
3. Review event schemas match expected format
4. Check consumer group lag
