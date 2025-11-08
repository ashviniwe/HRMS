# Docker Setup Fixes & Configuration Guide

## Summary of Changes

This document outlines all the fixes applied to the HRMS system to resolve Docker build and runtime issues.

---

## 1. Frontend Dockerfile Upgrade

### Issue
The frontend was using Node.js v20, but the `@netlify/vite-plugin-tanstack-start@1.1.0` package requires Node.js v22.12.0 or higher.

### Error
```
npm warn EBADENGINE Unsupported engine {
  package: '@netlify/vite-plugin-tanstack-start@1.1.0',
  required: { node: '^22.12.0' },
  current: { node: 'v20.19.5', npm: '10.8.2' }
}
```

### Fix Applied
**File**: `hrms_frontend/Dockerfile`
- Changed `FROM node:20-alpine AS builder` → `FROM node:22-alpine AS builder`
- Changed `FROM node:20-alpine` → `FROM node:22-alpine`

---

## 2. Backend Services Health Checks

### Issue
Services were failing health checks because:
1. `curl` was not installed in all service containers
2. Health check ports were incorrect (checking port 8000 instead of port 80 where services actually run)
3. Health check start periods were too short to allow database initialization

### Errors
```
dependency failed to start: container hrms_audit_service is unhealthy
dependency failed to start: container hrms_employee_service is unhealthy
```

### Fixes Applied

#### A. Install curl in Service Dockerfiles
**Files Modified**:
- `employee-management-service/Dockerfile`
- `attendance-management-service/Dockerfile`

Added `curl` to the apt-get install line:
```dockerfile
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

#### B. Fix Health Check Configuration in docker-compose.yml

Changed all health checks from:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

To:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:80/health"]
```

**Reason**: Services run on port 80 inside containers. Port 8000 is the external mapping only.

#### C. Increase Health Check Timeouts

Updated all service health checks with:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:80/health"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 120s
```

**Changes**:
- `start_period`: 60s → 120s (allows more time for database initialization)
- `retries`: 3 → 5 (more tolerance for transient failures)

---

## 3. Service Dependencies Optimization

### Issue
Cascading health check dependencies caused timeout failures during startup.

### Original Problem
Services were configured with:
```yaml
depends_on:
  some-service:
    condition: service_healthy
```

This created long chains where each service waited for all its dependencies to be healthy before starting, causing cumulative timeouts.

### Fix Applied

**Strategy**: Differentiate between critical and non-critical dependencies

**Critical Dependencies** (use `service_healthy`):
- All services depend on MySQL with `condition: service_healthy`

**Non-Critical Dependencies** (use `service_started`):
- Services that call other services use `condition: service_started`
- This allows services to start and retry connection logic rather than blocking startup

**Updated docker-compose.yml**:
```yaml
# Example: Leave Service
depends_on:
  mysql:
    condition: service_healthy      # Critical
  employee-service:
    condition: service_started      # Non-critical
  audit-service:
    condition: service_started      # Non-critical
  notification-service:
    condition: service_started      # Non-critical
  compliance-service:
    condition: service_started      # Non-critical
```

---

## 4. Asgardeo Authentication Configuration

### Issue
Frontend was failing with: `AsgardeoRuntimeError: Base URL is required to derive organization handle.`

### Root Cause
The frontend requires two environment variables for Asgardeo:
- `VITE_CLIENT_ID`
- `VITE_ORG_BASE_URL`

These must be available at **build time** (not runtime) because Vite compiles them into the JavaScript.

### Fix Applied

#### A. Update Frontend Dockerfile
**File**: `hrms_frontend/Dockerfile`

Added build arguments:
```dockerfile
# Accept build arguments for Asgardeo configuration
ARG VITE_CLIENT_ID=""
ARG VITE_ORG_BASE_URL=""

# Create .env.production file with build arguments
RUN echo "VITE_CLIENT_ID=${VITE_CLIENT_ID}" > .env.production && \
    echo "VITE_ORG_BASE_URL=${VITE_ORG_BASE_URL}" >> .env.production

