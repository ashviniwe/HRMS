# Compliance Service

**GDPR-Compliant Data Inventory & Access Control Management System**

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: October 30, 2024

## 🎯 What This Service Does

The Compliance Service provides four critical GDPR-compliant endpoints for managing data inventory, access controls, and retention:

1. **GET /compliance/data-inventory** - GDPR Article 30 (Records of Processing Activities)
   - Complete map of all data in system
   - Shows purpose, legal basis, retention, encryption, recipients

2. **GET /compliance/employee/{employee_id}/data-about-me** - GDPR Article 15 (Right of Access)
   - Simple summary of employee's own data
   - Shows data categories, retention schedule, who has access

3. **GET /compliance/employee/{employee_id}/access-controls**
   - What data this person can access and why
   - Access levels, roles, expiration dates

4. **GET /compliance/data-retention-report** - GDPR Article 5 (Storage Limitation)
   - Data age and what needs to be deleted
   - Status categorization and action items

## 📚 Documentation

### Start Here
- **[docs/README.md](./docs/README.md)** - Quick navigation and overview

### For Integration Engineers
- **[docs/INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md)** - How to connect with external services
  - Employee Service integration
  - User Management Service integration
  - Event notification patterns
  - Deployment topology
  - Troubleshooting guide

### For Developers & Architects
- **[docs/IMPLEMENTATION_SUMMARY.md](./docs/IMPLEMENTATION_SUMMARY.md)** - What was implemented and why
  - Architecture decisions
  - Database schema
  - Security implementation
  - GDPR compliance mapping
  - Deployment considerations

### Project Summary
- **[DELIVERABLES.md](./DELIVERABLES.md)** - Complete delivery summary
- **[FINAL_SUMMARY.txt](./FINAL_SUMMARY.txt)** - Quick reference checklist

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- MySQL 5.7+
- Virtual environment with dependencies installed

### Installation & Running

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the service
python -m uvicorn app.main:app --reload --port 8000

# Access API documentation
# Open: http://localhost:8000/docs
```

### Configuration

Copy `.env.local` to `.env` and update:
```bash
# Database
DB_NAME=compliance_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost

# External Services
EMPLOYEE_SERVICE_URL=http://localhost:8001
USER_MANAGEMENT_SERVICE_URL=http://localhost:8002

# JWT/JWKS
JWKS_URL=https://api.asgardeo.io/t/pookieland/oauth2/jwks
JWT_AUDIENCE=your-client-id
JWT_ISSUER=https://api.asgardeo.io/t/pookieland/oauth2/token
```

## 📊 Database Schema

### 4 Main Tables

**DataCategory**
- Classification of data types with sensitivity levels

**DataInventory** (GDPR Article 30 - RoPA)
- Complete record of all data processing activities
- Includes purpose, legal basis, retention, encryption, recipients

**EmployeeDataAccess**
- Tracks which employees can access which data and why
- Includes access levels, roles, expiration dates

**DataRetention** (GDPR Article 5 - Storage Limitation)
- Tracks data age and deletion requirements
- Identifies records marked for deletion

Tables are automatically created on first run using SQLModel.

## 🔐 Security

- ✅ **JWT Authentication** - JWKS-based token validation
- ✅ **Authorization** - Role-based (admin, compliance_officer) and permission-based
- ✅ **Row-Level Security** - Users can only view their own data
- ✅ **Audit Logging** - All operations logged with timestamps
- ✅ **CORS Middleware** - Configurable cross-origin requests
- ✅ **Input Validation** - Pydantic schema validation

## 📋 API Endpoints

### Compliance Reporting (Read-Only)
```
GET  /api/v1/compliance/data-inventory
GET  /api/v1/compliance/employee/{id}/data-about-me
GET  /api/v1/compliance/employee/{id}/access-controls
GET  /api/v1/compliance/data-retention-report
```

### Data Inventory Management (Admin Only)
```
POST   /api/v1/compliance/inventory/categories
GET    /api/v1/compliance/inventory/categories
GET    /api/v1/compliance/inventory/categories/{id}
PATCH  /api/v1/compliance/inventory/categories/{id}
DELETE /api/v1/compliance/inventory/categories/{id}

POST   /api/v1/compliance/inventory/entries
GET    /api/v1/compliance/inventory/entries
GET    /api/v1/compliance/inventory/entries/{id}
PATCH  /api/v1/compliance/inventory/entries/{id}
DELETE /api/v1/compliance/inventory/entries/{id}
GET    /api/v1/compliance/inventory/entries/{id}/stats
```

### Health & Authentication
```
GET  /health
GET  /api/v1/auth/whoami
GET  /api/v1/auth/verify
GET  /api/v1/auth/debug
```

**Total: 25+ endpoints**

## 🏗️ Architecture

### Service Communication
```
┌─────────────────────────────────────┐
│    Compliance Service               │
│  ┌──────────────────────────────┐   │
│  │ Compliance Reporting Layer   │   │
│  │ (GDPR Article 30, 15, 5)     │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Data Inventory Management    │   │
│  │ (CRUD Operations)            │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Security Layer               │   │
│  │ (JWT, RBAC, Row-Level)       │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Database Layer               │   │
│  │ (4 Tables)                   │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
         ↓              ↓
    Employee Service  User Management
