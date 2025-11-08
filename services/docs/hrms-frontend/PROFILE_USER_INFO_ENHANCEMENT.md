# Profile Page User Information Enhancement

## Overview
This document describes the enhancement of the profile page to display comprehensive user information from Asgardeo's decoded ID token, including proper authentication status checking and graceful handling of missing data.

## Implementation Details

### Technologies Used
- **Asgardeo React SDK** (`@asgardeo/react`)
- **Hook**: `useAsgardeo()` with `getDecodedIdToken()` method
- **Authentication Status**: Dynamic checking using `isSignedIn` state
- **Loading States**: Skeleton components for better UX during data fetching

## Features Implemented

### 1. Decoded ID Token User Information

The profile page now fetches and displays comprehensive user information from the decoded ID token:

#### BasicUserInfo Interface
```typescript
interface BasicUserInfo {
  email?: string;
  username?: string;
  displayName?: string;
  allowedScopes?: string;
  tenantDomain?: string;
  sessionState?: string;
  sub?: string;
  preferred_username?: string;
  org_id?: string;
  org_name?: string;
}
```

#### Information Displayed

**Primary User Details:**
- **Display Name**: Preferred username or subject from the token
- **Username**: User's username
- **Email**: User's email address
- **Subject (Sub)**: Unique identifier for the user

**Organization & Tenant Information:**
- **Tenant Domain**: The tenant domain to which the user belongs
- **Organization ID**: Unique organization identifier
- **Organization Name**: Organization name

**Session & Security:**
- **Session State**: Current session state identifier
- **Allowed Scopes**: Space-separated list of scopes granted to the user

### 2. Enhanced Authentication Status

The "Profile Status" card now shows real-time authentication status with visual indicators:

#### Status States
1. **Checking** (Yellow dot): Initial state while verifying authentication
2. **Active** (Green dot): User is successfully authenticated
3. **Inactive** (Red dot): User is not authenticated

#### Implementation
```tsx
const [authStatus, setAuthStatus] = useState<
  "checking" | "active" | "inactive"
>("checking");

useEffect(() => {
  const fetchUserInfo = async () => {
    if (!isSignedIn) {
      setAuthStatus("inactive");
      return;
    }
    
    try {
      const decodedToken = await getDecodedIdToken();
      setUserInfo(basicInfo);
      setAuthStatus("active");
    } catch (error) {
      setAuthStatus("inactive");
    }
  };
  
  fetchUserInfo();
}, [isSignedIn, getDecodedIdToken]);
```

### 3. Graceful Handling of Missing Data

The implementation includes robust fallback mechanisms:

#### Display Value Helper
```tsx
const displayValue = (
  value: string | undefined,
  fallback = "Not available",
) => {
  return value && value.trim() !== "" ? value : fallback;
};
```

#### Key Features
- **Null/Undefined Safety**: All fields are optional and safely accessed
- **Empty String Handling**: Trims whitespace and shows fallback if empty
- **Default Fallback**: Shows "Not available" for missing data
- **No Breaking**: Page remains functional even if Asgardeo returns partial data

### 4. Loading States

Enhanced user experience with loading skeletons:

```tsx
{isLoading ? (
  <div className="space-y-4">
    {[...Array(6)].map((_, i) => (
      <div key={i}>
        <Skeleton className="h-4 w-32 mb-2" />
        <Skeleton className="h-6 w-full" />
      </div>
    ))}
  </div>
) : (
  // Display user information
)}
```

## User Interface Layout

### Card Layout (Top Section)

**Card 1: Welcome Back**
- Personalized greeting with display name
- Shows skeleton during loading
- Fallback message if name not available

**Card 2: Profile Status**
- Real-time authentication status
- Color-coded indicator (green/yellow/red)
- Status text: Active/Checking/Inactive

**Card 3: Quick Actions**
- Static informational card
- Guides users to account management

### User Information Section (Bottom)

**Two-Column Grid Layout:**

**Left Column:**
- Display Name
- Username
- Email
- Subject (Sub)

**Right Column:**
- Tenant Domain
- Organization ID
- Organization Name
- Session State

**Full-Width Row:**
- Allowed Scopes (can be long, needs full width)

**All fields include:**
- Label in muted gray
- Value in larger text
- "Not available" fallback for missing data
- `break-all` or `break-words` for long values

## Code Structure

### State Management
```tsx
const [userInfo, setUserInfo] = useState<BasicUserInfo | null>(null);
const [isLoading, setIsLoading] = useState(true);
const [authStatus, setAuthStatus] = useState<
  "checking" | "active" | "inactive"
>("checking");
```

### Data Fetching Flow
1. Component mounts
2. Check if user is signed in
3. If signed in, fetch decoded ID token
4. Extract relevant fields from token
5. Set user info state
6. Update authentication status
7. Handle errors gracefully
8. Set loading to false

