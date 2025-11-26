# Quick Reference: Kafka Architecture

## Architecture Diagram (Text-based)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Frontend (React)                                   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API Gateway                                        │
└─────┬──────┬──────┬──────┬──────┬──────┬──────────────────────────────────┘
      │      │      │      │      │      │
      │      │      │      │      │      │
      ▼      ▼      ▼      ▼      ▼      ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  User   │ │Employee │ │  Leave  │ │Attendan │ │Complian │ │  Audit  │
│  Mgmt   │ │  Mgmt   │ │  Mgmt   │ │   ce    │ │   ce    │ │ Service │
│ Service │ │ Service │ │ Service │ │ Service │ │ Service │ │         │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────▲────┘
     │           │           │           │           │           │
     │ Sync      │ Sync      │ Sync      │ Sync      │           │
     │ (HTTP)    │ (HTTP)    │ (HTTP)    │ (HTTP)    │           │
     ▼           ▼           ▼           ▼           │           │
┌─────────────────────────────────────────────────┐  │           │
│         Employee Management Service             │  │           │
└─────────────────────────────────────────────────┘  │           │
                                                      │           │
     │           │           │           │           │           │
     │ Async     │ Async     │ Async     │ Async     │ Async     │
     │ (Kafka)   │ (Kafka)   │ (Kafka)   │ (Kafka)   │ (Kafka)   │
     ▼           ▼           ▼           ▼           ▼           │
┌─────────────────────────────────────────────────────────────────┐
│                    Kafka Cluster (3 Brokers)                    │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │ notification-queue   │  │   audit-queue        │            │
│  │ - 3 partitions       │  │ - 5 partitions       │            │
│  │ - 2 replicas         │  │ - 3 replicas         │            │
│  │ - 7 days retention   │  │ - 30 days retention  │            │
│  └──────────┬───────────┘  └──────────┬───────────┘            │
└─────────────┼──────────────────────────┼─────────────────────────┘
              │                          │
              ▼                          ▼
     ┌─────────────────┐        ┌─────────────────┐
     │  Notification   │        │  Audit Service  │
     │    Service      │        │   (Consumer)    │
     │   (Consumer)    │        └─────────────────┘
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  SMTP Server    │
     │  (Email Send)   │
     └─────────────────┘
```

## Communication Patterns

### 🟢 Synchronous (HTTP) - Keep As-Is

**Pattern**: Request → Response (blocking)

**Use Cases**:
1. **User Management → Employee Service**
   - Creating employee record when user is created
   - Updating employee status
   - **Why sync?** Need immediate confirmation of employee creation

2. **User Management → Compliance Service**
   - Policy validation before user deletion
   - Data retention checks
   - **Why sync?** Need immediate policy decision

3. **Leave/Attendance → Employee Service**
   - Verify employee exists before creating leave/attendance
   - **Why sync?** Need immediate validation

**Code Example**:
```python
# Keep this pattern
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{EMPLOYEE_SERVICE_URL}/api/v1/employees",
        json=employee_data
    )
    if response.status_code == 201:
        return response.json()
```

### 🔴 Asynchronous (Kafka) - Migrate to This

**Pattern**: Publish → Forget (non-blocking)

**Use Cases**:
1. **All Services → Notification Service**
   - Send welcome emails
   - Send approval notifications
   - Send alerts
   - **Why async?** Don't block main operation if email fails

2. **All Services → Audit Service**
   - Log user actions
   - Log employee changes
   - Log compliance checks
   - **Why async?** Audit logging shouldn't block operations

**Code Example**:
```python
# Migrate to this pattern
await kafka_producer.send(
    topic="notification-queue",
    value={
        "event_type": "user.created",
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name
    }
)
# Don't wait for response, continue processing
```

## Event Schema Examples

### Notification Events

```json
{
  "event_id": "uuid-v4",
  "event_type": "user.created",
  "timestamp": "2025-11-25T18:00:00Z",
  "source_service": "user-management-service",
  "data": {
    "user_id": 123,
    "email": "john.doe@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "template": "welcome_email"
  }
}
```

```json
{
  "event_id": "uuid-v4",
  "event_type": "leave.approved",
  "timestamp": "2025-11-25T18:00:00Z",
  "source_service": "leave-management-service",
  "data": {
    "leave_id": 456,
    "employee_id": 789,
    "employee_email": "jane.smith@company.com",
    "leave_type": "Annual Leave",
    "start_date": "2025-12-01",
    "end_date": "2025-12-05",
    "approved_by": "manager@company.com"
  }
}
```

### Audit Events

```json
{
  "event_id": "uuid-v4",
  "event_type": "audit.user.create",
  "timestamp": "2025-11-25T18:00:00Z",
  "source_service": "user-management-service",
  "data": {
    "user_id": 123,
    "action": "CREATE",
    "resource_type": "user",
    "resource_id": 123,
    "actor_id": 1,
    "actor_email": "admin@company.com",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "changes": {
      "email": "john.doe@company.com",
      "role": "employee"
    }
  }
}
```

## Kafka Topic Configuration

### notification-queue

```yaml
Topic: notification-queue
Partitions: 3
Replication Factor: 2
Retention: 7 days (604800000 ms)
Compression: lz4
Min In-Sync Replicas: 1

