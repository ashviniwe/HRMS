# HRMS Microservices Integration Architecture

## Overview

This document describes the integration architecture for the HRMS (Human Resource Management System) microservices ecosystem. It defines how services communicate, share data, and maintain consistency across the system.

## Services Architecture

### 1. Employee Management Service
**Purpose**: Central repository for all employee information and master data

**Key Endpoints**:
- `GET /api/v1/employees` - List all employees
- `GET /api/v1/employees/{employee_id}` - Get employee details
- `POST /api/v1/employees` - Create new employee
- `PUT /api/v1/employees/{employee_id}` - Update employee
- `DELETE /api/v1/employees/{employee_id}` - Delete employee
- `GET /api/v1/employees/{employee_id}/verify` - Verify employee exists

**Business Functions**:
- Employee CRUD operations
- Department and role management
- Salary and compensation tracking
- Employee status management (active, inactive, leave, etc.)

**Integration Points**:
- Called by: Leave Service (employee verification), Attendance Service (employee verification)
- Calls: Audit Service (log changes), Notification Service (notify on employee updates)
- Events: employee_created, employee_updated, employee_deleted, employee_status_changed

---

### 2. Leave Management Service
**Purpose**: Manage employee leave requests and approvals

**Key Endpoints**:
- `POST /api/v1/leaves` - Create leave request
- `GET /api/v1/leaves/{employee_id}` - Get employee's leave history
- `PUT /api/v1/leaves/{leave_id}/approve` - Approve leave
- `PUT /api/v1/leaves/{leave_id}/reject` - Reject leave
- `GET /api/v1/leaves/{leave_id}/balance` - Get leave balance
- `POST /api/v1/leaves/{leave_id}/cancel` - Cancel leave request

**Business Functions**:
- Leave request creation and management
- Leave approval workflow
- Leave balance tracking
- Leave policy enforcement
- Leave type categorization (sick, casual, annual, etc.)

**Integration Points**:
- Calls: Employee Service (employee verification), Audit Service (log all operations)
- Notifies via: Notification Service (employee, manager, HR)
- Compliance checks via: Compliance Service (leave policy validation)
- Updates: Employee records (leave balance deductions)

**Workflow**:
```
Employee Creates Leave Request
    ↓
Validates Employee Exists (Employee Service)
    ↓
Checks Leave Policy (Compliance Service)
    ↓
Creates Audit Log (Audit Service)
    ↓
Sends Notification to Manager (Notification Service)
    ↓
Manager Approves/Rejects Leave
    ↓
Updates Leave Status
    ↓
Logs Status Change (Audit Service)
    ↓
Sends Notification to Employee (Notification Service)
```

---

### 3. Attendance Management Service
**Purpose**: Track employee attendance and working hours

**Key Endpoints**:
- `POST /api/v1/attendance/check-in` - Record check-in
- `POST /api/v1/attendance/check-out` - Record check-out
- `GET /api/v1/attendance/{employee_id}` - Get attendance history
- `GET /api/v1/attendance/{employee_id}/monthly` - Get monthly summary
- `POST /api/v1/attendance/manual-entry` - Manually add attendance record
- `GET /api/v1/attendance/{employee_id}/late-arrivals` - Get late arrival records

**Business Functions**:
- Check-in/Check-out recording
- Attendance tracking and reporting
- Late arrival detection
- Working hours calculation
- Absenteeism tracking
- Overtime calculation

**Integration Points**:
- Calls: Employee Service (employee verification), Audit Service (log check-ins/outs)
- Notifies via: Notification Service (attendance alerts, late notifications)
- Integrates with: Leave Service (exclude leave days from attendance)
- Compliance checks: Validate attendance rules (Compliance Service)

