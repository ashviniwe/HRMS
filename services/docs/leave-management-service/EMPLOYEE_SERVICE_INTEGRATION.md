# Employee Service Integration Guide

## Overview

The Leave Management Service integrates with an external Employee Service to validate employee existence before processing leave requests. This document explains the integration architecture, configuration, and implementation details.

## Integration Architecture

### Current Implementation

The service uses a **fallback strategy** for employee verification:

1. **Primary**: Check local database (if Employee table exists locally)
2. **Secondary**: Call Employee Service API (if configured)
3. **Fallback**: Return error if neither source can verify the employee

### Why This Approach?

- **Resilience**: Works even if Employee Service is temporarily unavailable
- **Performance**: Local database queries are faster than API calls
- **Flexibility**: Can operate in different deployment scenarios
- **Caching**: Reduces redundant API calls through in-memory cache

## Configuration

### Setting Up Employee Service URL

Add the following to your `.env` file:

```env
EMPLOYEE_SERVICE_URL=http://localhost:8001
```

Or set it as an environment variable:

```bash
export EMPLOYEE_SERVICE_URL=http://employee-service:8001
```

### Configuration in `app/core/config.py`

Add this to the `Settings` class:

```python
# Employee Service Configuration
EMPLOYEE_SERVICE_URL: str | None = None  # Optional: set to enable external service calls
EMPLOYEE_SERVICE_TIMEOUT: int = 5  # Timeout in seconds for API calls
```

## API Integration Details

### Employee Service Expected Endpoints

Your Employee Service should expose:

#### Get Employee by ID
```
GET /api/v1/employees/{employee_id}
```

**Success Response (200):**
```json
{
    "id": 1,
    "name": "John Doe",
    "age": 30
}
```

**Not Found Response (404):**
```json
{
    "detail": "Employee not found"
}
```

### Implementation File

**Location**: `app/services/employee_service.py`

**Key Functions**:

- `verify_employee_exists(employee_id: int) -> bool`
  - Verifies employee exists in either Employee Service or local database
  - Returns `True` if found, `False` otherwise
  - Used in leave creation and employee leave retrieval endpoints

- `get_employee_name(employee_id: int) -> str | None`
  - Retrieves employee name for enriching leave responses
  - Optional feature for future use

- `_verify_via_employee_service(employee_id: int) -> bool`
  - Makes HTTP call to Employee Service API
  - Handles timeouts and connection errors gracefully

- `_verify_local_database(employee_id: int) -> bool`
  - Queries local Employee table
  - Used as fallback if Employee Service is unavailable

## How It Works

### Leave Creation Flow

```
POST /api/v1/leaves
{
    "employee_id": 1,
    "leave_type": "annual",
    "start_date": "2024-01-15T00:00:00",
    "end_date": "2024-01-17T00:00:00",
    "reason": "Vacation"
}
```

**Verification Process**:

1. Leave creation endpoint calls `verify_employee_exists(1)`
2. Service checks cache - not found
3. If `EMPLOYEE_SERVICE_URL` is configured:
   - Makes `GET /api/v1/employees/1` call
   - Returns `True` if 200 status, `False` if 404
   - Caches result
4. If Employee Service fails or not configured:
   - Falls back to local database query
   - Checks Employee table for ID 1
5. If employee found: Create leave with PENDING status
6. If employee not found: Return 404 error

### Employee Leaves Retrieval Flow

```
GET /api/v1/leaves/employee/1
```

Same verification process as leave creation to ensure employee exists before returning their leaves.

## Error Handling

### Scenarios and Responses

| Scenario | Status | Response |
|----------|--------|----------|
| Valid employee, leave created | 201 | Created leave object |
| Employee not found | 404 | `{"detail": "Employee not found"}` |
| Invalid date range | 400 | `{"detail": "start_date must be before end_date"}` |
| Employee Service timeout | 404 | Falls back to local database |
| Both sources unavailable | 404 | `{"detail": "Employee not found"}` |

## Performance Considerations

### Caching

The service implements an in-memory cache to reduce API calls:

```python
_employee_cache = {}  # Global cache dictionary
```

**Cache Behavior**:
- Employee verification results are cached for the lifetime of the application
- Cache is cleared on application restart
- No TTL (time-to-live) implemented - future enhancement opportunity