# Partition Strategy: Hash by user_id/employee_id
# This ensures all events for same user go to same partition (ordering)
```

### audit-queue

```yaml
Topic: audit-queue
Partitions: 5
Replication Factor: 3
Retention: 30 days (2592000000 ms)
Compression: lz4
Min In-Sync Replicas: 2

# Partition Strategy: Hash by resource_id
# This ensures all audit events for same resource are ordered
```

## Consumer Groups

```yaml
# Notification Service Consumer Group
Group ID: notification-service-group
Topics: [notification-queue]
Auto Offset Reset: earliest
Enable Auto Commit: false  # Manual commit after processing
Max Poll Records: 100

# Audit Service Consumer Group
Group ID: audit-service-group
Topics: [audit-queue]
Auto Offset Reset: earliest
Enable Auto Commit: false  # Manual commit after batch insert
Max Poll Records: 500  # Batch processing
```

## Environment Variables

### All Producer Services

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_NOTIFICATION_TOPIC=notification-queue
KAFKA_AUDIT_TOPIC=audit-queue
KAFKA_PRODUCER_ACKS=1  # 0=none, 1=leader, all=all replicas
KAFKA_PRODUCER_RETRIES=3
KAFKA_PRODUCER_TIMEOUT_MS=30000
```

### Consumer Services

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CONSUMER_GROUP_ID=notification-service-group  # or audit-service-group
KAFKA_CONSUMER_TOPICS=notification-queue  # or audit-queue
KAFKA_CONSUMER_AUTO_OFFSET_RESET=earliest
KAFKA_CONSUMER_ENABLE_AUTO_COMMIT=false
KAFKA_CONSUMER_MAX_POLL_RECORDS=100
```

## Monitoring Metrics

### Producer Metrics
- `kafka_producer_record_send_total` - Total records sent
- `kafka_producer_record_error_total` - Total send errors
- `kafka_producer_record_retry_total` - Total retries
- `kafka_producer_request_latency_avg` - Average send latency

### Consumer Metrics
- `kafka_consumer_records_consumed_total` - Total records consumed
- `kafka_consumer_lag` - Consumer lag (critical!)
- `kafka_consumer_commit_latency_avg` - Average commit latency
- `kafka_consumer_fetch_latency_avg` - Average fetch latency

### Broker Metrics
- `kafka_server_broker_topic_metrics_messages_in_per_sec` - Incoming message rate
- `kafka_server_broker_topic_metrics_bytes_in_per_sec` - Incoming byte rate
- `kafka_controller_stats_leader_election_rate_and_time_ms` - Leader elections
- `kafka_server_replica_manager_under_replicated_partitions` - Under-replicated partitions

## Alerting Rules

```yaml
# Critical Alerts
- alert: KafkaConsumerLagHigh
  expr: kafka_consumer_lag > 1000
  for: 5m
  severity: critical
  
- alert: KafkaProducerErrorRate
  expr: rate(kafka_producer_record_error_total[5m]) > 0.01
  for: 5m
  severity: critical

- alert: KafkaBrokerDown
  expr: up{job="kafka"} == 0
  for: 1m
  severity: critical

# Warning Alerts
- alert: KafkaConsumerLagWarning
  expr: kafka_consumer_lag > 500
  for: 10m
  severity: warning

