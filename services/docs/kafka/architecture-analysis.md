# HRMS Kafka Architecture Analysis & Implementation Plan

## Executive Summary

This document analyzes the current HRMS microservices architecture and provides a detailed plan for implementing Kafka-based asynchronous communication patterns based on the provided architecture diagram.

## Current Architecture Analysis

### Services Inventory

1. **User Management Service** (Port 8007)
   - User/Identity Service in diagram
   - Manages authentication and user lifecycle
   
2. **Employee Management Service** (Port 8001)
   - Core employee data management
   
3. **Leave Management Service** (Port 8002)
   - Leave & Attendance Service in diagram
   - Manages leave requests and approvals
   
4. **Attendance Management Service** (Port 8003)
   - Part of Leave & Attendance Service in diagram
   - Tracks employee attendance
   
5. **Notification Service** (Port 8004)
   - Sends emails and notifications
   
6. **Audit Service** (Port 8005)
   - Centralized audit logging
   
7. **Compliance Service** (Port 8006)
   - GDPR compliance and data inventory

### Current Communication Patterns

#### Synchronous (HTTP/REST) Calls

All inter-service communication is currently **synchronous** using `httpx` library:

1. **User Management → Employee Service**
   - `POST /api/v1/employees` - Create employee record
   - `PUT /api/v1/employees/{id}` - Update employee status
   - `GET /api/v1/employees/{id}` - Get employee info

2. **User Management → Audit Service**
   - `POST /api/v1/audit-logs` - Log user actions

3. **User Management → Compliance Service**
   - `POST /api/v1/policies/validate` - Validate policies

4. **User Management → Notification Service**
   - `POST /api/v1/notifications/email` - Send emails (fire-and-forget)

5. **Leave Management → Employee Service**
   - `GET /api/v1/employees/{id}` - Verify employee exists

6. **Attendance Management → Employee Service**
   - `GET /api/v1/employees/{id}` - Verify employee exists
   - `GET /api/v1/employees/` - List employees

7. **Employee Service → Audit/Notification/Compliance**
   - Various synchronous calls

#### Issues with Current Architecture

1. **Tight Coupling**: Services are tightly coupled via synchronous HTTP calls
2. **Cascading Failures**: If Notification/Audit services are down, main operations may fail
3. **Performance Bottlenecks**: Synchronous calls increase latency
4. **No Event Sourcing**: No event-driven patterns for audit trail
5. **Scalability Issues**: Cannot independently scale event consumers

## Proposed Kafka Architecture

Based on the architecture diagram, we need to implement **two Kafka queues**:

### 1. Notification Queue

**Purpose**: Decouple notification sending from business operations

**Producers**:
- User Management Service
- Employee Management Service  
- Leave Management Service
- Attendance Management Service
- Compliance Service

**Consumers**:
- Notification Service

**Event Types**:
```json
{
  "event_type": "user.created",
  "event_type": "user.password_changed",
  "event_type": "user.suspended",
  "event_type": "user.deleted",
  "event_type": "employee.created",
  "event_type": "employee.updated",
  "event_type": "leave.requested",
  "event_type": "leave.approved",
  "event_type": "leave.rejected",
  "event_type": "attendance.marked",
  "event_type": "compliance.violation"
}
```

**Benefits**:
- Fire-and-forget pattern for notifications
- Notification service can be down without affecting core operations
- Retry mechanism for failed notifications
- Can add multiple notification channels (SMS, Slack, etc.) without changing producers

### 2. Audit Event Queue

**Purpose**: Centralized audit logging with event sourcing

**Producers**:
- User Management Service
- Employee Management Service
- Leave Management Service
- Attendance Management Service
- Compliance Service

**Consumers**:
- Audit Service

**Event Types**:
```json
{
  "event_type": "audit.user.create",
  "event_type": "audit.user.update",
  "event_type": "audit.user.delete",
  "event_type": "audit.employee.create",
  "event_type": "audit.employee.update",
  "event_type": "audit.leave.create",
  "event_type": "audit.leave.approve",
  "event_type": "audit.attendance.mark",
  "event_type": "audit.compliance.check"
}
```

**Benefits**:
- Non-blocking audit logging
- Complete event sourcing capability
- Can replay events for compliance
- Audit service failures don't block operations

