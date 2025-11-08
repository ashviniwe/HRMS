# Attendance Management Service - Integration Guide

## Overview

The Attendance Management Service is a FastAPI-based microservice designed to handle all attendance-related operations for the HRMS (Human Resource Management System). This service is built to work seamlessly with a dedicated **Employee Management Service** for employee validation and enrichment.

## Architecture

### Service Communication

The Attendance Management Service communicates with the Employee Management Service to:
- Validate employee existence before recording attendance
- Retrieve employee details for enriched attendance reports
- Ensure data consistency across microservices

```
┌─────────────────────────────┐
│   Attendance Service        │
│  (Port: 8001)               │
└────────────┬────────────────┘
             │ HTTP/REST
             │ (AsyncIO)
             ▼
┌─────────────────────────────┐
│  Employee Service           │
│  (Port: 8000)               │
│  (External/Dedicated)       │
└─────────────────────────────┘
```

## Configuration

### Environment Variables

The Attendance Management Service requires the following environment variables for integration with the Employee Service:

```bash
# Employee Service Configuration
EMPLOYEE_SERVICE_URL=http://localhost:8000

# Application Settings
APP_NAME=Attendance Management Service
APP_VERSION=1.0.0
DEBUG=False

# Database Settings
DB_NAME=hrms_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_CHARSET=utf8

# CORS Settings
CORS_ORIGINS=https://localhost,http://localhost:3000
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

### Setting Up the Environment

1. **Create a `.env` file** in the service root directory:

```bash
cd attendance-management-service
cp .env.example .env
```

2. **Update the Employee Service URL** in `.env`:

```bash
# For local development
EMPLOYEE_SERVICE_URL=http://localhost:8000

# For Docker environment
EMPLOYEE_SERVICE_URL=http://employee-service:8000

# For production
EMPLOYEE_SERVICE_URL=https://employee-service.yourdomain.com
```

3. **Verify database connection settings** match your MySQL instance:

```bash
DB_HOST=localhost          # or your database host
DB_USER=root               # your database user
DB_PASSWORD=root           # your database password
DB_NAME=hrms_db            # database name
```

## API Integration Points

### Employee Service Endpoints Used

The Attendance Service communicates with the following Employee Service endpoints:

#### 1. Verify Employee Existence
```http
GET /api/v1/employees/{employee_id}
```

**Used in:**
- `POST /attendance/check-in`
- `POST /attendance/check-out`
- `POST /attendance/manual`
- `GET /attendance/employee/{employee_id}`
- `PUT /attendance/{attendance_id}`
- `GET /attendance/summary/{employee_id}/{month}`

**Response (Success - 200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30
}
```

**Response (Not Found - 404):**
```json
{
  "detail": "Employee not found"
}
```

#### 2. Get Employee Details
```http
GET /api/v1/employees/{employee_id}
```

Used to retrieve full employee information for attendance records enrichment.

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30,
  "department": "Engineering",
  "email": "john.doe@company.com"
}
```

#### 3. List Employees
```http
GET /api/v1/employees/?offset=0&limit=100
```

Can be used for bulk validation or generating department-wide attendance reports.

## Client Implementation

### Employee Service Client

The service includes a built-in HTTP client for communicating with the Employee Service:

**Location:** `app/api/clients/employee_service.py`

**Features:**
- Asynchronous HTTP requests using `httpx`
- Automatic error handling and logging
- Connection pooling and timeout management
- Graceful failure modes

### Client Methods

#### verify_employee_exists()
```python
async def verify_employee_exists(employee_id: int) -> bool:
    """
    Verify if an employee exists in the employee management service.
    Returns True if exists, False otherwise.
    """
```

**Example Usage:**
```python
from app.api.clients.employee_service import employee_service

exists = await employee_service.verify_employee_exists(employee_id=123)
if exists:
    print("Employee found")
else:
    print("Employee not found")
```

#### get_employee()
```python
async def get_employee(employee_id: int) -> Optional[dict]:
    """
    Retrieve employee details from the employee management service.
    Returns employee data if found, None otherwise.
    """
```

**Example Usage:**
```python
employee = await employee_service.get_employee(employee_id=123)
if employee:
    print(f"Employee name: {employee['name']}")
```

#### get_employees_list()
```python
async def get_employees_list(offset: int = 0, limit: int = 100) -> Optional[list]:
    """
    Retrieve list of employees with pagination.
    """
```

## Attendance Service API Endpoints

### Core Endpoints

#### 1. Employee Check-In
```http
POST /api/v1/attendance/check-in
Content-Type: application/json

{
  "employee_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "employee_id": 1,
  "date": "2024-01-15",
  "check_in_time": "2024-01-15T08:00:00",
  "check_out_time": null,
  "status": "present",
  "notes": null,
  "created_at": "2024-01-15T08:00:00",
  "updated_at": "2024-01-15T08:00:00"
}
```

**Errors:**
- `400`: Employee does not exist
- `404`: Invalid request data

#### 2. Employee Check-Out
```http
POST /api/v1/attendance/check-out
Content-Type: application/json