**Workflow**:
```
Employee Initiates Check-In
    ↓
Validates Employee Exists (Employee Service)
    ↓
Records Check-In with Timestamp, Location, Device Info
    ↓
Creates Audit Log (Audit Service)
    ↓
Notifies: Send arrival notification (Notification Service)
    ↓
[At End of Day]
    ↓
Employee Initiates Check-Out
    ↓
Validates Against Check-In Time
    ↓
Calculates Working Hours
    ↓
Creates Audit Log (Audit Service)
    ↓
[Overnight Processing]
    ↓
Calculate Daily Statistics
    ↓
Check Against Leave Records (Leave Service)
    ↓
Run Compliance Checks (Compliance Service)
    ↓
Log Exceptions (Audit Service)
```

---

### 4. Notification Service
**Purpose**: Central notification hub for all system communications

**Key Endpoints**:
- `POST /api/v1/notifications/send` - Send notification
- `POST /api/v1/notifications/email` - Send email
- `POST /api/v1/notifications/bulk` - Send bulk notifications
- `GET /api/v1/notifications/{user_id}` - Get user notifications
- `PUT /api/v1/notifications/{notification_id}/mark-read` - Mark as read
- `GET /api/v1/notifications/{user_id}/unread` - Get unread notifications

**Business Functions**:
- Email notifications
- In-app notifications
- SMS notifications (if configured)
- Push notifications (if configured)
- Notification templates
- Notification history

**Integration Points**:
- Called by: All other services (Employee, Leave, Attendance, Compliance)
- No dependencies on other services except configuration
- Independent operation

**Notification Types**:
```
leave.request_created - When employee creates leave request
leave.request_approved - When manager approves leave
leave.request_rejected - When manager rejects leave
leave.request_cancelled - When employee cancels leave

employee.created - When new employee is added
employee.updated - When employee data is updated
employee.deleted - When employee is deleted
employee.status_changed - When employee status changes

attendance.checked_in - When employee checks in
attendance.checked_out - When employee checks out
attendance.late - When employee is marked late
attendance.absent - When employee is absent

compliance.policy_updated - When compliance policy changes
compliance.violation_detected - When policy violation is detected
compliance.training_due - When compliance training is due

audit.critical_event - For critical audit events
```

---

### 5. Audit Service
**Purpose**: Centralized audit logging and compliance tracking

**Key Endpoints**:
- `POST /api/v1/audit-logs` - Create audit log
- `GET /api/v1/audit-logs` - Query audit logs
- `GET /api/v1/audit-logs/{audit_id}` - Get specific log
- `GET /api/v1/audit-logs/user/{user_id}` - Get user's activities
- `GET /api/v1/audit-logs/type/{log_type}` - Get logs by type
- `GET /api/v1/audit-logs/export` - Export audit logs

**Business Functions**:
- Centralized audit trail logging
- Compliance event tracking
- User activity logging
- Data change tracking
- Audit report generation
- Data retention management

**Integration Points**:
- Called by: All other services
- No dependencies on other services
- Receives audit events from all services

**Audit Log Types**:
```
leave_request_created
leave_request_approved
leave_request_rejected
leave_request_cancelled

employee_created
employee_updated
employee_deleted
employee_status_changed

attendance_check_in
attendance_check_out
attendance_manual_entry
attendance_correction

compliance_policy_created
compliance_policy_updated
compliance_violation_detected

notification_sent
notification_failed

user_login
user_logout
data_export
```

---

### 6. Compliance Service
**Purpose**: Manage compliance policies and validations

**Key Endpoints**:
- `GET /api/v1/compliance/policies` - List compliance policies
- `POST /api/v1/compliance/policies` - Create policy
- `PUT /api/v1/compliance/policies/{policy_id}` - Update policy
- `POST /api/v1/compliance/validate` - Validate against policies
- `GET /api/v1/compliance/violations` - Get compliance violations
- `GET /api/v1/compliance/training` - Get compliance training records

**Business Functions**:
- Leave policy management (max leave days, carryover rules, etc.)
- Attendance policy management (working hours, shift definitions, etc.)
- Work hour regulations
- Leave carryover policies
- Overtime rules
- Data retention policies

**Integration Points**:
- Called by: Leave Service (validate leave requests), Attendance Service (validate rules)
- Calls: Audit Service (log policy changes)
- Notifies via: Notification Service

