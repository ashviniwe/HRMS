# Service Communication Matrix

## Current vs Proposed Architecture

| Source Service | Target Service | Current (Sync/Async) | Proposed | Reason |
|---------------|----------------|---------------------|----------|---------|
| **User Management** | Employee Service | Sync (HTTP) | ✅ Keep Sync | Need immediate response for user creation |
| **User Management** | Audit Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget logging |
| **User Management** | Notification Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget notifications |
| **User Management** | Compliance Service | Sync (HTTP) | ✅ Keep Sync | Need immediate policy validation |
| **Employee Management** | Audit Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget logging |
| **Employee Management** | Notification Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget notifications |
| **Employee Management** | Compliance Service | Sync (HTTP) | ✅ Keep Sync | Need immediate policy validation |
| **Leave Management** | Employee Service | Sync (HTTP) | ✅ Keep Sync | Need to verify employee exists |
| **Leave Management** | Audit Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget logging |
| **Leave Management** | Notification Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget notifications |
| **Attendance Management** | Employee Service | Sync (HTTP) | ✅ Keep Sync | Need to verify employee exists |
| **Attendance Management** | Audit Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget logging |
| **Attendance Management** | Notification Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget notifications |
| **Compliance Service** | Audit Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget logging |
| **Compliance Service** | Notification Service | Sync (HTTP) | ❌ Make Async (Kafka) | Fire-and-forget alerts |

## Kafka Topics

### Topic 1: `notification-queue`

| Producers | Consumers | Partitions | Replication | Retention |
|-----------|-----------|------------|-------------|-----------|
| User Management<br>Employee Management<br>Leave Management<br>Attendance Management<br>Compliance Service | Notification Service | 3 | 2 | 7 days |

**Event Types**:
- `user.created`, `user.updated`, `user.deleted`, `user.suspended`, `user.password_changed`
- `employee.created`, `employee.updated`, `employee.terminated`
- `leave.requested`, `leave.approved`, `leave.rejected`, `leave.cancelled`
- `attendance.marked`, `attendance.updated`
- `compliance.violation`, `compliance.alert`

### Topic 2: `audit-queue`

| Producers | Consumers | Partitions | Replication | Retention |
|-----------|-----------|------------|-------------|-----------|
| User Management<br>Employee Management<br>Leave Management<br>Attendance Management<br>Compliance Service | Audit Service | 5 | 3 | 30 days |

**Event Types**:
- `audit.user.*` - All user operations
- `audit.employee.*` - All employee operations
- `audit.leave.*` - All leave operations
- `audit.attendance.*` - All attendance operations
- `audit.compliance.*` - All compliance operations

## Files to Modify

### Service Code Changes

#### 1. User Management Service
**Files to modify**:
- `services/user-management-service/pyproject.toml` - Add `aiokafka` dependency
- `services/user-management-service/app/core/integrations.py` - Replace HTTP calls with Kafka
- `services/user-management-service/app/core/kafka_producer.py` - **NEW** Kafka producer
- `services/user-management-service/app/core/config.py` - Add Kafka config

**Estimated LOC**: ~300 lines

#### 2. Employee Management Service
**Files to modify**:
- `services/employee-management-service/pyproject.toml` - Add `aiokafka` dependency
- `services/employee-management-service/app/core/kafka_producer.py` - **NEW** Kafka producer
- `services/employee-management-service/app/core/config.py` - Add Kafka config
- `services/employee-management-service/app/api/routes/employees.py` - Integrate Kafka

**Estimated LOC**: ~250 lines

#### 3. Leave Management Service
**Files to modify**:
- `services/leave-management-service/pyproject.toml` - Add `aiokafka` dependency
- `services/leave-management-service/app/core/kafka_producer.py` - **NEW** Kafka producer
- `services/leave-management-service/app/core/config.py` - Add Kafka config
- `services/leave-management-service/app/api/routes/leaves.py` - Integrate Kafka

**Estimated LOC**: ~250 lines

#### 4. Attendance Management Service
**Files to modify**:
- `services/attendance-management-service/pyproject.toml` - Add `aiokafka` dependency
- `services/attendance-management-service/app/core/kafka_producer.py` - **NEW** Kafka producer
- `services/attendance-management-service/app/core/config.py` - Add Kafka config
- `services/attendance-management-service/app/api/routes/attendance.py` - Integrate Kafka

