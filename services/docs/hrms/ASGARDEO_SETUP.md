# Asgardeo Authentication Setup Guide

## Overview

This HRMS system uses [Asgardeo](https://asgardeo.io/) for authentication. Asgardeo is a cloud-native identity and access management (IAM) platform that provides OAuth 2.0 and OpenID Connect support.

## Prerequisites

- An Asgardeo account (free tier available at https://asgardeo.io/)
- Access to the Asgardeo Console

## Step 1: Create an Asgardeo Organization

1. Go to [Asgardeo Console](https://console.asgardeo.io/)
2. Sign up or log in with your credentials
3. Create a new organization or use an existing one
4. Note your **organization handle** (e.g., `your-organization-name`)

## Step 2: Register Your Application

1. In the Asgardeo Console, go to **Applications**
2. Click **New Application**
3. Choose **Single Page Application (SPA)**
4. Fill in the application details:
   - **Name**: HRMS Frontend
   - **Protocol**: OpenID Connect
5. In the **Access Configuration**, set the following redirect URIs:
   - `http://localhost:3000/login` (for local development)
   - `http://localhost:3000` (for local development)
   - `https://your-production-domain.com/login` (for production)
   - `https://your-production-domain.com` (for production)

## Step 3: Get Your Credentials

After creating the application:

1. Go to the application's **Protocol** tab
2. Copy your **Client ID**
3. Note the **Organization Handle** from your organization settings

## Step 4: Configure Environment Variables

1. Create a `.env` file in the project root (or update the existing one):

```bash
# Asgardeo Configuration
VITE_CLIENT_ID=your-client-id-here
VITE_ORG_BASE_URL=https://api.asgardeo.io/t/your-organization-name
```

Replace:
- `your-client-id-here` with the Client ID from Step 3
- `your-organization-name` with your Asgardeo organization handle

## Step 5: Rebuild and Start the Application

```bash
docker compose down
docker compose up -d --build
```

The frontend will now build with your Asgardeo configuration embedded.

## Step 6: Access the Application

1. Open http://localhost:3000 in your browser
2. You should see the login page with "Login with Asgardeo" button
3. Click the button to authenticate with Asgardeo

## Troubleshooting

### Error: "Base URL is required to derive organization handle"

This error means the `VITE_ORG_BASE_URL` environment variable is not set or is empty.

**Solution:**
1. Verify your `.env` file exists in the project root
2. Check that `VITE_ORG_BASE_URL` is set correctly
3. Rebuild the frontend: `docker compose up -d --build frontend`

### Error: "Invalid Client ID"

This means the `VITE_CLIENT_ID` doesn't match your Asgardeo application.

**Solution:**
1. Go to Asgardeo Console → Applications → Your App → Protocol
2. Copy the correct Client ID
3. Update your `.env` file
4. Rebuild: `docker compose up -d --build frontend`

### Login redirects back to login page

This usually means the redirect URI is not configured in Asgardeo.

**Solution:**
1. Go to Asgardeo Console → Applications → Your App
2. Check the **Access Configuration** section
3. Verify that your callback URL is listed in the Allowed redirect URIs
4. Add it if it's missing

## Production Deployment

For production:

1. Set your production domain in the redirect URIs
2. Update `.env` with production domain URLs:
   ```bash
   VITE_ORG_BASE_URL=https://api.asgardeo.io/t/your-organization-name
   ```
3. Ensure your application is accessible from the production domain
4. Rebuild and deploy

## Additional Resources

- [Asgardeo Documentation](https://wso2.com/asgardeo/docs/)
- [OAuth 2.0 Authorization Code Flow](https://wso2.com/asgardeo/docs/guides/authentication/oauth2-authcode/)
- [OpenID Connect Configuration](https://wso2.com/asgardeo/docs/guides/authentication/oidc/)

## Support

For issues related to:
- **Asgardeo**: Visit [Asgardeo Support](https://wso2.com/asgardeo/support/)
- **This HRMS Application**: Check the project README
