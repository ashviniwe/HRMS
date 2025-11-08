# Profile Page Migration Documentation

## Overview

This document describes the migration from the old user page to the new shadcn-based profile page with integrated Asgardeo authentication.

## Changes Made

### 1. New Profile Page

**File**: `src/pages/profile.tsx`

- Created new profile page using shadcn's `sidebar-08` template
- Integrated Asgardeo authentication to display real user data
- Added breadcrumb navigation (Home → Profile)
- Displays user information including:
  - Username
  - Email
  - Authentication status
- Three info cards showing:
  - Welcome message with Asgardeo status
  - Profile authentication status
  - Quick actions section

### 2. Updated AppSidebar Component

**File**: `src/components/app-sidebar.tsx`

**Changes**:
- Integrated `useAsgardeo()` hook to fetch real user data
- Updated branding from "Acme Inc" to "HRMS" with Building2 icon
- User data now comes from Asgardeo instead of hardcoded values
- Changed home link to navigate to `/` instead of `#`

**User Data Source**:
```tsx
const userData = {
  name: user?.username || user?.name || "User",
  email: user?.email || "user@example.com",
  avatar: user?.profilePicture || user?.picture || "",
};
```

### 3. Updated NavUser Component

**File**: `src/components/nav-user.tsx`

**Changes**:
- Added Asgardeo logout functionality
- Implemented `handleLogout()` function that:
  - Calls `signOut()` from Asgardeo
  - Redirects to home page after successful logout
  - Handles errors by throwing custom error objects
- Added loading state for logout button
- Fixed avatar fallback to generate initials from username
- Fixed CSS class typo in dropdown width

**Logout Implementation**:
```tsx
const handleLogout = async () => {
  setIsLoggingOut(true);
  try {
    await signOut();
    window.location.href = "/";
  } catch (error) {
    console.error("Logout error:", error);
    setIsLoggingOut(false);
    throw {
      message: "Unable to logout. Please try again later.",
      from: "profile",
      title: "Logout Error",
    };
  }
};
```

### 4. Updated Router Configuration

**File**: `src/main.tsx`

**Changes**:
- Replaced `/user` route with `/profile` route
- Updated route component from `UserPage` to `ProfilePage`
- Updated document title to "Profile - HRMS"

**Route Definition**:
```tsx
const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/profile",
  component: ProfilePage,
  errorComponent: RouterErrorComponent,
  beforeLoad: () => {
    document.title = "Profile - HRMS";
  },
});
```

### 5. Updated Home Page

**File**: `src/App.tsx`

**Changes**:
- Updated profile button to navigate to `/profile` instead of `/user`
- Button text remains "Go to Profile"

### 6. Removed Old Files

**Deleted**:
- `src/pages/user.tsx` - Old user page with custom sidebar implementation

### 7. Updated Error Handling

**File**: `src/components/router-error.tsx`

**Changes**:
- Added support for `from: "profile"` error context
- Profile errors show appropriate error messages

## Component Hierarchy

```
ProfilePage
├── SidebarProvider
│   ├── AppSidebar
│   │   ├── SidebarHeader (HRMS branding)
│   │   ├── SidebarContent
│   │   │   ├── NavMain (navigation items)
│   │   │   ├── NavProjects (project links)
│   │   │   └── NavSecondary (support/feedback)
│   │   └── SidebarFooter
│   │       └── NavUser (user dropdown with logout)
│   └── SidebarInset
│       ├── Header (with breadcrumbs)
│       └── Content (user information)
```

## Routes

| Old Route | New Route  | Description           |
|-----------|------------|-----------------------|
| `/user`   | `/profile` | User profile page     |

## Navigation Flow

1. **Home Page (Authenticated)**
   - Shows "Go to Profile" button
   - Navigates to `/profile`

2. **Profile Page**
   - Displays user information from Asgardeo
   - Sidebar with navigation and user dropdown
   - Logout button in user dropdown

3. **Logout**
   - Click "Log out" in user dropdown
   - Asgardeo signOut called
   - Redirects to home page (`/`)
   - Home page shows "Go to Login" button

## User Data Integration

The profile page and sidebar components use Asgardeo's user data:

```tsx
const { user, isSignedIn } = useAsgardeo();

const userData = {
  name: user?.username || user?.name || "User",
  email: user?.email || "user@example.com",
  avatar: user?.profilePicture || user?.picture || "",
};
```

**Available User Properties**:
- `username` - User's username
- `name` - Full name
- `email` - Email address
- `profilePicture` / `picture` - Profile image URL

## Styling

The new profile page uses:
- shadcn/ui sidebar components
- Consistent color scheme with CSS variables
- Responsive design (mobile-friendly)
- Muted backgrounds for content areas
- Proper spacing and typography

## Error Handling

Logout errors are handled using the global error boundary:

```tsx
throw {
  message: "Unable to logout. Please try again later.",
  from: "profile",
  title: "Logout Error",
};
```

This automatically displays the error page with appropriate messaging.

## Testing

### Manual Testing Steps

1. **Profile Page Access**
   - Login to the application
   - From home page, click "Go to Profile"
   - Verify profile page loads with sidebar
   - Check that user information displays correctly

2. **User Data Display**
   - Verify username appears in sidebar footer
   - Verify email appears in sidebar footer
   - Verify user info appears in main content area
   - Check authentication status shows "Active"

3. **Logout Functionality**
   - Click on user dropdown in sidebar footer
   - Click "Log out"
   - Verify "Logging out..." text appears
   - Verify redirect to home page after logout
   - Verify home page shows "Go to Login" button

4. **Navigation**
   - Test sidebar navigation items
   - Test breadcrumb links
   - Test sidebar toggle on mobile
   - Test HRMS logo link to home

## Migration Checklist

- [x] Create new profile page with shadcn sidebar
- [x] Integrate Asgardeo authentication
- [x] Add logout functionality to NavUser
- [x] Update AppSidebar with real user data
- [x] Update router configuration
- [x] Update home page navigation
- [x] Remove old user page
- [x] Update error handling for profile context
- [x] Test authentication flow
- [x] Test logout functionality
- [x] Update documentation

## Known Issues

None currently identified.

## Future Enhancements

Potential improvements for the profile page:

1. **Profile Editing**: Allow users to update their profile information
2. **Avatar Upload**: Enable users to upload custom profile pictures
3. **Settings Page**: Add dedicated settings page for preferences
4. **Activity Log**: Show user activity history
5. **Notifications**: Integrate notification system
6. **Theme Toggle**: Add dark/light mode switcher
7. **Language Selection**: Multi-language support
8. **Two-Factor Authentication**: Enable 2FA settings
9. **Connected Accounts**: Manage linked social accounts
10. **Security Settings**: Password change, sessions, etc.

## Related Documentation

- [ASGARDEO_IMPLEMENTATION.md](./ASGARDEO_IMPLEMENTATION.md) - Asgardeo setup guide
- [ERROR_HANDLING.md](./ERROR_HANDLING.md) - Error handling documentation
- [README.md](./README.md) - General project documentation

## Support

For issues related to:
- **Profile Page**: Check this document and component files
- **Asgardeo Integration**: See ASGARDEO_IMPLEMENTATION.md
- **Sidebar Components**: Refer to shadcn/ui documentation
- **Routing**: Check TanStack Router documentation

---

Last Updated: January 2025