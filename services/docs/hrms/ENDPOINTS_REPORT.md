# HRMS Microservices - API Endpoints Report

## Overview
This document provides a comprehensive summary of all API endpoints across the HR Management System microservices. Each service exposes RESTful APIs with specific endpoints for managing different aspects of the HR system.

---

## 1. User Management Service

**Base URL**: `http://localhost:8001/api/v1`

### Authentication Endpoints

#### POST `/auth/signup`
- **Description**: Register a new user in the system
- **Request Body**: 
  - `email`: string (required)
  - `password`: string (required)
  - `name`: string (optional)
- **Response**: User object with authentication token
- **Status Codes**: 201 Created, 400 Bad Request
- **Authentication**: Not required (public endpoint)

#### POST `/auth/oauth-callback`
- **Description**: Handle OAuth callback from Asgardeo
- **Request Body**: OAuth callback data
- **Response**: Session token and user info
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Not required

#### POST `/auth/logout`
- **Description**: Logout current user and invalidate session
- **Request Body**: None
- **Response**: Success confirmation
- **Status Codes**: 200 OK
- **Authentication**: Required (Bearer token)

#### GET `/auth/whoami`
- **Description**: Get current authenticated user information
- **Query Parameters**: None
- **Response**: User profile with roles and permissions
- **Status Codes**: 200 OK, 401 Unauthorized
- **Authentication**: Required (Bearer token)

#### GET `/auth/verify-token`
- **Description**: Verify if JWT token is valid
- **Query Parameters**: None
- **Response**: Token validity status
- **Status Codes**: 200 OK, 401 Unauthorized
- **Authentication**: Required (Bearer token)

### User Management Endpoints

#### GET `/users`
- **Description**: List all users with pagination
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
- **Response**: Array of user objects
- **Status Codes**: 200 OK
- **Authentication**: Required

#### GET `/users/{user_id}`
- **Description**: Get specific user by ID
- **Path Parameters**: 
  - `user_id`: string (required)
- **Response**: User object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### PATCH `/users/{user_id}/role`
- **Description**: Update user role assignment
- **Path Parameters**: 
  - `user_id`: string (required)
- **Request Body**: 
  - `role_id`: string
  - `role_name`: string
- **Response**: Updated user object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin only)

#### PUT `/users/{user_id}/suspend`
- **Description**: Suspend a user account
- **Path Parameters**: 
  - `user_id`: string (required)
- **Request Body**: 
  - `reason`: string (optional)
- **Response**: Updated user with suspended status
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin only)

#### PUT `/users/{user_id}/activate`
- **Description**: Activate a suspended user account
- **Path Parameters**: 
  - `user_id`: string (required)
- **Request Body**: None
- **Response**: Updated user with active status
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin only)

#### DELETE `/users/{user_id}`
- **Description**: Delete a user permanently
- **Path Parameters**: 
  - `user_id`: string (required)
- **Request Body**: None
- **Response**: Confirmation message
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin only)

#### GET `/roles`
- **Description**: List all available roles in the system
- **Query Parameters**: None
- **Response**: Array of role objects with permissions
- **Status Codes**: 200 OK
- **Authentication**: Required

#### GET `/users/{user_id}/permissions`
- **Description**: Get all permissions for a specific user
- **Path Parameters**: 
  - `user_id`: string (required)
- **Query Parameters**: None
- **Response**: Array of permission objects
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### POST `/users/sync-asgardeo`
- **Description**: Sync users from Asgardeo identity provider
- **Request Body**: Sync configuration (optional)
- **Response**: Sync status and count of synced users
- **Status Codes**: 200 OK
- **Authentication**: Required (Admin only)

#### POST `/auth/change-password`
- **Description**: Change password for current user
- **Request Body**: 
  - `old_password`: string
  - `new_password`: string
- **Response**: Success confirmation
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required

---

## 2. Employee Management Service

