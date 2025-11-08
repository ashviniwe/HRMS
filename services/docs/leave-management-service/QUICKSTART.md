# Leave Management Service - Quick Start Guide

## Overview

The Leave Management Service provides REST APIs for managing employee leave requests with employee service integration.

## 7 API Endpoints

```
POST   /api/v1/leaves                          - Create leave
GET    /api/v1/leaves/{leave_id}               - Get specific leave
GET    /api/v1/leaves/employee/{employee_id}   - Get employee's leaves
GET    /api/v1/leaves                          - List all leaves
PUT    /api/v1/leaves/{leave_id}               - Update leave status
DELETE /api/v1/leaves/{leave_id}               - Cancel leave
GET    /health                                 - Health check
```

## Setup

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure Database
Update `.env` file:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=hrms_db
```

### 3. (Optional) Configure Employee Service Integration
Add to `.env`:
```env
EMPLOYEE_SERVICE_URL=http://localhost:8001
```

Without this, the service uses local database for employee verification.

### 4. Start Application
```bash
uvicorn app.main:app --reload
```

Access API documentation: `http://localhost:8000/docs`

## Quick Usage Examples

### Create Leave Request
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

Response (201):
```json
{
  "id": 1,
  "employee_id": 1,
  "leave_type": "annual",
  "start_date": "2024-02-01T00:00:00",
  "end_date": "2024-02-05T00:00:00",
  "reason": "Vacation",
  "status": "pending",
  "approved_by": null,
  "rejection_reason": null,
  "created_at": "2024-10-30T01:00:00",
  "updated_at": "2024-10-30T01:00:00"
}
```

### List All Leaves
```bash
curl http://localhost:8000/api/v1/leaves
```

With pagination and filtering:
```bash
curl "http://localhost:8000/api/v1/leaves?status=pending&offset=0&limit=10"
```

### Get Employee's Leaves
```bash
curl http://localhost:8000/api/v1/leaves/employee/1
```

### Approve Leave
```bash
curl -X PUT http://localhost:8000/api/v1/leaves/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_by": 2
  }'
```

### Reject Leave
```bash
curl -X PUT http://localhost:8000/api/v1/leaves/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "rejection_reason": "Resource conflict"
  }'
```

### Cancel Leave
```bash
curl -X DELETE http://localhost:8000/api/v1/leaves/1
```

### Get Specific Leave
```bash
curl http://localhost:8000/api/v1/leaves/1
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Leave Status Workflow

```
PENDING
├── Approve → APPROVED (requires approved_by)
├── Reject → REJECTED (requires rejection_reason)
└── Cancel → CANCELLED

APPROVED
└── Cancel → CANCELLED

REJECTED → [Terminal state]
CANCELLED → [Terminal state]
```

## Leave Types

- `annual` - Annual/vacation leave
- `sick` - Sick leave
- `casual` - Casual leave
- `maternity` - Maternity leave
- `paternity` - Paternity leave
- `unpaid` - Unpaid leave

## Error Responses

### Employee Not Found (404)
```json
{"detail": "Employee not found"}
```

### Invalid Date Range (400)
```json
{"detail": "start_date must be before end_date"}
```

### Leave Not Found (404)
```json
{"detail": "Leave not found"}
```

### Invalid Status Transition (400)
```json
{"detail": "Cannot change status from rejected to approved"}
```

### Missing Required Field (400)
```json
{"detail": "approved_by is required when approving a leave"}
```

## Database Schema

### Leave Table
- `id` - Primary key
- `employee_id` - Foreign key to Employee
- `leave_type` - Type of leave (enum)
- `start_date` - Leave start date/time
- `end_date` - Leave end date/time
- `reason` - Reason for leave (optional)
- `status` - Current status (enum)
- `approved_by` - Manager ID who approved (optional)
- `rejection_reason` - Reason for rejection (optional)
- `created_at` - Created timestamp
- `updated_at` - Updated timestamp

## Integration with Employee Service

### Why Two Systems?

The service integrates with Employee Service to validate employees. This ensures:
- Leave requests are for valid employees
- Data consistency across services
- Ability to enrich leave data with employee info

### How It Works

When creating a leave or querying employee leaves:
1. Service checks cache for employee
2. If configured, calls Employee Service API
3. Falls back to local database if service unavailable
4. Caches result for performance

### Employee Service Requirements

Your Employee Service should expose:
```
GET /api/v1/employees/{employee_id}

Response (200):
{
  "id": 1,
  "name": "John Doe",
  "age": 30
}

Response (404):
Employee not found
```

## Documentation

- **IMPLEMENTATION_SUMMARY.md** - What was built and why
- **EMPLOYEE_SERVICE_INTEGRATION.md** - How to integrate with Employee Service
- **API Documentation** - Visit `/docs` for interactive Swagger UI

## Common Tasks

### Test with Mock Data

1. Create employees via existing employee endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "age": 30}'
```

2. Create leaves for those employees:
```bash
curl -X POST http://localhost:8000/api/v1/leaves \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "leave_type": "sick",
    "start_date": "2024-02-01T00:00:00",
    "end_date": "2024-02-02T00:00:00"
  }'
```

### Test Employee Service Integration

1. Set `EMPLOYEE_SERVICE_URL` in `.env`
2. Ensure Employee Service is running
3. Try creating leave - should verify employee via API

### Debug Issues

Check application logs for detailed error messages:
- "Employee {id} verified" - successful verification
- "Employee {id} not found" - employee doesn't exist
- "Failed to connect to Employee Service" - service unavailable
- Falls back to local database

## Troubleshooting

### "Employee not found" for existing employee
- Check Employee Service is running (if configured)
- Verify employee exists in local Employee table
- Check EMPLOYEE_SERVICE_URL is correct

### Port already in use
```bash
uvicorn app.main:app --reload --port 8001
```

### Database connection failed
- Verify MySQL is running
- Check DB credentials in `.env`
- Ensure database exists: `CREATE DATABASE IF NOT EXISTS hrms_db;`

## Next Steps

1. Read **IMPLEMENTATION_SUMMARY.md** for architecture details
2. Read **EMPLOYEE_SERVICE_INTEGRATION.md** for integration guide
3. Explore `/docs` for full API documentation
4. Test all endpoints with provided examples