**Validation Examples**:
```
Leave Validation:
- Can employee take requested leave type?
- Does employee have sufficient balance?
- Does request comply with notice period?
- Are dates within carryover window?

Attendance Validation:
- Is attendance within working hours?
- Are working hours within allowed shift?
- Is daily overtime within limits?
- Are required breaks taken?
```

---

### 7. User Management Service
**Purpose**: Authentication and authorization (mention for context)

**Key Features**:
- User login/logout
- JWT token management
- Role-based access control
- Password management
- Session management

**Integration Points**:
- All services validate tokens through this service
- Audit Service logs login/logout events

---

## Communication Patterns

### 1. Synchronous Communication (Request/Response)

Used for:
- Employee verification
- Policy validation
- Real-time data retrieval

Example: Attendance Service → Employee Service
```
GET /api/v1/employees/{employee_id}/verify
Response: { "exists": true, "status": "active", "department": "HR" }
```

### 2. Asynchronous Notifications

Used for:
- Status updates
- Event notifications
- Non-critical updates

Example: Leave Service → Notification Service
```
POST /api/v1/notifications/send
{
  "recipient_type": "user",
  "recipient_id": "manager_123",
  "notification_type": "leave.request_created",
  "template": "leave_request_approval_needed",
  "context": {
    "employee_name": "John Doe",
    "leave_type": "Annual Leave",
    "start_date": "2024-01-15",
    "end_date": "2024-01-20",
    "leave_request_id": "leave_456"
  }
}
```

### 3. Audit Logging

All state-changing operations must log to Audit Service:
```
POST /api/v1/audit-logs
{
  "user_id": "emp_123",
  "action": "created",
  "log_type": "leave_request_created",
  "entity_type": "LeaveRequest",
  "entity_id": "leave_456",
  "service_name": "leave-management-service",
  "status": "success",
  "new_values": {
    "leave_type": "Annual",
    "start_date": "2024-01-15",
    "end_date": "2024-01-20",
    "status": "pending"
  },
  "old_values": null,
  "request_id": "req_abc123",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2024-01-10T10:30:45Z"
}
```

---

## Service-to-Service Integration Flows

### Flow 1: Employee Creates Leave Request

```
[1] Employee sends POST /api/v1/leaves
    {
      "employee_id": "emp_123",
      "leave_type": "Annual",
      "start_date": "2024-01-15",
      "end_date": "2024-01-20",
      "reason": "Vacation"
    }

[2] Leave Service validates:
    GET /api/v1/employees/emp_123/verify
    Response: { "exists": true, "status": "active" }

[3] Leave Service checks compliance:
    POST /api/v1/compliance/validate
    {
      "policy": "leave_request",
      "employee_id": "emp_123",
      "leave_type": "Annual",
      "start_date": "2024-01-15",
      "end_date": "2024-01-20"
    }
    Response: { "valid": true, "balance": 5, "required": 6 }

[4] Leave Service creates record in DB

[5] Leave Service logs to Audit Service:
    POST /api/v1/audit-logs
    {
      "user_id": "emp_123",
      "action": "created",
      "log_type": "leave_request_created",
      "entity_type": "LeaveRequest",
      "entity_id": "leave_456",
      "service_name": "leave-management-service",
      "status": "success",
      "new_values": { "leave_type": "Annual", ... }
    }

[6] Leave Service sends notifications:
    POST /api/v1/notifications/send (to manager)
    POST /api/v1/notifications/send (to HR)
    POST /api/v1/notifications/send (confirmation to employee)

[7] Return response to Employee:
    {
      "id": "leave_456",
      "status": "pending",
      "created_at": "2024-01-10T10:30:45Z"
    }
```

### Flow 2: Employee Checks In