## Services to Update

### High Priority (Async via Kafka)

#### 1. User Management Service
**Changes Required**:
- ✅ Keep sync: Employee Service calls (need immediate response for user creation flow)
- ❌ Make async: Audit logging → Kafka
- ❌ Make async: Notification sending → Kafka
- ⚠️ Keep sync: Compliance validation (need immediate response for policy checks)

**Kafka Integration**:
- Produce to `notification-queue` for user lifecycle events
- Produce to `audit-queue` for all user actions

#### 2. Employee Management Service
**Changes Required**:
- ❌ Make async: Audit logging → Kafka
- ❌ Make async: Notification sending → Kafka
- ⚠️ Keep sync: Compliance checks (when needed)

**Kafka Integration**:
- Produce to `notification-queue` for employee events
- Produce to `audit-queue` for employee CRUD operations

#### 3. Leave Management Service
**Changes Required**:
- ✅ Keep sync: Employee verification (need to validate employee exists)
- ❌ Make async: Audit logging → Kafka
- ❌ Make async: Notification sending → Kafka

**Kafka Integration**:
- Produce to `notification-queue` for leave approvals/rejections
- Produce to `audit-queue` for leave operations

#### 4. Attendance Management Service
**Changes Required**:
- ✅ Keep sync: Employee verification
- ❌ Make async: Audit logging → Kafka
- ❌ Make async: Notification sending → Kafka

**Kafka Integration**:
- Produce to `notification-queue` for attendance events
- Produce to `audit-queue` for attendance operations

#### 5. Compliance Service
**Changes Required**:
- ❌ Make async: Audit logging → Kafka
- ❌ Make async: Notification sending → Kafka (for compliance violations)

**Kafka Integration**:
- Produce to `notification-queue` for compliance alerts
- Produce to `audit-queue` for compliance checks

#### 6. Notification Service
**Changes Required**:
- Add Kafka consumer to listen to `notification-queue`
- Keep existing HTTP endpoints for backward compatibility
- Implement retry logic for failed notifications

**Kafka Integration**:
- Consume from `notification-queue`
- Process notification events asynchronously

#### 7. Audit Service
**Changes Required**:
- Add Kafka consumer to listen to `audit-queue`
- Keep existing HTTP endpoints for backward compatibility
- Implement batch processing for audit events

**Kafka Integration**:
- Consume from `audit-queue`
- Process audit events asynchronously

## Kafka Provisioning Strategy

### Option 1: Self-Managed Kafka in K8s (Recommended for GitOps)

**Location**: `/k8s-manifests/kafka/`

**Structure**:
```
k8s-manifests/
├── kafka/
│   ├── namespace.yaml
│   ├── zookeeper-statefulset.yaml
│   ├── zookeeper-service.yaml
│   ├── kafka-statefulset.yaml
│   ├── kafka-service.yaml
│   ├── kafka-topics.yaml
│   └── README.md
```

**Pros**:
- Full control over Kafka configuration
- No external dependencies
- Cost-effective
- GitOps-friendly

**Cons**:
- Need to manage Kafka operations
- Requires monitoring setup
- More complex initial setup

### Option 2: Helm Chart (Strimzi Kafka Operator)

**Location**: `/k8s-manifests/kafka/`

**Structure**:
```
k8s-manifests/
├── kafka/
│   ├── strimzi-operator.yaml
│   ├── kafka-cluster.yaml
│   ├── kafka-topics.yaml
│   └── README.md
```

**Pros**:
- Production-ready Kafka operator
- Easier management and upgrades
- Built-in monitoring
- GitOps-friendly

**Cons**:
- Additional operator overhead
- Learning curve for Strimzi CRDs

### Option 3: Managed Kafka (AWS MSK, Confluent Cloud)

**Location**: `/infra/terraform/kafka/` or `/ansible/kafka/`

**Pros**:
- Fully managed
- High availability out of the box
- Professional support

**Cons**:
- Additional cost
- Less control
- Vendor lock-in
- Not pure GitOps (infrastructure as code instead)

### Recommendation

**Use Option 2 (Strimzi Kafka Operator)** for the following reasons:

