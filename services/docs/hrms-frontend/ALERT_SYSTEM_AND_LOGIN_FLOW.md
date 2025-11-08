# Alert System and Login Flow Documentation

## Overview
This document describes the alert/toast notification system and enhanced login flow features implemented in the HRMS application.

## Alert System

### Implementation
A context-based alert system has been added to provide user feedback throughout the application.

#### Files Added
- `src/contexts/AlertContext.tsx` - Alert context provider and hook

#### Key Features
- **Toast-style notifications**: Alerts appear in the top-right corner of the screen
- **Auto-dismiss**: Alerts automatically disappear after 5 seconds
- **Multiple variants**: 
  - `success` - Green themed for successful operations
  - `destructive` - Red themed for errors
  - `default` - Standard themed for informational messages
- **Icons**: Each variant displays an appropriate icon (CheckCircle2, XCircle, Info)
- **Stacking**: Multiple alerts can be displayed simultaneously

#### Usage

```tsx
import { useAlert } from "@/contexts/AlertContext";

function MyComponent() {
  const { showAlert } = useAlert();

  const handleSuccess = () => {
    showAlert({
      title: "Success",
      message: "Operation completed successfully!",
      variant: "success"
    });
  };

  const handleError = () => {
    showAlert({
      title: "Error",
      message: "Something went wrong.",
      variant: "destructive"
    });
  };

  return (
    // Your component JSX
  );
}
```

### Integration
The `AlertProvider` is wrapped around the entire application in `main.tsx`:

```tsx
<AsgardeoProvider>
  <AlertProvider>
    <RouterProvider router={router} />
  </AlertProvider>
</AsgardeoProvider>
```

## Enhanced Login Flow

### Login Success Alert
When a user successfully logs in with Asgardeo:
1. The `signIn()` method sets a flag in `sessionStorage` (`justLoggedIn: "true"`)
2. After redirect back to the homepage, the app detects the flag
3. A success alert is displayed: "Login Successful - Welcome back! You have successfully logged in."
4. The flag is cleared to prevent showing the alert again on subsequent visits
5. The homepage displays an animated "Go to Profile" button

#### Implementation Details
- **File**: `src/App.tsx`
- **Mechanism**: `useEffect` hook monitors `isSignedIn` state and checks `sessionStorage`
- **One-time display**: Uses a `useRef` to prevent duplicate alerts during re-renders

### Already Logged In Check
If a user tries to log in while already authenticated:
1. The login form detects `isSignedIn` is already `true`
2. An alert is shown: "Already Logged In - You are already logged in. Redirecting to homepage..."
3. After 1.5 seconds, the user is automatically redirected to the homepage
4. The login process is prevented from executing

#### Implementation Details
- **File**: `src/components/login-form.tsx`
- **Check location**: Beginning of `handleAsgardeoLogin()` function
- **Prevents**: Unnecessary authentication API calls when already authenticated

### Animated Profile Button
The "Go to Profile" button on the homepage now uses the same `RainbowButton` animation as the "Go to Login" button:
- **Component**: `RainbowButton` from `src/components/ui/rainbow-button.tsx`
- **Animation**: Rainbow gradient border animation that cycles through colors
- **Styling**: Consistent with the login button for visual harmony

#### Before/After
**Before:**
```tsx
<Link to="/profile">
  <Button>Go to Profile</Button>
</Link>
```

**After:**
```tsx
<Link to="/profile">
  <RainbowButton className="px-10 py-5 rounded-lg text-lg font-semibold text-white">
    Go to Profile
  </RainbowButton>
</Link>
```

## Asgardeo User Object Handling

### Name Object Structure
Asgardeo's user object returns `name` as an object with the following structure:
```typescript
{
  givenName: string;
  familyName: string;
}
```

### Display Name Resolution
A helper function `getUserDisplayName()` has been added to properly handle various name formats:

```typescript
const getUserDisplayName = () => {
  if (user?.username) return user.username;
  if (user?.name) {
    if (typeof user.name === "string") return user.name;
    if (typeof user.name === "object" && user.name !== null) {
      const nameObj = user.name as {
        givenName?: string;
        familyName?: string;
      };
      return (
        `${nameObj.givenName || ""} ${nameObj.familyName || ""}`.trim() ||
        "User"
      );
    }
  }
  return "User";
};
```

This function is used in:
- `src/components/app-sidebar.tsx` - For sidebar user display
- `src/pages/profile.tsx` - For profile page user information

### Fallback Chain
1. Try `user.username`
2. Try `user.name` (as string)
3. Try `user.name.givenName` + `user.name.familyName`
4. Fallback to "User"

## Testing the Features

### Test Login Success Alert
1. Start the application in development mode
2. Navigate to the homepage (ensure you're not logged in)
3. Click "Go to Login"
4. Click "Login with Asgardeo"
5. Complete authentication with Asgardeo
6. After redirect to homepage, verify:
   - Green success alert appears in top-right corner
   - Alert shows "Login Successful" with welcome message
   - Homepage shows animated "Go to Profile" button
   - Alert auto-dismisses after 5 seconds

### Test Already Logged In Check
1. Log in successfully (follow steps above)
2. Navigate to `/login` route manually
3. Click "Login with Asgardeo" button
4. Verify:
   - Alert appears: "Already Logged In"
   - No authentication process is triggered
   - Automatic redirect to homepage after 1.5 seconds

### Test Animated Profile Button
1. Log in successfully
2. On the homepage, observe the "Go to Profile" button
3. Verify:
   - Button has rainbow gradient border animation
   - Animation cycles through colors continuously
   - Button matches the style of the "Go to Login" button

## Files Modified

### New Files
- `src/contexts/AlertContext.tsx` - Alert system implementation

### Modified Files
- `src/main.tsx` - Added AlertProvider wrapper
- `src/App.tsx` - Added login success alert detection and RainbowButton for profile
- `src/components/login-form.tsx` - Added already-logged-in check
- `src/components/app-sidebar.tsx` - Fixed name object handling
- `src/pages/profile.tsx` - Fixed name object handling
- `src/components/nav-user.tsx` - Works with properly formatted name string

## Technical Notes

### Session Storage Usage
- **Key**: `justLoggedIn`
- **Value**: `"true"` (string)
- **Lifetime**: Set before login, cleared after alert is shown
- **Purpose**: Persist login success state across redirect

### Alert Timing
- **Display duration**: 5000ms (5 seconds)
- **Redirect delay** (already logged in): 1500ms (1.5 seconds)
- **Auto-dismiss**: Implemented with `setTimeout`

### React Best Practices
- **useRef for one-time alerts**: Prevents duplicate alerts during re-renders
- **useCallback**: Alert functions are memoized to prevent unnecessary re-renders
- **Context pattern**: Centralized alert management accessible throughout the app

## Future Enhancements

Potential improvements for the alert system:
1. Manual dismiss button (X icon)
2. Configurable duration per alert
3. Alert queue management for better UX with many alerts
4. Pause auto-dismiss on hover
5. Sound notifications (optional)
6. Persistent alerts that don't auto-dismiss
7. Alert history/log
8. Animation transitions (slide-in/slide-out)