```
[1] Employee sends POST /api/v1/attendance/check-in
    {
      "employee_id": "emp_123",
      "location": "Office",
      "device": "Mobile"
    }

[2] Attendance Service verifies employee:
    GET /api/v1/employees/emp_123/verify

[3] Attendance Service records check-in in DB
    - Current timestamp
    - Location
    - Device info

[4] Attendance Service logs to Audit Service:
    POST /api/v1/audit-logs
    {
      "user_id": "emp_123",
      "action": "check_in",
      "log_type": "attendance_check_in",
      "entity_type": "Attendance",
      "entity_id": "att_789",
      "service_name": "attendance-management-service",
      "new_values": { "check_in_time": "2024-01-10T09:00:00Z", "location": "Office" }
    }

[5] Attendance Service sends notification:
    POST /api/v1/notifications/send
    {
      "recipient_type": "user",
      "recipient_id": "emp_123",
      "notification_type": "attendance.checked_in",
      "context": { "check_in_time": "09:00 AM", "location": "Office" }
    }

[6] Return response:
    {
      "check_in_time": "2024-01-10T09:00:00Z",
      "status": "success"
    }
```

### Flow 3: Manager Approves Leave Request

```
[1] Manager sends PUT /api/v1/leaves/leave_456/approve
    {
      "comments": "Approved"
    }

[2] Leave Service updates leave status to "approved" in DB

[3] Leave Service checks if leave is on a weekend/holiday via Compliance Service

[4] Leave Service updates employee leave balance

[5] Leave Service logs to Audit Service:
    POST /api/v1/audit-logs
    {
      "user_id": "manager_111",
      "action": "approved",
      "log_type": "leave_request_approved",
      "entity_type": "LeaveRequest",
      "entity_id": "leave_456",
      "service_name": "leave-management-service",
      "status": "success",
      "old_values": { "status": "pending" },
      "new_values": { "status": "approved" }
    }

[6] Leave Service sends notifications:
    POST /api/v1/notifications/send (to employee - approval)
    POST /api/v1/notifications/send (to HR - notification)

[7] Return response:
    {
      "id": "leave_456",
      "status": "approved",
      "approved_by": "manager_111",
      "approved_at": "2024-01-10T11:00:00Z"
    }
```

### Flow 4: Overnight Attendance Processing

```
[1] Scheduled Job runs at end of day (e.g., 00:30 AM)

[2] For each employee with check-in:
    - Query attendance records: GET /api/v1/attendance?date=2024-01-10

[3] For each attendance record:
    - Get employee details: GET /api/v1/employees/{employee_id}
    - Check if employee was on leave: GET /api/v1/leaves?date=2024-01-10&employee_id={employee_id}
    
[4] Calculate daily statistics:
    - If checked in and not on leave and checked out → Present
    - If checked in and not on leave but didn't check out → Incomplete
    - If not checked in and on leave → Leave day (exclude)
    - If not checked in and not on leave → Absent
    - Calculate worked hours if both check-in and check-out exist

[5] Validate against compliance rules:
    POST /api/v1/compliance/validate
    {
      "policy": "attendance_validation",
      "employee_id": "emp_123",
      "worked_hours": 8.5,
      "attendance_date": "2024-01-10"
    }

[6] Log processing results:
    POST /api/v1/audit-logs
    {
      "user_id": "system",
      "action": "processed",
      "log_type": "attendance_processed",
      "entity_type": "AttendanceDaily",
      "entity_id": "att_daily_emp_123_2024_01_10",
      "service_name": "attendance-management-service",
      "new_values": {
        "status": "present",
        "worked_hours": 8.5,
        "check_in_time": "09:00",
        "check_out_time": "17:30"
      }
    }

[7] Send notifications for exceptions:
    - If late arrival detected:
      POST /api/v1/notifications/send (to manager)
    - If absent:
      POST /api/v1/notifications/send (to HR)
    - If incomplete checkout:
      POST /api/v1/notifications/send (to employee - reminder)
```

---

## Data Models & Exchange Formats

### Employee Model
```json
{
  "id": "emp_123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@company.com",
  "phone": "555-0123",
  "department": "Engineering",
  "role": "Senior Engineer",
  "status": "active",
  "hire_date": "2020-01-15",
  "manager_id": "emp_111",
  "salary": 75000,
  "employment_type": "full_time",
  "created_at": "2020-01-15T08:00:00Z",
  "updated_at": "2024-01-10T10:00:00Z"
}
```

