# Compliance Service - Integration Guide

## Overview

The Compliance Service is designed to work in conjunction with external services (Employee Service, User Management Service) to provide comprehensive GDPR compliance tracking and data governance. This guide explains how to connect these services together.

## Architecture

The Compliance Service follows a microservices architecture where:

- **Compliance Service** (this service): Manages data inventory, access controls, and retention policies
- **Employee Service**: Provides employee information and data
- **User Management Service**: Manages user authentication and authorization

```
┌──────────────────────┐
│  Compliance Service  │
├──────────────────────┤
│  - Data Inventory    │
│  - Access Controls   │
│  - Retention Mgmt    │
└──────────────────────┘
           ↓
    ┌──────┴──────┐
    ↓             ↓
┌─────────────┐  ┌──────────────────┐
│  Employee   │  │  User Management │
│  Service    │  │  Service         │
└─────────────┘  └──────────────────┘
```

## Configuration

### Environment Variables

Configure these environment variables in `.env`:

```env
# Compliance Service
APP_NAME=Compliance Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_NAME=compliance_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306

# External Services (CRITICAL FOR INTEGRATION)
EMPLOYEE_SERVICE_URL=http://localhost:8001
USER_MANAGEMENT_SERVICE_URL=http://localhost:8002

# JWT/JWKS Settings
JWKS_URL=https://api.asgardeo.io/t/pookieland/oauth2/jwks
JWT_AUDIENCE=your-client-id
JWT_ISSUER=https://api.asgardeo.io/t/pookieland/oauth2/token

# CORS
CORS_ORIGINS=https://localhost,http://localhost:3000
```

## API Endpoints Reference

### Compliance Endpoints (Read-Only - Integration Points)

These endpoints are used by other services to query compliance data:

#### 1. Get Data Inventory (GDPR Article 30)
```
GET /api/v1/compliance/data-inventory
Headers: Authorization: Bearer <JWT_TOKEN>
Query Parameters:
  - category_id: int (optional)
  - data_type: string (optional)
  - sensitivity_level: string (optional)
  - skip: int (default: 0)
  - limit: int (default: 100, max: 1000)

Response: {
  "count": int,
  "inventory": [{
    "id": int,
    "data_name": string,
    "data_type": string,
    "storage_location": string,
    "purpose_of_processing": string,
    "legal_basis": string,
    "retention_days": int,
    "encryption_status": string,
    "access_control_level": string,
    "created_at": datetime,
    "updated_at": datetime
  }],
  "categories": [...],
  "gdpr_article": "Article 30 - Records of Processing Activities"
}
```

#### 2. Get Employee's Data About Me (GDPR Article 15)
```
GET /api/v1/compliance/employee/{employee_id}/data-about-me
Headers: Authorization: Bearer <JWT_TOKEN>

Response: {
  "employee_id": string,
  "data_summary": {
    "total_data_entries": int,
    "data_categories": [string],
    "retention_policies": {
      "category_name": {
        "data_type": string,
        "retention_days": int,
        "deletion_date": datetime
      }
    },
    "next_scheduled_deletion": datetime
  },
  "access_information": {
    "employees_with_access_to_your_data": int
  },
  "security_measures": {
    "encryption": string,
    "access_control": string,
    "audit_logging": string
  },
  "gdpr_article": "Article 15 - Right of Access"
}
```

#### 3. Get Employee Access Controls
```
GET /api/v1/compliance/employee/{employee_id}/access-controls
Headers: Authorization: Bearer <JWT_TOKEN>

Response: {
  "employee_id": string,
  "total_data_access_entries": int,
  "role_based_accesses": int,
  "direct_accesses": int,
  "accessible_data_categories": [{
    "data_id": int,
    "data_name": string,
    "data_type": string,
    "access_level": string,
    "access_reason": string,
    "role_based": bool,
    "role_name": string,
    "granted_at": datetime,
    "expires_at": datetime,
    "is_active": bool
  }],
  "access_summary": {
    "read_access": int,
    "write_access": int,
    "delete_access": int,
    "admin_access": int
  }
}
```

#### 4. Get Data Retention Report (GDPR Article 5)
```
GET /api/v1/compliance/data-retention-report
Headers: Authorization: Bearer <JWT_TOKEN>
Query Parameters:
  - status: string (optional, one of: active, expiring_soon, expired, deleted)
  - days_threshold: int (default: 30)

Response: {
  "total_records_tracked": int,
  "active_records": int,
  "expiring_soon": int,
  "expired_records": int,
  "deleted_records": int,
  "marked_for_deletion": int,
  "action_items": {
    "delete_immediately": int,
    "delete_within_days": int
  },
  "retention_items": [{
    "id": int,
    "data_name": string,
    "record_id": string,
    "data_created_at": datetime,
    "retention_expires_at": datetime,
    "days_until_deletion": int,
    "data_age_days": int,
    "category": string,
    "data_subject": string,
    "status": string,
    "marked_for_deletion": bool
  }],
  "summary_by_category": {...},
  "gdpr_article": "Article 5 - Storage Limitation"
}
```

