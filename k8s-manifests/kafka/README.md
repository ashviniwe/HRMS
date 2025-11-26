# Kafka Infrastructure for HRMS

This directory contains Kubernetes manifests for deploying Apache Kafka using the Strimzi operator.

## Overview

The Kafka infrastructure consists of:
- **Strimzi Operator**: Manages Kafka clusters in Kubernetes
- **Kafka Cluster**: 3-broker cluster with ZooKeeper
- **Topics**: Pre-configured topics for HRMS services
- **Monitoring**: Prometheus metrics and alerting

## Architecture

```
┌─────────────────────────────────────────┐
│         Strimzi Operator                │
│  (Manages Kafka lifecycle)              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      Kafka Cluster (hrms-kafka)         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Broker 1 │  │ Broker 2 │  │Broker 3││
│  └──────────┘  └──────────┘  └────────┘│
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  ZK 1    │  │  ZK 2    │  │  ZK 3  ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│            Topics                       │
│  • notification-queue (3 partitions)    │
│  • audit-queue (5 partitions)           │
│  • notification-dlq (1 partition)       │
│  • audit-dlq (1 partition)              │
└─────────────────────────────────────────┘
```

## Files

1. **01-strimzi-operator.yaml**
   - Installs Strimzi Kafka Operator
   - Creates namespace, RBAC, and operator deployment
   - Version: Strimzi 0.39.0 (Kafka 3.6.0)

2. **02-kafka-cluster.yaml**
   - Defines 3-broker Kafka cluster
   - 3-node ZooKeeper ensemble
   - Persistent storage (10Gi per broker, 5Gi per ZK)
   - Prometheus metrics configuration

3. **03-kafka-topics.yaml**
   - `notification-queue`: 3 partitions, 2 replicas, 7-day retention
   - `audit-queue`: 5 partitions, 3 replicas, 30-day retention
   - Dead letter queues for failed message processing

4. **04-kafka-monitoring.yaml**
   - ServiceMonitors for Prometheus
   - Alert rules for Kafka health
   - Metrics for brokers, consumers, and producers

## Prerequisites

1. **Kubernetes Cluster**: v1.23+
2. **Storage Class**: Update `class: gp2` in `02-kafka-cluster.yaml` to match your cluster's storage class
3. **Prometheus Operator** (optional): For monitoring and alerting

## Installation

### Step 1: Install Strimzi Operator

```bash
kubectl apply -f 01-strimzi-operator.yaml
```

Wait for the operator to be ready:

```bash
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

### Step 2: Deploy Kafka Cluster

```bash
kubectl apply -f 02-kafka-cluster.yaml
```

This will create:
- 3 Kafka brokers
- 3 ZooKeeper nodes
- Persistent volumes for data storage

Wait for Kafka cluster to be ready (this may take 5-10 minutes):

```bash
kubectl wait kafka/hrms-kafka --for=condition=Ready --timeout=600s -n kafka
```

### Step 3: Create Topics

```bash
kubectl apply -f 03-kafka-topics.yaml
```

Verify topics are created:

```bash
kubectl get kafkatopics -n kafka
```

Expected output:
```
NAME                 CLUSTER      PARTITIONS   REPLICATION FACTOR   READY
notification-queue   hrms-kafka   3            2                    True
audit-queue          hrms-kafka   5            3                    True
notification-dlq     hrms-kafka   1            2                    True
audit-dlq            hrms-kafka   1            2                    True
```

### Step 4: Set up Monitoring (Optional)

If you have Prometheus Operator installed:

```bash
kubectl apply -f 04-kafka-monitoring.yaml
```

## Verification

### Check Kafka Cluster Status

```bash
kubectl get kafka -n kafka
```

Expected output:
```
NAME         DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS   READY   WARNINGS
hrms-kafka   3                        3                     True
```

### Check Pods

```bash
kubectl get pods -n kafka
```

Expected pods:
```
NAME                                        READY   STATUS    RESTARTS   AGE
hrms-kafka-kafka-0                          1/1     Running   0          5m
hrms-kafka-kafka-1                          1/1     Running   0          5m
hrms-kafka-kafka-2                          1/1     Running   0          5m
hrms-kafka-zookeeper-0                      1/1     Running   0          6m
hrms-kafka-zookeeper-1                      1/1     Running   0          6m
hrms-kafka-zookeeper-2                      1/1     Running   0          6m
hrms-kafka-entity-operator-xxxxx            3/3     Running   0          4m
strimzi-cluster-operator-xxxxx              1/1     Running   0          10m
```

### Test Kafka Connection

Create a test producer pod:

```bash
kubectl run kafka-producer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.0 --rm=true --restart=Never -n kafka -- bin/kafka-console-producer.sh --bootstrap-server hrms-kafka-kafka-bootstrap:9092 --topic notification-queue
```

In another terminal, create a test consumer:

```bash
kubectl run kafka-consumer -ti --image=quay.io/strimzi/kafka:0.39.0-kafka-3.6.0 --rm=true --restart=Never -n kafka -- bin/kafka-console-consumer.sh --bootstrap-server hrms-kafka-kafka-bootstrap:9092 --topic notification-queue --from-beginning
```

## Configuration

### Kafka Bootstrap Servers

For services in the same Kubernetes cluster:
```
hrms-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
```

For services in the `hrms` namespace (short form):
```
hrms-kafka-kafka-bootstrap.kafka:9092
```

Or simply (if DNS search path is configured):
```
hrms-kafka-kafka-bootstrap:9092
```

### Environment Variables for Services

Add these to your service deployments:

```yaml
env:
  - name: KAFKA_BOOTSTRAP_SERVERS
    value: "hrms-kafka-kafka-bootstrap.kafka:9092"
  - name: KAFKA_NOTIFICATION_TOPIC
    value: "notification-queue"
  - name: KAFKA_AUDIT_TOPIC
    value: "audit-queue"
