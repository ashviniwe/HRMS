# Error Handling Guide 🚨

Complete guide for error handling in the HRMS application using the error-page-01 block.

## Overview

The application now has comprehensive error handling for:
- ✅ 404 Not Found (routes that don't exist)
- ✅ Login failures (no backend validation)
- ✅ Custom error messages
- ✅ Generic error fallback

## File Structure

```
src/
├── pages/
│   ├── error.tsx          # Base error page component (reusable)
│   ├── error-route.tsx    # Error route with dynamic messages
│   ├── 404.tsx            # 404 Not Found page
│   ├── login.tsx          # Login page
│   └── App.tsx            # Home page
├── components/
│   ├── login-form.tsx     # Login form with error handling
│   └── shadcn-studio/
│       └── blocks/
│           └── error-page-01/  # Original shadcn block
└── main.tsx               # Router with error routes
```

## Routes

### `/error` - Dynamic Error Page
- Displays custom error messages
- Accepts URL search parameters
- Used for runtime errors

### `/*` (Catch-all) - 404 Page
- Matches any undefined route
- Shows "Page not found" message
- Example: `/random-page-that-doesnt-exist` → 404

## How It Works

### 1. 404 - Route Not Found

When a user navigates to a route that doesn't exist:

```
User visits: http://localhost:3000/some-random-page
↓
Router can't find matching route
↓
Shows NotFoundPage (404.tsx)
```

**Try it:**
- Visit: `http://localhost:3000/nonexistent`
- Visit: `http://localhost:3000/admin/dashboard/xyz`

### 2. Login Error - No Backend

When a user tries to login (no backend connected):

```
User enters email and clicks Login
↓
Form validates and simulates API call
↓
Detects no backend is connected
↓
Navigates to /error with message
↓
Shows ErrorRoutePage with custom message
```

**Try it:**
1. Go to `/login`
2. Enter any email
3. Click "Login" button
4. See error page: "Unable to connect to authentication service"

## Error Page Component (`error.tsx`)

### Props

```typescript
interface ErrorPageProps {
  title?: string;          // Main title (default: "Whoops!")
  message?: string;        // Error description
  statusCode?: number;     // HTTP status code (optional)
  showBackButton?: boolean; // Show/hide back button (default: true)
}
```

### Usage Examples

#### Example 1: Simple Error

```tsx
import ErrorPage from "@/pages/error"

<ErrorPage 
  title="Something went wrong"
  message="We couldn't process your request. Please try again."
/>
```

#### Example 2: 404 Error

```tsx
<ErrorPage 
  title="404"
  message="Page not found"
  statusCode={404}
/>
```

#### Example 3: No Back Button

```tsx
<ErrorPage 
  title="Maintenance"
  message="We're currently down for maintenance."
  showBackButton={false}
/>
```

## Navigating to Error Page

### Method 1: Programmatic Navigation (Recommended)

```tsx
import { useNavigate } from "@tanstack/react-router"

const navigate = useNavigate()

// Navigate with custom message
navigate({
  to: "/error",
  search: {
    message: "Your custom error message here",
    from: "component-name",
    statusCode: "500"
  }
})
```

### Method 2: Link Component

```tsx
import { Link } from "@tanstack/react-router"

<Link 
  to="/error" 
  search={{ message: "Something went wrong" }}
>
  View Error
</Link>
```

## Customizing Error Messages

### Login Form Error

Edit `src/components/login-form.tsx`:

```tsx
// Change the error message
navigate({
  to: "/error",
  search: {
    message: "Your custom login error message",
    from: "login",
  },
});
```

### Error Route Page

Edit `src/pages/error-route.tsx` to customize messages based on context:

```tsx
if (search.from === "login") {
  errorTitle = "Login Failed";
  errorMessage = "Your custom message for login errors";
}

// Add more contexts
if (search.from === "payment") {
  errorTitle = "Payment Failed";
  errorMessage = "Unable to process payment";
}
```

## Real Backend Integration

When you connect to a real backend, update the login form:

```tsx
// src/components/login-form.tsx

const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setIsLoading(true);
  setError("");

  try {
    // Replace with your actual API call
    const response = await fetch("https://your-api.com/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      // Backend error - show error page
      navigate({
        to: "/error",
        search: {
          message: "Invalid credentials. Please try again.",
          from: "login",
          statusCode: response.status.toString(),
        },
      });
      return;
    }

    const data = await response.json();
    
    // Success - store token and navigate
    localStorage.setItem("token", data.token);
    navigate({ to: "/dashboard" });
    
  } catch (err) {
    // Network error
    navigate({
      to: "/error",
      search: {
        message: "Unable to connect to server. Please check your internet connection.",
        from: "login",
      },
    });
  } finally {
    setIsLoading(false);
  }
};
```

## Advanced: Error Boundaries

For React component errors, you can add error boundaries:

```tsx
// src/components/error-boundary.tsx
import { Component, ReactNode } from "react";
import ErrorPage from "@/pages/error";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorPage
          title="Application Error"
          message="An unexpected error occurred. Please refresh the page."
        />
      );
    }

    return this.props.children;
  }
}
```

Then wrap your app:

```tsx
// src/main.tsx
<ErrorBoundary>
  <RouterProvider router={router} />
</ErrorBoundary>
```

## Customizing the Error Page Design

### Change Colors

Edit `src/pages/error.tsx`:

```tsx
// Change background color of the illustration
<div className="h-full w-full rounded-2xl bg-blue-600"></div>

// Change button color
<Button className="bg-blue-600 hover:bg-blue-700">
  Back to home page
</Button>
```

### Change Illustration

Replace the image URL in `src/pages/error.tsx`:

```tsx
<img
  src="https://your-custom-image-url.com/error-illustration.png"
  alt="Error illustration"
  className="absolute top-1/2 left-1/2 h-[clamp(260px,25vw,406px)] -translate-x-1/2 -translate-y-1/2"
/>
```

### Remove Illustration

Remove the entire right section:

```tsx
// Delete this entire div
<div className="relative max-h-screen w-full p-2 max-lg:hidden">
  ...
</div>

// Make the left section full width
<div className="grid min-h-screen grid-cols-1"> {/* Remove lg:grid-cols-2 */}
```

## Testing Error Scenarios

### Test 404 Page
```bash
# Visit any non-existent route
http://localhost:3000/this-does-not-exist
http://localhost:3000/random/path/here
```

### Test Login Error
```bash
# Visit login page
http://localhost:3000/login

# Enter any email and click Login
# Should redirect to error page
```

### Test Direct Error Page
```bash
# Visit error page directly with custom message
http://localhost:3000/error?message=Custom%20error%20message&statusCode=500
```

## Common Error Scenarios

### Scenario 1: API Timeout

```tsx
try {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);
  
  const response = await fetch(url, { signal: controller.signal });
  clearTimeout(timeoutId);
  
} catch (err) {
  if (err.name === 'AbortError') {
    navigate({
      to: "/error",
      search: { message: "Request timeout. Please try again." }
    });
  }
}
```

### Scenario 2: Unauthorized Access

```tsx
if (response.status === 401) {
  navigate({
    to: "/error",
    search: {
      message: "Session expired. Please log in again.",
      statusCode: "401"
    }
  });
}
```

### Scenario 3: Server Error

```tsx
if (response.status >= 500) {
  navigate({
    to: "/error",
    search: {
      message: "Server error. Our team has been notified.",
      statusCode: response.status.toString()
    }
  });
}
```

## Tips & Best Practices

1. **Always provide context**: Include `from` parameter to customize error messages
2. **User-friendly messages**: Don't show technical errors to users
3. **Log errors**: Console.log or send to error tracking service
4. **Test error states**: Regularly test error scenarios
5. **Loading states**: Always show loading state during async operations
6. **Retry options**: Consider adding retry buttons for network errors

## Summary

✅ Error page is fully integrated
✅ 404 page catches all undefined routes  
✅ Login form navigates to error page on failure
✅ Customizable error messages via URL params
✅ Beautiful error UI from shadcn blocks
✅ Ready for backend integration

**Next Steps:**
1. Connect to your actual backend API
2. Customize error messages for your use cases
3. Add more error scenarios as needed
4. Consider adding error logging/monitoring

---

Need help with error handling? Check the examples above or ask for assistance! 🚀