### Leave Model
```json
{
  "id": "leave_456",
  "employee_id": "emp_123",
  "leave_type": "Annual",
  "start_date": "2024-01-15",
  "end_date": "2024-01-20",
  "duration_days": 6,
  "reason": "Vacation",
  "status": "pending",
  "created_by": "emp_123",
  "created_at": "2024-01-10T10:30:45Z",
  "approved_by": null,
  "approved_at": null,
  "rejected_reason": null,
  "cancelled_at": null
}
```

### Attendance Model
```json
{
  "id": "att_789",
  "employee_id": "emp_123",
  "date": "2024-01-10",
  "check_in_time": "2024-01-10T09:00:00Z",
  "check_in_location": "Office",
  "check_in_device": "Mobile",
  "check_out_time": "2024-01-10T17:30:00Z",
  "check_out_location": "Office",
  "check_out_device": "Mobile",
  "worked_hours": 8.5,
  "status": "present",
  "notes": null,
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-10T17:30:00Z"
}
```

### Notification Model
```json
{
  "id": "notif_999",
  "recipient_type": "user",
  "recipient_id": "emp_123",
  "notification_type": "leave.request_created",
  "title": "Leave Request Submitted",
  "body": "Your leave request for Annual Leave from Jan 15-20 has been submitted for approval",
  "template": "leave_request_confirmation",
  "context": {
    "employee_name": "John Doe",
    "leave_type": "Annual",
    "start_date": "2024-01-15",
    "end_date": "2024-01-20"
  },
  "channel": "email",
  "status": "sent",
  "sent_at": "2024-01-10T10:30:46Z",
  "read_at": null,
  "created_at": "2024-01-10T10:30:46Z"
}
```

### Audit Log Model
```json
{
  "id": 1001,
  "user_id": "emp_123",
  "action": "created",
  "log_type": "leave_request_created",
  "entity_type": "LeaveRequest",
  "entity_id": "leave_456",
  "service_name": "leave-management-service",
  "status": "success",
  "description": "Leave request created",
  "old_values": null,
  "new_values": {
    "leave_type": "Annual",
    "start_date": "2024-01-15",
    "end_date": "2024-01-20",
    "status": "pending"
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0",
  "request_id": "req_abc123",
  "error_message": null,
  "timestamp": "2024-01-10T10:30:45Z",
  "created_at": "2024-01-10T10:30:45Z"
}
```

---

## Configuration & Environment Variables

### Employee Management Service
```env
APP_NAME=Employee Management Service
DB_NAME=hrms_employees_db
DB_HOST=mysql
DB_USER=hrms_user
DB_PASSWORD=secure_password
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
JWKS_URL=https://api.asgardeo.io/t/company/oauth2/jwks
```

### Leave Management Service
```env
APP_NAME=Leave Management Service
DB_NAME=hrms_leaves_db
DB_HOST=mysql
DB_USER=hrms_user
DB_PASSWORD=secure_password
EMPLOYEE_SERVICE_URL=http://employee-service:8000/api/v1
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8000/api/v1
JWKS_URL=https://api.asgardeo.io/t/company/oauth2/jwks
```

### Attendance Management Service
```env
APP_NAME=Attendance Management Service
DB_NAME=hrms_attendance_db
DB_HOST=mysql
DB_USER=hrms_user
DB_PASSWORD=secure_password
EMPLOYEE_SERVICE_URL=http://employee-service:8000/api/v1
LEAVE_SERVICE_URL=http://leave-service:8000/api/v1
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
COMPLIANCE_SERVICE_URL=http://compliance-service:8000/api/v1
JWKS_URL=https://api.asgardeo.io/t/company/oauth2/jwks
```