**Estimated LOC**: ~250 lines

#### 5. Compliance Service
**Files to modify**:
- `services/compliance-service/pyproject.toml` - Add `aiokafka` dependency
- `services/compliance-service/app/core/kafka_producer.py` - **NEW** Kafka producer
- `services/compliance-service/app/core/config.py` - Add Kafka config
- `services/compliance-service/app/api/routes/compliance.py` - Integrate Kafka

**Estimated LOC**: ~200 lines

#### 6. Notification Service (Consumer)
**Files to modify**:
- `services/notification-service/pyproject.toml` - Add `aiokafka` dependency
- `services/notification-service/app/core/kafka_consumer.py` - **NEW** Kafka consumer
- `services/notification-service/app/core/config.py` - Add Kafka config
- `services/notification-service/app/consumers/notification_consumer.py` - **NEW** Event handlers
- `services/notification-service/app/main.py` - Start consumer on startup

**Estimated LOC**: ~400 lines

#### 7. Audit Service (Consumer)
**Files to modify**:
- `services/audit-service/pyproject.toml` - Add `aiokafka` dependency
- `services/audit-service/app/core/kafka_consumer.py` - **NEW** Kafka consumer
- `services/audit-service/app/core/config.py` - Add Kafka config
- `services/audit-service/app/consumers/audit_consumer.py` - **NEW** Event handlers
- `services/audit-service/app/main.py` - Start consumer on startup

**Estimated LOC**: ~400 lines

### Infrastructure Changes

#### Kubernetes Manifests (GitOps)

**New files to create** in `k8s-manifests/kafka/`:

```
k8s-manifests/kafka/
├── 00-namespace.yaml                    # Kafka namespace (or use hrms namespace)
├── 01-strimzi-operator.yaml            # Strimzi Kafka operator
├── 02-kafka-cluster.yaml               # Kafka cluster definition (3 brokers)
├── 03-kafka-topics.yaml                # Topic definitions
├── 04-kafka-monitoring.yaml            # Prometheus metrics
└── README.md                           # Kafka operations guide
```

**Estimated LOC**: ~500 lines

**Files to modify**:
- `k8s-manifests/services/user-service.yaml` - Add Kafka env vars
- `k8s-manifests/services/employee-service.yaml` - Add Kafka env vars
- `k8s-manifests/services/leave-service.yaml` - Add Kafka env vars
- `k8s-manifests/services/attendance-service.yaml` - Add Kafka env vars
- `k8s-manifests/services/notification-service.yaml` - Add Kafka env vars
- `k8s-manifests/services/audit-service.yaml` - Add Kafka env vars
- `k8s-manifests/services/compliance-service.yaml` - Add Kafka env vars

**Estimated LOC**: ~50 lines (7 files × ~7 lines each)

#### Docker Compose (Local Development)

**Files to modify**:
- `services/docker-compose.yml` - Add Kafka and Zookeeper services

**Estimated LOC**: ~80 lines

## Implementation Checklist

### Phase 1: Infrastructure (Week 1)

- [ ] Create `k8s-manifests/kafka/` directory structure
- [ ] Add Strimzi operator manifests
- [ ] Define Kafka cluster (3 brokers, 2 replicas)
- [ ] Create topic definitions (`notification-queue`, `audit-queue`)
- [ ] Add Kafka to docker-compose.yml for local dev
- [ ] Deploy Kafka to K8s cluster
- [ ] Verify Kafka cluster health
- [ ] Create topics and verify
- [ ] Set up Kafka monitoring (Prometheus/Grafana)

### Phase 2: Shared Libraries (Week 1-2)

- [ ] Create shared Kafka producer library
- [ ] Create shared Kafka consumer library
- [ ] Define event schemas (Pydantic models)
- [ ] Add error handling and retry logic
- [ ] Add unit tests for Kafka libraries
- [ ] Document event schema contracts

### Phase 3: Consumer Services (Week 2)