**Base URL**: `http://localhost:8002/api/v1`

### Employee Endpoints

#### POST `/employees`
- **Description**: Create a new employee record
- **Request Body**: 
  - `name`: string (required)
  - `email`: string (required)
  - `department`: string (optional)
  - `position`: string (optional)
  - `hire_date`: date (optional)
  - `salary`: float (optional)
- **Response**: Created employee object with ID
- **Status Codes**: 201 Created, 400 Bad Request
- **Authentication**: Required (Admin/HR only)

#### GET `/employees`
- **Description**: List all employees with pagination
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
- **Response**: Array of employee objects
- **Status Codes**: 200 OK
- **Authentication**: Required

#### GET `/employees/{employee_id}`
- **Description**: Get specific employee by ID
- **Path Parameters**: 
  - `employee_id`: int (required)
- **Response**: Employee object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### PATCH `/employees/{employee_id}`
- **Description**: Update employee information (partial update)
- **Path Parameters**: 
  - `employee_id`: int (required)
- **Request Body**: Any employee fields to update
- **Response**: Updated employee object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin/HR only)

#### DELETE `/employees/{employee_id}`
- **Description**: Delete an employee record
- **Path Parameters**: 
  - `employee_id`: int (required)
- **Response**: Confirmation message
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin only)

---

## 3. Attendance Management Service

**Base URL**: `http://localhost:8003/api/v1`

### Check-in/Check-out Endpoints

#### POST `/attendance/check-in`
- **Description**: Record employee check-in
- **Request Body**: 
  - `employee_id`: int (required)
- **Response**: Attendance record with check-in timestamp
- **Status Codes**: 201 Created, 400 Bad Request
- **Authentication**: Required

#### POST `/attendance/check-out`
- **Description**: Record employee check-out
- **Request Body**: 
  - `employee_id`: int (required)
- **Response**: Attendance record with check-out timestamp
- **Status Codes**: 200 OK, 400 Bad Request, 404 Not Found
- **Authentication**: Required

### Manual Attendance Entry

#### POST `/attendance/manual`
- **Description**: Manually create attendance entry (admin only)
- **Request Body**: 
  - `employee_id`: int (required)
  - `date`: string in YYYY-MM-DD format (required)
  - `check_in_time`: datetime (optional)
  - `check_out_time`: datetime (optional)
  - `status`: string (present/absent/late) (optional)
- **Response**: Created attendance record
- **Status Codes**: 201 Created, 400 Bad Request
- **Authentication**: Required (Admin/HR only)

### Attendance Query Endpoints

#### GET `/attendance/{attendance_id}`
- **Description**: Get specific attendance record
- **Path Parameters**: 
  - `attendance_id`: int (required)
- **Response**: Attendance record
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### GET `/attendance/employee/{employee_id}`
- **Description**: Get all attendance records for an employee
- **Path Parameters**: 
  - `employee_id`: int (required)
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
  - `start_date`: string in YYYY-MM-DD format (optional)
  - `end_date`: string in YYYY-MM-DD format (optional)
- **Response**: Array of attendance records
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required

#### GET `/attendance/summary/{employee_id}/{month}`
- **Description**: Get monthly attendance summary with statistics
- **Path Parameters**: 
  - `employee_id`: int (required)
  - `month`: string in YYYY-MM format (required)
- **Response**: Monthly summary with working hours and statistics
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required

### Attendance Update

#### PUT `/attendance/{attendance_id}`
- **Description**: Update attendance record
- **Path Parameters**: 
  - `attendance_id`: int (required)
- **Request Body**: Any attendance fields to update
- **Response**: Updated attendance record
- **Status Codes**: 200 OK, 404 Not Found, 400 Bad Request
- **Authentication**: Required (Admin/HR only)

### Health Check

#### GET `/attendance/health`
- **Description**: Health check endpoint for service status
- **Response**: Service status and timestamp
- **Status Codes**: 200 OK
- **Authentication**: Not required