### Notification Service
```env
APP_NAME=Notification Service
DB_NAME=hrms_notifications_db
DB_HOST=mysql
DB_USER=hrms_user
DB_PASSWORD=secure_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=hrms@company.com
SMTP_PASSWORD=app_password
SMTP_FROM_EMAIL=hrms@company.com
SMTP_FROM_NAME=HRMS System
JWKS_URL=https://api.asgardeo.io/t/company/oauth2/jwks
```

### Audit Service
```env
APP_NAME=Audit Service
DB_NAME=audit_service_db
DB_HOST=mysql
DB_USER=hrms_user
DB_PASSWORD=secure_password
RETENTION_DAYS=365
JWKS_URL=https://api.asgardeo.io/t/company/oauth2/jwks
```

### Compliance Service
```env
APP_NAME=Compliance Service
DB_NAME=hrms_compliance_db
DB_HOST=mysql
DB_USER=hrms_user
DB_PASSWORD=secure_password
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
NOTIFICATION_SERVICE_URL=http://notification-service:8000/api/v1
JWKS_URL=https://api.asgardeo.io/t/company/oauth2/jwks
```

---

## Docker Compose Setup

```yaml
version: '3.9'

services:
  # MySQL Database
  mysql:
    image: mysql:8.0
    container_name: hrms_mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_USER: hrms_user
      MYSQL_PASSWORD: secure_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Employee Management Service
  employee-service:
    build:
      context: ./employee-management-service
    container_name: hrms_employee_service
    ports:
      - "8001:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: hrms_employees_db
      AUDIT_SERVICE_URL: http://audit-service:8000/api/v1
      NOTIFICATION_SERVICE_URL: http://notification-service:8000/api/v1
    depends_on:
      mysql:
        condition: service_healthy
      audit-service:
        condition: service_started
      notification-service:
        condition: service_started

  # Leave Management Service
  leave-service:
    build:
      context: ./leave-management-service
    container_name: hrms_leave_service
    ports:
      - "8002:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: hrms_leaves_db
      EMPLOYEE_SERVICE_URL: http://employee-service:8000/api/v1
      AUDIT_SERVICE_URL: http://audit-service:8000/api/v1
      NOTIFICATION_SERVICE_URL: http://notification-service:8000/api/v1
      COMPLIANCE_SERVICE_URL: http://compliance-service:8000/api/v1
    depends_on:
      mysql:
        condition: service_healthy
      employee-service:
        condition: service_started
      audit-service:
        condition: service_started
      notification-service:
        condition: service_started
      compliance-service:
        condition: service_started

  # Attendance Management Service
  attendance-service:
    build:
      context: ./attendance-management-service
    container_name: hrms_attendance_service
    ports:
      - "8003:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: hrms_attendance_db
      EMPLOYEE_SERVICE_URL: http://employee-service:8000/api/v1
      LEAVE_SERVICE_URL: http://leave-service:8000/api/v1
      AUDIT_SERVICE_URL: http://audit-service:8000/api/v1
      NOTIFICATION_SERVICE_URL: http://notification-service:8000/api/v1
      COMPLIANCE_SERVICE_URL: http://compliance-service:8000/api/v1
    depends_on:
      mysql:
        condition: service_healthy
      employee-service:
        condition: service_started
      leave-service:
        condition: service_started
      audit-service:
        condition: service_started
      notification-service:
        condition: service_started
      compliance-service:
        condition: service_started

  # Audit Service
  audit-service:
    build:
      context: ./audit-service
    container_name: hrms_audit_service
    ports:
      - "8004:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: audit_service_db
      RETENTION_DAYS: 365
    depends_on:
      mysql:
        condition: service_healthy

  # Notification Service
  notification-service:
    build:
      context: ./notification-service
    container_name: hrms_notification_service
    ports:
      - "8005:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: hrms_notifications_db
      SMTP_HOST: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USERNAME: ${SMTP_USERNAME}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      SMTP_FROM_EMAIL: ${SMTP_FROM_EMAIL}
    depends_on:
      mysql:
        condition: service_healthy

  # Compliance Service
  compliance-service:
    build:
      context: ./compliance-service
    container_name: hrms_compliance_service
    ports:
      - "8006:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: hrms_compliance_db
      AUDIT_SERVICE_URL: http://audit-service:8000/api/v1
      NOTIFICATION_SERVICE_URL: http://notification-service:8000/api/v1
    depends_on:
      mysql:
        condition: service_healthy
      audit-service:
        condition: service_started
      notification-service:
        condition: service_started

volumes:
  mysql_data:
```

