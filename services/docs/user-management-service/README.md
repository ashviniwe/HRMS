# User Management Service

A lightweight, production-ready FastAPI microservice for managing users, authentication, and authorization.

## Features

- **User Management**: Create, read, update, and delete user records
- **JWT Authentication**: Secure token-based authentication with JWKS support
- **Role-Based Access Control (RBAC)**: Fine-grained permission management
- **MySQL Database**: Persistent data storage with SQLModel ORM
- **CORS Middleware**: Pre-configured for cross-origin requests
- **Structured Logging**: Consistent logging across the application
- **Health Checks**: Built-in endpoints for monitoring service status

## Quick Start

### Prerequisites

- Python 3.13+
- MySQL 8.0+
- UV package manager (or pip)

### Installation

1. Clone the repository and install dependencies:

```bash
uv sync
```

2. Configure your environment:

```bash
cp .env.example .env.development
```

3. Update `.env.development` with your database and JWT settings:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=user_management_db
JWKS_URL=https://your-auth-provider.com/.well-known/jwks.json
```

4. Run the application:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Health Endpoints

- `GET /` - Simple health check
- `GET /health` - Detailed health check with database info

### User Endpoints

- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - List users (with pagination)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PATCH /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Authentication Endpoints

- `GET /api/v1/auth/verify` - Verify JWT token
- `GET /api/v1/auth/whoami` - Get current user info
- `GET /api/v1/auth/debug` - Debug token contents (detailed claims)
- `GET /api/v1/auth/roles` - List current user roles
- `GET /api/v1/auth/permissions` - List current user permissions

### Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
app/
├── main.py              # Application entry point
├── api/
│   ├── auth.py          # Authentication routes
│   ├── users.py         # User CRUD routes
│   └── dependencies.py   # Shared dependencies
├── core/
│   ├── config.py        # Configuration and settings
│   ├── database.py      # Database engine and sessions
│   ├── logging.py       # Logging setup
│   └── security.py      # JWT and security utilities
└── models/
    └── users.py         # User data models
```

## Configuration

Settings are managed through `app/core/config.py` and loaded from environment variables.

### Key Settings

- `APP_NAME` - Service name (default: "User Management Service")
- `DEBUG` - Enable debug mode (default: False)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database connection
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `JWKS_URL` - JWKS endpoint for JWT validation
- `JWT_AUDIENCE` - Expected JWT audience (optional)
- `JWT_ISSUER` - Expected JWT issuer (optional)

## Authentication

This service uses JWT tokens with JWKS validation. Include your token in requests:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/auth/whoami
```

### Role-Based Access

Protect endpoints with required roles:

```python
from fastapi import Depends
from app.core.security import require_role

@app.get("/admin-only")
async def admin_endpoint(
    user: Annotated[TokenData, Depends(require_role("admin"))]
):
    return {"message": "Admin access granted"}
```

## Development

### Run Tests

```bash
uv run pytest
```

### Format Code

```bash
uv run ruff format .
uv run ruff check . --fix
```

### Docker

Build and run with Docker:

```bash
docker build -t user-management-service .
docker run -p 8000:8000 --env-file .env.development user-management-service
```

## Dependencies

- **fastapi[all]** - Web framework
- **sqlmodel** - ORM and data validation
- **mysqlclient** - MySQL database driver
- **pydantic-settings** - Configuration management
- **python-jose** - JWT token handling
- **pyjwt** - JWT validation
- **cryptography** - Cryptographic operations

## License

Proprietary - HR Management System