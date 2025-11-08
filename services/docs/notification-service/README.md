# Notification Service

A robust, scalable FastAPI-based notification service for the HRMS (Human Resource Management System). This service handles email notifications with support for retry logic, status tracking, and comprehensive notification management.

## Features

- **Email Notifications**: Send emails asynchronously using SMTP
- **Notification Tracking**: Track notification status (pending, sent, failed, retrying)
- **Retry Logic**: Automatic retry mechanism for failed notifications
- **Background Processing**: Async task processing for non-blocking email sends
- **Pagination**: List notifications with offset/limit pagination
- **Employee Notifications**: Track notifications per employee
- **Status Filtering**: Filter notifications by status
- **Database Persistence**: All notifications stored in MySQL for audit trail

## Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **SQLModel**: SQL database ORM combining SQLAlchemy and Pydantic
- **aiosmtplib**: Async SMTP client for email sending
- **MySQL**: Relational database for notification storage
- **Pydantic**: Data validation using Python type annotations

## Project Structure

```
notification-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependency injection
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── notifications.py # Notification endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database setup and session management
│   │   ├── logging.py         # Logging configuration
│   │   └── security.py        # Security utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── notification.py    # Notification model and schemas
│   └── services/
│       ├── __init__.py
│       └── email.py           # Email sending service
├── pyproject.toml             # Project metadata and dependencies
├── .env.example               # Environment variables template
├── .gitignore
└── README.md                  # This file
```

## API Endpoints

### Send Notification
```
POST /api/v1/notifications/send
```
Create and send a new notification.

**Request Body:**
```json
{
  "employee_id": 1,
  "recipient_email": "john@example.com",
  "recipient_name": "John Doe",
  "subject": "Welcome to HRMS",
  "body": "Your account has been created successfully",
  "channel": "email"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "employee_id": 1,
  "recipient_email": "john@example.com",
  "recipient_name": "John Doe",
  "subject": "Welcome to HRMS",
  "body": "Your account has been created successfully",
  "channel": "email",
  "status": "pending",
  "retry_count": 0,
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "sent_at": null
}
```

### Get Notification Status
```
GET /api/v1/notifications/{notification_id}
```
Retrieve a specific notification's status and details.

**Response (200 OK):**
```json
{
  "id": 1,
  "employee_id": 1,
  "recipient_email": "john@example.com",
  "recipient_name": "John Doe",
  "subject": "Welcome to HRMS",
  "body": "Your account has been created successfully",
  "channel": "email",
  "status": "sent",
  "retry_count": 0,
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:05",
  "sent_at": "2024-01-15T10:30:05"
}
```

### Get Employee Notifications
```
GET /api/v1/notifications/employee/{employee_id}
```
List all notifications for a specific employee with pagination.

**Query Parameters:**
- `offset` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100, max: 100): Maximum records to return

**Response (200 OK):**
```json
{
  "total": 5,
  "offset": 0,
  "limit": 100,
  "items": [
    {
      "id": 1,
      "employee_id": 1,
      "recipient_email": "john@example.com",
      "recipient_name": "John Doe",
      "subject": "Welcome to HRMS",
      "body": "Your account has been created successfully",
      "channel": "email",
      "status": "sent",
      "retry_count": 0,
      "error_message": null,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:05",
      "sent_at": "2024-01-15T10:30:05"
    }
  ]
}
```

### List All Notifications
```
GET /api/v1/notifications
```
List all notifications across all employees with optional filtering.

**Query Parameters:**
- `offset` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100, max: 100): Maximum records to return
- `status` (string, optional): Filter by status (pending, sent, failed, retrying)

**Response (200 OK):**
```json
{
  "total": 25,
  "offset": 0,
  "limit": 100,
  "items": [...]
}
```

### Retry Failed Notification
```
PUT /api/v1/notifications/{notification_id}/retry
```
Retry sending a failed or retrying notification.

**Response (200 OK):**
```json
{
  "id": 1,
  "employee_id": 1,
  "recipient_email": "john@example.com",
  "recipient_name": "John Doe",
  "subject": "Welcome to HRMS",
  "body": "Your account has been created successfully",
  "channel": "email",
  "status": "retrying",
  "retry_count": 1,
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00",
  "sent_at": null
}
```

