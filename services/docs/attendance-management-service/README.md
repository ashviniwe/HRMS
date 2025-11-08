# Attendance Management Service

A FastAPI-based microservice for managing employee attendance tracking, check-in/check-out operations, and attendance reporting. This service is part of the HRMS (Human Resource Management System) and integrates with a dedicated Employee Management Service.

## Features

- ✅ **Employee Check-In/Check-Out**: Real-time attendance tracking
- ✅ **Manual Attendance Entry**: Administrative attendance record creation
- ✅ **Attendance Records**: Full CRUD operations for attendance data
- ✅ **Monthly Summaries**: Aggregated attendance statistics and reports
- ✅ **Employee Service Integration**: Automatic employee validation
- ✅ **Date Range Filtering**: Query attendance records by date ranges
- ✅ **Async Operations**: Non-blocking HTTP calls using asyncio
- ✅ **Comprehensive Logging**: Detailed operation tracking
- ✅ **RESTful API**: Clean, documented API with Swagger UI
- ✅ **MySQL Integration**: Persistent attendance data storage

## Technology Stack

- **Framework**: FastAPI 0.119.0+
- **Database**: MySQL with SQLModel ORM
- **Async HTTP**: httpx for inter-service communication
- **Authentication**: JWKS/JWT support (Asgardeo)
- **Documentation**: Swagger UI & ReDoc
- **Language**: Python 3.13+

## Quick Start

### Prerequisites

- Python 3.13+
- MySQL 8.0+
- Employee Management Service running on accessible network

### Installation

1. **Clone the repository**
```bash
cd attendance-management-service
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -e .
# Or using uv (if available)
uv sync
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

5. **Update `.env` file with your settings**
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=hrms_db

# Employee Service
EMPLOYEE_SERVICE_URL=http://localhost:8000

# Application
DEBUG=False
APP_NAME=Attendance Management Service
```

6. **Run the service**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

7. **Access the API**
- API Documentation: http://localhost:8001/docs
- ReDoc Documentation: http://localhost:8001/redoc
- Health Check: http://localhost:8001/health

## API Endpoints

### Health Check
```
GET /health
GET /
```

### Attendance Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/attendance/check-in` | Employee check-in |
| `POST` | `/api/v1/attendance/check-out` | Employee check-out |
| `POST` | `/api/v1/attendance/manual` | Manual attendance entry |
| `GET` | `/api/v1/attendance/{attendance_id}` | Get specific record |
| `GET` | `/api/v1/attendance/employee/{employee_id}` | Get employee's records |
| `PUT` | `/api/v1/attendance/{attendance_id}` | Update attendance record |
| `GET` | `/api/v1/attendance/summary/{employee_id}/{month}` | Monthly summary |

## Usage Examples

### Check-In
```bash
curl -X POST http://localhost:8001/api/v1/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1}'
```

### Check-Out
```bash
curl -X POST http://localhost:8001/api/v1/attendance/check-out \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1}'
```

### Get Employee Attendance
```bash
curl -X GET "http://localhost:8001/api/v1/attendance/employee/1?offset=0&limit=30&start_date=2024-01-01&end_date=2024-01-31"
```

### Get Monthly Summary
```bash
curl -X GET http://localhost:8001/api/v1/attendance/summary/1/2024-01
```

### Manual Entry
```bash
curl -X POST http://localhost:8001/api/v1/attendance/manual \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "date": "2024-01-15",
    "check_in_time": "2024-01-15T09:00:00",
    "check_out_time": "2024-01-15T17:30:00",
    "status": "present",
    "notes": "Manual entry"
  }'
```

## Project Structure

```
attendance-management-service/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py          # Shared dependencies (SessionDep)
│   │   ├── clients/                 # External service clients
│   │   │   ├── __init__.py
│   │   │   └── employee_service.py  # Employee Service client
│   │   └── routes/
│   │       ├── attendance.py        # All attendance endpoints
│   │       ├── employees.py         # Employee endpoints
│   │       └── auth.py              # Authentication endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Settings management
│   │   ├── database.py              # MySQL connection & tables
│   │   ├── logging.py               # Logging configuration
│   │   └── security.py              # JWT/JWKS validation
│   └── models/
│       ├── __init__.py
│       ├── attendance.py            # Attendance model & schemas
│       └── employee.py              # Employee model & schemas
├── .env.example
├── .gitignore
├── pyproject.toml              # Project dependencies
├── uv.lock                     # Dependency lock file
├── README.md                   # This file
├── INTEGRATION_GUIDE.md        # Employee Service integration documentation
└── Dockerfile                  # Docker image definition
```

## Database Schema

### Attendance Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT PRIMARY KEY | Unique record identifier |
| `employee_id` | INT NOT NULL | Reference to employee |
| `date` | VARCHAR(10) NOT NULL | Date in YYYY-MM-DD format |
| `check_in_time` | DATETIME | Check-in timestamp |
| `check_out_time` | DATETIME | Check-out timestamp |
| `status` | VARCHAR(50) | Status: pending, present, absent, late |
| `notes` | VARCHAR(500) | Additional notes |
| `created_at` | DATETIME | Record creation time |
| `updated_at` | DATETIME | Last update time |

