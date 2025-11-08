# Asgardeo Authentication Implementation Guide

## Overview

This document describes the Asgardeo authentication integration in the HRMS application. The implementation provides a complete authentication flow with login, user profile management, and logout functionality.

## Architecture

### Authentication Flow

1. **Unauthenticated State**
   - User lands on the home page (`/`)
   - Sees a "Go to Login" button
   - Can navigate to the login page

2. **Login Process**
   - User clicks "Go to Login" and navigates to `/login`
   - Email and password fields are displayed but **disabled** (for UI consistency)
   - User clicks "Login with Asgardeo" button
   - Application redirects to Asgardeo for authentication
   - User completes authentication on Asgardeo's platform
   - User is redirected back to the application

3. **Authenticated State**
   - User lands back on the home page (`/`)
   - Sees a "Go to Profile" button instead of "Go to Login"
   - Can navigate to the user profile page (`/user`)

4. **User Profile Page**
   - Displays user information from Asgardeo
   - Shows sidebar with navigation options
   - User dropdown in sidebar footer with logout option

5. **Logout Process**
   - User clicks logout from the dropdown menu
   - Application calls Asgardeo's signOut method
   - User is redirected back to the home page
   - Authentication state is cleared

## File Structure

### Core Files

#### 1. `src/main.tsx`
- **Purpose**: Application entry point and router configuration
- **Key Changes**:
  - Wrapped entire app with `AsgardeoProvider`
  - Added `/user` route for user profile page
  - Configuration uses environment variables

```tsx
<AsgardeoProvider
  clientId={import.meta.env.VITE_CLIENT_ID || ""}
  baseUrl={import.meta.env.VITE_ORG_BASE_URL || ""}
>
  <RouterProvider router={router} />
</AsgardeoProvider>
```

#### 2. `src/App.tsx`
- **Purpose**: Home page component
- **Key Changes**:
  - Uses `useAsgardeo()` hook to check authentication state
  - Conditionally renders "Go to Login" or "Go to Profile" button
  - Uses `isSignedIn` property to determine auth state

```tsx
const { isSignedIn } = useAsgardeo();

{isSignedIn ? (
  <Link to="/user">
    <Button>Go to Profile</Button>
  </Link>
) : (
  <Link to="/login">
    <RainbowButton>Go to Login</RainbowButton>
  </Link>
)}
```

#### 3. `src/components/login-form.tsx`
- **Purpose**: Login form with Asgardeo integration
- **Key Changes**:
  - Email and password fields are **disabled** (shown for UI consistency only)
  - Login button triggers `signIn()` from Asgardeo
  - Handles errors by navigating to error page

```tsx
const { signIn } = useAsgardeo();

const handleAsgardeoLogin = async () => {
  try {
    await signIn();
  } catch (err) {
    navigate({ to: "/error", search: { message: "..." } });
  }
};
```

#### 4. `src/pages/user.tsx`
- **Purpose**: User profile page with sidebar
- **Key Changes**:
  - Displays user information from Asgardeo
  - Implements sidebar with navigation
  - User dropdown in sidebar footer
  - Logout functionality via `signOut()`

```tsx
const { user, signOut, isSignedIn } = useAsgardeo();

const handleLogout = async () => {
  await signOut();
  navigate({ to: "/" });
};
```

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Asgardeo Configuration
VITE_CLIENT_ID=your_asgardeo_client_id
VITE_ORG_BASE_URL=https://api.asgardeo.io/t/your-organization
```

### Getting Asgardeo Credentials

1. Sign up at [Asgardeo](https://asgardeo.io/)
2. Create a new application in your organization
3. Select **Single-Page Application** as the application type
4. Configure the following:
   - **Authorized redirect URLs**: `http://localhost:3000`
   - **Allowed origins**: `http://localhost:3000`
5. Copy the **Client ID** to your `.env` file as `VITE_CLIENT_ID`
6. Copy your **Organization URL** to your `.env` file as `VITE_ORG_BASE_URL`

## Asgardeo Hooks and Properties

### `useAsgardeo()` Hook

The main hook for accessing Asgardeo functionality:

```tsx
const {
  isSignedIn,      // Boolean: authentication status
  user,            // Object: user information
  signIn,          // Function: trigger sign in
  signOut,         // Function: trigger sign out
  isLoading,       // Boolean: loading state
  getAccessToken,  // Function: get access token
  // ... more properties
} = useAsgardeo();
```

### User Object Properties