- alert: KafkaUnderReplicatedPartitions
  expr: kafka_server_replica_manager_under_replicated_partitions > 0
  for: 5m
  severity: warning
```

## Troubleshooting Guide

### Issue: Consumer Lag Increasing

**Symptoms**: `kafka_consumer_lag` metric increasing

**Causes**:
1. Consumer processing too slow
2. Too many messages being produced
3. Consumer crashed/restarted

**Solutions**:
```bash
# Check consumer group status
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group notification-service-group

# Increase consumer instances (scale deployment)
kubectl scale deployment notification-service --replicas=3

# Increase partition count (if needed)
kafka-topics.sh --bootstrap-server kafka:9092 \
  --alter --topic notification-queue --partitions 5
```

### Issue: Messages Not Being Consumed

**Symptoms**: Messages in topic but not processed

**Causes**:
1. Consumer not running
2. Consumer group offset reset issue
3. Deserialization errors

**Solutions**:
```bash
# Check if consumer is running
kubectl get pods -l app=notification-service

# Check consumer logs
kubectl logs -f deployment/notification-service

# Reset consumer offset (CAUTION: may reprocess messages)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group notification-service-group --reset-offsets \
  --to-earliest --topic notification-queue --execute
```

### Issue: Producer Send Failures

**Symptoms**: `kafka_producer_record_error_total` increasing

**Causes**:
1. Kafka broker unavailable
2. Network issues
3. Topic doesn't exist

**Solutions**:
```bash
# Check Kafka broker health
kubectl get pods -n hrms -l app=kafka

# Check topic exists
kafka-topics.sh --bootstrap-server kafka:9092 --list

# Check producer service logs
kubectl logs -f deployment/user-service | grep -i kafka
```

## GitOps Repository Structure

```
k8s-manifests/
├── kafka/
│   ├── 00-namespace.yaml              # Optional: separate kafka namespace
│   ├── 01-strimzi-operator.yaml       # Strimzi Kafka Operator
│   ├── 02-kafka-cluster.yaml          # Kafka cluster (3 brokers)
│   ├── 03-kafka-topics.yaml           # Topic definitions
│   ├── 04-kafka-monitoring.yaml       # ServiceMonitor for Prometheus
│   └── README.md                      # Operations guide
├── services/
│   ├── user-service.yaml              # Updated with Kafka env vars
│   ├── employee-service.yaml          # Updated with Kafka env vars
│   ├── leave-service.yaml             # Updated with Kafka env vars
│   ├── attendance-service.yaml        # Updated with Kafka env vars
│   ├── notification-service.yaml      # Updated with Kafka env vars
│   ├── audit-service.yaml             # Updated with Kafka env vars
│   └── compliance-service.yaml        # Updated with Kafka env vars
└── monitoring/
    ├── prometheus-rules.yaml          # Kafka alerting rules
    └── grafana-dashboards.yaml        # Kafka dashboards
```

## Decision Matrix: Sync vs Async

| Criteria | Sync (HTTP) | Async (Kafka) |
|----------|-------------|---------------|
| **Need immediate response** | ✅ Yes | ❌ No |
| **Fire-and-forget operation** | ❌ No | ✅ Yes |
| **Can tolerate delays** | ❌ No | ✅ Yes |
| **Critical for main flow** | ✅ Yes | ❌ No |
| **Audit/logging operation** | ❌ No | ✅ Yes |
| **Notification sending** | ❌ No | ✅ Yes |
| **Data validation** | ✅ Yes | ❌ No |
| **Policy enforcement** | ✅ Yes | ❌ No |
| **Event sourcing** | ❌ No | ✅ Yes |
| **Decoupling services** | ❌ No | ✅ Yes |

## Summary

### ✅ Keep Synchronous (HTTP)
- User Management → Employee Service (create/update)
- User Management → Compliance Service (policy validation)
- Leave/Attendance → Employee Service (employee verification)

### ❌ Make Asynchronous (Kafka)
- **All services** → Notification Service
- **All services** → Audit Service

### 📍 Kafka Provisioning Location
**`k8s-manifests/kafka/`** using **Strimzi Kafka Operator**

This is your GitOps repository for Kubernetes manifests, making it the perfect location for Kafka infrastructure as code.