### Management Endpoints (Admin-Only)

#### Data Categories
```
POST   /api/v1/compliance/inventory/categories          (Create)
GET    /api/v1/compliance/inventory/categories          (List)
GET    /api/v1/compliance/inventory/categories/{id}     (Get)
PATCH  /api/v1/compliance/inventory/categories/{id}     (Update)
DELETE /api/v1/compliance/inventory/categories/{id}     (Delete)
```

#### Data Inventory Entries
```
POST   /api/v1/compliance/inventory/entries             (Create)
GET    /api/v1/compliance/inventory/entries             (List)
GET    /api/v1/compliance/inventory/entries/{id}        (Get)
PATCH  /api/v1/compliance/inventory/entries/{id}        (Update)
DELETE /api/v1/compliance/inventory/entries/{id}        (Delete)
GET    /api/v1/compliance/inventory/entries/{id}/stats  (Statistics)
```

## Integration Patterns

### Pattern 1: Employee Service Integration

**Use Case**: Employee Service needs to display what data is held about an employee

```
Employee Service → Compliance Service API
GET /api/v1/compliance/employee/{employee_id}/data-about-me
```

**Example Flow**:
1. User logs into Employee Portal
2. Clicks "My Data" button
3. Employee Service makes authenticated request to Compliance Service
4. Displays employee's data summary with retention schedule
5. User can request data deletion if compliant with retention policy

**Implementation Example (Python)**:
```python
import httpx
from app.core.config import settings

async def get_employee_data(employee_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.COMPLIANCE_SERVICE_URL}/api/v1/compliance/employee/{employee_id}/data-about-me",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### Pattern 2: User Management Integration

**Use Case**: User Management needs to track access permissions for compliance audits

```
User Management Service → Compliance Service API
GET /api/v1/compliance/employee/{employee_id}/access-controls
```

**Example Flow**:
1. Security auditor requests access review for an employee
2. User Management Service queries Compliance Service
3. Gets comprehensive list of data access and reasons
4. Generates compliance report
5. Archives for audit trail

**Implementation Example (Python)**:
```python
async def audit_employee_access(employee_id: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.COMPLIANCE_SERVICE_URL}/api/v1/compliance/employee/{employee_id}/access-controls",
            headers={"Authorization": f"Bearer {token}"}
        )
        access_data = response.json()
        
        # Generate audit report
        report = {
            "employee_id": employee_id,
            "timestamp": datetime.utcnow(),
            "accesses": access_data["accessible_data_categories"],
            "total_entries": access_data["total_data_access_entries"]
        }
        return report
```

### Pattern 3: Automated Compliance Monitoring

**Use Case**: Scheduled job to check data retention compliance

```
Scheduler (Celery/APScheduler) → Compliance Service API
GET /api/v1/compliance/data-retention-report?status=expired
```

**Example Flow**:
1. Scheduled job runs daily at 2 AM
2. Queries Compliance Service for expired records
3. Initiates deletion workflow
4. Sends notification to Data Protection Officer
5. Logs actions for audit trail

**Implementation Example (Python)**:
```python
from celery import shared_task
from datetime import datetime

@shared_task
def check_data_retention():
    """Daily retention compliance check"""
    response = await httpx.get(
        f"{settings.COMPLIANCE_SERVICE_URL}/api/v1/compliance/data-retention-report",
        params={"status": "expired"},
        headers={"Authorization": f"Bearer {SERVICE_JWT_TOKEN}"}
    )
    
    data = response.json()
    
    if data["expired_records"] > 0:
        # Send alert to DPO
        send_alert(
            f"Found {data['expired_records']} expired records requiring deletion"
        )
        # Log in audit trail
        log_compliance_event("expired_records_found", data)
```

### Pattern 4: Data Inventory Synchronization

**Use Case**: Employee Service has new data sources that need to be registered

```
Employee Service → Compliance Service (via Admin/Compliance Officer)
POST /api/v1/compliance/inventory/entries
```

**Example**: When Employee Service adds a new salary tracking system:
```python
new_inventory = {
    "data_name": "Salary and Compensation",
    "category_id": 2,  # Financial Data
    "data_type": "financial",
    "storage_location": "salary_db.compensation_table",
    "purpose_of_processing": "Employee payroll and compensation management",
    "legal_basis": "Employment Contract",
    "retention_days": 365,
    "data_subjects": "Employees",
    "encryption_status": "encrypted",
    "access_control_level": "restricted",
    "processing_system": "payroll-system-v2"
}