# Build the application
RUN npm run build
```

#### B. Update docker-compose.yml
**File**: `docker-compose.yml`

Added build args to frontend service:
```yaml
frontend:
  build:
    context: ./hrms_frontend
    dockerfile: Dockerfile
    args:
      VITE_CLIENT_ID: ${VITE_CLIENT_ID:-}
      VITE_ORG_BASE_URL: ${VITE_ORG_BASE_URL:-}
```

#### C. Create .env Configuration File
**File**: `.env` (project root)

```bash
# Asgardeo Configuration
VITE_CLIENT_ID=your-client-id-here
VITE_ORG_BASE_URL=https://api.asgardeo.io/t/your-organization-name

# SMTP Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=hrms@company.com

# JWT Configuration (Optional)
SECRET_KEY=your-secret-key-change-this-in-production
```

---

## How to Use

### Initial Setup

1. **Configure Asgardeo credentials** (if not already done):
   - Create a `.env` file in the project root
   - Add your Asgardeo `VITE_CLIENT_ID` and `VITE_ORG_BASE_URL`
   - See `ASGARDEO_SETUP.md` for detailed instructions

2. **Build and start all services**:
   ```bash
   cd hr-management-system
   docker compose down -v  # Clean up any previous containers
   docker compose up -d --build
   ```

3. **Wait for services to become healthy**:
   ```bash
   # Check status
   docker compose ps
   
   # Watch status in real-time
   watch docker compose ps
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Employee Service: http://localhost:8001
   - Leave Service: http://localhost:8002
   - Attendance Service: http://localhost:8003
   - Notification Service: http://localhost:8004
   - Audit Service: http://localhost:8005
   - Compliance Service: http://localhost:8006
   - User Service: http://localhost:8007

### Rebuilding After Changes

If you modify Asgardeo configuration:
```bash
docker compose up -d --build frontend
```

For other service changes:
```bash
docker compose up -d --build
```

### Troubleshooting

#### All services are unhealthy
```bash
# Check logs for the problematic service
docker logs hrms_service_name

# Restart everything fresh
docker compose down -v
docker compose up -d --build
```

#### Database connection errors
```bash
# Verify MySQL is healthy
docker compose ps mysql

# Check MySQL logs
docker logs hrms_mysql
```

#### Frontend showing blank page or Asgardeo errors
```bash
# Verify frontend built correctly
docker logs hrms_frontend

# Check that .env file exists and has VITE values
cat .env | grep VITE_

# Rebuild frontend
docker compose up -d --build frontend
```

---

## Technical Details

### Why These Changes Were Necessary

1. **Node.js 22 Requirement**: Netlify's Vite plugin requires modern Node.js APIs not available in v20
2. **Health Check Corrections**: Internal container ports (80) differ from external mappings (8000)
3. **Extended Timeouts**: Database schema creation can take >60 seconds during first start
4. **Smart Dependencies**: Prevents timeout cascades while ensuring database readiness
5. **Build-Time Environment Variables**: Vite embeds config at build time, not runtime

### Performance Impact

- **Startup Time**: ~2-3 minutes for all services to become healthy (first run with DB initialization)
- **Subsequent Starts**: ~30-60 seconds (if volumes persist)
- **Memory Usage**: ~2-3 GB for full stack
- **Disk Space**: ~5-8 GB for images and volumes

---

## Files Modified

1. ✅ `hrms_frontend/Dockerfile` - Node.js v22, build args for Asgardeo
2. ✅ `employee-management-service/Dockerfile` - Added curl
3. ✅ `attendance-management-service/Dockerfile` - Added curl
4. ✅ `docker-compose.yml` - Health checks, dependencies, build args
5. ✅ `.env` - Environment variables template
6. ✅ `ASGARDEO_SETUP.md` - Detailed Asgardeo configuration guide

---

## Next Steps

1. **Configure Asgardeo**: Follow `ASGARDEO_SETUP.md` to set up authentication
2. **Test Login**: Verify the login flow works with your Asgardeo credentials
3. **Configure Services**: Set up any additional services (SMTP, databases, etc.)
4. **Deploy**: Adapt this setup for production environments