### Error Handling
- Try-catch block wraps token decoding
- Console error logging for debugging
- Sets auth status to inactive on error
- Loading state always resolves (finally block)
- No application crashes on missing data

## Token Field Mapping

| Asgardeo Token Field | UI Display Label | Notes |
|---------------------|------------------|-------|
| `email` | Email | Primary contact |
| `username` | Username | Login identifier |
| `preferred_username` | Display Name | Preferred display name |
| `sub` | Subject (Sub) | Unique user ID |
| `scope` | Allowed Scopes | Space-separated scopes |
| `tenant_domain` | Tenant Domain | Tenant identifier |
| `session_state` | Session State | Session identifier |
| `org_id` | Organization ID | Org unique ID |
| `org_name` | Organization Name | Org display name |

## Testing Scenarios

### Scenario 1: Full User Data
**Given**: User logs in with complete profile
**When**: Profile page loads
**Then**: 
- All fields display actual values
- No "Not available" fallbacks shown
- Authentication status shows "Active" with green dot

### Scenario 2: Partial User Data
**Given**: User logs in with incomplete profile
**When**: Profile page loads
**Then**: 
- Available fields show actual values
- Missing fields show "Not available"
- Page remains functional
- No errors in console

### Scenario 3: Not Authenticated
**Given**: User is not logged in
**When**: User navigates to profile (if allowed)
**Then**: 
- Loading completes quickly
- Authentication status shows "Inactive" with red dot
- User info section shows "Not available" for all fields

### Scenario 4: Token Fetch Error
**Given**: User is logged in
**When**: Token decoding fails
**Then**: 
- Error is logged to console
- Authentication status shows "Inactive"
- No application crash
- User sees appropriate fallback messages

## Benefits

### User Experience
✅ **Comprehensive Information**: Users can view all available profile data
✅ **Real-time Status**: Clear visual indication of authentication state
✅ **Loading Feedback**: Skeleton loaders prevent confusion during data fetch
✅ **No Broken UI**: Graceful handling of missing data

### Developer Experience
✅ **Type Safety**: TypeScript interfaces for user info
✅ **Error Resilience**: Robust error handling prevents crashes
✅ **Maintainable**: Clear separation of concerns
✅ **Extensible**: Easy to add more fields from token

### Security
✅ **Token-based**: Uses official Asgardeo SDK methods
✅ **No Sensitive Data Exposure**: Only displays user-appropriate information
✅ **Session Validation**: Real-time authentication checking

## Future Enhancements

### Potential Improvements
1. **Refresh Token Info**: Button to manually refresh user data
2. **Edit Profile**: Link to Asgardeo profile editor
3. **Copy to Clipboard**: Copy buttons for long values (Sub, Session State, Org ID)
4. **Token Expiry Display**: Show when access token expires
5. **Linked Accounts**: Display linked social/enterprise accounts
6. **Groups/Roles**: Display user's groups and roles if available
7. **Last Login Time**: Show last successful authentication time
8. **MFA Status**: Display multi-factor authentication status
9. **Export Profile**: Download user profile data as JSON
10. **Activity Log**: Recent authentication activities

## API Reference

### `getDecodedIdToken()`
**Source**: `@asgardeo/react` - `useAsgardeo()` hook

**Returns**: `Promise<IdToken>`

**Description**: Retrieves and decodes the ID token, returning the payload with user claims and information.

**Usage**:
```tsx
const { getDecodedIdToken } = useAsgardeo();

const fetchUserInfo = async () => {
  try {
    const decodedToken = await getDecodedIdToken();
    // Access token fields: decodedToken.email, decodedToken.sub, etc.
  } catch (error) {
    console.error("Error decoding token:", error);
  }
};
```

### `isSignedIn`
**Source**: `@asgardeo/react` - `useAsgardeo()` hook

**Type**: `boolean`

**Description**: Flag indicating whether the user is currently signed in.

**Usage**:
```tsx
const { isSignedIn } = useAsgardeo();

if (isSignedIn) {
  // User is authenticated
} else {
  // User is not authenticated
}
```

## File Changes

### Modified Files
- `src/pages/profile.tsx` - Complete rewrite with enhanced user info display

### Dependencies Added
- `Skeleton` component from `@/components/ui/skeleton` (already existed)
- Enhanced state management with `useState` for loading and auth status
- `useEffect` for async data fetching

### No Breaking Changes
- Existing routes and navigation remain unchanged
- Sidebar and breadcrumb functionality preserved
- Compatible with existing authentication flow

## Conclusion

The enhanced profile page provides a comprehensive view of user information from Asgardeo's ID token while maintaining excellent user experience through loading states and graceful error handling. The implementation is production-ready, type-safe, and handles edge cases appropriately.