#### Notification Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Implement Kafka consumer
- [ ] Add event handlers for each notification type
- [ ] Implement retry logic for failed notifications
- [ ] Add dead letter queue handling
- [ ] Update main.py to start consumer
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

#### Audit Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Implement Kafka consumer
- [ ] Add event handlers for audit events
- [ ] Implement batch processing
- [ ] Add event sourcing capability
- [ ] Update main.py to start consumer
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

### Phase 4: Producer Services (Week 2-3)

#### User Management Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Create Kafka producer module
- [ ] Replace audit HTTP calls with Kafka events
- [ ] Replace notification HTTP calls with Kafka events
- [ ] Add fallback to HTTP (dual-write pattern)
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

#### Employee Management Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Create Kafka producer module
- [ ] Replace audit HTTP calls with Kafka events
- [ ] Replace notification HTTP calls with Kafka events
- [ ] Add fallback to HTTP (dual-write pattern)
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

#### Leave Management Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Create Kafka producer module
- [ ] Replace audit HTTP calls with Kafka events
- [ ] Replace notification HTTP calls with Kafka events
- [ ] Add fallback to HTTP (dual-write pattern)
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

#### Attendance Management Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Create Kafka producer module
- [ ] Replace audit HTTP calls with Kafka events
- [ ] Replace notification HTTP calls with Kafka events
- [ ] Add fallback to HTTP (dual-write pattern)
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

#### Compliance Service
- [ ] Add `aiokafka` to pyproject.toml
- [ ] Create Kafka producer module
- [ ] Replace audit HTTP calls with Kafka events
- [ ] Replace notification HTTP calls with Kafka events
- [ ] Add fallback to HTTP (dual-write pattern)
- [ ] Add integration tests
- [ ] Update K8s manifest with Kafka env vars

### Phase 5: Testing & Validation (Week 3-4)

- [ ] End-to-end integration tests
- [ ] Load testing (simulate high event volume)
- [ ] Failover testing (Kafka broker failures)
- [ ] Consumer lag monitoring
- [ ] Performance benchmarking
- [ ] Verify event ordering
- [ ] Test dead letter queue handling
- [ ] Chaos engineering tests

### Phase 6: Deployment & Migration (Week 4)

- [ ] Deploy Kafka to production
- [ ] Deploy consumer services (Notification, Audit)
- [ ] Deploy producer services with dual-write
- [ ] Monitor Kafka metrics for 1 week
- [ ] Verify no message loss
- [ ] Remove HTTP fallback code
- [ ] Update documentation
- [ ] Create runbooks for operations
- [ ] Train team on Kafka operations

### Phase 7: Monitoring & Optimization (Ongoing)

- [ ] Set up alerting for consumer lag
- [ ] Set up alerting for dead letter queue
- [ ] Optimize partition count based on load
- [ ] Tune consumer batch sizes
- [ ] Configure retention policies
- [ ] Set up backup/restore procedures
- [ ] Document disaster recovery plan

## Effort Estimation

| Phase | Duration | Effort (Person-Days) |
|-------|----------|---------------------|
| Phase 1: Infrastructure | 1 week | 3 days |
| Phase 2: Shared Libraries | 1 week | 4 days |
| Phase 3: Consumer Services | 1 week | 5 days |
| Phase 4: Producer Services | 2 weeks | 8 days |
| Phase 5: Testing | 1 week | 5 days |
| Phase 6: Deployment | 1 week | 3 days |
| Phase 7: Monitoring | Ongoing | 2 days |
| **Total** | **7 weeks** | **30 days** |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kafka cluster failure | High | 3 brokers with replication factor 2-3 |
| Message loss | High | Enable producer acknowledgments, consumer commits |
| Consumer lag | Medium | Monitor lag, auto-scale consumers |
| Schema evolution | Medium | Use versioned event schemas |
| Network partitions | Medium | Configure proper timeouts and retries |
| Operational complexity | Low | Use Strimzi operator for automation |

## Success Metrics

- ✅ 99.9% message delivery rate
- ✅ Consumer lag < 1000 messages
- ✅ P95 latency < 100ms for event production
- ✅ Zero data loss
- ✅ Notification delivery within 5 seconds
- ✅ Audit events persisted within 10 seconds
