# Error Handling Documentation

## Overview

This project uses a centralized error handling system powered by TanStack Router's built-in error boundary functionality. All errors are automatically caught and displayed using a consistent error page component.

## Architecture

### Components

1. **`RouterErrorComponent`** (`src/components/router-error.tsx`)
   - Central error handler for the entire application
   - Receives error information from TanStack Router
   - Transforms errors into user-friendly messages
   - Renders the `ErrorPage` component with appropriate props

2. **`ErrorPage`** (`src/pages/error.tsx`)
   - Reusable UI component for displaying errors
   - Shows error title, message, and optional status code
   - Includes "Back to home" button for navigation
   - Beautiful design with illustration

3. **`ErrorRoutePage`** (`src/pages/error-route.tsx`)
   - Legacy route-based error handler (kept for manual navigation)
   - Used for specific error route (`/error`)
   - Reads error details from URL search params

## How It Works

### Automatic Error Handling

Every route in the application has the `RouterErrorComponent` configured as its error boundary:

```tsx
const rootRoute = createRootRoute({
  errorComponent: RouterErrorComponent,
  // ...
});

const indexRoute = createRoute({
  errorComponent: RouterErrorComponent,
  // ...
});
```

When an error occurs anywhere in the route component tree, TanStack Router automatically:
1. Catches the error
2. Renders the `RouterErrorComponent`
3. Passes the error object to the component

### Throwing Errors

Instead of manually navigating to an error page, you can now simply **throw an error object** with custom properties:

```tsx
// ❌ OLD WAY (manual navigation)
navigate({
  to: "/error",
  search: {
    message: "Something went wrong",
    from: "login",
  },
});

// ✅ NEW WAY (throw error)
throw {
  message: "Something went wrong",
  from: "login",
  title: "Login Error",
  statusCode: 401,
};
```

### Error Object Structure

You can throw an object with the following properties:

```typescript
interface CustomError {
  message?: string;      // Error message shown to user
  title?: string;        // Error title/heading
  statusCode?: number;   // HTTP status code (optional)
  from?: string;         // Source of error (e.g., "login", "user")
}
```

## Examples

### Example 1: Authentication Error

```tsx
import { useAsgardeo } from "@asgardeo/react";

const { signIn } = useAsgardeo();

const handleLogin = async () => {
  try {
    await signIn();
  } catch (err) {
    throw {
      message: "Unable to connect to authentication service.",
      from: "login",
      title: "Authentication Error",
    };
  }
};
```

### Example 2: Button Click Error

```tsx
<Button
  onClick={() => {
    throw {
      message: "This feature is not available yet.",
      title: "Feature Unavailable",
      from: "dashboard",
    };
  }}
>
  Beta Feature
</Button>
```

### Example 3: Standard JavaScript Error

```tsx
// Standard errors are also caught automatically
const processData = () => {
  if (!data) {
    throw new Error("Data is required");
  }
  // ... process data
};
```

### Example 4: Async Operation Error

```tsx
const loadUserData = async () => {
  try {
    const response = await fetch("/api/user");
    if (!response.ok) {
      throw {
        message: "Failed to load user profile",
        title: "Profile Error",
        statusCode: response.status,
        from: "user",
      };
    }
    return response.json();
  } catch (error) {
    // Error will be caught by RouterErrorComponent
    throw error;
  }
};
```

## Context-Aware Errors

The `RouterErrorComponent` customizes error messages based on the `from` property:

### Login Context (`from: "login"`)
```tsx
throw {
  from: "login",
  // Defaults:
  // title: "Login Failed"
  // message: "Unable to verify credentials..."
};
```

### User Profile Context (`from: "user"`)
```tsx
throw {
  from: "user",
  // Defaults:
  // title: "Profile Error"
  // message: "Unable to load your profile..."
};
```

### Generic Errors
```tsx
throw {
  message: "Custom error message",
  title: "Custom Title",
  // No specific defaults applied
};
```

## Migration Guide

### Migrating Old Code

If you have existing code that manually navigates to error pages:

**Before:**
```tsx
import { useNavigate } from "@tanstack/react-router";

const navigate = useNavigate();

// In your error handler:
navigate({
  to: "/error",
  search: {
    message: "Something went wrong",
    from: "login",
  },
});
```

