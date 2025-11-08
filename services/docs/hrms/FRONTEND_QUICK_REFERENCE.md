# HRMS Frontend - Quick Reference Guide

## Services & Base URLs

| Service | Port | Base URL |
|---------|------|----------|
| User Management | 8001 | `http://localhost:8001/api/v1` |
| Employee Management | 8002 | `http://localhost:8002/api/v1` |
| Attendance Management | 8003 | `http://localhost:8003/api/v1` |
| Leave Management | 8004 | `http://localhost:8004/api/v1` |
| Notification Service | 8005 | `http://localhost:8005/api/v1` |
| Audit Service | 8006 | `http://localhost:8006/api/v1` |
| Compliance Service | 8007 | `http://localhost:8007/api/v1` |

---

## Core Endpoints Quick Access

### Authentication (User Service - Port 8001)
```
POST   /auth/signup              → Register user
POST   /auth/oauth-callback      → OAuth login
POST   /auth/logout              → Logout
GET    /auth/whoami              → Current user info
GET    /auth/verify-token        → Verify JWT
PUT    /auth/change-password     → Change password
```

### Users Management (Port 8001)
```
GET    /users                    → List all users (pagination)
GET    /users/{user_id}          → Get user details
PUT    /users/{user_id}/role     → Update user role
PUT    /users/{user_id}/suspend  → Suspend user (Admin)
PUT    /users/{user_id}/activate → Activate user (Admin)
DELETE /users/{user_id}          → Delete user (Admin)
GET    /roles                    → List all roles
```

### Employees (Employee Service - Port 8002)
```
POST   /employees                → Create employee
GET    /employees                → List employees (pagination)
GET    /employees/{emp_id}       → Get employee details
PATCH  /employees/{emp_id}       → Update employee
DELETE /employees/{emp_id}       → Delete employee (Admin)
```

### Attendance (Attendance Service - Port 8003)
```
POST   /attendance/check-in                    → Check in
POST   /attendance/check-out                   → Check out
POST   /attendance/manual                      → Manual entry (Admin)
GET    /attendance/{attendance_id}             → Get record
GET    /attendance/employee/{emp_id}           → List records
GET    /attendance/summary/{emp_id}/{month}    → Monthly summary
PUT    /attendance/{attendance_id}             → Update record (Admin)
```

### Leaves (Leave Service - Port 8004)
```
POST   /leaves                           → Create request
GET    /leaves                           → List requests (filter by status)
GET    /leaves/{leave_id}                → Get request details
GET    /leaves/employee/{emp_id}         → List employee requests
PUT    /leaves/{leave_id}                → Approve/Reject/Cancel
DELETE /leaves/{leave_id}                → Cancel request
```

### Notifications (Notification Service - Port 8005)
```
POST   /notifications/send                    → Send notification
GET    /notifications/{notification_id}       → Get notification
GET    /notifications                         → List notifications
GET    /notifications/employee/{emp_id}       → List employee notifications
PUT    /notifications/{notification_id}/retry → Retry failed (Admin)
```

### Audit Logs (Audit Service - Port 8006)
```
POST   /audit-logs                          → Create audit log (Internal)
GET    /audit-logs                          → List logs (advanced filters)
GET    /audit-logs/{audit_id}               → Get log details
GET    /audit-logs/user/{user_id}           → User's audit history
GET    /audit-logs/type/{log_type}          → Logs by type
PATCH  /audit-logs/{audit_id}               → Update log
DELETE /audit-logs/{audit_id}               → Delete log (Admin, caution!)
```

### Compliance (Compliance Service - Port 8007)
```
GET    /compliance/data-inventory                        → Data inventory (GDPR Art 30)
GET    /compliance/employee/{emp_id}/data-about-me       → Right of access (GDPR Art 15)
GET    /compliance/employee/{emp_id}/access-controls     → Access control info
GET    /compliance/data-retention-report                 → Retention policy (GDPR Art 5)
```

---

## Common Query Parameters

### Pagination
- `offset`: Records to skip (default: 0)
- `limit`: Max records to return (default: 100, max: 100 or 1000 for audit)

### Date Filtering
- `start_date`: Date in YYYY-MM-DD format
- `end_date`: Date in YYYY-MM-DD format

### Attendance
- Month: YYYY-MM format (e.g., 2024-01)

### Filtering
- `status`: For leaves (PENDING, APPROVED, REJECTED, CANCELLED)
- `status`: For notifications (PENDING, SENT, FAILED, RETRYING)
- `log_type`: For audit logs
- `service_name`: For audit logs

---

## Standard Response Format

### Success Response (200/201)
```json
{
  "id": 1,
  "name": "John Doe",
  ...
}
```

### Paginated Response
```json
{
  "total": 150,
  "offset": 0,
  "limit": 50,
  "items": [...]
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

---

## HTTP Headers Required

### All Authenticated Requests
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Try again later |

---

## Leave Status Workflow

```
PENDING → APPROVED → (work)
   ↓
REJECTED

