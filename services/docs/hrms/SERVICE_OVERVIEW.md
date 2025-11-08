# HRMS Microservices - Complete Service Overview & Architecture

## System Architecture Overview

The HR Management System (HRMS) is built as a microservices architecture with 7 independent services that communicate via REST APIs. Each service is containerized with Docker and connected through a PostgreSQL database backend.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/Vue)                      │
└──────────┬──────────────────────────────────────────────────────┘
           │
    ┌──────┴─────────────────────────────────────────────────┐
    │                                                         │
┌───▼────────────────┐  ┌──────────────────┐  ┌────────────▼─────┐
│   User Management  │  │   Employee Mgmt  │  │  Attendance Mgmt  │
│   Service (8001)   │  │  Service (8002)  │  │  Service (8003)   │
│                    │  │                  │  │                   │
│ • Auth (OAuth2)    │  │ • CRUD Ops       │  │ • Check-in/out    │
│ • User Mgmt        │  │ • Profile Info   │  │ • Records         │
│ • Roles/Perms      │  │ • Departments    │  │ • Monthly Summary │
└────────────────────┘  └──────────────────┘  └───────────────────┘

┌──────────────────────┐  ┌──────────────────┐  ┌────────────────┐
│  Leave Management    │  │  Notification    │  │  Audit Service │
│  Service (8004)      │  │  Service (8005)  │  │  (8006)        │
│                      │  │                  │  │                │
│ • Leave Requests     │  │ • Email Send     │  │ • Audit Logs   │
│ • Approvals          │  │ • Status Track   │  │ • Trail Mgmt   │
│ • Status Workflow    │  │ • Retry Logic    │  │ • Compliance   │
└──────────────────────┘  └──────────────────┘  └────────────────┘

                    ┌──────────────────────────┐
                    │ Compliance Service (8007)│
                    │                          │
                    │ • GDPR Compliance        │
                    │ • Data Inventory         │
                    │ • Access Controls        │
                    │ • Retention Policies     │
                    └──────────────────────────┘

           ┌─────────────────────────────────────┐
           │    Shared PostgreSQL Database       │
           │                                     │
           │ • user_management DB               │
           │ • employee_management DB           │
           │ • attendance_management DB         │
           │ • leave_management DB              │
           │ • notification_management DB       │
           │ • audit_management DB              │
           │ • compliance_management DB         │
           └─────────────────────────────────────┘
```

---

## 1. USER MANAGEMENT SERVICE (Port 8001)

### Purpose
Centralized authentication and authorization service. Integrates with Asgardeo (WSO2) for OAuth2/OIDC-based authentication. Manages user lifecycle, roles, permissions, and access control.

### Key Features
- **OAuth2/OIDC Authentication**: Integration with Asgardeo identity provider
- **JWT Token Management**: Secure token generation and validation
- **Role-Based Access Control (RBAC)**: Admin, Manager, HR, Employee roles
- **User Lifecycle**: Create, activate, suspend, delete users
- **Permission Management**: Granular permission assignment
- **User Synchronization**: Sync users from Asgardeo

### Main Endpoints
```
Authentication:
POST   /auth/signup                    - User registration
POST   /auth/oauth-callback            - OAuth callback handler
POST   /auth/logout                    - User logout
GET    /auth/whoami                    - Current user info
GET    /auth/verify-token              - Token validation
PUT    /auth/change-password           - Change password

