# Audit Service

A centralized audit logging and compliance service for the HRMS microservices ecosystem. This service provides comprehensive audit trail management, enabling all microservices to log, query, and monitor user actions and system events.

## Overview

The Audit Service is a FastAPI-based microservice that:
- Centrally logs all audit events from across the HRMS system
- Provides RESTful APIs for creating, querying, and managing audit logs
- Enables compliance and regulatory reporting
- Supports advanced filtering and log type categorization
- Maintains comprehensive audit trails for security and forensics

## Features

✅ **Comprehensive Audit Logging** - Track all user actions and system events
✅ **Multiple Log Types** - Pre-defined categories for different event types (leave requests, payroll, attendance, etc.)
✅ **Advanced Querying** - Filter logs by user, type, date range, service, and more
✅ **JWT Authentication** - Secure endpoints with Asgardeo JWKS integration
✅ **CORS Support** - Configured for multi-origin microservice communication
✅ **MySQL Database** - Scalable relational storage with indexed queries
✅ **Comprehensive Logging** - Detailed application logs for debugging and monitoring
✅ **API Documentation** - Auto-generated Swagger/OpenAPI documentation

## Technology Stack

- **Framework**: FastAPI 0.119.0+
- **Database**: MySQL (with SQLModel ORM)
- **Authentication**: JWT with JWKS (Asgardeo)
- **Python**: 3.13+
- **Package Manager**: UV

## Quick Start

### Prerequisites

- Python 3.13 or higher
- MySQL 8.0 or higher
- UV package manager (or pip)

### Installation

1. **Clone the repository**
```bash
cd audit-service
```

2. **Create virtual environment** (if not using UV)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
uv pip install -e .
# OR with pip:
pip install -e .
```

4. **Configure environment**
Create a `.env` file in the project root:
```env
# Application
APP_NAME=Audit Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_NAME=audit_service_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306

# CORS
CORS_ORIGINS=https://localhost,http://localhost:3000

# JWT/JWKS
JWKS_URL=https://api.asgardeo.io/t/your-tenant/oauth2/jwks
JWT_AUDIENCE=your_client_id
JWT_ISSUER=https://api.asgardeo.io/t/your-tenant/oauth2/token
```

5. **Ensure MySQL is running**
```bash
# The service will automatically create the database and tables on startup
```

6. **Run the service**
```bash
uvicorn app.main:app --reload
```

The service will start on `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check

```
GET /
GET /health
GET /ready
```

Returns service status and version information.

### Authentication

```
POST /api/v1/auth/verify
GET /api/v1/auth/whoami
GET /api/v1/auth/debug
```

Verify JWT tokens and get current user information.

### Audit Logs - Main Endpoints

#### Create Audit Log
```
POST /api/v1/audit-logs
```

**Request Body:**
```json
{
  "user_id": "string (required)",
  "action": "string (required)",
  "log_type": "string (required)",
  "entity_type": "string (required)",
  "entity_id": "string (required)",
  "service_name": "string (required)",
  "status": "string (default: success)",
  "description": "string (optional)",
  "old_values": "string (optional, JSON)",
  "new_values": "string (optional, JSON)",
  "ip_address": "string (optional)",
  "user_agent": "string (optional)",
  "request_id": "string (optional)",
  "error_message": "string (optional)"
}
```

**Response:**
```json
{
  "id": "integer",
  "user_id": "string",
  "action": "string",
  "log_type": "string",
  "entity_type": "string",
  "entity_id": "string",
  "service_name": "string",
  "status": "string",
  "description": "string",
  "timestamp": "datetime",
  "old_values": "string",
  "new_values": "string",
  "ip_address": "string",
  "user_agent": "string",
  "request_id": "string",
  "error_message": "string"
}
```

#### List All Audit Logs
```
GET /api/v1/audit-logs?offset=0&limit=100&log_type=leave_request&user_id=user123
```

**Response:**
```json
{
  "total": 500,
  "items": [
    {
      "id": 1,
      "user_id": "user123",
      "action": "created",
      "log_type": "leave_request"
    }
  ],
  "limit": 100,
  "offset": 0
}
```

#### Get Specific Audit Log
```
GET /api/v1/audit-logs/{audit_id}
```

**Response:**
```json
{
  "id": 123,
  "user_id": "user123",
  "action": "created",
  "log_type": "leave_request",
  "timestamp": "2024-01-10T10:30:45.123456"
}
```

#### Get User's All Audit Logs
```
GET /api/v1/audit-logs/user/{user_id}?offset=0&limit=100&log_type=leave_request
```

**Response:**
```json
{
  "total": 50,
  "items": [...],
  "limit": 100,
  "offset": 0
}
```