response = await httpx.post(
    f"{settings.COMPLIANCE_SERVICE_URL}/api/v1/compliance/inventory/entries",
    json=new_inventory,
    headers={"Authorization": f"Bearer {admin_token}"}
)
```

## Authentication Flow

All endpoints require valid JWT tokens. The token must include:

```json
{
  "sub": "user-id",
  "username": "user@example.com",
  "email": "user@example.com",
  "roles": ["admin", "compliance_officer"],
  "permissions": ["compliance:read", "compliance:write"],
  "iat": 1234567890,
  "exp": 1234571490
}
```

### Token Validation
1. Service validates token signature using JWKS endpoint
2. Verifies token hasn't expired
3. Checks audience claim
4. Extracts roles and permissions
5. Enforces role-based access control

### Required Roles by Endpoint

| Endpoint | Required Role |
|----------|---------------|
| GET /compliance/data-inventory | None (any authenticated user) |
| GET /compliance/employee/{id}/data-about-me | User viewing own data OR admin |
| GET /compliance/employee/{id}/access-controls | User viewing own data OR admin |
| GET /compliance/data-retention-report | None (any authenticated user) |
| POST/PATCH/DELETE management endpoints | admin OR compliance_officer |

## Error Handling

### Common Error Responses

```
401 Unauthorized
{
  "detail": "Invalid token or token expired"
}

403 Forbidden
{
  "detail": "Insufficient permissions. Required roles: admin, compliance_officer"
}

404 Not Found
{
  "detail": "Data inventory entry not found"
}

400 Bad Request
{
  "detail": "Data category with this name already exists"
}
```

## Best Practices

### 1. Token Management
- Use service-to-service tokens with appropriate scopes
- Set reasonable expiration times (30-60 minutes)
- Implement token refresh mechanism
- Never hardcode tokens in code

### 2. Error Handling
```python
try:
    response = await client.get(compliance_endpoint, headers=headers)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        # Handle token expiration, refresh and retry
        pass
    elif e.response.status_code == 403:
        # Log unauthorized access attempt
        log_security_event("unauthorized_access", e)
    else:
        raise
```

### 3. Rate Limiting
- Implement exponential backoff for retries
- Cache responses when appropriate (with TTL)
- Use connection pooling to reuse connections

### 4. Audit Logging
- Log all compliance API calls with:
  - Timestamp
  - User ID / Service ID
  - Endpoint and method
  - Request parameters
  - Response status
  - Data accessed

### 5. Data Privacy
- Never log sensitive data in plaintext
- Mask PII in logs
- Implement request/response encryption for sensitive operations
- Use TLS/HTTPS for all API calls

## Testing Integration

### Unit Test Example
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_employee_data_integration():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "employee_id": "emp-123",
            "data_summary": {
                "total_data_entries": 5
            }
        }
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await get_employee_data("emp-123", "fake-token")
        assert result["employee_id"] == "emp-123"
```

### Integration Test Example
```python
@pytest.mark.integration
async def test_compliance_service_integration():
    # Start both services
    # Create test data
    # Make API calls
    # Verify results
    
    response = await client.get(
        "/api/v1/compliance/data-inventory",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["inventory"]) > 0
```

## Troubleshooting

### Service Connection Issues
- Verify `EMPLOYEE_SERVICE_URL` and `USER_MANAGEMENT_SERVICE_URL` in `.env`
- Check network connectivity between services
- Verify firewall rules allow inter-service communication
- Check service logs for connection errors

### Authentication Failures
- Verify JWT token is valid and not expired
- Check token includes required claims
- Verify JWKS endpoint is accessible
- Check token audience matches configuration

### Data Not Found
- Verify data inventory entries have been created
- Check category IDs are correct
- Verify employee IDs match those in Employee Service
- Check access controls are properly configured

## Performance Considerations

### Caching Strategy
- Cache data inventory (1 hour TTL)
- Cache employee access controls (30 minute TTL)
- Cache retention reports (1 hour TTL)
- Implement cache invalidation on data changes

### Pagination
- Always use pagination for list endpoints
- Default limit is 100, max is 1000
- Use `skip` parameter for offset pagination

### Connection Pooling
```python
# Reuse client connections
client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=50
    )
)
```

## Monitoring and Alerts

### Key Metrics to Monitor
- API response times
- Error rates by endpoint
- Number of unauthorized access attempts
- Data retention compliance rate
- Access control violations

### Alert Thresholds
- Response time > 2 seconds: Warning
- Error rate > 5%: Alert
- Unauthorized attempts > 10/hour: Critical
- Expired records not deleted within SLA: Critical

## Support and Maintenance

For integration issues or questions:
1. Check this guide first
2. Review API documentation at `/docs`
3. Check service logs
4. Contact compliance team
