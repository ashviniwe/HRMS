# HRMS Microservices - Deployment & Setup Guide

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment](#docker-deployment)
5. [Service Configuration](#service-configuration)
6. [Database Setup](#database-setup)
7. [Integration Testing](#integration-testing)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Common Issues & Solutions](#common-issues--solutions)

---

## System Architecture Overview

The HRMS system consists of 7 microservices, each with its own database and specific responsibilities:

```
┌─────────────────────────────────────────────────────────────────┐
│                    HRMS Frontend (React)                         │
│                     http://localhost:3000                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬──────────────┬────────┐
        │                │                │              │        │
        ▼                ▼                ▼              ▼        ▼
┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────┐  ┌────────┐
│  Employee    │  │  Leave       │  │ Attendance │  │Notif.│  │Audit   │
│  Management  │  │ Management   │  │Management  │  │Svc   │  │Service │
│   (8001)     │  │   (8002)     │  │   (8003)   │  │(8004)│  │ (8005) │
└──────────────┘  └──────────────┘  └────────────┘  └──────┘  └────────┘
        │                │                │              │        │
        └────────────────┼────────────────┴──────────────┴────────┘
                         │
        ┌────────────────┼──────────────────────┐
        │                │                      │
        ▼                ▼                      ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────────┐
│ Compliance   │  │    User      │  │   MySQL Database   │
│  Service     │  │  Management  │  │   (Single Shared)  │
│   (8006)     │  │   (8007)     │  │                    │
└──────────────┘  └──────────────┘  └────────────────────┘
```

### Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Employee Management | 8001 | Employee CRUD operations |
| Leave Management | 8002 | Leave requests and approvals |
| Attendance Management | 8003 | Check-in/out and attendance tracking |
| Notification Service | 8004 | Email and in-app notifications |
| Audit Service | 8005 | Centralized audit logging |
| Compliance Service | 8006 | Policy validation and compliance checks |
| User Management | 8007 | Authentication and authorization |
| Frontend | 3000 | React application |
| MySQL Database | 3306 | Shared database for all services |

---

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **CPU**: 4 cores minimum (8+ recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 20GB free space

### Required Software

- **Docker Desktop**: 20.10+ (includes Docker Compose)
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
  
- **Git**: 2.25+
  - [Download Git](https://git-scm.com/downloads)
  
- **Python**: 3.13+ (for local development without Docker)
  - [Download Python](https://www.python.org/downloads/)
  
- **Node.js**: 18+ (for frontend development)
  - [Download Node.js](https://nodejs.org/)

### Optional Tools

- **Postman** or **Insomnia**: For API testing
- **MySQL Workbench**: For database management
- **VS Code**: For code editing
- **Docker Scout**: For security scanning

---

## Local Development Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/hrms.git
cd hr-management-system

# List services
ls -la
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
# Database Configuration
MYSQL_ROOT_PASSWORD=root
MYSQL_USER=hrms_user
MYSQL_PASSWORD=hrms_password

# SMTP Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=hrms@company.com
SMTP_FROM_NAME=HRMS System

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Authentication
JWKS_URL=https://api.asgardeo.io/t/your-tenant/oauth2/jwks
JWT_AUDIENCE=your_client_id
JWT_ISSUER=https://api.asgardeo.io/t/your-tenant/oauth2/token

# Service URLs (for inter-service communication)
EMPLOYEE_SERVICE_URL=http://employee-service:8001/api/v1
LEAVE_SERVICE_URL=http://leave-service:8002/api/v1
ATTENDANCE_SERVICE_URL=http://attendance-service:8003/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8004/api/v1
AUDIT_SERVICE_URL=http://audit-service:8005/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8006/api/v1
USER_SERVICE_URL=http://user-service:8007/api/v1
EOF
```

### 3. Build Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build employee-service

# Build without using cache
docker-compose build --no-cache
```

### 4. Start All Services

```bash
# Start services in detached mode
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up -d employee-service
```

### 5. Verify Services Are Running

```bash
# Check running containers
docker-compose ps

# Check if all services are healthy
docker-compose ps --format "table {{.Service}}\t{{.Status}}"

# Test service endpoints
curl http://localhost:8001/health    # Employee Service
curl http://localhost:8002/health    # Leave Service
curl http://localhost:8003/health    # Attendance Service
curl http://localhost:8004/health    # Notification Service
curl http://localhost:8005/health    # Audit Service
curl http://localhost:8006/health    # Compliance Service
curl http://localhost:8007/health    # User Service
curl http://localhost:3000           # Frontend
```

### 6. Access Services

Open your browser to:

- **Frontend**: http://localhost:3000
- **Employee Service Docs**: http://localhost:8001/docs
- **Leave Service Docs**: http://localhost:8002/docs
- **Attendance Service Docs**: http://localhost:8003/docs
- **Notification Service Docs**: http://localhost:8004/docs
- **Audit Service Docs**: http://localhost:8005/docs
- **Compliance Service Docs**: http://localhost:8006/docs
- **User Service Docs**: http://localhost:8007/docs

---

## Docker Deployment

### Quick Start

```bash
# Start all services with one command
docker-compose up -d

# Wait for services to be healthy (typically 30-60 seconds)
sleep 60

# Verify all services
docker-compose ps

# View logs for a specific service
docker-compose logs -f employee-service

# View logs for all services
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Compose Commands Reference

```bash
# Build images
docker-compose build
docker-compose build --no-cache
docker-compose build --progress=plain

# Start services
docker-compose up
docker-compose up -d
docker-compose up -d --scale service=3

# Stop services
docker-compose stop
docker-compose down
docker-compose down -v

# View status
docker-compose ps
docker-compose ps --format "table {{.Service}}\t{{.Status}}"
docker-compose ps -a

# View logs
docker-compose logs
docker-compose logs -f [service-name]
docker-compose logs --tail=100
docker-compose logs -f --since=10m

# Execute commands in running container
docker-compose exec employee-service bash
docker-compose exec mysql mysql -u root -p hrms_employees_db

# Restart services
docker-compose restart [service-name]

# Remove specific service data
docker-compose rm [service-name]
```

### Network Connectivity

Services communicate using Docker's internal network. Service names are automatically resolved to their IP addresses:

```bash
# Test connectivity from one service to another
docker-compose exec employee-service curl http://leave-service:8000/health

# Test database connectivity
docker-compose exec mysql mysql -u hrms_user -phrms_password -e "SHOW DATABASES;"

# Test from container to host
docker-compose exec employee-service curl http://host.docker.internal:3000
```

---

## Service Configuration

### Employee Management Service

**Configuration File**: `employee-management-service/.env`

```env
APP_NAME=Employee Management Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=hrms_employees_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# External Services
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8000/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8001
```

### Leave Management Service

**Configuration File**: `leave-management-service/.env`

```env
APP_NAME=Leave Management Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=hrms_leaves_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# External Services
EMPLOYEE_SERVICE_URL=http://employee-service:8000/api/v1
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8000/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8002
```

### Attendance Management Service

**Configuration File**: `attendance-management-service/.env`

```env
APP_NAME=Attendance Management Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=hrms_attendance_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# External Services
EMPLOYEE_SERVICE_URL=http://employee-service:8000/api/v1
LEAVE_SERVICE_URL=http://leave-service:8000/api/v1
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8000/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8003
```

### Notification Service

**Configuration File**: `notification-service/.env`

```env
APP_NAME=Notification Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=hrms_notifications_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=hrms@company.com
SMTP_FROM_NAME=HRMS System

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8004
```

### Audit Service

**Configuration File**: `audit-service/.env`

```env
APP_NAME=Audit Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=audit_service_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# Audit Settings
RETENTION_DAYS=365
MAX_BATCH_SIZE=1000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8005
```

### Compliance Service

**Configuration File**: `compliance-service/.env`

```env
APP_NAME=Compliance Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=hrms_compliance_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# External Services
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8006
```

### User Management Service

**Configuration File**: `user-management-service/.env`

```env
APP_NAME=User Management Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_HOST=mysql
DB_NAME=hrms_users_db
DB_USER=hrms_user
DB_PASSWORD=hrms_password
DB_PORT=3306

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8007
```

---

## Database Setup

### Initial Setup

MySQL is automatically initialized when Docker Compose starts. Each service creates its own database on first run.

### Manual Database Initialization

If you need to manually initialize databases:

```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -p

# At the mysql> prompt, create databases:
CREATE DATABASE hrms_employees_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE hrms_leaves_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE hrms_attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE hrms_notifications_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE audit_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE hrms_compliance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE hrms_users_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user
CREATE USER 'hrms_user'@'%' IDENTIFIED BY 'hrms_password';

# Grant privileges
GRANT ALL PRIVILEGES ON hrms_*.* TO 'hrms_user'@'%';
GRANT ALL PRIVILEGES ON audit_service_db.* TO 'hrms_user'@'%';
FLUSH PRIVILEGES;

# Exit
EXIT;
```

### Database Backup

```bash
# Backup all databases
docker-compose exec mysql mysqldump -u root -p --all-databases > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup specific database
docker-compose exec mysql mysqldump -u root -p hrms_employees_db > employees_backup.sql

# Restore from backup
docker-compose exec -T mysql mysql -u root -p < backup.sql
```

### Database Monitoring

```bash
# List all databases
docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"

# Check database sizes
docker-compose exec mysql mysql -u root -p -e "
SELECT table_schema, ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
GROUP BY table_schema
ORDER BY size_mb DESC;
"

# Monitor active connections
docker-compose exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

## Integration Testing

### Test All Services Are Running

```bash
# Create test script
cat > test_services.sh << 'EOF'
#!/bin/bash

SERVICES=("8001" "8002" "8003" "8004" "8005" "8006" "8007")
SERVICE_NAMES=("Employee" "Leave" "Attendance" "Notification" "Audit" "Compliance" "User")

echo "Testing HRMS Services..."
echo "========================"

for i in "${!SERVICES[@]}"; do
    PORT="${SERVICES[$i]}"
    NAME="${SERVICE_NAMES[$i]}"
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/health)
    
    if [ "$RESPONSE" = "200" ]; then
        echo "✓ $NAME Service (port $PORT) - OK"
    else
        echo "✗ $NAME Service (port $PORT) - FAILED (HTTP $RESPONSE)"
    fi
done

echo "========================"
echo "Frontend: http://localhost:3000"
echo "Database: localhost:3306"
EOF

chmod +x test_services.sh
./test_services.sh
```

### Test Service Integration

```bash
# Test Employee Service
curl -X GET http://localhost:8001/api/v1/employees

# Test Leave Service
curl -X GET http://localhost:8002/api/v1/leaves

# Test Attendance Service
curl -X GET http://localhost:8003/api/v1/attendance

# Test Audit Service
curl -X GET http://localhost:8005/api/v1/audit-logs

# Test Compliance Service
curl -X GET http://localhost:8006/api/v1/compliance/policies
```

### Test with Postman

Import the following collection URLs:

```
Employee Service: http://localhost:8001/openapi.json
Leave Service: http://localhost:8002/openapi.json
Attendance Service: http://localhost:8003/openapi.json
Notification Service: http://localhost:8004/openapi.json
Audit Service: http://localhost:8005/openapi.json
Compliance Service: http://localhost:8006/openapi.json
User Service: http://localhost:8007/openapi.json
```

---

## Monitoring & Troubleshooting

### View Service Logs

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f employee-service

# View last 100 lines
docker-compose logs --tail=100

# View logs from last 10 minutes
docker-compose logs -f --since=10m

# Save logs to file
docker-compose logs > all_logs.txt
docker-compose logs employee-service > employee_service.log
```

### Monitor Service Health

```bash
# Create health check script
cat > check_health.sh << 'EOF'
#!/bin/bash

SERVICES=(
    "Employee:8001"
    "Leave:8002"
    "Attendance:8003"
    "Notification:8004"
    "Audit:8005"
    "Compliance:8006"
    "User:8007"
)

while true; do
    clear
    echo "HRMS Services Health Check - $(date)"
    echo "====================================="
    
    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port <<< "$service"
        status=$(curl -s http://localhost:$port/health | jq -r '.status' 2>/dev/null || echo "FAILED")
        echo "$name Service (8$port): $status"
    done
    
    sleep 5
done
EOF

chmod +x check_health.sh
./check_health.sh
```

### Check Database Connectivity

```bash
# Test database connectivity
docker-compose exec mysql mysql -u hrms_user -phrms_password -e "SELECT 1;"

# List all databases
docker-compose exec mysql mysql -u hrms_user -phrms_password -e "SHOW DATABASES;"

# Check table structures
docker-compose exec mysql mysql -u hrms_user -phrms_password hrms_employees_db -e "SHOW TABLES;"
```

### Performance Monitoring

```bash
# Monitor container resources
docker stats

# Check specific container
docker stats hrms_employee_service

# View CPU and memory usage
docker-compose ps --format "table {{.Names}}\t{{.Size}}"
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All environment variables configured correctly
- [ ] SSL/TLS certificates obtained
- [ ] Database backups configured
- [ ] Monitoring and alerting setup
- [ ] Log aggregation configured
- [ ] Security audit completed
- [ ] Performance testing passed
- [ ] Disaster recovery plan documented
- [ ] Team training completed

### Production Docker Compose

```yaml
# Create production-specific docker-compose file
# docker-compose.prod.yml

version: '3.9'

services:
  mysql:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - mysql_backup:/backup
    ports:
      - "127.0.0.1:3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Service definitions here with production settings
  # - restart: always
  # - resource limits
  # - logging configuration
  # - health checks

volumes:
  mysql_data:
  mysql_backup:
```

### Kubernetes Deployment (Optional)

```bash
# Install Kubernetes manifests
kubectl apply -f k8s/

# Monitor deployment
kubectl get pods -n hrms
kubectl get services -n hrms

# View logs
kubectl logs -f deployment/employee-service -n hrms

# Scale services
kubectl scale deployment/leave-service --replicas=3 -n hrms
```

### SSL/TLS Configuration

```bash
# Generate self-signed certificates for development
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Configure NGINX reverse proxy (optional)
# See nginx.conf for configuration
```

---

## Common Issues & Solutions

### Issue 1: Services Not Starting

**Symptoms**: `docker-compose up` fails or services exit immediately

**Solutions**:
```bash
# Check logs
docker-compose logs

# Verify Docker is running
docker ps

# Check port conflicts
lsof -i :8001
lsof -i :3306

# Rebuild images
docker-compose build --no-cache

# Clear and restart
docker-compose down -v
docker-compose up -d
```

### Issue 2: Database Connection Errors

**Symptoms**: `Can't connect to MySQL server`

**Solutions**:
```bash
# Wait for MySQL to be ready
sleep 30

# Test MySQL connectivity
docker-compose exec mysql mysql -u root -p -e "SELECT 1;"

# Check MySQL logs
docker-compose logs mysql

# Verify credentials in .env
cat .env | grep MYSQL
```

### Issue 3: Service Communication Failures

**Symptoms**: Services cannot reach each other

**Solutions**:
```bash
# Test inter-service connectivity
docker-compose exec employee-service curl http://leave-service:8000/health

# Check network
docker network ls
docker network inspect hrms_network

# Verify service URLs in environment variables
docker-compose exec employee-service env | grep SERVICE_URL
```

### Issue 4: High Memory Usage

**Symptoms**: Docker containers consuming excessive memory

**Solutions**:
```bash
# Check memory usage
docker stats

# Set memory limits in docker-compose.yml
services:
  employee-service:
    deploy:
      resources:
        limits:
          memory: 512M

# Restart services
docker-compose restart
```

### Issue 5: Slow Queries

**Symptoms**: API responses are slow

**Solutions**:
```bash
# Check slow query log
docker-compose exec mysql mysql -u root -p -e "SET GLOBAL slow_query_log = 'ON';"

# Monitor queries
docker-compose exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# Create indexes
docker-compose exec mysql mysql -u root -p hrms_employees_db -e "
CREATE INDEX idx_employee_status ON employees(status);
CREATE INDEX idx_employee_department ON employees(department);
"
```

### Issue 6: Port Already in Use

**Symptoms**: `Bind for 0.0.0.0:8001 failed: port is already allocated`

**Solutions**:
```bash
# Find process using port
lsof -i :8001

# Kill process using port
kill -9 <PID>

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Change first number to different port

# Use different port range
ports:
  - "9001:8000"
```

### Issue 7: Frontend Cannot Connect to Services

**Symptoms**: CORS errors, connection refused

**Solutions**:
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" \
  -X OPTIONS http://localhost:8001/api/v1/employees -v

# Update CORS in docker-compose.yml
environment:
  CORS_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000"

# Clear browser cache and restart
```

### Issue 8: Database Disk Space Full

**Symptoms**: Write operations fail, containers crash

**Solutions**:
```bash
# Check disk space
docker system df

# Remove old containers and images
docker container prune
docker image prune

# Cleanup volumes
docker volume prune

# Archive old audit logs
docker-compose exec mysql mysql -u root -p -e "
DELETE FROM audit_log WHERE timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);
"
```

---

## Useful Commands Reference

### Docker Compose Management

```bash
# Build and start
docker-compose up -d --build

# Scale services
docker-compose up -d --scale leave-service=3

# View resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Cleanup everything
docker-compose down -v --remove-orphans
```

### Database Management

```bash
# MySQL prompt
docker-compose exec mysql mysql -u root -p

# Execute SQL file
docker-compose exec mysql mysql -u root -p < schema.sql

# Dump database
docker-compose exec mysql mysqldump -u root -p [db_name] > dump.sql
```

### Service Debugging

```bash
# Execute commands in container
docker-compose exec employee-service bash

# View environment variables
docker-compose exec employee-service env

# Install debugging tools
docker-compose exec employee-service apt-get install -y curl
```

### Log Management

```bash
# Follow logs with timestamp
docker-compose logs -f --timestamps

# Filter logs by service
docker-compose logs -f employee-service | grep ERROR

# Export logs
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
```

---

## Support & Resources

- **Documentation**: See `MICROSERVICES_INTEGRATION.md`
- **API Documentation**: http://localhost:[service-port]/docs
- **Issues**: Create GitHub issues with logs and error messages
- **Contact**: Platform Engineering Team

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-10 | Initial deployment guide |

---

**Last Updated**: January 10, 2024  
**Document Status**: Active  
**Maintained By**: Platform Engineering Team