**After:**
```tsx
// Simply throw the error
throw {
  message: "Something went wrong",
  from: "login",
  title: "Error Title",
};
```

### Benefits of the New Approach

1. **Less Code**: No need to import `useNavigate` or construct navigation objects
2. **Automatic**: Works anywhere in the component tree
3. **Type Safe**: Error structure is clearly defined
4. **Consistent**: All errors handled the same way
5. **Better UX**: Users stay on the same route (better for history/back button)

## Advanced Usage

### Custom Error Components per Route

You can override the error component for specific routes:

```tsx
const specialRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/special",
  component: SpecialComponent,
  errorComponent: CustomErrorComponent, // Route-specific error handler
});
```

### Error Boundaries in Components

For component-level error handling, use React Error Boundaries:

```tsx
import { ErrorBoundary } from "react-error-boundary";

function MyComponent() {
  return (
    <ErrorBoundary
      fallback={<div>Something went wrong</div>}
      onError={(error) => console.error(error)}
    >
      <ChildComponent />
    </ErrorBoundary>
  );
}
```

## Testing Error Handling

### Manual Testing

1. Navigate to a page with error-prone functionality
2. Trigger the error (e.g., click a button that throws)
3. Verify the error page displays correctly
4. Check that the error message is user-friendly
5. Click "Back to home page" to verify navigation works

### Test Button Example

```tsx
// Add this to any page for testing
<Button
  onClick={() => {
    throw {
      message: "This is a test error",
      title: "Test Error",
      statusCode: 500,
    };
  }}
>
  Test Error Handling
</Button>
```

## Error Page Customization

The `ErrorPage` component can be customized with these props:

```tsx
interface ErrorPageProps {
  title?: string;           // Heading text
  message?: string;         // Detailed message
  statusCode?: number;      // Display error code
  showBackButton?: boolean; // Show/hide back button
}
```

## Troubleshooting

### Error Not Caught

**Problem**: Error is not being caught by error boundary

**Solutions**:
- Ensure error is thrown synchronously or in an async function called from the component
- Check that the route has `errorComponent` configured
- Verify error is thrown inside the component tree, not outside React

### Error Page Not Displaying

**Problem**: Error occurs but page doesn't update

**Solutions**:
- Check browser console for error details
- Verify `RouterErrorComponent` is properly imported in `main.tsx`
- Ensure all routes have error component configured

### Error Details Lost

**Problem**: Custom error properties not showing up

**Solutions**:
- Ensure error object structure matches `CustomError` interface
- Check that `RouterErrorComponent` is accessing error properties correctly
- Add console.log in `RouterErrorComponent` to debug error object

## Best Practices

1. **Always provide context**: Use the `from` property to indicate error source
2. **User-friendly messages**: Write error messages for end users, not developers
3. **Avoid technical jargon**: Use simple language in error messages
4. **Include actionable information**: Tell users what they can do next
5. **Log errors for debugging**: Use `console.error()` before throwing
6. **Don't expose sensitive data**: Never include passwords, tokens, etc. in error messages
7. **Provide status codes**: When applicable, include HTTP status codes
8. **Keep it simple**: Don't over-engineer error objects

## Error Message Guidelines

### Good Error Messages ✅

- "Unable to connect to authentication service. Please check your internet connection."
- "This feature is not available yet. Please try again later."
- "Failed to load user profile. Please refresh the page."

### Bad Error Messages ❌

- "Error: ECONNREFUSED 127.0.0.1:3000" (too technical)
- "Something went wrong" (not specific enough)
- "500 Internal Server Error" (not user-friendly)

## Related Files

- `src/components/router-error.tsx` - Main error handler
- `src/pages/error.tsx` - Error UI component
- `src/pages/error-route.tsx` - Legacy error route
- `src/pages/404.tsx` - Not found page
- `src/main.tsx` - Router configuration with error components

## Resources

- [TanStack Router Error Handling](https://tanstack.com/router/latest/docs/guide/error-handling)
- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [Error Handling Best Practices](https://www.smashingmagazine.com/2022/08/error-handling-user-experience-best-practices/)

---

Last Updated: January 2025