The `user` object contains:

```tsx
{
  username: string;     // User's username
  name: string;         // Full name
  email: string;        // Email address
  picture?: string;     // Profile picture URL
  // ... additional claims
}
```

## UI Components Used

### Sidebar Components (from shadcn/ui)

- `Sidebar` - Main sidebar container
- `SidebarHeader` - Top section with app branding
- `SidebarContent` - Main navigation area
- `SidebarFooter` - Bottom section with user dropdown
- `SidebarInset` - Content area alongside sidebar
- `SidebarTrigger` - Mobile menu toggle

### Other Components

- `Avatar` / `AvatarImage` / `AvatarFallback` - User profile image
- `DropdownMenu` - User actions menu
- `Button` - Action buttons
- `Sheet` - Mobile sidebar overlay
- `Tooltip` - Hover information
- `Skeleton` - Loading placeholders

## Routes

| Route     | Component      | Auth Required | Description                |
|-----------|----------------|---------------|----------------------------|
| `/`       | `App`          | No            | Home page                  |
| `/login`  | `LoginPage`    | No            | Login page                 |
| `/user`   | `UserPage`     | Recommended   | User profile with sidebar  |
| `/error`  | `ErrorPage`    | No            | Error display page         |
| `*`       | `NotFoundPage` | No            | 404 page                   |

## Authentication State Management

Authentication state is managed by Asgardeo internally. The SDK handles:

- Token storage (in session/local storage)
- Token refresh
- Session management
- Redirect handling

Your application only needs to:
- Check `isSignedIn` status
- Access `user` data when needed
- Call `signIn()` and `signOut()` methods

## Error Handling

All authentication errors redirect to the `/error` page with descriptive messages:

```tsx
navigate({
  to: "/error",
  search: {
    message: "Unable to connect to authentication service...",
    from: "login",
  },
});
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **HTTPS**: Use HTTPS in production
3. **Redirect URLs**: Configure exact redirect URLs in Asgardeo dashboard
4. **Token Storage**: Asgardeo SDK handles secure token storage
5. **CORS**: Configure allowed origins in Asgardeo dashboard

## Testing

### Development Testing

1. Ensure `.env` file is configured with valid credentials
2. Start the development server: `npm run dev`
3. Navigate to `http://localhost:3000`
4. Click "Go to Login"
5. Click "Login with Asgardeo"
6. Complete authentication on Asgardeo
7. Verify redirect back to home page
8. Click "Go to Profile"
9. Test logout from user dropdown

### Production Deployment

1. Update Asgardeo dashboard with production URLs
2. Update `.env` or environment variables with production values
3. Build the application: `npm run build`
4. Deploy the `dist` folder to your hosting provider

## Troubleshooting

### Issue: "Cannot read properties of undefined"

**Cause**: Environment variables not loaded
**Solution**: Ensure `.env` file exists and variables are prefixed with `VITE_`

### Issue: Redirect loop after login

**Cause**: Redirect URL mismatch
**Solution**: Ensure Asgardeo dashboard redirect URLs match your application URL exactly

### Issue: User data is null

**Cause**: User might not be authenticated or data not loaded
**Solution**: Check `isSignedIn` before accessing `user` properties

### Issue: Build fails with Tailwind errors

**Cause**: Conflicting CSS configurations
**Solution**: Ensure no duplicate `@layer base` sections in `styles.css`

## Future Enhancements

Potential improvements for the authentication system:

1. **Protected Routes**: Add route guards for authenticated-only pages
2. **Role-Based Access**: Implement role-based permissions
3. **Token Refresh UI**: Show notifications when tokens are refreshed
4. **Session Timeout**: Warning before session expires
5. **Multi-Factor Authentication**: Enable MFA through Asgardeo
6. **Social Login**: Add additional identity providers
7. **Profile Editing**: Allow users to update their profile
8. **Remember Me**: Persistent sessions option

## Resources

- [Asgardeo Documentation](https://wso2.com/asgardeo/docs/)
- [Asgardeo React SDK](https://github.com/asgardeo/asgardeo-auth-react-sdk)
- [TanStack Router](https://tanstack.com/router)
- [shadcn/ui Components](https://ui.shadcn.com/)

## Support

For issues related to:
- **Asgardeo Configuration**: Check Asgardeo documentation or support
- **Application Issues**: Check this repository's issues or create a new one
- **UI Components**: Refer to shadcn/ui documentation

---

Last Updated: January 2025