```

## Topic Configuration

### notification-queue

- **Partitions**: 3
- **Replication Factor**: 2
- **Retention**: 7 days
- **Use Case**: User notifications, emails, alerts
- **Producers**: User, Employee, Leave, Attendance, Compliance services
- **Consumers**: Notification service

### audit-queue

- **Partitions**: 5
- **Replication Factor**: 3
- **Retention**: 30 days
- **Use Case**: Audit logging, compliance tracking
- **Producers**: All services
- **Consumers**: Audit service

## Monitoring

### Prometheus Metrics

Kafka exposes metrics on port 9404:
- Broker metrics: `http://hrms-kafka-kafka-<n>.kafka:9404/metrics`
- ZooKeeper metrics: `http://hrms-kafka-zookeeper-<n>.kafka:9404/metrics`

### Key Metrics to Monitor

1. **Consumer Lag**: `kafka_consumergroup_lag`
2. **Under-replicated Partitions**: `kafka_server_replicamanager_underreplicatedpartitions`
3. **Offline Partitions**: `kafka_controller_kafkacontroller_offlinepartitionscount`
4. **Disk Usage**: Check PVC usage
5. **Producer Errors**: `kafka_producer_record_error_total`

### Grafana Dashboards

Import these Grafana dashboard IDs:
- **Strimzi Kafka**: 11962
- **Kafka Exporter**: 7589

## Troubleshooting

### Kafka Broker Not Starting

Check logs:
```bash
kubectl logs hrms-kafka-kafka-0 -n kafka
```

Common issues:
- Insufficient resources (increase memory/CPU)
- Storage class not available
- ZooKeeper not ready

### Topic Not Created

Check topic operator logs:
```bash
kubectl logs deployment/hrms-kafka-entity-operator -c topic-operator -n kafka
```

### Consumer Lag Increasing

1. Check consumer is running:
```bash
kubectl get pods -l app=notification-service -n hrms
```

2. Scale consumers:
```bash
kubectl scale deployment notification-service --replicas=3 -n hrms
```

3. Check consumer logs for errors

### Disk Space Issues

Check PVC usage:
```bash
kubectl get pvc -n kafka
```

To increase disk size, edit the Kafka CR:
```bash
kubectl edit kafka hrms-kafka -n kafka
```

Update `storage.size` and apply.

## Maintenance

### Scaling Kafka Brokers

Edit `02-kafka-cluster.yaml` and change `kafka.replicas`:

```yaml
kafka:
  replicas: 5  # Increase from 3 to 5
```

Apply:
```bash
kubectl apply -f 02-kafka-cluster.yaml
```

### Upgrading Kafka

Update the `kafka.version` in `02-kafka-cluster.yaml`:

```yaml
kafka:
  version: 3.7.0  # Upgrade version
```

Apply and Strimzi will perform a rolling upgrade.

### Backup and Restore

Kafka data is stored in PVCs. To backup:

1. Take snapshots of PVCs (cloud provider specific)
2. Or use Velero for backup/restore

## Security Considerations

### Current Setup (Development)

- **TLS**: Enabled on port 9093 (optional)
- **Authentication**: None (open access)
- **Authorization**: None

### Production Recommendations

1. **Enable TLS** for all listeners
2. **Enable SASL authentication** (SCRAM-SHA-512)
3. **Enable ACLs** for topic access control
4. **Network Policies** to restrict access
5. **Encryption at rest** for PVCs

Example TLS configuration:

```yaml
listeners:
  - name: tls
    port: 9093
    type: internal
    tls: true
    authentication:
      type: scram-sha-512
```

## Uninstallation

To remove Kafka infrastructure:

```bash
# Delete topics
kubectl delete -f 03-kafka-topics.yaml

# Delete Kafka cluster
kubectl delete -f 02-kafka-cluster.yaml

# Delete operator
kubectl delete -f 01-strimzi-operator.yaml

# Delete namespace (optional)
kubectl delete namespace kafka
```

**Warning**: This will delete all Kafka data. Ensure you have backups!

## Resources

- [Strimzi Documentation](https://strimzi.io/docs/operators/latest/overview.html)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Strimzi GitHub](https://github.com/strimzi/strimzi-kafka-operator)

## Support

For issues or questions:
1. Check Strimzi operator logs
2. Check Kafka broker logs
3. Review Strimzi documentation
4. Open an issue in the project repository
