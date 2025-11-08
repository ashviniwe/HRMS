# Leave Management Service

A microservice for managing employee leave requests in the HR Management System. This service provides REST APIs for creating, updating, and managing employee leave requests with integration capabilities for employee service validation.

## Features

- **Complete Leave Management** - Create, retrieve, update, and cancel leave requests
- **Leave Status Workflow** - PENDING → APPROVED/REJECTED/CANCELLED status management
- **Employee Validation** - Validates employees through employee service integration
- **Pagination & Filtering** - List endpoints support offset/limit pagination and status filtering
- **Comprehensive Validation** - Date range validation, status transition validation, and required field validation
- **Audit Trail** - Timestamps and approval tracking for compliance
- **Fallback Strategy** - Works with local database when employee service is unavailable
- **Production Ready** - Structured logging, error handling, and database migrations

## Technology Stack

- **Framework**: FastAPI 0.119.0+
- **ORM**: SQLModel 0.0.27
- **Database**: MySQL
- **HTTP Client**: httpx (for service-to-service calls)
- **Data Validation**: Pydantic v2
- **Python**: 3.13+

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/leaves` | Create new leave request |
| GET | `/api/v1/leaves` | List all leaves (with filtering and pagination) |
| GET | `/api/v1/leaves/{leave_id}` | Get specific leave by ID |
| GET | `/api/v1/leaves/employee/{employee_id}` | Get all leaves for an employee |
| PUT | `/api/v1/leaves/{leave_id}` | Update leave status (approve/reject) |
| DELETE | `/api/v1/leaves/{leave_id}` | Cancel leave request |
| GET | `/health` | Health check endpoint |

## Installation

### Prerequisites

- Python 3.13+
- MySQL 5.7+
- pip or uv (recommended)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd leave-management-service
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

3. Configure environment variables by creating `.env`:
```bash
cp .env.example .env
```

4. Update `.env` with your settings:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=hrms_db
DEBUG=False

# Optional: Employee Service Integration
EMPLOYEE_SERVICE_URL=http://localhost:8001
EMPLOYEE_SERVICE_TIMEOUT=5
```

5. Start the service:
```bash
uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

## Quick Start

### View API Documentation

Interactive API documentation (Swagger UI):
```
http://localhost:8000/docs
```

ReDoc documentation:
```
http://localhost:8000/redoc
```

### Example: Create a Leave Request

```bash
curl -X POST http://localhost:8000/api/v1/leaves \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "leave_type": "annual",
    "start_date": "2024-02-01T00:00:00",
    "end_date": "2024-02-05T00:00:00",
    "reason": "Vacation"
  }'
```

### Example: List All Leaves

```bash
curl http://localhost:8000/api/v1/leaves
```

### Example: Approve a Leave

```bash
curl -X PUT http://localhost:8000/api/v1/leaves/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_by": 2
  }'
```

### Example: Health Check

```bash
curl http://localhost:8000/health
```

## Leave Status Workflow

```
PENDING (Initial state)
├── Approve → APPROVED (requires approved_by manager ID)
├── Reject → REJECTED (requires rejection_reason)
└── Cancel → CANCELLED

APPROVED
└── Cancel → CANCELLED

REJECTED (Terminal state - no transitions)
CANCELLED (Terminal state - no transitions)
```

## Leave Types

- `annual` - Annual/vacation leave
- `sick` - Sick leave
- `casual` - Casual leave
- `maternity` - Maternity leave
- `paternity` - Paternity leave
- `unpaid` - Unpaid leave

## Employee Service Integration

The Leave Management Service integrates with an Employee Service to validate employee existence before processing leave requests.

### Configuration

Add to `.env`:
```env
EMPLOYEE_SERVICE_URL=http://employee-service:8001
```

If not set, the service uses local database for validation.

### Employee Service Requirements

Your Employee Service should expose:

**Endpoint**: `GET /api/v1/employees/{employee_id}`

**Success Response (200)**:
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 30
}
```