#### GET `/auth/debug`
- **Description**: Debug token information (development)
- **Response**: Decoded JWT token details
- **Status Codes**: 200 OK, 401 Unauthorized
- **Authentication**: Required

#### GET `/auth/verify`
- **Description**: Verify token validity
- **Response**: Verification status
- **Status Codes**: 200 OK, 401 Unauthorized
- **Authentication**: Required

---

## 4. Leave Management Service

**Base URL**: `http://localhost:8004/api/v1`

### Leave Request Endpoints

#### POST `/leaves`
- **Description**: Create a new leave request
- **Request Body**: 
  - `employee_id`: int (required)
  - `start_date`: date (required)
  - `end_date`: date (required, must be after start_date)
  - `reason`: string (optional)
  - `leave_type`: string (optional)
- **Response**: Created leave request with status PENDING
- **Status Codes**: 201 Created, 400 Bad Request, 404 Not Found
- **Authentication**: Required
- **Notes**: Employee must exist, start_date must be before end_date

#### GET `/leaves`
- **Description**: List all leave requests with filtering and pagination
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
  - `status`: string (PENDING, APPROVED, REJECTED, CANCELLED) (optional)
- **Response**: Array of leave requests
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required

#### GET `/leaves/{leave_id}`
- **Description**: Get specific leave request by ID
- **Path Parameters**: 
  - `leave_id`: int (required)
- **Response**: Leave request object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### GET `/leaves/employee/{employee_id}`
- **Description**: Get all leaves for a specific employee
- **Path Parameters**: 
  - `employee_id`: int (required)
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
  - `status`: string (optional)
- **Response**: Array of leave requests for employee
- **Status Codes**: 200 OK, 404 Not Found, 400 Bad Request
- **Authentication**: Required

#### PUT `/leaves/{leave_id}`
- **Description**: Update leave status (approve, reject, or cancel)
- **Path Parameters**: 
  - `leave_id`: int (required)
- **Request Body**: 
  - `status`: string (APPROVED, REJECTED, CANCELLED) (required)
  - `approved_by`: string (required if status is APPROVED)
  - `rejection_reason`: string (required if status is REJECTED)
- **Response**: Updated leave request
- **Status Codes**: 200 OK, 404 Not Found, 400 Bad Request
- **Authentication**: Required (Manager/Admin only)
- **Notes**: PENDING can transition to APPROVED/REJECTED. APPROVED/PENDING can be CANCELLED.

#### DELETE `/leaves/{leave_id}`
- **Description**: Cancel a leave request
- **Path Parameters**: 
  - `leave_id`: int (required)
- **Response**: Confirmation message
- **Status Codes**: 200 OK, 404 Not Found, 400 Bad Request
- **Authentication**: Required
- **Notes**: Only PENDING or APPROVED leaves can be cancelled

---

## 5. Notification Service

**Base URL**: `http://localhost:8005/api/v1`

### Notification Endpoints

#### POST `/notifications/send`
- **Description**: Send a new notification (email)
- **Request Body**: 
  - `employee_id`: int (required)
  - `recipient_email`: string (required)
  - `recipient_name`: string (required)
  - `subject`: string (required)
  - `body`: string (required)
  - `notification_type`: string (optional)
- **Response**: Created notification with status PENDING
- **Status Codes**: 201 Created, 400 Bad Request
- **Authentication**: Required
- **Notes**: Sends email in background task

#### GET `/notifications/{notification_id}`
- **Description**: Get specific notification by ID
- **Path Parameters**: 
  - `notification_id`: int (required)
- **Response**: Notification object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### GET `/notifications`
- **Description**: List all notifications with filtering and pagination
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
  - `status`: string (PENDING, SENT, FAILED, RETRYING) (optional)
- **Response**: Paginated list of notifications
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required

