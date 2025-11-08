# Audit Service - Quick Reference

## Service Overview

**URL**: `http://audit-service:8000/api/v1`  
**Health Check**: `GET http://audit-service:8000/health`  
**Documentation**: `http://audit-service:8000/docs`

---

## Endpoints At A Glance

### Create Audit Log
```
POST /audit-logs
```
**Required Fields**: `user_id`, `action`, `log_type`, `entity_type`, `entity_id`, `service_name`

**Example**:
```bash
curl -X POST "http://audit-service:8000/api/v1/audit-logs" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "action": "created",
    "log_type": "leave_request",
    "entity_type": "LeaveRequest",
    "entity_id": "leave456",
    "service_name": "leave-management-service",
    "status": "success",
    "description": "Leave request created",
    "new_values": "{\"days\": 5, \"status\": \"pending\"}"
  }'
```

### List All Logs
```
GET /audit-logs
Query: offset=0&limit=100&log_type=leave_request&user_id=user123
```

### Get Specific Log
```
GET /audit-logs/{audit_id}
```

### Get User's Logs
```
GET /audit-logs/user/{user_id}
Query: offset=0&limit=100&log_type=leave_request
```

### Get Logs by Type
```
GET /audit-logs/type/{log_type}
Query: offset=0&limit=100&start_date=2024-01-01&end_date=2024-01-31
```

### Update Log
```
PATCH /audit-logs/{audit_id}
{
  "status": "failure",
  "error_message": "Database error"
}
```

### Delete Log
```
DELETE /audit-logs/{audit_id}
```

---

## Log Types

| Type | Use | Service |
|------|-----|---------|
| `leave_request` | Leave request creation | leave-management-service |
| `leave_approval` | Leave approval/rejection | leave-management-service |
| `attendance` | Check-in/check-out | attendance-service |
| `payroll` | Payroll processing | payroll-service |
| `employee_create` | New employee | employee-service |
| `employee_update` | Employee info change | employee-service |
| `employee_delete` | Employee deletion | employee-service |
| `policy_create` | New policy | policy-service |
| `policy_update` | Policy change | policy-service |
| `policy_delete` | Policy deletion | policy-service |
| `document_upload` | File upload | document-service |
| `document_delete` | File deletion | document-service |
| `role_assignment` | User role grant | iam-service |
| `permission_change` | Permission update | iam-service |
| `login` | User login | auth-service |
| `logout` | User logout | auth-service |
| `export` | Data export | any-service |
| `import` | Data import | any-service |
| `other` | Miscellaneous | any-service |

---

## Python Integration (Minimal)

```python
import httpx
import json
from typing import Optional, Dict, Any

async def log_audit(
    user_id: str,
    action: str,
    log_type: str,
    entity_type: str,
    entity_id: str,
    service_name: str,
    status: str = "success",
    new_values: Optional[Dict[str, Any]] = None,
    old_values: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
):
    """Log an audit event"""
    payload = {
        "user_id": user_id,
        "action": action,
        "log_type": log_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "service_name": service_name,
        "status": status,
        "new_values": json.dumps(new_values) if new_values else None,
        "old_values": json.dumps(old_values) if old_values else None,
        "error_message": error_message,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://audit-service:8000/api/v1/audit-logs",
            json=payload,
            timeout=5.0
        )
        return response.json()

# Usage
await log_audit(
    user_id="user123",
    action="created",
    log_type="leave_request",
    entity_type="LeaveRequest",
    entity_id="leave456",
    service_name="leave-management-service",
    new_values={"days": 5, "status": "pending"}
)
```

---

## JavaScript Integration (Minimal)

```javascript
async function logAudit(data) {
    const response = await fetch("http://audit-service:8000/api/v1/audit-logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: data.userId,
            action: data.action,
            log_type: data.logType,
            entity_type: data.entityType,
            entity_id: data.entityId,
            service_name: data.serviceName,
            status: data.status || "success",
            new_values: JSON.stringify(data.newValues),
            old_values: JSON.stringify(data.oldValues),
            error_message: data.errorMessage
        })
    });
    return response.json();
}

// Usage
logAudit({
    userId: "user123",
    action: "created",
    logType: "leave_request",
    entityType: "LeaveRequest",
    entityId: "leave456",
    serviceName: "leave-management-service",
    newValues: { days: 5, status: "pending" }
});
```

---

## cURL Examples

### Create Log
```bash
curl -X POST "http://localhost:8000/api/v1/audit-logs" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "action": "created",
    "log_type": "leave_request",
    "entity_type": "LeaveRequest",
    "entity_id": "leave456",
    "service_name": "leave-management-service"
  }'
```

### List Logs
```bash
curl "http://localhost:8000/api/v1/audit-logs?limit=50&offset=0"
```

### Get User Logs
```bash
curl "http://localhost:8000/api/v1/audit-logs/user/user123?limit=50"
```

### Get Logs by Type
```bash
curl "http://localhost:8000/api/v1/audit-logs/type/leave_request?limit=50&start_date=2024-01-01&end_date=2024-01-31"
```

### Get Specific Log
```bash
curl "http://localhost:8000/api/v1/audit-logs/123"
```

### Update Log
```bash
curl -X PATCH "http://localhost:8000/api/v1/audit-logs/123" \
  -H "Content-Type: application/json" \
  -d '{"status": "failure", "error_message": "Error occurred"}'
```

### Delete Log
```bash
curl -X DELETE "http://localhost:8000/api/v1/audit-logs/123"
```

---