**Not Found Response (404)**:
```json
{
  "detail": "Employee not found"
}
```

### Integration Strategy

1. Check cache for employee
2. Call Employee Service API (if configured)
3. Fall back to local database if service unavailable
4. Cache result for performance

For detailed integration guide, see `EMPLOYEE_SERVICE_INTEGRATION.md`

## Database Schema

### Leave Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| employee_id | INT | Foreign key to Employee |
| leave_type | ENUM | Type of leave |
| start_date | DATETIME | Leave start date/time |
| end_date | DATETIME | Leave end date/time |
| reason | VARCHAR(500) | Reason for leave (optional) |
| status | ENUM | Current status |
| approved_by | INT | Manager ID who approved (optional) |
| rejection_reason | VARCHAR(500) | Reason for rejection (optional) |
| created_at | DATETIME | Created timestamp |
| updated_at | DATETIME | Updated timestamp |

## Project Structure

```
leave-management-service/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── leaves.py          # Leave API endpoints
│   │   └── deps.py                # API dependencies
│   ├── core/
│   │   ├── config.py              # Settings and configuration
│   │   ├── database.py            # Database connection
│   │   └── logging.py             # Logging setup
│   ├── models/
│   │   └── leave.py               # Leave database model
│   ├── schemas/
│   │   └── leave.py               # Leave Pydantic schemas
│   ├── services/
│   │   └── employee_service.py    # Employee validation service
│   └── main.py                    # FastAPI application
├── .env                           # Environment variables
├── .env.example                   # Example environment variables
├── pyproject.toml                 # Project dependencies
├── README.md                      # This file
├── IMPLEMENTATION_SUMMARY.md      # Implementation details
├── EMPLOYEE_SERVICE_INTEGRATION.md # Integration guide
└── QUICKSTART.md                  # Quick start guide
```

## Development

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Running in Debug Mode

```bash
uvicorn app.main:app --reload --log-level debug
```

## Error Handling

The service returns appropriate HTTP status codes and error messages:

- `200 OK` - Successful GET request
- `201 Created` - Successful resource creation
- `400 Bad Request` - Invalid input or state transition
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Example Error Response

```json
{
  "detail": "start_date must be before end_date"
}
```

## Logging

All operations are logged with appropriate context:

- Application startup/shutdown
- Leave operations (create, update, delete)
- Employee verification results
- Errors and warnings

View logs in console when running with `--log-level debug`

## Documentation

- **IMPLEMENTATION_SUMMARY.md** - What was implemented and design decisions
- **EMPLOYEE_SERVICE_INTEGRATION.md** - How to integrate with Employee Service
- **QUICKSTART.md** - Quick start guide with examples
- **API Documentation** - Visit `/docs` endpoint for interactive Swagger UI

## Performance Considerations

- Leave listing supports pagination to handle large datasets
- Employee verification results are cached to reduce repeated lookups
- Database queries are optimized with proper indexing
- Configurable timeout for employee service calls

## Security Considerations

- Input validation on all endpoints
- Status transitions are validated to prevent invalid states
- Soft deletes preserve audit trail
- All operations are logged for compliance

## Future Enhancements

- [ ] Authentication and authorization
- [ ] Leave quota management
- [ ] Conflict detection (overlapping leaves)
- [ ] Email notifications
- [ ] Analytics endpoints
- [ ] Approval workflows
- [ ] Cache TTL implementation
- [ ] Prometheus metrics

## Troubleshooting

### "Employee not found" for existing employee

1. Verify Employee Service is running (if configured)
2. Check employee exists in local Employee table
3. Verify EMPLOYEE_SERVICE_URL is correct in `.env`
4. Check application logs for detailed error messages

### Database connection failed

1. Verify MySQL is running
2. Check database credentials in `.env`
3. Ensure database exists or will be created

### Port already in use

```bash
uvicorn app.main:app --reload --port 8001
```

## Support

For issues or questions, please refer to the documentation or check application logs for detailed error messages.

## License

This project is part of the HR Management System.