#### GET `/notifications/employee/{employee_id}`
- **Description**: Get all notifications for a specific employee
- **Path Parameters**: 
  - `employee_id`: int (required)
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 100)
- **Response**: Paginated list of employee notifications
- **Status Codes**: 200 OK
- **Authentication**: Required

#### PUT `/notifications/{notification_id}/retry`
- **Description**: Retry sending a failed notification
- **Path Parameters**: 
  - `notification_id`: int (required)
- **Request Body**: None
- **Response**: Updated notification with status RETRYING
- **Status Codes**: 200 OK, 404 Not Found, 400 Bad Request
- **Authentication**: Required (Admin only)
- **Notes**: Can only retry FAILED or RETRYING notifications

---

## 6. Audit Service

**Base URL**: `http://localhost:8006/api/v1`

### Audit Log Endpoints

#### POST `/audit-logs`
- **Description**: Create a new audit log entry
- **Request Body**: 
  - `user_id`: string (required)
  - `action`: string (created, updated, deleted, viewed) (required)
  - `log_type`: string (leave_request, attendance, employee, etc.) (required)
  - `entity_type`: string (required)
  - `entity_id`: string (required)
  - `service_name`: string (required)
  - `status`: string (success, failure) (optional)
  - `description`: string (optional)
  - `new_values`: string (JSON format) (optional)
- **Response**: Created audit log with timestamp
- **Status Codes**: 201 Created, 400 Bad Request
- **Authentication**: Required

#### GET `/audit-logs`
- **Description**: List audit logs with advanced filtering and pagination
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 1000)
  - `user_id`: string (optional)
  - `log_type`: string (optional)
  - `service_name`: string (optional)
  - `entity_type`: string (optional)
  - `start_date`: datetime (optional)
  - `end_date`: datetime (optional)
- **Response**: Paginated list of audit logs
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required

#### GET `/audit-logs/{audit_id}`
- **Description**: Get specific audit log by ID
- **Path Parameters**: 
  - `audit_id`: int (required)
- **Response**: Audit log object
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### GET `/audit-logs/user/{user_id}`
- **Description**: Get all audit logs for a specific user
- **Path Parameters**: 
  - `user_id`: string (required)
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 1000)
  - `log_type`: string (optional)
  - `start_date`: datetime (optional)
  - `end_date`: datetime (optional)
- **Response**: Paginated list of user audit logs
- **Status Codes**: 200 OK
- **Authentication**: Required

#### GET `/audit-logs/type/{log_type}`
- **Description**: Get audit logs filtered by type
- **Path Parameters**: 
  - `log_type`: string (required)
- **Query Parameters**: 
  - `offset`: int (default: 0)
  - `limit`: int (default: 100, max: 1000)
  - `service_name`: string (optional)
  - `user_id`: string (optional)
  - `start_date`: datetime (optional)
  - `end_date`: datetime (optional)
- **Response**: Paginated list of typed audit logs
- **Status Codes**: 200 OK
- **Authentication**: Required

#### PATCH `/audit-logs/{audit_id}`
- **Description**: Update audit log (partial update)
- **Path Parameters**: 
  - `audit_id`: int (required)
- **Request Body**: Any audit log fields to update
- **Response**: Updated audit log
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required

#### DELETE `/audit-logs/{audit_id}`
- **Description**: Delete audit log entry
- **Path Parameters**: 
  - `audit_id`: int (required)
- **Request Body**: None
- **Response**: Confirmation message
- **Status Codes**: 200 OK, 404 Not Found
- **Authentication**: Required (Admin only)
- **Notes**: Use with caution - may violate compliance requirements

---

## 7. Compliance Service

**Base URL**: `http://localhost:8007/api/v1`

### Data Inventory Endpoints