User Management:
GET    /users                          - List users
GET    /users/{user_id}                - Get user details
PATCH  /users/{user_id}/role           - Update role
PUT    /users/{user_id}/suspend        - Suspend user
PUT    /users/{user_id}/activate       - Activate user
DELETE /users/{user_id}                - Delete user
GET    /roles                          - List roles
GET    /users/{user_id}/permissions    - Get permissions
POST   /users/sync-asgardeo            - Sync from Asgardeo
```

### Database Tables
- `users` - User accounts
- `roles` - Role definitions
- `permissions` - Permission definitions
- `user_roles` - User-role mappings
- `role_permissions` - Role-permission mappings

### Dependencies
- Asgardeo Identity Provider
- JWT Library (PyJWT)
- SQLModel ORM

### Security Features
- JWT token-based authentication
- Password strength validation
- OAuth2 integration
- Role-based access control
- Token expiration and refresh

---

## 2. EMPLOYEE MANAGEMENT SERVICE (Port 8002)

### Purpose
Central repository for employee information. Manages employee records, personal details, departmental information, and organizational structure.

### Key Features
- **Employee CRUD Operations**: Create, read, update, delete employee records
- **Profile Management**: Store comprehensive employee information
- **Department Tracking**: Organizational hierarchy
- **Employment History**: Hire dates, positions, salary tracking
- **Employee Verification**: Service used by other microservices to verify employee existence

### Main Endpoints
```
POST   /employees                      - Create employee
GET    /employees                      - List employees (pagination)
GET    /employees/{employee_id}        - Get employee details
PATCH  /employees/{employee_id}        - Update employee
DELETE /employees/{employee_id}        - Delete employee
```

### Database Tables
- `employees` - Employee master records
- `departments` - Department information
- `positions` - Position/job title definitions
- `employee_history` - Employment history

### Data Model
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@company.com",
  "department": "IT",
  "position": "Senior Developer",
  "hire_date": "2022-01-15",
  "phone": "+1-555-0123",
  "address": "123 Main St",
  "status": "active",
  "salary": 75000
}
```

### Dependencies
- User Management Service (for user verification)
- PostgreSQL Database

### Key Relationships
- One-to-Many: Employee → Attendance Records
- One-to-Many: Employee → Leave Requests
- One-to-Many: Employee → Notifications
- Many-to-One: Employee ← Department

---

## 3. ATTENDANCE MANAGEMENT SERVICE (Port 8003)

### Purpose
Tracks employee attendance, working hours, and attendance patterns. Provides real-time check-in/check-out functionality and monthly attendance summaries.

### Key Features
- **Real-time Check-In/Check-Out**: Record employee presence
- **Manual Attendance Entry**: Admin can manually record attendance
- **Attendance Records**: Store check-in/check-out times and status
- **Monthly Summaries**: Aggregate statistics (present, absent, late counts)
- **Working Hours Calculation**: Total hours worked per day/month
- **Date Range Filtering**: Query attendance for specific periods

### Main Endpoints
```
Check-in/Check-out:
POST   /attendance/check-in             - Employee check-in
POST   /attendance/check-out            - Employee check-out
POST   /attendance/manual               - Manual entry (Admin)

Query:
GET    /attendance/{attendance_id}      - Get record
GET    /attendance/employee/{emp_id}    - List records
GET    /attendance/summary/{emp_id}/{month} - Monthly summary
PUT    /attendance/{attendance_id}      - Update record
DELETE /attendance/{attendance_id}      - Delete record

Utility:
GET    /attendance/health               - Health check
```

### Database Tables
- `attendance` - Individual attendance records
- `attendance_summary` - Monthly aggregated data
- `attendance_status` - Status reference (present, absent, late)

### Data Model
```json
{
  "id": 1,
  "employee_id": 1,
  "date": "2024-01-15",
  "check_in_time": "2024-01-15T09:00:00Z",
  "check_out_time": "2024-01-15T17:30:00Z",
  "status": "present",
  "working_hours": 8.5,
  "notes": "Regular day"
}
```

### Workflow
1. Employee checks in → Record check_in_time, set status to "present"
2. Employee checks out → Record check_out_time
3. System calculates working hours automatically
4. Admin can override or manually create entries

### Integration Points
- Verifies employee exists with Employee Service
- Logs audit events to Audit Service
- Sends notifications for attendance events

---

## 4. LEAVE MANAGEMENT SERVICE (Port 8004)

### Purpose
Manages employee leave requests, approvals, and leave policies. Implements a multi-step workflow for leave request processing.

### Key Features
- **Leave Request Creation**: Employees submit leave requests
- **Status Workflow**: PENDING → APPROVED/REJECTED → CANCELLED
- **Date Validation**: Ensures start_date < end_date
- **Manager Approval**: Managers approve/reject requests
- **Leave History**: Track all leave requests and history
- **Status Filtering**: Query by leave status