PENDING → CANCELLED
APPROVED → CANCELLED
```

**Required Fields:**
- APPROVED: `status`, `approved_by`
- REJECTED: `status`, `rejection_reason`
- CANCELLED: `status`

---

## Attendance Summary Response

```json
{
  "employee_id": 1,
  "month": "2024-01",
  "total_days_worked": 20,
  "total_present": 20,
  "total_absent": 2,
  "total_late": 3,
  "working_hours": 160.5,
  "records": [...]
}
```

---

## Role-Based Access Control

### Available Roles
- `admin` - Full system access
- `manager` - Team management & approvals
- `hr` - HR operations
- `employee` - Self-service access

### Common Access Patterns
- **Admin only**: User suspend/activate, delete operations, audit logs
- **Manager+**: Leave approvals
- **Self-service**: Check-in/out, own data access
- **Compliance**: Admins only for most compliance endpoints

---

## Authentication Flow

1. **Signup/Login**
   ```
   POST /auth/signup or /auth/oauth-callback
   → Returns JWT token
   ```

2. **Use Token**
   ```
   Include in all requests:
   Authorization: Bearer <token>
   ```

3. **Verify Token**
   ```
   GET /auth/verify-token
   GET /auth/whoami
   ```

4. **Logout**
   ```
   POST /auth/logout
   ```

---

## Common API Patterns

### Create Resource
```javascript
POST /resource
{
  "name": "value",
  "field": "data"
}
```

### List Resources
```javascript
GET /resource?offset=0&limit=20
```

### Get Single Resource
```javascript
GET /resource/{id}
```

### Update Resource
```javascript
PUT /resource/{id}    // Full update
PATCH /resource/{id}  // Partial update
{
  "field": "new_value"
}
```

### Delete Resource
```javascript
DELETE /resource/{id}
```

---

## Popular Workflow Examples

### Employee Check-In/Out
```javascript
// Check in
POST /attendance/check-in
{ "employee_id": 1 }

// Check out
POST /attendance/check-out
{ "employee_id": 1 }
```

### Leave Request Workflow
```javascript
// Create request
POST /leaves
{
  "employee_id": 1,
  "start_date": "2024-01-15",
  "end_date": "2024-01-20",
  "reason": "Vacation"
}

// List pending (for manager)
GET /leaves?status=PENDING

// Approve
PUT /leaves/{id}
{
  "status": "APPROVED",
  "approved_by": "manager_id"
}
```

### Send Notification
```javascript
POST /notifications/send
{
  "employee_id": 1,
  "recipient_email": "user@example.com",
  "recipient_name": "John Doe",
  "subject": "Leave Approved",
  "body": "Your leave request has been approved"
}
```

### Get Audit Trail
```javascript
GET /audit-logs?user_id=user123&start_date=2024-01-01&end_date=2024-01-31
```

---

## Frontend Integration Checklist

- [ ] Configure base URLs for each service
- [ ] Implement token storage (localStorage/sessionStorage)
- [ ] Add token refresh mechanism
- [ ] Implement error handling for 401/403
- [ ] Add pagination UI component
- [ ] Create date picker components
- [ ] Implement role-based UI rendering
- [ ] Add loading states
- [ ] Handle background notification tasks
- [ ] Implement audit logging for user actions
- [ ] Add GDPR compliance data display
- [ ] Create monthly summary reports

---

## Environment Configuration

### Development
```
REACT_APP_USER_SERVICE_URL=http://localhost:8001/api/v1
REACT_APP_EMPLOYEE_SERVICE_URL=http://localhost:8002/api/v1
REACT_APP_ATTENDANCE_SERVICE_URL=http://localhost:8003/api/v1
REACT_APP_LEAVE_SERVICE_URL=http://localhost:8004/api/v1
REACT_APP_NOTIFICATION_SERVICE_URL=http://localhost:8005/api/v1
REACT_APP_AUDIT_SERVICE_URL=http://localhost:8006/api/v1
REACT_APP_COMPLIANCE_SERVICE_URL=http://localhost:8007/api/v1
```

### Production
Replace `localhost` with actual domain names

---

## Date Format Reference

- **Date**: `YYYY-MM-DD` (e.g., 2024-01-15)
- **Month**: `YYYY-MM` (e.g., 2024-01)
- **DateTime**: ISO 8601 (e.g., 2024-01-15T14:30:00Z)

---

## Enum Values

### Leave Status
- `PENDING` - Awaiting approval
- `APPROVED` - Approved by manager
- `REJECTED` - Rejected with reason
- `CANCELLED` - Cancelled by employee

### Notification Status
- `PENDING` - Not yet sent
- `SENT` - Successfully sent
- `FAILED` - Failed to send
- `RETRYING` - Retrying after failure

### Attendance Status
- `PRESENT` - Employee present
- `ABSENT` - Employee absent
- `LATE` - Employee arrived late

### Audit Log Actions
- `created` - Resource created
- `updated` - Resource updated
- `deleted` - Resource deleted
- `viewed` - Resource accessed

---

## Troubleshooting

### 401 Unauthorized
- Token expired or invalid
- Token not included in header
- **Solution**: Re-authenticate and get new token

### 403 Forbidden
- User lacks required role/permission
- **Solution**: Check user roles, use appropriate user account

### 404 Not Found
- Resource ID doesn't exist
- Incorrect endpoint URL
- **Solution**: Verify ID and endpoint path

### 400 Bad Request
- Invalid input format
- Missing required fields
- Date format incorrect
- **Solution**: Check request body and field formats

### 500 Server Error
- Server-side issue
- **Solution**: Check server logs, retry after delay

---

## Useful Tips

1. **Always validate dates** - Use YYYY-MM-DD format
2. **Implement token refresh** - Handle 401 gracefully
3. **Use pagination** - Don't fetch unlimited records
4. **Filter early** - Use query params to reduce data transfer
5. **Cache user roles** - Reduce permission checks
6. **Handle background tasks** - Notifications send asynchronously
7. **Log all actions** - For audit trail compliance
8. **Test with multiple roles** - Verify access control works

---

## Support & Debugging

### Check Service Health
```bash
curl http://localhost:8003/api/v1/attendance/health
```

### Debug Token
```bash
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8003/api/v1/auth/debug
```

### Get Current User
```bash
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8001/api/v1/auth/whoami
```

---

## Version
- **API Version**: v1
- **Last Updated**: 2024
- **Framework**: FastAPI (Python)