**Indexes**:
- `idx_employee_id` on `employee_id`
- `idx_date` on `date`
- Combined index on `(employee_id, date)`

## Configuration

### Environment Variables

```env
# Application
APP_NAME=Attendance Management Service
APP_VERSION=1.0.0
DEBUG=False

# Database
DB_NAME=hrms_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_CHARSET=utf8

# Employee Service Integration
EMPLOYEE_SERVICE_URL=http://localhost:8000

# CORS
CORS_ORIGINS=https://localhost,http://localhost:3000
CORS_ALLOW_CREDENTIALS=True

# JWT/JWKS
JWKS_URL=https://api.asgardeo.io/t/pookieland/oauth2/jwks
JWT_AUDIENCE=null
JWT_ISSUER=null
```

## Integration with Employee Service

The Attendance Service requires a running Employee Management Service for:

1. **Employee Validation**: Verifying employee exists before recording attendance
2. **Data Consistency**: Ensuring referenced employees are valid
3. **Enriched Reporting**: Accessing employee details for attendance reports

### Employee Service Endpoints Required

```
GET /api/v1/employees/{employee_id}     - Verify/retrieve employee
GET /api/v1/employees/                  - List all employees
```

For detailed integration instructions, see [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

## Docker Deployment

### Build Image
```bash
docker build -t attendance-management:latest .
```

### Run Container
```bash
docker run -d \
  --name attendance-service \
  -p 8001:8000 \
  -e EMPLOYEE_SERVICE_URL=http://employee-service:8000 \
  -e DB_HOST=mysql \
  -e DB_USER=root \
  -e DB_PASSWORD=root \
  attendance-management:latest
```

### Docker Compose

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md#docker-setup) for complete Docker Compose configuration.

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black app/
flake8 app/
```

### Type Checking
```bash
mypy app/
```

### Dependency Management

Using `uv` (recommended):
```bash
uv sync                    # Install dependencies
uv add package-name        # Add new dependency
uv remove package-name     # Remove dependency
```

Or using pip:
```bash
pip install -e .
pip install package-name
```

## Performance Optimization

### Database Indexing
Ensure proper indexes are created:
```sql
CREATE INDEX idx_employee_date ON attendance(employee_id, date);
CREATE INDEX idx_date ON attendance(date);
```

### Connection Pooling
The service uses connection pooling for database and HTTP client:
- Database: `pool_pre_ping=True`, `pool_recycle=3600`
- HTTP: AsyncClient connection pooling via httpx

### Async Operations
All external service calls are asynchronous, enabling high concurrency without blocking.

## Troubleshooting

### Employee Service Connection Issues
1. Verify Employee Service is running: `curl http://localhost:8000/health`
2. Check network connectivity between services
3. Verify `EMPLOYEE_SERVICE_URL` in `.env` is correct
4. Review logs for detailed error messages

### Database Connection Issues
1. Verify MySQL is running and accessible
2. Check database credentials in `.env`
3. Ensure database user has necessary privileges
4. Run: `mysql -h localhost -u root -p -e "SELECT 1;"`

### No Attendance Records Created
1. Verify employee exists in Employee Service
2. Check attendance table indexes are created
3. Review application logs for validation errors
4. Manually test employee verification: `curl http://employee-service:8000/api/v1/employees/1`

### CORS Errors
1. Verify frontend URL is in `CORS_ORIGINS` in `.env`
2. Check CORS middleware is enabled in `app/main.py`
3. Ensure credentials are handled properly in client requests

## Logging

The service includes comprehensive logging:

```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

Logs include:
- Employee verification attempts
- Attendance record operations
- Employee Service communication
- Database queries (debug mode)
- Request/response details

## Security

### Authentication
- JWT/JWKS support via Asgardeo
- Bearer token validation
- Optional audience and issuer validation

### Input Validation
- Employee IDs must be positive integers
- Dates must be in ISO format (YYYY-MM-DD)
- Status values restricted to predefined set
- All strings have length limits

### CORS
Configurable CORS settings to restrict cross-origin requests

## Monitoring

### Health Checks
```bash
# Basic health check
curl http://localhost:8001/health

# With curl for more details
curl -i http://localhost:8001/health
```

### Metrics to Monitor
- Average response time for attendance operations
- Employee Service API call success rate
- Database query performance
- Error rates and types

## Contributing

When contributing to this service:

1. Follow PEP 8 style guidelines
2. Add docstrings to functions and classes
3. Include type hints
4. Write tests for new features
5. Update documentation accordingly

## License

This project is part of the HRMS system.

## Support

For integration issues with Employee Service, see [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

For API documentation, visit: `http://localhost:8001/docs`

## Changelog

### v1.0.0
- Initial release
- Check-in/check-out functionality
- Manual attendance entry
- Monthly attendance summaries
- Employee Service integration
- Full API documentation