### Main Endpoints
```
POST   /leaves                         - Create leave request
GET    /leaves                         - List requests (filter by status)
GET    /leaves/{leave_id}              - Get request details
GET    /leaves/employee/{emp_id}       - List employee requests
PUT    /leaves/{leave_id}              - Update status (approve/reject)
DELETE /leaves/{leave_id}              - Cancel request
```

### Database Tables
- `leaves` - Leave request records
- `leave_types` - Leave type definitions (vacation, sick, emergency, etc.)
- `leave_status_history` - Status change history

### Leave Status Workflow
```
Creation (PENDING)
    ↓
Manager Review
    ├→ APPROVED (with approved_by)
    ├→ REJECTED (with rejection_reason)
    └→ (stays PENDING)
    
At any point:
    → CANCELLED (employee initiated)
```

### Data Model
```json
{
  "id": 1,
  "employee_id": 1,
  "start_date": "2024-01-15",
  "end_date": "2024-01-20",
  "reason": "Family vacation",
  "leave_type": "vacation",
  "status": "PENDING",
  "approved_by": null,
  "rejection_reason": null,
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-10T10:00:00Z"
}
```

### Validation Rules
- Employee must exist in Employee Service
- start_date must be before end_date
- Cannot approve already rejected leaves
- Can only cancel PENDING or APPROVED leaves
- Rejection requires rejection_reason
- Approval requires approved_by field

### Integration Points
- Employee Service: Verify employee exists
- Notification Service: Send approval/rejection notifications
- Audit Service: Log leave status changes
- Compliance Service: Track data for GDPR compliance

---

## 5. NOTIFICATION SERVICE (Port 8005)

### Purpose
Handles all notification delivery, primarily email notifications. Implements background task processing for asynchronous email sending with retry logic.

### Key Features
- **Email Notification Sending**: Send emails asynchronously
- **Status Tracking**: Track notification delivery status
- **Retry Mechanism**: Automatic retry for failed sends (max 3 attempts)
- **Background Processing**: FastAPI background tasks
- **Notification History**: Store all notifications for audit trail
- **Status Categories**: PENDING, SENT, FAILED, RETRYING

### Main Endpoints
```
POST   /notifications/send             - Send notification
GET    /notifications/{notification_id} - Get notification
GET    /notifications                  - List notifications (filter by status)
GET    /notifications/employee/{emp_id} - List employee notifications
PUT    /notifications/{notification_id}/retry - Retry failed
```

### Database Tables
- `notifications` - Notification records
- `notification_status` - Status reference
- `email_template` - Email templates

### Data Model
```json
{
  "id": 1,
  "employee_id": 1,
  "recipient_email": "john@company.com",
  "recipient_name": "John Doe",
  "subject": "Leave Request Approved",
  "body": "Your leave request has been approved.",
  "notification_type": "leave_approval",
  "status": "SENT",
  "sent_at": "2024-01-15T10:30:00Z",
  "retry_count": 0,
  "error_message": null,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Notification Status Lifecycle
```
POST /send
    ↓
PENDING (created in DB)
    ↓
Background Task Triggered
    ├→ Email sent successfully
    │   └→ SENT
    └→ Email failed
        ├→ Retry attempts < 3
        │   └→ RETRYING
        └→ Max retries exceeded
            └→ FAILED
