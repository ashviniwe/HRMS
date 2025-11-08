# Quick Start Guide - HRMS with Asgardeo

## Prerequisites
- Docker and Docker Compose installed
- An Asgardeo account (free at https://asgardeo.io)

## 5-Minute Setup

### Step 1: Get Your Asgardeo Credentials (2 minutes)

1. Go to [Asgardeo Console](https://console.asgardeo.io)
2. Create or log into your organization
3. Go to **Applications** → **New Application**
4. Select **Single Page Application (SPA)**
5. Name it "HRMS Frontend"
6. In **Access Configuration**, add these Redirect URIs:
   - `http://localhost:3000`
   - `http://localhost:3000/login`
7. Go to **Protocol** tab and copy your **Client ID**
8. Note your **organization handle** from the URL or settings

### Step 2: Configure Environment (1 minute)

Create a `.env` file in the project root:

```bash
# Asgardeo Configuration
VITE_CLIENT_ID=your-client-id-here
VITE_ORG_BASE_URL=https://api.asgardeo.io/t/your-organization-name
```

Replace:
- `your-client-id-here` → Your Client ID from Step 1
- `your-organization-name` → Your organization handle from Step 1

### Step 3: Start the Application (2 minutes)

```bash
cd hr-management-system
docker compose up -d --build
```

Wait for services to start (they'll show as "healthy"):

```bash
docker compose ps
```

### Step 4: Access the Application

Open http://localhost:3000 in your browser

You should see a login page with "Login with Asgardeo" button.

Click it to authenticate with your Asgardeo credentials.

---

## Common Issues

### "Base URL is required" Error

**Solution**: 
- Check `.env` file exists in project root
- Verify `VITE_ORG_BASE_URL` is set correctly
- Rebuild: `docker compose up -d --build frontend`

### "Invalid Client ID" Error

**Solution**:
- Copy the correct Client ID from Asgardeo Console
- Update `.env` file
- Rebuild: `docker compose up -d --build frontend`

### Login redirects back to login page

**Solution**:
- Add `http://localhost:3000` and `http://localhost:3000/login` to Asgardeo redirect URIs
- Rebuild: `docker compose up -d --build frontend`

### Services are unhealthy

**Solution**:
```bash
docker compose down -v
docker compose up -d --build
```

---

## Service Ports

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Employee API | http://localhost:8001 | 8001 |
| Leave API | http://localhost:8002 | 8002 |
| Attendance API | http://localhost:8003 | 8003 |
| Notification API | http://localhost:8004 | 8004 |
| Audit API | http://localhost:8005 | 8005 |
| Compliance API | http://localhost:8006 | 8006 |
| User API | http://localhost:8007 | 8007 |
| MySQL Database | localhost:3307 | 3307 |

---

## Next Steps

1. **User Management**: Create users in Asgardeo Console
2. **API Testing**: Use Postman to test backend APIs on ports 8001-8007
3. **Email Configuration**: Set up SMTP in `.env` for notifications
4. **Production Deployment**: Update Asgardeo redirect URIs with your production domain

---

## For More Details

- Full Docker setup guide: See `DOCKER_SETUP_FIXES.md`
- Detailed Asgardeo setup: See `ASGARDEO_SETUP.md`
- Backend API documentation: Check individual service README files