**Example**:
```python
# First call: Makes API/DB call
verify_employee_exists(1)  # Queries database or service

# Subsequent calls: Uses cache
verify_employee_exists(1)  # Returns cached result
```

### Clearing Cache

For testing or when employee data changes:

```python
from app.services.employee_service import clear_employee_cache
clear_employee_cache()
```

## Extending the Integration

### Option 1: Adding JWT Validation to Employee Service Calls

```python
def _verify_via_employee_service(employee_id: int) -> bool:
    """With JWT authentication"""
    headers = {
        "Authorization": f"Bearer {get_service_token()}"
    }
    with httpx.Client(timeout=5.0) as client:
        response = client.get(url, headers=headers)
```

### Option 2: Implementing Cache TTL

```python
from datetime import datetime, timedelta

_employee_cache = {}

def verify_employee_exists(employee_id: int) -> bool:
    cache_entry = _employee_cache.get(employee_id)
    if cache_entry:
        cached_result, timestamp = cache_entry
        if datetime.utcnow() - timestamp < timedelta(hours=1):
            return cached_result
    
    # Get fresh result...
    result = ...
    _employee_cache[employee_id] = (result, datetime.utcnow())
    return result
```

### Option 3: Service-to-Service Authentication

If your Employee Service requires authentication:

```python
# Add to Settings class
EMPLOYEE_SERVICE_AUTH_TYPE: str = "none"  # or "basic", "bearer", "oauth2"
EMPLOYEE_SERVICE_API_KEY: str | None = None
EMPLOYEE_SERVICE_CLIENT_ID: str | None = None
```

Then implement appropriate headers in `_verify_via_employee_service()`.

## Testing

### Local Testing (Without External Service)

1. Ensure Employee records exist in local database
2. Set `EMPLOYEE_SERVICE_URL` to empty/None in `.env`
3. Service will automatically fall back to local database

### Integration Testing (With External Service)

```python
# test_employee_integration.py
import pytest
from app.services.employee_service import verify_employee_exists, clear_employee_cache

@pytest.fixture(autouse=True)
def clear_cache():
    clear_employee_cache()
    yield
    clear_employee_cache()

def test_verify_existing_employee(client):
    """Test verification of existing employee"""
    response = client.post("/api/v1/leaves", json={
        "employee_id": 1,
        "leave_type": "annual",
        "start_date": "2024-01-15T00:00:00",
        "end_date": "2024-01-17T00:00:00"
    })
    assert response.status_code == 201

def test_verify_nonexistent_employee(client):
    """Test verification of non-existent employee"""
    response = client.post("/api/v1/leaves", json={
        "employee_id": 99999,
        "leave_type": "annual",
        "start_date": "2024-01-15T00:00:00",
        "end_date": "2024-01-17T00:00:00"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"
```

## Troubleshooting

### Issue: "Employee not found" for existing employees

**Solution**:
1. Verify `EMPLOYEE_SERVICE_URL` is correctly configured
2. Test Employee Service directly: `curl http://localhost:8001/api/v1/employees/1`
3. Clear the cache: `clear_employee_cache()`
4. Check logs for specific error messages

### Issue: Employee Service calls timing out

**Solution**:
1. Increase `EMPLOYEE_SERVICE_TIMEOUT` in config
2. Verify Employee Service is running and accessible
3. Check network connectivity between services
4. Service will fall back to local database after timeout

### Issue: High latency in leave creation

**Solution**:
1. Enable caching by accessing same employees multiple times
2. Ensure Employee Service is nearby (same network/datacenter)
3. Consider increasing cache TTL if implementing TTL-based caching
4. Monitor Employee Service performance

## Future Enhancements

1. **Cache Expiration**: Implement TTL-based cache invalidation
2. **Metrics**: Add Prometheus metrics for API call success rates
3. **Circuit Breaker**: Implement circuit breaker pattern for cascading failures
4. **Batch Verification**: Support bulk employee verification
5. **Webhooks**: Subscribe to employee deletion events
6. **Service Discovery**: Use service mesh (Istio, Consul) for dynamic service location

## Related Files

- `app/services/employee_service.py` - Integration implementation
- `app/api/routes/leaves.py` - Leave endpoints using the integration
- `app/core/config.py` - Configuration settings
- `app/models/leave.py` - Leave database model