### Health Check
```
GET /health
```
Detailed health check endpoint.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Notification Service",
  "version": "1.0.0",
  "database": "hrms_db",
  "features": ["email_notifications", "notification_tracking", "retry_logic"]
}
```

## Setup and Installation

### Prerequisites

- Python 3.13+
- MySQL 8.0+
- pip or uv package manager

### 1. Clone the Repository

```bash
cd notification-service
```

### 2. Create Environment File

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application Settings
APP_NAME=Notification Service
APP_VERSION=1.0.0
DEBUG=False

# Database Settings
DB_NAME=hrms_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_CHARSET=utf8

# Email Settings (SMTP Configuration)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@hrms.com
SMTP_FROM_NAME=HRMS Notification Service
SMTP_TLS=True

# CORS Settings
CORS_ORIGINS=https://localhost,http://localhost:3000
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# Notification Settings
MAX_RETRIES=3
RETRY_DELAY_SECONDS=300
```

### 3. Install Dependencies

Using `uv` (recommended):

```bash
uv sync
```

Or using `pip`:

```bash
pip install -e .
```

### 4. Run the Application

Using `uv`:

```bash
uv run fastapi dev app/main.py
```

Or using Python:

```bash
python -m fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`

Access the interactive API documentation at `http://localhost:8000/docs`

## Configuration

### Email Configuration

The service uses SMTP for sending emails. Ensure you have:

1. **Gmail**: Enable "Less secure app access" or use an app-specific password
2. **Other Providers**: Configure appropriate SMTP credentials

### Database Configuration

Update `.env` with your MySQL credentials. The service will automatically create the database and tables on startup.

## Notification Status

- **PENDING**: Notification created, awaiting sending
- **RETRYING**: Notification send failed, will retry
- **SENT**: Notification successfully delivered
- **FAILED**: Notification failed after max retries

## Error Handling

The service includes comprehensive error handling:

- Invalid email addresses are rejected at the model validation level
- SMTP connection failures are logged and retried
- Failed notifications are marked with error messages for debugging
- 404 errors for non-existent notifications
- 400 errors for invalid operations (e.g., retry on sent notification)

## Logging

Logs are output to stdout with timestamps and log levels. Debug mode can be enabled by setting `DEBUG=True` in `.env`.

Log levels:
- `INFO`: General information about operations
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations

## Background Tasks

The service uses FastAPI's background tasks for async email sending:

- Email sending doesn't block the HTTP response
- Notifications are created and returned immediately
- Emails are sent asynchronously in the background
- Status updates are reflected in the database

## Database Schema

### Notifications Table

```sql
CREATE TABLE notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  employee_id INT NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,
  recipient_name VARCHAR(255) NOT NULL,
  subject VARCHAR(500) NOT NULL,
  body LONGTEXT NOT NULL,
  channel VARCHAR(50) DEFAULT 'email',
  status VARCHAR(50) DEFAULT 'pending',
  retry_count INT DEFAULT 0,
  error_message LONGTEXT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  sent_at DATETIME NULL,
  INDEX idx_employee_id (employee_id),
  INDEX idx_recipient_email (recipient_email),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
);
```

## Development

### Run Tests

```bash
pytest
```

### Code Style

The codebase follows PEP 8 guidelines with type hints for all functions.

## Docker Support

To run in Docker, create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY app ./app

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0"]
```

Build and run:

```bash
docker build -t notification-service .
docker run -p 8000:8000 --env-file .env notification-service
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Ensure code follows the project style
4. Submit a pull request

## License

This project is part of the HRMS system.

## Support

For issues or questions, please contact the development team or check the HRMS documentation.

## Roadmap

- [ ] SMS notification support
- [ ] Push notification support
- [ ] Notification templates
- [ ] Batch email sending
- [ ] Webhook support for external integrations
- [ ] Advanced scheduling
- [ ] Email attachment support
- [ ] Notification preferences per employee