1. **GitOps Alignment**: Kafka cluster defined as Kubernetes CRDs in `k8s-manifests/`
2. **Production Ready**: Strimzi is CNCF sandbox project, battle-tested
3. **Ease of Management**: Operator handles upgrades, scaling, and monitoring
4. **Cost-Effective**: No managed service costs
5. **Flexibility**: Can migrate to managed service later if needed

## Implementation Phases

### Phase 1: Infrastructure Setup (Week 1)

1. **Add Strimzi Operator to k8s-manifests**
   - Create `/k8s-manifests/kafka/` directory
   - Add Strimzi operator manifests
   - Deploy Kafka cluster (3 brokers for HA)
   - Create topics: `notification-queue`, `audit-queue`

2. **Update CI/CD**
   - Add Kafka deployment to CI/CD pipeline
   - Configure health checks

### Phase 2: Notification Queue Implementation (Week 2)

1. **Update Notification Service** (Consumer)
   - Add `aiokafka` dependency
   - Implement Kafka consumer
   - Add event handlers for different notification types
   - Implement retry logic

2. **Update Producer Services**
   - User Management Service
   - Employee Management Service
   - Leave Management Service
   - Attendance Management Service
   - Compliance Service

3. **Testing**
   - Integration tests for notification flow
   - Load testing

### Phase 3: Audit Queue Implementation (Week 3)

1. **Update Audit Service** (Consumer)
   - Add `aiokafka` dependency
   - Implement Kafka consumer
   - Add batch processing
   - Implement event sourcing

2. **Update Producer Services**
   - Same services as Phase 2
   - Add audit event production

3. **Testing**
   - Integration tests for audit flow
   - Verify event sourcing

### Phase 4: Monitoring & Optimization (Week 4)

1. **Add Monitoring**
   - Kafka metrics (Prometheus + Grafana)
   - Consumer lag monitoring
   - Dead letter queue setup

2. **Performance Tuning**
   - Optimize batch sizes
   - Tune consumer groups
   - Configure retention policies

3. **Documentation**
   - Update architecture diagrams
   - Add runbooks for Kafka operations
   - Document event schemas

## Kafka Configuration

### Topics Configuration

```yaml
# notification-queue
partitions: 3
replication-factor: 2
retention.ms: 604800000  # 7 days
compression.type: lz4

# audit-queue
partitions: 5
replication-factor: 3
retention.ms: 2592000000  # 30 days
compression.type: lz4
```

### Consumer Groups

- `notification-service-group` → consumes from `notification-queue`
- `audit-service-group` → consumes from `audit-queue`

## Service Dependencies Update

### Python Dependencies to Add

All producer services need:
```toml
aiokafka = "^0.11.0"
```

Consumer services (Notification, Audit) need:
```toml
aiokafka = "^0.11.0"
```

### Environment Variables to Add

All services:
```env
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_NOTIFICATION_TOPIC=notification-queue
KAFKA_AUDIT_TOPIC=audit-queue
```

## Migration Strategy

### Backward Compatibility

During migration, maintain **dual-write** pattern:
1. Write to Kafka (new)
2. Keep HTTP calls (old) - with deprecation warnings
3. Monitor Kafka success rate
4. Remove HTTP calls after 2 weeks of stable Kafka operation

### Rollback Plan

If Kafka fails:
1. Services fall back to HTTP calls
2. Log Kafka errors
3. Alert operations team
4. Investigate and fix Kafka issues

## Summary

### Synchronous Calls to Keep (Need Immediate Response)
- ✅ User Management → Employee Service (create/update employee)
- ✅ User Management → Compliance Service (policy validation)
- ✅ Leave/Attendance → Employee Service (employee verification)

### Asynchronous Calls via Kafka (Fire-and-Forget)
- ❌ All services → Notification Service
- ❌ All services → Audit Service

### Kafka Provisioning Location
**Recommended**: `/k8s-manifests/kafka/` using **Strimzi Kafka Operator**

This provides the best balance of:
- GitOps alignment
- Production readiness
- Cost-effectiveness
- Operational simplicity

## Next Steps

1. Review and approve this architecture plan
2. Create Kafka infrastructure manifests in `k8s-manifests/kafka/`
3. Implement Kafka producer/consumer libraries
4. Update services in phases as outlined above
5. Set up monitoring and alerting
6. Document event schemas and contracts