```

### Configuration
- SMTP server settings
- Email templates
- Retry policy (3 attempts)
- Background task timeout

### Integration Points
- Used by Leave Service for approval notifications
- Used by Attendance Service for attendance alerts
- Used by Employee Service for account notifications
- Logs events to Audit Service

---

## 6. AUDIT SERVICE (Port 8006)

### Purpose
Comprehensive audit logging system. Tracks all significant actions across all microservices for compliance, security, and operational purposes.

### Key Features
- **Comprehensive Logging**: Log all CRUD operations
- **Multi-filter Querying**: Search by user, action type, service, entity, date range
- **Audit Trail**: Complete history of changes
- **User Tracking**: Track actions by user ID
- **Service Tracking**: Know which service performed actions
- **Status Tracking**: Log success/failure of operations

### Main Endpoints
```
POST   /audit-logs                     - Create audit log (internal)
GET    /audit-logs                     - List with advanced filtering
GET    /audit-logs/{audit_id}          - Get log entry
GET    /audit-logs/user/{user_id}      - Get user's audit history
GET    /audit-logs/type/{log_type}     - Get logs by type
PATCH  /audit-logs/{audit_id}          - Update log
DELETE /audit-logs/{audit_id}          - Delete log (caution!)
```

### Database Tables
- `audit_logs` - Audit log entries
- `audit_log_types` - Log type reference
- `audit_actions` - Action reference

### Data Model
```json
{
  "id": 1,
  "user_id": "user123",
  "action": "created",
  "log_type": "leave_request",
  "entity_type": "Leave",
  "entity_id": "leave456",
  "service_name": "leave-management-service",
  "status": "success",
  "description": "Leave request created for employee",
  "new_values": "{\"status\": \"PENDING\", \"days\": 5}",
  "old_values": null,
  "timestamp": "2024-01-15T10:00:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

### Audit Log Types
- `created` - Resource created
- `updated` - Resource modified
- `deleted` - Resource deleted
- `viewed` - Resource accessed
- `leave_request` - Leave-specific actions
- `attendance` - Attendance-specific actions
- `user_management` - User actions
- `permission_change` - Permission changes

### Compliance Features
- Immutable audit trail (append-only)
- Timestamp tracking
- User identification
- Action categorization
- Search and filter capabilities

### Integration Points
- All services call this service to log events
- Called for every significant operation
- Supports compliance reporting

---

## 7. COMPLIANCE SERVICE (Port 8007)

### Purpose
Ensures GDPR compliance and data governance. Provides transparency regarding data processing, access controls, and retention policies.

### Key Features
- **Data Inventory (GDPR Article 30)**: Complete map of all data
- **Right of Access (GDPR Article 15)**: Employee access to their data
- **Access Control Transparency**: Show what data each employee can access
- **Data Retention (GDPR Article 5)**: Retention policies and schedules
- **Encryption Status**: Track encryption for sensitive data
- **Third-party Sharing**: Document external data recipients

### Main Endpoints
```
GET    /compliance/data-inventory      - Data inventory (GDPR Art 30)
GET    /compliance/employee/{emp_id}/data-about-me - Right of Access (Art 15)
GET    /compliance/employee/{emp_id}/access-controls - Access control info
GET    /compliance/data-retention-report - Retention policy (Art 5)
```

### Database Tables
- `data_inventory` - Data categories and classifications
- `data_category` - Category definitions
- `employee_data_access` - Access control records
- `data_retention` - Retention policies
- `data_encryption_status` - Encryption tracking

### Data Model - Data Inventory
```json
{
  "id": 1,
  "data_name": "Employee Personal Information",
  "description": "Name, email, phone, address",
  "category_id": 1,
  "data_type": "personal",
  "storage_location": "PostgreSQL DB",
  "purpose_of_processing": "HR operations and employee management",
  "legal_basis": "Employment Contract",
  "retention_days": 365,
  "retention_policy": "Delete 1 year after employment termination",
  "data_subjects": "Employees",
  "recipients": "HR Department, Managers",
  "third_party_sharing": false,
  "third_party_recipients": [],
  "encryption_status": "AES-256",
  "access_control_level": "role-based"
}
```

### GDPR Compliance Implementation

#### Article 30 - Records of Processing Activities (ROPA)
- `GET /compliance/data-inventory`
- Shows all data processed by the system
- Includes storage location, purpose, legal basis
- Lists recipients and third-party sharing

#### Article 15 - Right of Access
- `GET /compliance/employee/{emp_id}/data-about-me`
- Employees can request their personal data
- Shows all data collected about them
- Lists deletion schedules
- Restricted: Employees see only their own data

#### Article 5 - Storage Limitation
- `GET /compliance/data-retention-report`
- Shows retention policies for all data
- Lists deletion schedules
- Tracks data lifecycle

### Data Protection Features
- Role-based access control
- Encryption status tracking
- Access logging
- Data retention policies
- Third-party tracking
- Right to erasure support

### Integration Points
- Employee Service: Get employee data
- Attendance Service: Track attendance data retention
- Leave Service: Track leave data retention
- Audit Service: Log compliance activities

---

## Cross-Service Communication

### Service Dependencies
```
User Management Service
    ↓ (provides authentication)
Employee Management Service
    ↓ (depends on User Service)
    ├→ Attendance Service (uses for employee verification)
    ├→ Leave Service (uses for employee verification)
    ├→ Notification Service (sends notifications)
    └→ Audit Service (logs events)

Compliance Service
    ↓ (depends on Employee Service)
    └→ Aggregates data from all services
```

### Inter-Service API Calls

#### Employee Service → User Service
- Verify JWT token validity
- Get user information

#### Attendance Service → Employee Service
```
GET /employees/{employee_id}
(Verify employee exists before recording attendance)
```

#### Leave Service → Employee Service
```
GET /employees/{employee_id}
(Verify employee exists before creating leave)
```

#### Leave Service → Notification Service
```
POST /notifications/send
{
  "employee_id": 1,
  "recipient_email": "...",
  "subject": "Leave Approved",
  "body": "..."
}
```

#### All Services → Audit Service
```
POST /audit-logs
{
  "user_id": "user123",
  "action": "created",
  "service_name": "leave-management-service",
  ...
}
```

---

## Authentication & Authorization Flow

### 1. User Authentication
```
User → /auth/signup or /auth/oauth-callback
    ↓
User Management Service validates credentials
    ↓
Asgardeo Identity Provider verifies (for OAuth)
    ↓
JWT token generated
    ↓
User receives token
```

### 2. Service-to-Service Authentication
```
Service A needs data from Service B
    ↓
Service A includes user's JWT in Authorization header
    ↓
Service B extracts and validates JWT
    ↓
Service B checks user roles/permissions
    ↓
If authorized → Return data
If not authorized → Return 403 Forbidden
```

### 3. Authorization Checks
```
Request arrives at endpoint
    ↓
Authentication middleware validates JWT
    ↓
Extract user roles from JWT claims
    ↓
Check if user has required role
    ↓
If authorized → Process request
If not authorized → Return 403 Forbidden
```

---

## Data Flow Examples

### Leave Request Workflow
```
1. Employee submits leave request
   POST /leaves
   {
     "employee_id": 1,
     "start_date": "2024-01-15",
     "end_date": "2024-01-20"
   }

2. Leave Service verifies employee exists
   GET /employees/1 (to Employee Service)

3. Leave request created in database
   Status: PENDING

4. Audit log created
   POST /audit-logs (to Audit Service)

5. Manager reviews and approves
   PUT /leaves/{id}
   {
     "status": "APPROVED",
     "approved_by": "manager123"
   }

6. Notification sent to employee
   POST /notifications/send (to Notification Service)

7. Background task sends email

8. Audit log updated
   Status: SENT
```

### Check-In Workflow
```
1. Employee checks in
   POST /attendance/check-in
   {
     "employee_id": 1
   }

2. Verify employee exists
   GET /employees/1 (to Employee Service)

3. Check for existing today's record
   Query: WHERE date = TODAY

4. If exists: Update with check_in_time
   If not: Create new record

5. Audit log created
   POST /audit-logs (to Audit Service)

6. Return attendance record
```

---

## Database Architecture

### Database Per Service Pattern
Each service has its own database schema, preventing tight coupling:

```
User Management DB
├── users
├── roles
├── permissions
└── user_roles

Employee Management DB
├── employees
├── departments
└── positions

Attendance Management DB
├── attendance
├── attendance_summary
└── attendance_status

Leave Management DB
├── leaves
├── leave_types
└── leave_status_history

Notification DB
├── notifications
├── notification_status
└── email_template

Audit DB
├── audit_logs
├── audit_log_types
└── audit_actions

Compliance DB
├── data_inventory
├── data_category
├── employee_data_access
├── data_retention
└── data_encryption_status
```

### Key Relationships Across Services
```
employees.id ← attendance.employee_id
employees.id ← leaves.employee_id
employees.id ← notifications.employee_id
users.id ← audit_logs.user_id (as string)
```

---

## Error Handling Strategy

### HTTP Status Codes
```
200 OK              - Successful GET, PUT
201 Created         - Successful POST
400 Bad Request     - Validation error, invalid input
401 Unauthorized    - Missing/invalid authentication
403 Forbidden       - Insufficient permissions
404 Not Found       - Resource doesn't exist
500 Server Error    - Internal server error
```

### Error Response Format
```json
{
  "detail": "Descriptive error message",
  "status_code": 400
}
```

### Common Validation Errors
- Missing required fields
- Invalid date format (use YYYY-MM-DD)
- Employee ID doesn't exist
- Leave dates invalid (start >= end)
- User lacks required role
- Resource already exists

---

## Security Measures

### Authentication
- JWT tokens with expiration
- OAuth2/OIDC via Asgardeo
- Secure password storage (hashed)

### Authorization
- Role-based access control (RBAC)
- Permission-based fine-grained access
- Self-service data access (GDPR compliance)

### Data Protection
- HTTPS/TLS for transport
- Database encryption for sensitive fields
- SQL injection prevention (ORM usage)
- CORS protection

### Audit & Compliance
- Comprehensive audit logging
- GDPR Article 15 (Right of Access) implementation
- GDPR Article 30 (ROPA) implementation
- GDPR Article 5 (Storage Limitation) implementation
- Data retention policies

---

## Deployment & Containerization

### Docker Containers
Each service runs in its own Docker container:
```
user-management-service:8001
employee-management-service:8002
attendance-management-service:8003
leave-management-service:8004
notification-service:8005
audit-service:8006
compliance-service:8007
```

### Docker Compose
```yaml
services:
  user-management:
    image: user-management-service:latest
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - JWT_SECRET_KEY=...
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=...
```

### Environment Variables
Each service requires:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for token signing
- `ASGARDEO_CLIENT_ID` - OAuth client ID
- `ASGARDEO_CLIENT_SECRET` - OAuth client secret
- `SMTP_HOST`, `SMTP_PORT` - Email service
- `LOG_LEVEL` - Logging verbosity

---

## Performance & Scalability

### Pagination
- Default limit: 100 records
- Maximum limit: 100-1000 depending on endpoint
- Use offset/limit for large datasets

### Database Optimization
- Indexed columns: user_id, employee_id, date, status
- Connection pooling
- Query optimization

### Background Processing
- Notification emails sent asynchronously
- No blocking operations in request handlers
- FastAPI background tasks

### Monitoring & Logging
- Structured logging with contextual information
- Health check endpoints
- Service-to-service communication logging
- Audit trail for compliance

---

## Future Enhancements

### Potential Improvements
1. **Caching Layer** - Redis for frequently accessed data
2. **Message Queue** - RabbitMQ for async messaging
3. **API Gateway** - Kong or similar for request routing
4. **Monitoring** - Prometheus + Grafana for metrics
5. **Tracing** - OpenTelemetry for distributed tracing
6. **Rate Limiting** - Per-user or per-service limits
7. **GraphQL API** - Alongside REST APIs
8. **Batch Processing** - For large-scale attendance/payroll
9. **Mobile App** - Native mobile clients
10. **Advanced Reporting** - BI dashboards and reports

---

## Conclusion

The HRMS microservices architecture provides:
- **Scalability**: Independent scaling of each service
- **Flexibility**: Services can be updated independently
- **Resilience**: Failure in one service doesn't affect others
- **Security**: Role-based access control and audit trails
- **Compliance**: GDPR compliance built-in
- **Maintainability**: Clear separation of concerns

Each service is focused, independently deployable, and communicates via well-defined REST APIs, enabling rapid development and deployment of new features.

---

**Document Version**: 1.0
**Last Updated**: 2024
**Framework**: FastAPI (Python)
**Database**: PostgreSQL
**Container**: Docker