#### Get Audit Logs by Type
```
GET /api/v1/audit-logs/type/{log_type}?offset=0&limit=100&start_date=2024-01-01&end_date=2024-01-31
```

**Response:**
```json
{
  "total": 250,
  "items": [...],
  "limit": 100,
  "offset": 0
}
```

#### Update Audit Log
```
PATCH /api/v1/audit-logs/{audit_id}
```

**Request Body:**
```json
{
  "status": "failure",
  "error_message": "Database connection timeout",
  "description": "Updated description"
}
```

#### Delete Audit Log
```
DELETE /api/v1/audit-logs/{audit_id}
```

## Audit Log Types

| Type | Description | Service |
|------|-------------|---------|
| `leave_request` | Leave request creation | leave-management-service |
| `leave_approval` | Leave approval/rejection | leave-management-service |
| `attendance` | Check-in/check-out events | attendance-service |
| `payroll` | Payroll processing | payroll-service |
| `employee_create` | New employee creation | employee-service |
| `employee_update` | Employee record updates | employee-service |
| `employee_delete` | Employee deletion | employee-service |
| `policy_create` | Policy document creation | policy-service |
| `policy_update` | Policy updates | policy-service |
| `policy_delete` | Policy deletion | policy-service |
| `document_upload` | File/document uploads | document-service |
| `document_delete` | File/document deletion | document-service |
| `role_assignment` | User role assignment | iam-service |
| `permission_change` | Permission changes | iam-service |
| `login` | User authentication | auth-service |
| `logout` | User logout | auth-service |
| `export` | Data export operations | any-service |
| `import` | Data import operations | any-service |
| `other` | Miscellaneous events | any-service |

## Integration Guide for Other Services

### How to Call Audit Service from Your Microservice

#### Python Example (using `httpx`)

```python
import httpx
import json
from typing import Optional, Dict, Any

async def log_audit_event(
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
    """Log an audit event to the Audit Service"""
    audit_service_url = "http://audit-service:8000/api/v1/audit-logs"
    
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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                audit_service_url,
                json=payload,
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        print(f"Failed to log audit event: {e}")
        return None


# Example usage in Leave Management Service
async def create_leave_request(user_id: str, days: int):
    # ... create leave request logic ...
    
    # Log the event
    await log_audit_event(
        user_id=user_id,
        action="created",
        log_type="leave_request",
        entity_type="LeaveRequest",
        entity_id="leave456",
        service_name="leave-management-service",
        new_values={"days": days, "status": "pending"}
    )
```

#### cURL Example

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
    "description": "Leave request created successfully",
    "new_values": "{\"days\": 5, \"status\": \"pending\"}"
  }'
```

#### JavaScript/Node.js Example

```javascript
async function logAuditEvent(data) {
    const auditServiceUrl = "http://audit-service:8000/api/v1/audit-logs";
    
    const response = await fetch(auditServiceUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
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
            description: data.description
        })
    });
    
    return response.json();
}

// Example usage
async function createLeaveRequest(userId, days) {
    // ... create leave request logic ...
    
    await logAuditEvent({
        userId: userId,
        action: "created",
        logType: "leave_request",
        entityType: "LeaveRequest",
        entityId: "leave456",
        serviceName: "leave-management-service",
        newValues: {
            status: "pending",
            days: days,
            startDate: "2024-01-15"
        }
    });
}
```

### Best Practices for Integration

1. **Always include `service_name`** - This identifies which service logged the event
2. **Log both success and failure** - Include both success and error cases
3. **Capture state changes** - For updates, include both `old_values` and `new_values`
4. **Use appropriate log types** - Select from the predefined list to maintain consistency
5. **Never log sensitive data** - Avoid logging passwords, API keys, or personal sensitive data
6. **Include request context** - Pass IP address, user agent, and request ID when available
7. **Handle failures gracefully** - Audit logging failures should not crash your service

```python
"""
Safe audit logging with error handling
"""
try:
    await log_audit_event(
        user_id=current_user.id,
        action="updated",
        log_type="employee_update",
        entity_type="Employee",
        entity_id=str(employee.id),
        service_name="employee-service",
        old_values=old_employee.dict(),
        new_values=new_employee.dict()
    )
except Exception as e:
    logger.error(f"Failed to log audit event: {e}")
    # Continue with operation even if audit logging fails
