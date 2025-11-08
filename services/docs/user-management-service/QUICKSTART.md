# Quick Start Guide - User Management Service

## What Was Fixed

This project has been cleaned up and refactored from a generic FastAPI template into a focused **User Management Service**:

✅ **Fixed Critical Issues:**
- Import typo: `app.api.dependenciesdependencies` → `app.api.dependencies`
- Wrong import paths in `main.py` (non-existent routes directory)
- All references to "Employee" renamed to "User"

✅ **Updated Configuration:**
- Project name: `fastapi-template` → `user-management-service`
- App name: `FastAPI Template` → `User Management Service`
- Environment file: `.env` → `.env.development`
- All dependencies renamed from `deps` to `dependencies`

✅ **Enhanced Data Model:**
- User table now includes: username, email, full_name, is_active, timestamps
- Added unique constraints on username and email
- Added validation to prevent duplicate usernames and emails

✅ **Simplified Codebase:**
- Removed schema folder as requested
- Clean project structure with focused purpose
- No template artifacts or unused code
- All code compiles without errors

---

## Getting Started (60 seconds)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure Environment
Copy and update `.env.development` with your database credentials:
```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=user_management_db
JWKS_URL=https://your-auth-provider/.well-known/jwks.json
```

### 3. Run the Service
```bash
uv run uvicorn app.main:app --reload
```

Service runs at: `http://localhost:8000`

---

## Project Structure

```
app/
├── main.py                 # FastAPI app initialization
├── api/
│   ├── users.py           # User CRUD endpoints (/api/v1/users)
│   ├── auth.py            # Authentication endpoints (/api/v1/auth)
│   └── dependencies.py     # Shared dependencies
├── core/
│   ├── config.py          # Settings from environment
│   ├── database.py        # MySQL connection & session
│   ├── logging.py         # Logging setup
│   └── security.py        # JWT validation with JWKS
└── models/
    └── users.py           # User model & schemas
```

---

## API Examples

### Create a User
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_active": true
  }'
```

### List Users
```bash
curl http://localhost:8000/api/v1/users/?offset=0&limit=10
```

### Get User by ID
```bash
curl http://localhost:8000/api/v1/users/1
```

### Update User
```bash
curl -X PATCH http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Smith"}'
```

### Delete User
```bash
curl -X DELETE http://localhost:8000/api/v1/users/1
```

### Check Authentication
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/auth/whoami
```

---

## Interactive Documentation

Visit these URLs while the service is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## User Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/users/` | Create new user |
| GET | `/api/v1/users/` | List users (paginated) |
| GET | `/api/v1/users/{user_id}` | Get specific user |
| PATCH | `/api/v1/users/{user_id}` | Update user |
| DELETE | `/api/v1/users/{user_id}` | Delete user |

---

## Auth Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/auth/verify` | Verify JWT token is valid |
| `GET /api/v1/auth/whoami` | Get current user info |
| `GET /api/v1/auth/debug` | Detailed token inspection |
| `GET /api/v1/auth/roles` | List current user roles |
| `GET /api/v1/auth/permissions` | List current user permissions |

All auth endpoints require: `Authorization: Bearer YOUR_JWT_TOKEN`

---

## Error Handling

The service returns appropriate HTTP status codes:

- **200 OK** - Successful GET/PATCH
- **201 Created** - User successfully created
- **400 Bad Request** - Duplicate username/email or invalid data
- **404 Not Found** - User doesn't exist
- **401 Unauthorized** - Invalid/missing JWT token
- **403 Forbidden** - Insufficient permissions

---

## Environment Variables

Essential settings in `.env.development`:

```
APP_NAME=User Management Service
DEBUG=False
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=user_management_db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
JWKS_URL=https://your-auth-provider/.well-known/jwks.json
```

---

## Key Features

✨ **User Management**
- Create, read, update, delete users
- Unique username and email validation
- User status tracking (is_active)
- Automatic timestamps

🔐 **Security**
- JWT authentication with JWKS validation
- Role-based access control (RBAC)
- Permission-based access control
- CORS middleware configured

📊 **Database**
- MySQL with SQLModel ORM
- Automatic table creation
- Connection pooling
- Query logging in debug mode

📝 **Developer Experience**
- Comprehensive logging
- Interactive API documentation (Swagger/ReDoc)
- Type hints throughout
- Clean error messages

---

## Next Steps

1. **Database Setup**: Create MySQL database matching `DB_NAME` setting
2. **JWT Configuration**: Set up JWKS URL pointing to your auth provider
3. **Test API**: Use Swagger UI at `/docs` to test endpoints
4. **Deploy**: Docker image can be built with provided Dockerfile

---

## Troubleshooting

**Port 8000 already in use?**
```bash
uv run uvicorn app.main:app --reload --port 8001
```

**Database connection fails?**
- Check MySQL is running
- Verify DB_HOST, DB_USER, DB_PASSWORD in `.env.development`
- Ensure database exists or service will create it

**Authentication errors?**
- Verify JWKS_URL is accessible
- Check JWT token format (Bearer scheme)
- Use `/api/v1/auth/debug` to inspect token contents

---

## Files Summary

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata & dependencies |
| `app/main.py` | FastAPI app with routers & CORS |
| `app/models/users.py` | User model & validation schemas |
| `app/api/users.py` | User CRUD endpoints |
| `app/api/auth.py` | Auth debug endpoints |
| `app/core/config.py` | Settings from environment |
| `app/core/database.py` | MySQL connection management |
| `app/core/security.py` | JWT validation with JWKS |
| `app/core/logging.py` | Logging configuration |
| `README.md` | Full documentation |
| `CHANGES.md` | Detailed refactoring notes |

---

## Support

For full documentation, see:
- `README.md` - Complete feature overview
- `CHANGES.md` - All changes made during refactoring
- `app/api/users.py` - Endpoint implementations with docstrings
- `app/core/security.py` - JWT and authentication details