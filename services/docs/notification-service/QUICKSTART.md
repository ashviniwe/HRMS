# Notification Service - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd notification-service
uv sync
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and update these critical values:

**Database:**
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=hrms_db
```

**Email (Gmail example):**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@hrms.com
SMTP_TLS=True
```

> **Gmail Note**: Generate app password at https://myaccount.google.com/apppasswords (requires 2FA enabled)

### 3. Start the Service
```bash
uv run fastapi dev app/main.py
```

The service will start at `http://localhost:8000`

## Verify It Works

### Test Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Notification Service",
  "version": "1.0.0",
  "database": "hrms_db",
  "features": ["email_notifications", "notification_tracking", "retry_logic"]
}
```

### Send a Test Notification
```bash
curl -X POST "http://localhost:8000/api/v1/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "recipient_email": "test@example.com",
    "recipient_name": "Test User",
    "subject": "Welcome to HRMS",
    "body": "This is your first notification!",
    "channel": "email"
  }'
```

Expected response:
```json
{
  "id": 1,
  "employee_id": 1,
  "recipient_email": "test@example.com",
  "recipient_name": "Test User",
  "subject": "Welcome to HRMS",
  "body": "This is your first notification!",
  "channel": "email",
  "status": "pending",
  "retry_count": 0,
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "sent_at": null
}
```

### Check Notification Status
```bash
curl http://localhost:8000/api/v1/notifications/1
```

After a few seconds, status should change to `sent` and `sent_at` will have a timestamp.

## API Reference

### Send Notification
```bash
POST /api/v1/notifications/send
Content-Type: application/json

{
  "employee_id": 1,
  "recipient_email": "user@example.com",
  "recipient_name": "John Doe",
  "subject": "Notification Subject",
  "body": "Notification message",
  "channel": "email"
}
```

### Get Notification
```bash
GET /api/v1/notifications/{id}
```

### List Employee Notifications
```bash
GET /api/v1/notifications/employee/{employee_id}?offset=0&limit=10
```

### List All Notifications
```bash
GET /api/v1/notifications?offset=0&limit=10&status=sent
```

Status filter options: `pending`, `sent`, `failed`, `retrying`

### Retry Failed Notification
```bash
PUT /api/v1/notifications/{id}/retry
```

## Interactive API Docs

Visit these URLs in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Email Not Sending?

**Check SMTP credentials:**
```bash
# Verify .env has correct SMTP settings
cat .env | grep SMTP
```

**Check logs:**
- Look for error messages in console output
- Check notification status: `GET /api/v1/notifications/1`
- Error details stored in `error_message` field

**Common SMTP errors:**
- `Authentication failed`: Wrong email/password
- `Connection refused`: Wrong host/port
- `Certificate verification failed`: Set `SMTP_TLS=True`

### Database Connection Failed?

**Verify MySQL is running:**
```bash
mysql -h localhost -u root -p -e "SELECT 1;"
```

**Check database credentials in `.env`:**
```env
DB_HOST=localhost      # Not 127.0.0.1
DB_USER=root           # Your MySQL user
DB_PASSWORD=your_pass  # Your MySQL password
DB_NAME=hrms_db        # Database name
```

### Port 8000 Already in Use?

```bash
# Use different port
uv run fastapi dev app/main.py --port 8001
```

## Email Provider Setup

### Gmail
1. Enable 2-factor authentication: https://myaccount.google.com/security
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use app password in `SMTP_PASSWORD`
4. Set `SMTP_HOST=smtp.gmail.com` and `SMTP_PORT=587`

### SendGrid
1. Get API key from SendGrid dashboard
2. Set `SMTP_USER=apikey`
3. Set `SMTP_PASSWORD=<your-api-key>`
4. Set `SMTP_HOST=smtp.sendgrid.net` and `SMTP_PORT=587`

### Office 365
1. Use your Office 365 email and password
2. Set `SMTP_HOST=smtp.office365.com` and `SMTP_PORT=587`

### AWS SES
1. Get SMTP credentials from AWS SES console
2. Set `SMTP_HOST=email-smtp.<region>.amazonaws.com`
3. Set `SMTP_PORT=587`

## Common Tasks

### Send Bulk Notifications
```bash
# Send multiple notifications in sequence
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/notifications/send" \
    -H "Content-Type: application/json" \
    -d "{
      \"employee_id\": $i,
      \"recipient_email\": \"emp$i@example.com\",
      \"recipient_name\": \"Employee $i\",
      \"subject\": \"Test Notification\",
      \"body\": \"This is notification $i\",
      \"channel\": \"email\"
    }"
done
```

### Check Failed Notifications
```bash
curl "http://localhost:8000/api/v1/notifications?status=failed"
```

### Retry All Failed Notifications
```bash
# Get failed notifications
FAILED=$(curl -s "http://localhost:8000/api/v1/notifications?status=failed" | jq '.items[].id')

# Retry each one
for id in $FAILED; do
  curl -X PUT "http://localhost:8000/api/v1/notifications/$id/retry"
done
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker build -t notification-service .
docker run -p 8000:8000 --env-file .env notification-service
```

### Environment Variables for Production
```env
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
SMTP_TLS=True
MAX_RETRIES=3
```

## Database Setup

The database and tables are created automatically on first run. To recreate:

```bash
# Drop and recreate database (destructive!)
mysql -u root -p hrms_db -e "DROP TABLE IF EXISTS notifications;"
```

Then restart the service.

## Monitoring

### Check Service Status
```bash
curl http://localhost:8000/health
```

### View Logs
Logs output to console by default. Look for:
- `Notification created` - New notification added
- `Email sent successfully` - Email delivered
- `Failed to send email` - Delivery failed
- `Notification marked for retry` - Retry initiated

### Database Queries
```sql
-- All notifications
SELECT * FROM notifications ORDER BY created_at DESC;

-- Failed notifications
SELECT * FROM notifications WHERE status = 'failed';

-- By employee
SELECT * FROM notifications WHERE employee_id = 1;

-- Recent (last 24 hours)
SELECT * FROM notifications WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 DAY);

-- Statistics
SELECT status, COUNT(*) as count FROM notifications GROUP BY status;
```

## Next Steps

1. **Integrate with Employee Service**: Call this service when creating/updating employees
2. **Add Email Templates**: Store HTML templates for different notification types
3. **Set Up Monitoring**: Add error alerts for failed notifications
4. **Scale**: Configure multiple workers for production load
5. **Add Authentication**: Implement JWT/JWKS authentication (optional)

## Help & Documentation

- **Full README**: `README.md`
- **Build Summary**: `BUILD_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs
- **Code Examples**: See README.md section "Example Usage"

## Key Endpoints Summary

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Send notification | `/api/v1/notifications/send` | POST |
| Get status | `/api/v1/notifications/{id}` | GET |
| List (employee) | `/api/v1/notifications/employee/{id}` | GET |
| List (all) | `/api/v1/notifications` | GET |
| Retry | `/api/v1/notifications/{id}/retry` | PUT |
| Health | `/health` | GET |

## Support

For issues:
1. Check console logs for error messages
2. Verify `.env` configuration
3. Check database connectivity: `mysql -u root -p`
4. Verify SMTP credentials work with a test tool
5. Check API documentation at `/docs`