```

## 🔄 Integration with External Services

### Employee Service
- Fetch employee data and verify existence
- Display employee's data about them
- Show employee access controls
- Sync department changes

See: **docs/INTEGRATION_GUIDE.md** → Employee Service Integration

### User Management Service
- User authentication (JWT tokens)
- Authorization (roles and permissions)
- Token validation via JWKS

See: **docs/INTEGRATION_GUIDE.md** → User Management Service Integration

## 📈 GDPR Compliance

| Article | Endpoint | Feature |
|---------|----------|---------|
| **30** | GET /data-inventory | Records of Processing Activities (RoPA) |
| **15** | GET /employee/{id}/data-about-me | Right of Access |
| **17** | DataRetention model | Right to Erasure (deletion tracking) |
| **5** | GET /data-retention-report | Storage Limitation (retention tracking) |

Full compliance mapping in: **docs/IMPLEMENTATION_SUMMARY.md** → GDPR Compliance Implementation

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Endpoint info: `GET http://localhost:8000/docs/endpoints`

### Testing Endpoints
```bash
# Get data inventory (requires JWT token)
curl -H "Authorization: Bearer <JWT_TOKEN>" \
  http://localhost:8000/api/v1/compliance/data-inventory

# Get employee's data
curl -H "Authorization: Bearer <JWT_TOKEN>" \
  http://localhost:8000/api/v1/compliance/employee/emp-123/data-about-me
```

See: **docs/INTEGRATION_GUIDE.md** → Testing Integration

## 📁 Project Structure

```
compliance-service/
├── app/
│   ├── main.py                 # Application entry point
│   ├── models/                 # Database models
│   │   ├── data_inventory.py   # DataCategory, DataInventory
│   │   └── employee_data_access.py # EmployeeDataAccess, DataRetention
│   ├── schemas/                # API schemas
│   │   ├── employee.py         # Data Inventory schemas
│   │   └── access_and_retention.py # Access & Retention schemas
│   ├── api/
│   │   ├── routes/
│   │   │   ├── compliance.py   # 4 GDPR compliance endpoints
│   │   │   ├── data_inventory_management.py # CRUD endpoints
│   │   │   └── auth.py         # Authentication endpoints
│   │   └── deps.py             # API dependencies
│   └── core/
│       ├── config.py           # Configuration & settings
│       ├── database.py         # Database setup
│       ├── security.py         # JWT & authorization
│       └── logging.py          # Logging setup
├── docs/
│   ├── INTEGRATION_GUIDE.md    # Integration with external services
│   ├── IMPLEMENTATION_SUMMARY.md # What was done and why
│   └── README.md               # Quick reference
├── DELIVERABLES.md             # Project delivery summary
├── FINAL_SUMMARY.txt           # Quick checklist
├── pyproject.toml              # Project dependencies
└── .env.local                  # Example environment variables
```

## 🚀 Deployment

### Local Development
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker build -t compliance-service:1.0.0 .
docker run -p 8000:8000 --env-file .env compliance-service:1.0.0
```

### Kubernetes
See: **docs/INTEGRATION_GUIDE.md** → Deployment Topology

## 📦 Dependencies

Core:
- FastAPI 0.119+
- SQLModel 0.0.27+
- Pydantic 2.0+

Database:
- mysqlclient 2.2+

Security:
- PyJWT 2.8+
- python-jose 3.3+
- cryptography 41.0+

See: `pyproject.toml` for full dependency list

## ⚙️ Configuration

### Environment Variables
- `DB_NAME` - Database name (default: compliance_db)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `EMPLOYEE_SERVICE_URL` - Employee Service URL
- `USER_MANAGEMENT_SERVICE_URL` - User Management Service URL
- `JWKS_URL` - Token validation endpoint
- `JWT_AUDIENCE`, `JWT_ISSUER` - Token claims

See: `.env.local` for complete list with examples

### Application Settings
- `APP_NAME` - Service name (default: Compliance Service)
- `APP_VERSION` - Service version (default: 1.0.0)
- `DEBUG` - Debug mode (default: False)
- `CORS_ORIGINS` - Allowed origins for CORS

## 🔍 Troubleshooting

### Service won't start
1. Check MySQL is running
2. Verify database credentials in `.env`
3. Check all required environment variables are set
4. Review logs for error messages

### Database errors
1. Verify MySQL connection string
2. Check database user has necessary permissions
3. Ensure database exists or can be created
4. Check `app/core/database.py` logs

### Authentication failures
1. Verify JWKS_URL is accessible
2. Check JWT token hasn't expired
3. Verify JWT_AUDIENCE matches token claims
4. Review token at https://jwt.io

### Integration issues
See: **docs/INTEGRATION_GUIDE.md** → Troubleshooting

## 📞 Support

### Documentation
1. **Getting Started**: Read `docs/README.md`
2. **Integration Help**: See `docs/INTEGRATION_GUIDE.md`
3. **Architecture Details**: Review `docs/IMPLEMENTATION_SUMMARY.md`
4. **API Docs**: Access `/docs` endpoint

### Files to Consult
- `DELIVERABLES.md` - Project delivery details
- `FINAL_SUMMARY.txt` - Quick reference checklist
- `.env.local` - Configuration template
- `pyproject.toml` - Dependencies

## ✅ Status

- ✅ All 4 GDPR endpoints implemented
- ✅ 25+ total endpoints available
- ✅ 4 database models created
- ✅ Security features implemented
- ✅ Comprehensive documentation provided
- ✅ Code tested and verified
- ✅ Ready for production deployment

**Status**: Production Ready  
**Version**: 1.0.0  
**GDPR Compliance**: Articles 5, 15, 17, 30

## 📝 Next Steps

1. **Read Documentation**: Start with `docs/README.md`
2. **Configure Service**: Update `.env` with your settings
3. **Start Service**: Run `uvicorn app.main:app --reload`
4. **Test Endpoints**: Visit `http://localhost:8000/docs`
5. **Integrate**: Follow patterns in `docs/INTEGRATION_GUIDE.md`
6. **Deploy**: Follow deployment topology in documentation

## 📄 License & Version

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: October 30, 2024

---

For detailed information, refer to the comprehensive documentation in the `docs/` directory.