```

## Querying Audit Logs

### Common Query Scenarios

1. **Get all logs for a specific user**
```
GET /api/v1/audit-logs/user/user123?limit=100
```

2. **Get all leave requests from the last 30 days**
```
GET /api/v1/audit-logs/type/leave_request?start_date=2023-12-11&end_date=2024-01-10&limit=1000
```

3. **Get all failed operations**
```
GET /api/v1/audit-logs?status=failure&limit=100
```

4. **Track all changes to a specific employee**
```
GET /api/v1/audit-logs?entity_type=Employee&entity_id=emp456&limit=500
```

5. **Export audit trail for compliance**
```
GET /api/v1/audit-logs?start_date=2024-01-01&end_date=2024-01-31&limit=10000
```

## Database Schema

### audit_logs Table

The service automatically creates the following table structure:

```sql
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    log_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    old_values JSON,
    new_values JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    service_name VARCHAR(255) NOT NULL,
    request_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    description TEXT,
    
    INDEX idx_user_id (user_id),
    INDEX idx_log_type (log_type),
    INDEX idx_entity_type (entity_type),
    INDEX idx_entity_id (entity_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_service_name (service_name),
    INDEX idx_action (action),
    COMPOSITE INDEX idx_user_log_time (user_id, log_type, timestamp),
    COMPOSITE INDEX idx_entity_time (entity_type, entity_id, timestamp),
    COMPOSITE INDEX idx_log_time (log_type, timestamp),
    COMPOSITE INDEX idx_service_time (service_name, timestamp)
);
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Audit Service | Application name |
| `APP_VERSION` | 1.0.0 | Application version |
| `DEBUG` | False | Debug mode (True/False) |
| `DB_NAME` | audit_service_db | MySQL database name |
| `DB_USER` | root | MySQL username |
| `DB_PASSWORD` | root | MySQL password |
| `DB_HOST` | localhost | MySQL host |
| `DB_PORT` | 3306 | MySQL port |
| `DB_CHARSET` | utf8 | MySQL charset |
| `CORS_ORIGINS` | https://localhost,http://localhost:3000 | Comma-separated CORS origins |
| `JWKS_URL` | https://api.asgardeo.io/... | JWKS URL for JWT validation |
| `JWT_AUDIENCE` | None | Expected JWT audience |
| `JWT_ISSUER` | None | Expected JWT issuer |
| `RETENTION_DAYS` | 365 | How many days to retain logs |
| `MAX_BATCH_SIZE` | 1000 | Maximum batch size for operations |

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: audit_service_db
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 5

  audit-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: mysql
      DB_NAME: audit_service_db
      DB_USER: root
      DB_PASSWORD: root
      DEBUG: "False"
    depends_on:
      mysql:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

## Troubleshooting

### Database Connection Error

**Error**: `Can't connect to MySQL server on 'localhost'`

**Solution**:
1. Verify MySQL is running: `mysql -u root -p`
2. Check database credentials in `.env`
3. Ensure `DB_HOST` is correct (use `host.docker.internal` on Docker for Mac)

### CORS Error

**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution**:
1. Check `CORS_ORIGINS` environment variable
2. Verify the origin making the request matches the configured origins
3. For development, you can set `CORS_ORIGINS=*`

### JWT Token Error

**Error**: `Invalid token` or `Token expired`

**Solution**:
1. Verify the JWKS URL is correct
2. Check that JWT_AUDIENCE and JWT_ISSUER match your token
3. Verify token hasn't expired
4. Test with: `/api/v1/auth/debug` endpoint

### High Query Latency

**Problem**: Queries are slow

**Solution**:
1. Check database indexes are created (see Database Schema section)
2. Monitor MySQL performance: `SHOW PROCESSLIST;`
3. Consider archiving old logs (older than RETENTION_DAYS)
4. Limit query result size with appropriate `limit` parameter

## Performance Optimization

### Query Best Practices

1. **Always use pagination** - Never query all records at once
```
GET /api/v1/audit-logs?limit=100&offset=0
```

2. **Filter by specific criteria** - Use indexed fields
```
GET /api/v1/audit-logs?user_id=user123&log_type=leave_request&limit=100
```

3. **Use date range filters** - Limit temporal scope
```
GET /api/v1/audit-logs/type/leave_request?start_date=2024-01-01&end_date=2024-01-31
```

4. **Archive old logs** - Implement retention policy
```
DELETE FROM audit_log WHERE timestamp < DATE_SUB(NOW(), INTERVAL 365 DAY);
```

## License

This project is part of the HRMS microservices ecosystem.

## Support

For issues, questions, or contributions, please refer to the project documentation:

- **Full Documentation**: See this README
- **Integration Guide**: See `INTEGRATION_GUIDE.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`
- **API Documentation**: http://localhost:8000/docs

---

**Version**: 1.0.0  
**Last Updated**: January 2024