---

## Error Handling & Resilience

### Circuit Breaker Pattern
Implement circuit breaker for service-to-service calls to prevent cascading failures:

```python
from pybreaker import CircuitBreaker

employee_service_breaker = CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    listeners=[logger]
)

@employee_service_breaker
async def get_employee(employee_id: str):
    return await httpx_client.get(
        f"{EMPLOYEE_SERVICE_URL}/employees/{employee_id}"
    )
```

### Retry Policy
Implement exponential backoff for failed requests:

```python
async def call_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Retry {attempt + 1} after {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
```

### Fallback Values
Provide sensible defaults when service calls fail:

```python
async def get_employee_safe(employee_id: str):
    try:
        return await get_employee(employee_id)
    except Exception as e:
        logger.error(f"Failed to get employee: {e}")
        # Return minimal info to allow operation to continue
        return {
            "id": employee_id,
            "status": "unknown"
        }
```

---

## Monitoring & Observability

### Key Metrics to Track

1. **Service Health Metrics**
   - Response times for each endpoint
   - Error rates (4xx, 5xx)
   - Request volume per service
   - Database connection pool utilization

2. **Business Metrics**
   - Leave requests created/approved/rejected
   - Attendance check-ins
   - Late arrivals
   - Compliance violations

3. **Integration Metrics**
   - Inter-service call latency
   - Circuit breaker state (open/closed/half-open)
   - Failed retries
   - Message delivery rates

### Logging Standards
All services should log with consistent format:

```json
{
  "timestamp": "2024-01-10T10:30:45Z",
  "service": "leave-service",
  "level": "INFO",
  "request_id": "req_abc123",
  "user_id": "emp_123",
  "action": "create_leave",
  "status": "success",
  "duration_ms": 245,
  "message": "Leave request created successfully"
}
```

---

## Security Considerations

1. **JWT Authentication**: All services validate JWT tokens via JWKS endpoint
2. **HTTPS**: All inter-service communication should use HTTPS in production
3. **API Rate Limiting**: Implement rate limiting to prevent abuse
4. **Data Encryption**: Sensitive data should be encrypted at rest
5. **Access Control**: Implement role-based access control
6. **Audit Logging**: All state changes must be logged to Audit Service
7. **CORS**: Configure appropriate CORS policies
8. **Input Validation**: All inputs should be validated and sanitized

---

## Deployment & Scaling

### Service Dependencies
Services can be started in this order:
1. MySQL Database
2. Audit Service (no dependencies)
3. Notification Service (no dependencies)
4. Compliance Service
5. Employee Service
6. Leave Service
7. Attendance Service

### Scaling Strategies
1. **Horizontal Scaling**: Run multiple instances behind a load balancer
2. **Database Optimization**: Create indexes on frequently queried fields
3. **Caching**: Cache employee and compliance data with TTL
4. **Message Queues**: For high-volume notifications, consider using message queues (RabbitMQ, Kafka)
5. **Database Replicas**: For read-heavy services, use database replicas

---

## Testing Strategy

### Unit Tests
Test individual service endpoints in isolation

### Integration Tests
Test inter-service communication with mocked responses

### End-to-End Tests
Test complete workflows (e.g., create leave → approve leave → send notification)

### Performance Tests
Test service behavior under load

### Contract Tests
Verify service contracts are maintained when APIs change

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2024-01-10 | Initial microservices integration architecture |

---

## Support & Contact

For questions about this integration architecture, please contact:
- Platform Engineering Team
- Architecture Review Board
- Service Owners

---

**Last Updated**: January 10, 2024  
**Document Owner**: Platform Engineering Team  
**Status**: Active