#### GET `/compliance/data-inventory`
- **Description**: Get complete data inventory (GDPR Article 30 - ROPA)
- **Query Parameters**: 
  - `category_id`: int (optional)
  - `data_type`: string (optional)
  - `sensitivity_level`: string (optional)
  - `skip`: int (default: 0)
  - `limit`: int (default: 100, max: 1000)
- **Response**: Complete data inventory with all categories and metadata
- **Status Codes**: 200 OK, 400 Bad Request
- **Authentication**: Required
- **Compliance**: GDPR Article 30 - Records of Processing Activities

### Employee Data Rights Endpoints

#### GET `/compliance/employee/{employee_id}/data-about-me`
- **Description**: Get summary of employee's personal data (GDPR Article 15)
- **Path Parameters**: 
  - `employee_id`: string (required)
- **Response**: Data summary with retention policies and deletion schedule
- **Status Codes**: 200 OK, 404 Not Found, 403 Forbidden
- **Authentication**: Required
- **Compliance**: GDPR Article 15 - Right of Access
- **Security Notes**: Employees can only view their own data; admins can view any

#### GET `/compliance/employee/{employee_id}/access-controls`
- **Description**: Get what data employee can access and why
- **Path Parameters**: 
  - `employee_id`: string (required)
- **Response**: Access control information with permissions and reasons
- **Status Codes**: 200 OK, 404 Not Found, 403 Forbidden
- **Authentication**: Required
- **Security Notes**: Only admin, HR, or the employee themselves

### Data Retention & Reporting

#### GET `/compliance/data-retention-report`
- **Description**: Get data retention policies report (GDPR Article 5)
- **Query Parameters**: 
  - `skip`: int (default: 0)
  - `limit`: int (default: 100)
- **Response**: Data retention summary with expiration dates
- **Status Codes**: 200 OK
- **Authentication**: Required
- **Compliance**: GDPR Article 5 - Storage Limitation

---

## Data Types & Models

### Common Response Structures

#### Pagination Response
```
{
  "total": int,
  "offset": int,
  "limit": int,
  "items": array
}
```

#### Error Response
```
{
  "detail": string,
  "status_code": int
}
```

#### Success Response
```
{
  "ok": boolean,
  "message": string (optional)
}
```

### Leave Status Enum
- `PENDING`: Leave request submitted, awaiting approval
- `APPROVED`: Leave request approved by manager
- `REJECTED`: Leave request rejected with reason
- `CANCELLED`: Leave request cancelled by employee

### Notification Status Enum
- `PENDING`: Notification created, not yet sent
- `SENT`: Email sent successfully
- `FAILED`: Email failed to send
- `RETRYING`: Retry in progress after failure

### Attendance Status Enum
- `PRESENT`: Employee present for the day
- `ABSENT`: Employee absent
- `LATE`: Employee arrived late

### AuditLogType Enum
- `created`: Resource creation event
- `updated`: Resource update event
- `deleted`: Resource deletion event
- `viewed`: Resource access event
- `leave_request`: Leave-related actions
- `attendance`: Attendance-related actions
- `employee`: Employee record changes

---

## Authentication & Authorization

### Token Format
All authenticated endpoints require an Authorization header with a JWT Bearer token:
```
Authorization: Bearer <JWT_TOKEN>
```

### Role-Based Access Control (RBAC)
The system implements role-based access control with the following roles:
- `admin`: Full system access
- `manager`: Can manage team members and approve requests
- `hr`: Human resources operations
- `employee`: Standard employee access

### Common Authorization Requirements
- **Admin-only endpoints**: `/users/{id}/suspend`, `/users/{id}/activate`, DELETE endpoints
- **Manager-only endpoints**: `/leaves/{id}` (PUT for approval)
- **Employee endpoints**: Own data only unless admin
- **Public endpoints**: `/auth/signup`, `/auth/oauth-callback`

---

## Error Handling

### HTTP Status Codes Used
- `200 OK`: Successful GET, PUT requests
- `201 Created`: Successful POST requests
- `400 Bad Request`: Invalid input or validation error
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

