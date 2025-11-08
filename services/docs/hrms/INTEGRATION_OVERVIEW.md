# HRMS - Human Resource Management System
## Complete Microservices Integration Overview

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Services Overview](#services-overview)
4. [Quick Start](#quick-start)
5. [Key Features](#key-features)
6. [Technology Stack](#technology-stack)
7. [Integration Flows](#integration-flows)
8. [Documentation Structure](#documentation-structure)
9. [Getting Help](#getting-help)

---

## Project Overview

The HRMS (Human Resource Management System) is a modern, microservices-based Human Resources platform built with FastAPI and React. It provides comprehensive employee management, leave tracking, attendance monitoring, and compliance management capabilities across distributed microservices.

### Key Objectives

✅ **Modular Architecture** - Each service independently deployable and scalable  
✅ **Centralized Audit Trail** - All actions logged for compliance and forensics  
✅ **Policy Compliance** - Enforce business rules and regulatory requirements  
✅ **Real-time Notifications** - Instant communication for all events  
✅ **Attendance Tracking** - Comprehensive check-in/out and working hours tracking  
✅ **Leave Management** - Complete leave request lifecycle management  
✅ **Employee Management** - Central repository for all employee data  
✅ **User Authentication** - Secure JWT-based authentication  

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend Application                       │
│              (React - http://localhost:3000)                │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────────────────────────┐
        │            │                                │
        ▼            ▼                                ▼
   ┌─────────┐  ┌─────────┐                    ┌─────────────┐
   │Employee │  │ Leave   │    ┌────────────┐  │  Audit      │
   │Service  │  │ Service │    │Attendance  │  │  Service    │
   │ :8001   │  │ :8002   │    │ Service    │  │  :8005      │
   │         │  │         │    │  :8003     │  │             │
   └────┬────┘  └────┬────┘    └────┬───────┘  └─────────────┘
        │            │              │
        └────────────┼──────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
        ▼            ▼            ▼              ▼
   ┌──────────┐  ┌─────────┐ ┌──────────┐ ┌──────────┐
   │Compliance│  │Notification Service  │ │   User   │
   │ Service  │  │      :8004           │ │ Service  │
   │ :8006    │  └──────────────────────┘ │ :8007    │
   └──────────┘                            └──────────┘
        │
        └────────────────┬─────────────────┐
                         │                 │
                         ▼                 ▼
                    ┌──────────────────────────┐
                    │   MySQL Database         │
                    │  (Shared - :3306)        │
                    │                          │
                    │ - hrms_employees_db      │
                    │ - hrms_leaves_db         │
                    │ - hrms_attendance_db     │
                    │ - hrms_notifications_db  │
                    │ - audit_service_db       │
                    │ - hrms_compliance_db     │
                    │ - hrms_users_db          │
                    └──────────────────────────┘
```

### Service Dependencies Graph

```
Employee Service
  ├── Audit Service
  ├── Notification Service
  └── Compliance Service

Leave Service
  ├── Employee Service
  ├── Audit Service
  ├── Notification Service
  └── Compliance Service

Attendance Service
  ├── Employee Service
  ├── Leave Service
  ├── Audit Service
  ├── Notification Service
  └── Compliance Service

Notification Service
  (No dependencies - core utility service)

Audit Service
  (No dependencies - core logging service)

Compliance Service
  ├── Audit Service
  └── Notification Service

User Service
  └── Audit Service
```

---

## Services Overview

### 1. Employee Management Service (Port 8001)

**Purpose**: Central repository for all employee data and master data management

**Responsibilities**:
- Employee CRUD operations
- Department and position management
- Role assignment
- Salary and compensation tracking
- Employee status management

**Key Endpoints**:
```
GET    /api/v1/employees              - List all employees
GET    /api/v1/employees/{id}         - Get employee details
POST   /api/v1/employees              - Create new employee
PATCH  /api/v1/employees/{id}         - Update employee
DELETE /api/v1/employees/{id}         - Delete employee
GET    /api/v1/employees/{id}/verify  - Verify employee exists
```

**Integrations**:
- Calls: Audit Service (log changes), Notification Service (send notifications)
- Called By: Leave Service, Attendance Service
- Events: employee_created, employee_updated, employee_deleted

---

### 2. Leave Management Service (Port 8002)

**Purpose**: Manage employee leave requests and approvals

**Responsibilities**:
- Leave request creation and tracking
- Leave approval/rejection workflow
- Leave balance management
- Leave type categorization
- Leave policy enforcement

**Key Endpoints**:
```
POST   /api/v1/leaves                   - Create leave request
GET    /api/v1/leaves                   - List leave requests
GET    /api/v1/leaves/{id}              - Get leave details
PATCH  /api/v1/leaves/{id}/approve      - Approve leave
PATCH  /api/v1/leaves/{id}/reject       - Reject leave
GET    /api/v1/leaves/{emp_id}/balance  - Get leave balance
POST   /api/v1/leaves/{id}/cancel       - Cancel leave
```

**Integrations**:
- Calls: Employee Service (verify employee), Audit Service (log), 
         Notification Service (notify), Compliance Service (validate)
- Called By: Attendance Service
- Events: leave_created, leave_approved, leave_rejected, leave_cancelled

---

### 3. Attendance Management Service (Port 8003)

**Purpose**: Track employee attendance and working hours

**Responsibilities**:
- Check-in/check-out recording
- Attendance tracking and reporting
- Late arrival detection
- Working hours calculation
- Absenteeism tracking

**Key Endpoints**:
```
POST   /api/v1/attendance/check-in           - Record check-in
POST   /api/v1/attendance/check-out          - Record check-out
GET    /api/v1/attendance/{emp_id}           - Get attendance history
GET    /api/v1/attendance/{emp_id}/monthly   - Get monthly summary
POST   /api/v1/attendance/manual-entry       - Manual attendance entry
GET    /api/v1/attendance/{emp_id}/late      - Get late arrivals
```

**Integrations**:
- Calls: Employee Service (verify), Leave Service (check leave status),
         Audit Service (log), Notification Service (notify),
         Compliance Service (validate rules)
- Called By: None directly
- Events: check_in, check_out, late_arrival, absent

---

### 4. Notification Service (Port 8004)

**Purpose**: Centralized notification delivery system

**Responsibilities**:
- Email notifications
- In-app notifications
- SMS notifications (optional)
- Notification templating
- Delivery tracking

**Key Endpoints**:
```
POST   /api/v1/notifications/send       - Send notification
POST   /api/v1/notifications/email      - Send email
POST   /api/v1/notifications/bulk       - Bulk notifications
GET    /api/v1/notifications/{user_id}  - Get notifications
PATCH  /api/v1/notifications/{id}/read  - Mark as read
```

**Integrations**:
- Called By: All other services (Employee, Leave, Attendance, Compliance, Audit)
- No dependencies on other business services
- Events: notification_sent, notification_failed, email_delivered

---

### 5. Audit Service (Port 8005)

**Purpose**: Centralized audit logging for compliance and forensics

**Responsibilities**:
- Log all significant system events
- Maintain immutable audit trail
- Support compliance reporting
- Track data access and changes
- Archive old logs

**Key Endpoints**:
```
POST   /api/v1/audit-logs                              - Create log
GET    /api/v1/audit-logs                              - Query logs
GET    /api/v1/audit-logs/{id}                         - Get specific log
GET    /api/v1/audit-logs/user/{user_id}               - User activities
GET    /api/v1/audit-logs/type/{log_type}              - Logs by type
GET    /api/v1/audit-logs/entity/{type}/{entity_id}    - Entity changes
```

**Integrations**:
- Called By: All other services
- No dependencies on other business services
- Events: All significant actions logged

---

### 6. Compliance Service (Port 8006)

**Purpose**: Ensure business rules and regulatory compliance

**Responsibilities**:
- Define compliance policies
- Validate business rules
- Manage compliance templates
- Track compliance violations
- Generate compliance reports

**Key Endpoints**:
```
POST   /api/v1/compliance/policies        - Create policy
GET    /api/v1/compliance/policies        - List policies
POST   /api/v1/compliance/validate        - Validate against policies
GET    /api/v1/compliance/violations      - Get violations
GET    /api/v1/compliance/reports         - Generate reports
```

**Integrations**:
- Calls: Audit Service (log policy changes), Notification Service (notify)
- Called By: Leave Service, Attendance Service, Employee Service
- Events: policy_created, policy_updated, violation_detected

---

### 7. User Management Service (Port 8007)

**Purpose**: Authentication and authorization

**Responsibilities**:
- User authentication (login/logout)
- JWT token generation and validation
- Role-based access control
- Permission management
- Session management

**Key Endpoints**:
```
POST   /api/v1/auth/login           - User login
POST   /api/v1/auth/logout          - User logout
GET    /api/v1/auth/verify          - Verify token
GET    /api/v1/auth/whoami           - Current user info
GET    /api/v1/users                 - List users
POST   /api/v1/users                 - Create user
PATCH  /api/v1/users/{id}            - Update user
```

**Integrations**:
- Calls: Audit Service (log auth events)
- Called By: All services (for token validation)
- Events: user_login, user_logout, token_issued, token_revoked

---

## Quick Start

### Prerequisites
- Docker Desktop 20.10+
- Git
- 8GB RAM minimum
- 20GB free disk space

### Start All Services (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/hrms.git
cd hr-management-system

# 2. Copy environment variables
cp .env.example .env

# 3. Start all services with Docker Compose
docker-compose up -d

# 4. Wait for services to be healthy
sleep 60

# 5. Verify all services are running
docker-compose ps

# 6. Access the system
Frontend:           http://localhost:3000
Employee Service:   http://localhost:8001/docs
Leave Service:      http://localhost:8002/docs
Attendance Service: http://localhost:8003/docs
Notification Service: http://localhost:8004/docs
Audit Service:      http://localhost:8005/docs
Compliance Service: http://localhost:8006/docs
User Service:       http://localhost:8007/docs
```

### Stop Services

```bash
# Stop all services
docker-compose stop

# Remove all containers
docker-compose down

# Remove everything including data
docker-compose down -v
```

---

## Key Features

### 1. Comprehensive Employee Management
- Employee profiles with detailed information
- Department and role management
- Salary and compensation tracking
- Employee status tracking (active, on leave, terminated, etc.)

### 2. Leave Management System
- Multiple leave types (annual, sick, casual, unpaid, etc.)
- Leave request creation and tracking
- Manager approval/rejection workflow
- Leave balance tracking and reporting
- Carryover policy management

### 3. Attendance Tracking
- Real-time check-in/check-out
- Location tracking
- Working hours calculation
- Late arrival detection
- Attendance summary reports
- Leave integration (exclude leave days)

### 4. Centralized Audit Logging
- Immutable audit trail
- User activity tracking
- Data change history
- Compliance event logging
- Audit reports and queries
- Data retention policies

### 5. Compliance Management
- Policy definition and management
- Rule enforcement
- Compliance validation
- Violation tracking
- Compliance reporting
- Regulatory support

### 6. Notification System
- Email notifications
- In-app notifications
- SMS notifications (optional)
- Bulk notification support
- Delivery tracking
- Notification templates

### 7. User Authentication & Authorization
- JWT-based authentication
- JWKS support for external identity providers
- Role-based access control
- Permission management
- Session management

---

## Technology Stack

### Backend Services
- **Framework**: FastAPI 0.119.0+
- **Database**: MySQL 8.0
- **ORM**: SQLModel
- **Authentication**: JWT with JWKS
- **Language**: Python 3.13+

### Frontend
- **Framework**: React 18+
- **UI Library**: React Material-UI or equivalent
- **State Management**: Redux/Context API
- **API Client**: Axios/Fetch

### DevOps & Deployment
- **Container**: Docker & Docker Compose
- **Orchestration**: Docker Compose (local), Kubernetes (production-ready)
- **CI/CD**: GitHub Actions (recommended)
- **Monitoring**: Prometheus/Grafana (optional)

### API Documentation
- **Swagger/OpenAPI**: Automatic at `/docs` endpoint
- **ReDoc**: Alternative docs at `/redoc` endpoint

---

## Integration Flows

### Flow 1: Employee Creates Leave Request

```
1. Employee submits leave request via frontend
   ↓
2. Leave Service receives request
   ├─ Validates employee exists (Employee Service)
   ├─ Checks leave policies (Compliance Service)
   ├─ Saves to database
   └─ Logs action (Audit Service)
   ↓
3. Notification Service sends:
   ├─ Confirmation to employee
   └─ Alert to manager
   ↓
4. Manager approves/rejects leave
   ├─ Leave Service updates status
   ├─ Logs action (Audit Service)
   └─ Notification Service notifies employee
   ↓
5. Frontend displays updated leave request
```

### Flow 2: Employee Checks In

```
1. Employee initiates check-in via mobile/web
   ↓
2. Attendance Service records check-in
   ├─ Verifies employee (Employee Service)
   ├─ Records timestamp, location, device
   ├─ Logs action (Audit Service)
   └─ Checks against leave (Leave Service)
   ↓
3. Compliance Service validates check-in time
   ↓
4. Notification Service sends confirmation
   ↓
5. Frontend displays check-in confirmation
```

### Flow 3: Overnight Attendance Processing

```
1. Scheduled job runs at end of day
   ↓
2. For each employee:
   ├─ Get check-in/check-out records
   ├─ Calculate working hours
   ├─ Check against leave records
   ├─ Validate compliance rules
   └─ Log processing (Audit Service)
   ↓
3. Generate daily statistics
   ├─ Mark as Present/Absent/On Leave
   ├─ Calculate overtime
   └─ Detect late arrivals
   ↓
4. Send notifications for exceptions
   ├─ Late arrivals to managers
   ├─ Absences to HR
   └─ Incomplete checkouts to employees
```

---

## Documentation Structure

### Main Documentation Files

1. **MICROSERVICES_INTEGRATION.md**
   - Comprehensive microservices architecture
   - Service responsibilities and APIs
   - Communication patterns
   - Data models
   - Integration flows
   - Error handling strategies

2. **DEPLOYMENT_GUIDE.md**
   - Quick start instructions
   - Docker Compose setup
   - Service configuration
   - Database management
   - Troubleshooting guide
   - Production deployment checklist

3. **INTEGRATION_OVERVIEW.md** (this file)
   - Project overview
   - System architecture
   - Service descriptions
   - Quick start guide
   - Technology stack

### Service-Specific Documentation

Each microservice has its own documentation:

- **Employee Service**: `employee-management-service/README.md`
- **Leave Service**: `leave-management-service/README.md`
- **Attendance Service**: `attendance-management-service/README.md`
- **Notification Service**: `notification-service/README.md`
- **Audit Service**: `audit-service/README.md`
- **Compliance Service**: `compliance-service/README.md`
- **User Service**: `user-management-service/README.md`

### API Documentation

Each service exposes interactive API documentation:
- **Swagger UI**: `/docs` endpoint
- **ReDoc**: `/redoc` endpoint
- **OpenAPI JSON**: `/openapi.json`

---

## Environment Variables

### Core Configuration

```env
# Database
DB_HOST=mysql
DB_PORT=3306
DB_USER=hrms_user
DB_PASSWORD=hrms_password

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
JWKS_URL=https://auth-provider/jwks

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8001

# Services
EMPLOYEE_SERVICE_URL=http://employee-service:8000/api/v1
LEAVE_SERVICE_URL=http://leave-service:8000/api/v1
ATTENDANCE_SERVICE_URL=http://attendance-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8000/api/v1

# Email/SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=hrms@company.com
SMTP_FROM_NAME=HRMS System
```

---

## Project Structure

```
hr-management-system/
├── employee-management-service/          # Employee management microservice
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── leave-management-service/             # Leave request management
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── attendance-management-service/        # Attendance tracking
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── notification-service/                 # Notification delivery
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── audit-service/                        # Audit logging service
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── compliance-service/                   # Compliance management
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── user-management-service/              # Authentication & authorization
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── hrms_frontend/                        # React frontend application
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml                    # Docker Compose orchestration
├── MICROSERVICES_INTEGRATION.md           # Integration architecture
├── DEPLOYMENT_GUIDE.md                    # Deployment instructions
├── INTEGRATION_OVERVIEW.md                # This file
└── .env                                  # Environment variables (create from .env.example)
```

---

## Common Commands

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose stop

# Remove everything
docker-compose down -v

# Rebuild services
docker-compose build --no-cache
```

### Database

```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -p

# Backup database
docker-compose exec mysql mysqldump -u root -p --all-databases > backup.sql

# List databases
docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"
```

### Testing

```bash
# Test service health
curl http://localhost:8001/health

# Test all services
./test_services.sh  # See DEPLOYMENT_GUIDE.md for script

# Run specific service tests
docker-compose exec employee-service pytest tests/
```

---

## Getting Help

### Documentation
- Read `MICROSERVICES_INTEGRATION.md` for detailed architecture
- Read `DEPLOYMENT_GUIDE.md` for setup and troubleshooting
- Check service-specific README files
- Visit `/docs` endpoint in any service for API documentation

### Troubleshooting
1. Check logs: `docker-compose logs [service-name]`
2. Verify connectivity: `docker-compose exec [service] curl http://other-service:8000/health`
3. Check database: `docker-compose exec mysql mysql -u root -p -e "SELECT 1;"`
4. Review error messages in logs for specific issues

### Contact
- **Platform Engineering Team**: [contact info]
- **Issues**: Create GitHub issue with logs and error messages
- **Documentation**: Check service README files

---

## Roadmap & Future Enhancements

### Phase 1 (Current)
✅ Microservices architecture
✅ Core services (Employee, Leave, Attendance)
✅ Audit logging
✅ Notification system
✅ Docker deployment

### Phase 2 (Planned)
- [ ] Message queue integration (RabbitMQ/Kafka)
- [ ] Service mesh (Istio)
- [ ] Advanced caching (Redis)
- [ ] GraphQL API layer
- [ ] Enhanced security (OAuth2)

### Phase 3 (Future)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and reporting
- [ ] ML-based anomaly detection
- [ ] Workflow automation
- [ ] Multi-tenancy support

---

## License

This project is licensed under the [Your License Type] License. See LICENSE file for details.

---

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

---

## Support & Community

- **Documentation**: See all markdown files in this directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@company.com

---

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: January 2024
- **Status**: Production Ready
- **Last Updated**: January 10, 2024

---

## Acknowledgments

- FastAPI community and documentation
- React and React ecosystem
- Open source contributors
- Platform Engineering Team

---

**For detailed integration architecture, see [MICROSERVICES_INTEGRATION.md](MICROSERVICES_INTEGRATION.md)**

**For deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

**For API documentation, visit service endpoints at `/docs`**

---

Generated: January 2024  
Maintained By: Platform Engineering Team  
Status: Active ✓