## Request Fields Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `user_id` | string | ✓ | ID of user performing action |
| `action` | string | ✓ | Action name (created, updated, etc.) |
| `log_type` | string | ✓ | One of the predefined types |
| `entity_type` | string | ✓ | Type of entity (LeaveRequest, Employee, etc.) |
| `entity_id` | string | ✓ | ID of the entity |
| `service_name` | string | ✓ | Name of calling service |
| `status` | string | - | "success" or "failure" (default: "success") |
| `description` | string | - | Human-readable description |
| `old_values` | JSON string | - | Previous state (for updates) |
| `new_values` | JSON string | - | New state |
| `ip_address` | string | - | Client IP address |
| `user_agent` | string | - | Client user agent |
| `request_id` | string | - | Request ID for tracing |
| `error_message` | string | - | Error details if status is failure |

---

## Response Fields

```json
{
  "id": 123,
  "user_id": "user123",
  "action": "created",
  "log_type": "leave_request",
  "entity_type": "LeaveRequest",
  "entity_id": "leave456",
  "service_name": "leave-management-service",
  "status": "success",
  "description": "Leave request created",
  "timestamp": "2024-01-10T10:30:45.123456",
  "old_values": null,
  "new_values": "{\"days\": 5, \"status\": \"pending\"}",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "request_id": "req-12345",
  "error_message": null
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Failed to create audit log: Invalid field"
}
```

### 404 Not Found
```json
{
  "detail": "Audit log not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Query Parameters

### Pagination
- `offset` (int, default: 0) - Skip N records
- `limit` (int, default: 100, max: 1000) - Return N records

### Filtering
- `user_id` (string) - Filter by user
- `log_type` (string) - Filter by log type
- `service_name` (string) - Filter by service
- `entity_type` (string) - Filter by entity type
- `status` (string) - Filter by status (success/failure)
- `start_date` (ISO datetime) - From date
- `end_date` (ISO datetime) - To date

### Example
```
/audit-logs?offset=0&limit=50&log_type=leave_request&user_id=user123&start_date=2024-01-01
```

---

## Best Practices Checklist

- [ ] Always include `service_name` to identify calling service
- [ ] Log both success and failure cases
- [ ] Include `old_values` and `new_values` for updates
- [ ] Use appropriate `log_type` from predefined list
- [ ] Never log sensitive data (passwords, SSN, etc.)
- [ ] Include `request_id` for tracing
- [ ] Use ISO format for dates: `2024-01-01T10:30:00`
- [ ] JSON encode complex values
- [ ] Handle audit service failures gracefully
- [ ] Use meaningful descriptions

---

## Common Patterns

### Logging Creation
```python
await log_audit(
    user_id=user.id,
    action="created",
    log_type="leave_request",
    entity_type="LeaveRequest",
    entity_id=str(leave.id),
    service_name="leave-management-service",
    new_values=leave.to_dict()
)
```

### Logging Update
```python
await log_audit(
    user_id=user.id,
    action="updated",
    log_type="leave_request",
    entity_type="LeaveRequest",
    entity_id=str(leave.id),
    service_name="leave-management-service",
    old_values=old_leave.to_dict(),
    new_values=new_leave.to_dict()
)
```

### Logging Deletion
```python
await log_audit(
    user_id=user.id,
    action="deleted",
    log_type="leave_request",
    entity_type="LeaveRequest",
    entity_id=str(leave.id),
    service_name="leave-management-service",
    old_values=leave.to_dict()
)
```

### Logging Failure
```python
await log_audit(
    user_id=user.id,
    action="create_failed",
    log_type="leave_request",
    entity_type="LeaveRequest",
    entity_id="unknown",
    service_name="leave-management-service",
    status="failure",
    error_message=str(e)
)
```

---

## Environment Setup

### Docker Compose
```yaml
services:
  audit-service:
    image: audit-service:latest
    environment:
      DB_HOST: mysql
      DB_NAME: audit_service_db
      DB_USER: root
      DB_PASSWORD: root
      DEBUG: "False"
    ports:
      - "8000:8000"
```

### Environment Variables
```env
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
SERVICE_NAME=your-service-name
AUDIT_SERVICE_TIMEOUT=5
AUDIT_SERVICE_RETRIES=3
```

---

## Health Checks

### Service Health
```bash
curl http://localhost:8000/health
```

### API Health
```bash
curl http://localhost:8000/api/v1/health
```

### Readiness (Kubernetes)
```bash
curl http://localhost:8000/ready
```

---

## Database Query Examples

### Get all logs for a user
```
GET /audit-logs/user/user123?limit=1000
```

### Get failed operations
```
GET /audit-logs?status=failure&limit=100
```

### Get all leave requests from last 30 days
```
GET /audit-logs/type/leave_request?start_date=2023-12-11&end_date=2024-01-10&limit=1000
```

### Track changes to specific employee
```
GET /audit-logs?entity_type=Employee&entity_id=emp456&limit=500
```

### Export audit trail for compliance
```
GET /audit-logs?start_date=2024-01-01&end_date=2024-01-31&limit=10000
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Connection refused | Check if service is running: `curl http://audit-service:8000/health` |
| Logs not appearing | Verify `AUDIT_SERVICE_URL` and network connectivity |
| Timeouts | Increase timeout: `timeout=10.0` |
| "Invalid log_type" | Use one of the predefined types from the table above |
| "Missing required field" | Check all required fields are included in request |

---

## Support Resources

- **Full Documentation**: See `README.md`
- **Integration Guide**: See `INTEGRATION_GUIDE.md`
- **API Docs**: `http://audit-service:8000/docs`
- **Example Code**: See `INTEGRATION_GUIDE.md` for language-specific examples

---

**Version**: 1.0.0  
**Last Updated**: January 2024