---

## Rate Limiting

- **Default Limit**: 100 records per page
- **Maximum Limit**: 1000 records per page (audit logs)
- **Pagination**: Use `offset` and `limit` query parameters

---

## Key Features by Service

### User Management
- OAuth2/OIDC integration via Asgardeo
- Role and permission management
- User lifecycle management (create, suspend, activate, delete)
- User synchronization from identity provider

### Employee Management
- Employee CRUD operations
- Employee profile management
- Department and position tracking

### Attendance Management
- Real-time check-in/check-out
- Manual attendance entries
- Monthly attendance summary with statistics
- Working hours calculation
- Date range filtering

### Leave Management
- Leave request creation and management
- Multi-step approval workflow
- Status tracking (PENDING → APPROVED/REJECTED/CANCELLED)
- Employee-specific leave queries
- Leave cancellation

### Notifications
- Email notification sending
- Background task processing
- Notification status tracking
- Retry mechanism for failed sends
- Employee notification history

### Audit Service
- Comprehensive audit logging
- Multi-filter querying (user, type, service, entity, date range)
- Audit trail maintenance
- Compliance reporting

### Compliance Service
- GDPR Article 15 support (Right of Access)
- GDPR Article 30 support (Records of Processing Activities)
- GDPR Article 5 support (Storage Limitation)
- Data inventory management
- Access control transparency
- Data retention reporting

---

## Service Architecture

### Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL/MySQL (via SQLModel ORM)
- **Authentication**: JWT with Asgardeo integration
- **Background Jobs**: FastAPI Background Tasks
- **Email**: SMTP integration
- **Containerization**: Docker

### Service Ports
- User Management Service: `8001`
- Employee Management Service: `8002`
- Attendance Management Service: `8003`
- Leave Management Service: `8004`
- Notification Service: `8005`
- Audit Service: `8006`
- Compliance Service: `8007`

### Inter-Service Communication
Services communicate with each other via HTTP REST APIs:
- Attendance → Employee Service (verify employee exists)
- Leave → Employee Service (verify employee exists)
- Multiple services → Audit Service (log events)
- Multiple services → Notification Service (send notifications)

---

## Frontend Integration Notes

### Base URL Configuration
Each service has a specific port and base path:
```
API_BASE_URL = http://localhost:{PORT}/api/v1
```

### Authentication Flow
1. User signs up or logs in via `/auth/signup` or `/auth/oauth-callback`
2. Receive JWT token in response
3. Include token in all subsequent requests: `Authorization: Bearer {token}`
4. Use `/auth/whoami` to verify current session

### Pagination Pattern
Most list endpoints support pagination:
```
GET /resource?offset=0&limit=20
```

### Filtering Pattern
Many endpoints support filtering via query parameters (see individual endpoints for details)

### Error Handling
Always check HTTP status code and handle errors gracefully:
- `4xx` errors: Client-side issues (validation, not found, etc.)
- `5xx` errors: Server-side issues (retry with exponential backoff)

---

## Testing Endpoints

### Quick Health Checks
```bash
# Attendance Service Health
curl http://localhost:8003/api/v1/attendance/health

# Token Verification
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8003/api/v1/auth/verify
```

### Sample API Calls

**Create Leave Request:**
```bash
curl -X POST http://localhost:8004/api/v1/leaves \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "start_date": "2024-01-15",
    "end_date": "2024-01-20",
    "reason": "Vacation"
  }'
```

**Check In:**
```bash
curl -X POST http://localhost:8003/api/v1/attendance/check-in \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1
  }'
```

**List Employees:**
```bash
curl -X GET "http://localhost:8002/api/v1/employees?offset=0&limit=10" \
  -H "Authorization: Bearer TOKEN"
```

---

## Document Version
- **Version**: 1.0
- **Last Updated**: 2024
- **Status**: Complete for all 7 microservices