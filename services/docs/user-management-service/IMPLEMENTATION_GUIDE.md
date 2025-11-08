# User Management Service - Implementation Guide

A comprehensive FastAPI microservice for user authentication, authorization, and lifecycle management with **Asgardeo** integration and service orchestration.

## 🎯 Overview

This service implements a complete user management solution that:

- ✅ Integrates with **Asgardeo** (OAuth 2.0 / OIDC) identity provider
- ✅ Manages user signup, login, and profile management
- ✅ Implements role-based access control (RBAC)
- ✅ Orchestrates integration with Employee, Compliance, Notification, and Audit services
- ✅ Provides RESTful API with comprehensive documentation
- ✅ Includes health checks and readiness/liveness probes

---

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Authentication Flow](#authentication-flow)
- [Database Schema](#database-schema)
- [Integration Architecture](#integration-architecture)
- [Deployment](#deployment)
- [Testing](#testing)

---

## 🚀 Installation

### Prerequisites

- Python 3.13+
- MySQL 8.0+
- UV package manager

### Setup

1. **Clone and install dependencies:**

```bash
cd user-management-service
uv sync
```

2. **Configure environment:**

```bash
cp .env.example .env.development
```

3. **Update `.env.development`:**

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=user_management_db

# Asgardeo Configuration
ASGARDEO_DOMAIN=https://api.asgardeo.io/t/your-tenant
ASGARDEO_CLIENT_ID=your_client_id
ASGARDEO_CLIENT_SECRET=your_client_secret
ASGARDEO_BEARER_TOKEN=your_scim_bearer_token
ASGARDEO_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback

# Service URLs
EMPLOYEE_SERVICE_URL=http://employee-service:8001
COMPLIANCE_SERVICE_URL=http://compliance-service:8006
NOTIFICATION_SERVICE_URL=http://notification-service:8004
AUDIT_SERVICE_URL=http://audit-service:8005

# JWT Configuration
JWT_SECRET=your_secret_key_change_this
JWT_EXPIRY_SECONDS=3600

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

4. **Run the service:**

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**

---

## 📚 API Endpoints

### Authentication (`/api/v1/auth`)

#### Sign Up
```
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}

Response: 201 Created
{
  "user_id": 1,
  "email": "user@example.com",
  "asgardeo_id": "uuid-from-asgardeo",
  "status": "created"
}
```

#### OAuth Callback
```
POST /api/v1/auth/callback?code=AUTH_CODE&state=STATE_VALUE

Response: 200 OK
{
  "session_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "email": "user@example.com",
  "role": "employee",
  "employee_id": 1,
  "expires_in": 3600
}
```

#### Get Profile
```
GET /api/v1/auth/users/me
Authorization: Bearer {session_token}

Response: 200 OK
{
  "id": 1,
  "asgardeo_id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "employee",
  "status": "active",
  "employee_id": 1,
  "created_at": "2025-01-24T10:00:00",
  "last_login": "2025-01-24T14:30:00"
}
```

#### Update Profile
```
PUT /api/v1/auth/users/me
Authorization: Bearer {session_token}
Content-Type: application/json

{
  "first_name": "Jane",
  "phone": "+9876543210"
}
```

#### Change Password
```
PUT /api/v1/auth/users/me/change-password
Authorization: Bearer {session_token}
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

#### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer {session_token}

Response: 200 OK
{
  "message": "logged out successfully"
}
```

#### Verify Token
```
GET /api/v1/auth/verify
Authorization: Bearer {session_token}

Response: 200 OK
{
  "valid": true,
  "user_id": "1",
  "message": "Token is valid"
}
```

#### Get Current User Info
```
GET /api/v1/auth/whoami
Authorization: Bearer {session_token}

Response: 200 OK
{
  "user_id": "1",
  "email": "user@example.com",
  "role": "employee",
  "employee_id": 1
}
```

---

### User Management (`/api/v1/users`)

#### List Users (Admin Only)
```
GET /api/v1/users?role=manager&status=active&limit=50&offset=0
Authorization: Bearer {admin_token}

Response: 200 OK
{
  "total": 150,
  "users": [...]
}
```

#### Get User
```
GET /api/v1/users/{user_id}
Authorization: Bearer {token}

Response: 200 OK
{ user details }
```

#### Update User Role (Admin Only)
```
POST /api/v1/users/{user_id}/role
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "role": "manager"
}
```

#### Suspend User (Admin Only)
```
PUT /api/v1/users/{user_id}/suspend
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "reason": "Conduct violation"
}
```

#### Activate User (Admin Only)
```
PUT /api/v1/users/{user_id}/activate
Authorization: Bearer {admin_token}
```

#### Delete User (Admin Only)
```
DELETE /api/v1/users/{user_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "reason": "Left company"
}
```

#### Get User Permissions
```
GET /api/v1/users/{user_id}/permissions
Authorization: Bearer {token}

Response: 200 OK
{
  "user_id": 1,
  "role": "hr_manager",
  "permissions": [
    "users:read",
    "employees:manage",
    "leaves:approve",
    ...
  ]
}
```

#### List Available Roles
```
GET /api/v1/users/permissions/roles
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "role_id": 1,
    "role_name": "admin",
    "description": "System administrator"
  },
  ...
]
```

---

### Health Checks

```
GET /health
GET /health/ready          # Kubernetes readiness probe
GET /health/live           # Kubernetes liveness probe
```

---

## 🔐 Authentication Flow

### Signup Flow

```
1. Frontend → POST /auth/signup
   ├─ Validate email & password
   ├─ Create user in Asgardeo (SCIM API)
   ├─ Create user in local database
   ├─ Create employee record
   ├─ Log audit event
   └─ Send welcome email

2. Frontend redirects to Asgardeo login
```

### Login Flow (OAuth)

```
1. Frontend → Redirect to Asgardeo login
   
2. Asgardeo → Redirect to /auth/callback
   
3. Backend:
   ├─ Exchange code for tokens (OAuth)
   ├─ Decode ID token
   ├─ Look up user
   ├─ Create session token (JWT)
   ├─ Update last login
   └─ Log audit event
   
4. Frontend stores session token
```

### Authorization

- **Session Token**: JWT token created by this service
- **Token Claims**:
  - `sub`: User ID
  - `user_id`: User ID (duplicate)
  - `email`: User email
  - `asgardeo_id`: ID from Asgardeo
  - `role`: User role
  - `employee_id`: Employee ID
  - `exp`: Expiration time
  - `iat`: Issued at

---

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  
  -- Asgardeo sync
  asgardeo_id VARCHAR(255) UNIQUE NOT NULL,
  
  -- Identity
  email VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  phone VARCHAR(20),
  
  -- Role & Status
  role ENUM('admin', 'hr_manager', 'manager', 'employee') DEFAULT 'employee',
  status ENUM('active', 'suspended', 'deleted') DEFAULT 'active',
  
  -- Service Links
  employee_id INT,
  
  -- Timestamps
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_login DATETIME,
  deleted_at DATETIME,
  
  INDEX idx_email (email),
  INDEX idx_asgardeo_id (asgardeo_id),
  INDEX idx_status (status),
  INDEX idx_role (role)
);
```

### Roles

- **admin**: Full system access
- **hr_manager**: Employee management, leave approval
- **manager**: Team management, leave approval
- **employee**: Basic access

---

## 🔗 Integration Architecture

### Service Integration Pattern

```
User Management Service
│
├─→ Asgardeo (OAuth 2.0 / SCIM)
│   └─ User creation, updates, authentication
│
├─→ Employee Service
│   └─ Create/update/terminate employee records
│
├─→ Audit Service
│   └─ Log all user operations
│
├─→ Compliance Service
│   └─ Validate deletion policies
│
└─→ Notification Service
    └─ Send emails (async, fire-and-forget)
```

### Signup Integration Flow

```
Frontend Signup
    ↓
User Service (Create user in Asgardeo & local DB)
    ├─→ Employee Service (Create employee)
    ├─→ Audit Service (Log signup)
    └─→ Notification Service (Send welcome email)
```

### User Deletion Integration Flow

```
Admin DELETE /users/{id}
    ↓
Compliance Service (Check deletion policy)
    ↓
User Service (Set status=deleted, disable in Asgardeo)
    ├─→ Employee Service (Terminate employee)
    ├─→ Audit Service (Log deletion)
    └─→ Notification Service (Send deletion email)
```

---

## 🐳 Deployment

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
services:
  user-service:
    build: ./user-management-service
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql
      - ASGARDEO_DOMAIN=https://api.asgardeo.io/t/your-tenant
      - EMPLOYEE_SERVICE_URL=http://employee-service:8001
    depends_on:
      - mysql
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-management-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: user-service
        image: user-management-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: user-service-config
              key: db-host
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## 🧪 Testing

### Manual Testing with cURL

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890"
  }'

# Get current user
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/users/me

# List users (admin)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/users?role=employee&limit=10
```

### Integration Tests

See `/tests` directory for comprehensive test suite covering:
- Signup and login flows
- Profile management
- Role-based access control
- Service integrations
- Error handling

---

## 📖 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🔧 Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | False | Debug mode |
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 3306 | Database port |
| `DB_NAME` | user_management_db | Database name |
| `ASGARDEO_DOMAIN` | https://api.asgardeo.io | Asgardeo domain |
| `JWT_SECRET` | your-secret | JWT signing secret |
| `JWT_EXPIRY_SECONDS` | 3600 | Token expiry |
| `MIN_PASSWORD_LENGTH` | 8 | Min password length |
| `REQUIRE_UPPERCASE` | True | Uppercase required |
| `REQUIRE_NUMBERS` | True | Numbers required |
| `REQUIRE_SPECIAL_CHARS` | True | Special chars required |

---

## 📝 Project Structure

```
user-management-service/
├── app/
│   ├── api/
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── users.py                # User management endpoints
│   │   └── dependencies.py         # Shared dependencies
│   ├── core/
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # Database setup
│   │   ├── logging.py              # Logging config
│   │   ├── security.py             # Security utilities
│   │   ├── asgardeo.py             # Asgardeo SCIM client
│   │   └── integrations.py         # Service integrations
│   ├── models/
│   │   └── users.py                # User models & schemas
│   └── main.py                     # FastAPI app
├── tests/
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_integrations.py
├── README.md
└── pyproject.toml
```

---

## ✅ Key Features Implemented

### ✅ User Signup & Authentication
- Email and password validation
- Integration with Asgardeo SCIM API
- Automatic employee creation
- Welcome email notifications

### ✅ User Profile Management
- View current user profile
- Update user information
- Change password securely
- Sync to Asgardeo automatically

### ✅ Admin User Management
- List all users with filtering
- Update user roles
- Suspend/activate accounts
- Delete users (soft delete)
- View user permissions

### ✅ Role-Based Access Control
- Four roles: Admin, HR Manager, Manager, Employee
- Role-based permission mapping
- Protected endpoints with role validation

### ✅ Service Integration
- **Employee Service**: Create/terminate employees
- **Audit Service**: Log all operations
- **Compliance Service**: Validate deletion policies
- **Notification Service**: Send emails

### ✅ Security
- JWT token-based authentication
- Password strength validation
- HTTPS-ready configuration
- CORS middleware
- Secure headers

### ✅ Observability
- Health check endpoints
- Kubernetes readiness/liveness probes
- Comprehensive logging
- Audit logging for compliance

---

## 📞 Support

For issues or questions:
- Check the API documentation at `/docs`
- Review logs for detailed error messages
- Consult the integration guide for service interactions

---

## 📄 License

Proprietary - HR Management System