{
  "employee_id": 1
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "employee_id": 1,
  "date": "2024-01-15",
  "check_in_time": "2024-01-15T08:00:00",
  "check_out_time": "2024-01-15T17:30:00",
  "status": "present",
  "notes": null,
  "created_at": "2024-01-15T08:00:00",
  "updated_at": "2024-01-15T17:30:00"
}
```

**Errors:**
- `400`: Employee does not exist
- `404`: No check-in record found for today

#### 3. Manual Attendance Entry
```http
POST /api/v1/attendance/manual
Content-Type: application/json

{
  "employee_id": 1,
  "date": "2024-01-15",
  "check_in_time": "2024-01-15T08:30:00",
  "check_out_time": "2024-01-15T17:00:00",
  "status": "present",
  "notes": "Approved late arrival"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "employee_id": 1,
  "date": "2024-01-15",
  "check_in_time": "2024-01-15T08:30:00",
  "check_out_time": "2024-01-15T17:00:00",
  "status": "present",
  "notes": "Approved late arrival",
  "created_at": "2024-01-15T08:00:00",
  "updated_at": "2024-01-15T08:00:00"
}
```

#### 4. Get Specific Attendance Record
```http
GET /api/v1/attendance/{attendance_id}
```

**Response (200 OK):** Returns attendance record by ID

#### 5. Get Employee's Attendance Records
```http
GET /api/v1/attendance/employee/{employee_id}?offset=0&limit=100&start_date=2024-01-01&end_date=2024-01-31
```

**Query Parameters:**
- `offset`: Skip N records (default: 0)
- `limit`: Return max N records (default: 100, max: 100)
- `start_date`: Filter from date (YYYY-MM-DD format)
- `end_date`: Filter to date (YYYY-MM-DD format)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "employee_id": 1,
    "date": "2024-01-15",
    "check_in_time": "2024-01-15T08:00:00",
    "check_out_time": "2024-01-15T17:30:00",
    "status": "present",
    "notes": null,
    "created_at": "2024-01-15T08:00:00",
    "updated_at": "2024-01-15T08:00:00"
  }
]
```

#### 6. Update Attendance Record
```http
PUT /api/v1/attendance/{attendance_id}
Content-Type: application/json

{
  "status": "late",
  "notes": "Traffic delay"
}
```

**Response (200 OK):** Returns updated attendance record

#### 7. Get Monthly Summary
```http
GET /api/v1/attendance/summary/{employee_id}/{month}
```

**Parameters:**
- `employee_id`: Employee ID
- `month`: Month in YYYY-MM format (e.g., 2024-01)

**Response (200 OK):**
```json
{
  "employee_id": 1,
  "month": "2024-01",
  "total_days_worked": 20,
  "total_present": 18,
  "total_absent": 1,
  "total_late": 1,
  "working_hours": 160.5,
  "records": [
    {
      "id": 1,
      "employee_id": 1,
      "date": "2024-01-01",
      "check_in_time": "2024-01-01T08:00:00",
      "check_out_time": "2024-01-01T17:30:00",
      "status": "present",
      "notes": null,
      "created_at": "2024-01-01T08:00:00",
      "updated_at": "2024-01-01T08:00:00"
    }
  ]
}
```

#### 8. Health Check
```http
GET /api/v1/attendance/health
GET /health
GET /
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "attendance-management-service",
  "version": "1.0.0"
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Status Code | Scenario | Description |
|-------------|----------|-------------|
| 200 | Success | Request processed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or employee doesn't exist |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists (duplicate record) |
| 500 | Server Error | Internal server error |

### Employee Service Connection Errors

If the Employee Service is unreachable:

1. **Timeout (>30 seconds)**
   - Logged as error
   - Returns `400 Bad Request` with generic message
   - Service continues operating

2. **Connection Refused**
   - Logged as error
   - Returns `400 Bad Request`
   - Suggests employee service is down

3. **Invalid Response**
   - Logged as error
   - Returns `400 Bad Request`
   - Helps debug integration issues

## Testing Integration

### 1. Verify Employee Service is Running

```bash
curl -X GET http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "employee-management-service",
  "version": "1.0.0"
}
```

### 2. Test Check-In (with valid employee)

Assuming employee with ID 1 exists:

```bash
curl -X POST http://localhost:8001/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1}'
```

### 3. Test Check-In (with invalid employee)

```bash
curl -X POST http://localhost:8001/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 99999}'
```

Expected: `400 Bad Request` with message "Employee 99999 does not exist"

### 4. Test Monthly Summary

```bash
curl -X GET http://localhost:8001/api/v1/attendance/summary/1/2024-01
```

### 5. Interactive Testing with Swagger UI

Navigate to: `http://localhost:8001/docs`

This provides an interactive interface to test all endpoints.

## Deployment Scenarios

### Local Development

```bash
# Terminal 1: Run Employee Service
cd employee-management-service
uvicorn app.main:app --host localhost --port 8000

# Terminal 2: Run Attendance Service
cd attendance-management-service
EMPLOYEE_SERVICE_URL=http://localhost:8000 \
uvicorn app.main:app --host localhost --port 8001
```

### Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: hrms_db
    ports:
      - "3306:3306"

  employee-service:
    build:
      context: ./employee-management-service
      dockerfile: Dockerfile
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: root
      DB_NAME: hrms_db
    ports:
      - "8000:8000"
    depends_on:
      - mysql

  attendance-service:
    build:
      context: ./attendance-management-service
      dockerfile: Dockerfile
    environment:
      DB_HOST: mysql
      DB_USER: root
      DB_PASSWORD: root
      DB_NAME: hrms_db
      EMPLOYEE_SERVICE_URL: http://employee-service:8000
    ports:
      - "8001:8000"
    depends_on:
      - mysql
      - employee-service

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - employee-service
      - attendance-service
```

Run with:
```bash
docker-compose up
```

### Kubernetes Deployment

Example ConfigMap for environment variables:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: attendance-service-config
spec:
  data:
    EMPLOYEE_SERVICE_URL: http://employee-service:8000
    APP_NAME: Attendance Management Service
    DB_HOST: mysql-service
    DB_NAME: hrms_db
```

## Troubleshooting

### Issue: "Employee does not exist" error for valid employees

**Diagnosis:**
1. Verify Employee Service is running: `curl http://localhost:8000/health`
2. Check employee exists: `curl http://localhost:8000/api/v1/employees/1`
3. Verify `EMPLOYEE_SERVICE_URL` in `.env`

**Solution:**
- Ensure Employee Service URL is correct
- Check network connectivity between services
- Verify database has employee records

### Issue: Connection timeout to Employee Service

**Diagnosis:**
- Check if Employee Service is running on the configured URL
- Verify firewall rules allow communication

**Solution:**
```bash
# Test connectivity
telnet localhost 8000

# Or use curl with verbose flag
curl -v http://localhost:8000/health
```

### Issue: Database table not created

**Diagnosis:**
- Check MySQL connection settings
- Verify database user has CREATE TABLE permissions

**Solution:**
```bash
# Run database creation manually
python3 -c "from app.core.database import create_db_and_tables; create_db_and_tables()"
```

### Issue: CORS errors when calling from frontend

**Diagnosis:**
- Check `CORS_ORIGINS` in `.env`
- Verify frontend URL matches configured origins

**Solution:**
Update `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://yourdomain.com
```

## Database Schema

### Attendance Table

```sql
CREATE TABLE attendance (
  id INT PRIMARY KEY AUTO_INCREMENT,
  employee_id INT NOT NULL,
  check_in_time DATETIME,
  check_out_time DATETIME,
  date VARCHAR(10) NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  notes VARCHAR(500),
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  INDEX idx_employee_id (employee_id),
  INDEX idx_date (date)
);
```

**Indexes:**
- `employee_id`: Quick lookup of employee records
- `date`: Efficient date-range queries

## Performance Considerations

### Employee Service Caching

The client includes built-in connection pooling via `httpx.AsyncClient`. For high-volume scenarios, consider:

1. **Response Caching**: Cache employee existence for 5-10 minutes
2. **Batch Validation**: Validate multiple employees in single request
3. **Load Balancing**: Deploy multiple Attendance Service instances

### Database Indexing

Ensure these indexes exist for optimal query performance:

```sql
CREATE INDEX idx_employee_date ON attendance(employee_id, date);
CREATE INDEX idx_date ON attendance(date);
```

## Security Considerations

### Service-to-Service Authentication

For production deployments, add authentication between services:

```python
# In employee_service.py
async def verify_employee_exists(self, employee_id: int) -> bool:
    headers = {
        "Authorization": f"Bearer {SERVICE_TOKEN}",
        "X-Service-ID": "attendance-service"
    }
    # ... use headers in request
```

### Input Validation

All endpoints validate:
- Employee IDs must be positive integers
- Dates must be in ISO format (YYYY-MM-DD)
- Status values are restricted to: `present`, `absent`, `late`

### Rate Limiting

Consider implementing rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/check-in")
@limiter.limit("100/minute")
async def check_in(request: CheckInRequest, session: SessionDep):
    # ...
```

## Support and Maintenance

### Logging

All operations are logged to help with debugging:

```python
from app.core.logging import get_logger
logger = get_logger(__name__)

# Logs include:
# - Employee verification attempts
# - HTTP client errors
# - Database operations
# - Request/response details
```

### Monitoring

Key metrics to monitor:

1. **Employee Service Response Time**: Track average response time
2. **Attendance Record Creation Rate**: Monitor peak usage
3. **Database Performance**: Watch slow queries
4. **Error Rates**: Track validation failures

### Updates and Compatibility

When updating services:

1. **Backward Compatibility**: Maintain old API endpoints for 1 version
2. **Database Migrations**: Plan for schema changes
3. **Versioning**: Use `/api/v1`, `/api/v2` paths for versions

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Contact and Support

For issues or questions regarding integration:

1. Check the troubleshooting section above
2. Review service logs for detailed error messages
3. Verify all environment variables are correctly set
4. Test Employee Service connectivity independently