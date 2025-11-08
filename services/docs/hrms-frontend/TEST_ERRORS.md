# Quick Error Testing Guide 🧪

## How to Test Each Error Scenario

### ✅ Test 1: 404 Not Found Page

**Steps:**
1. Start your dev server: `npm run dev`
2. Visit any non-existent route in your browser:
   - `http://localhost:3000/random-page`
   - `http://localhost:3000/admin/dashboard`
   - `http://localhost:3000/anything-here`

**Expected Result:**
- Should see the error page with:
  - Title: "404"
  - Message: "The page you're looking for doesn't exist..."
  - Status code shown: "Error 404"
  - "Back to home page" button

---

### ✅ Test 2: Login Error (No Backend)

**Steps:**
1. Navigate to: `http://localhost:3000/login`
2. Enter any email in the input field (e.g., `test@example.com`)
3. Click the "Login" button
4. Wait 1 second for the simulated API call

**Expected Result:**
- Should redirect to error page with:
  - Title: "Login Failed"
  - Message: "Unable to connect to authentication service..."
  - "Back to home page" button
- Clicking "Back to home page" returns you to `/`

---

### ✅ Test 3: Direct Error Page with Custom Message

**Steps:**
1. Visit this URL directly:
   ```
   http://localhost:3000/error?message=This%20is%20a%20custom%20error&statusCode=500
   ```

**Expected Result:**
- Should see error page with:
  - Your custom message displayed
  - Status code: "Error 500"

---

### ✅ Test 4: Navigation Between Pages

**Steps:**
1. Start at home: `http://localhost:3000/`
2. Click "Go to Login" button → Should go to `/login`
3. Try to login → Should redirect to `/error`
4. Click "Back to home page" → Should return to `/`
5. Visit a random URL: `/xyz` → Should show 404 page
6. Click "Back to home page" → Should return to `/`

**Expected Result:**
- All navigation should work smoothly
- No console errors
- Proper page transitions

---

## Checklist for Complete Testing

- [ ] 404 page shows for undefined routes
- [ ] Login button navigates to error page
- [ ] Error page shows correct custom messages
- [ ] "Back to home page" button works
- [ ] No console errors appear
- [ ] Pages load quickly (no lag)
- [ ] Mobile responsive (test on mobile view)
- [ ] Dark mode works (if implemented)

---

## Current Behavior (Before Backend)

### Login Form
- ✅ Accepts any email
- ✅ Shows loading state for 1 second
- ✅ Always navigates to error page (simulating backend failure)
- ✅ Displays "Unable to connect to authentication service"

### When to Update
Once you connect to a real backend, update this line in `src/components/login-form.tsx`:

```tsx
// Change this:
const simulateBackendError = true;

// To this:
const simulateBackendError = false;

// Or replace with actual API call
```

---

## Quick Debug Commands

```bash
# Check for TypeScript errors
npm run build

# Run the dev server
npm run dev

# View all routes (check TanStack Router DevTools at bottom of page)
# Navigate to any page and open DevTools
```

---

## What Each Error Type Shows

| Error Type | Title | Message | Status Code |
|------------|-------|---------|-------------|
| 404 Route | "404" | "The page you're looking for doesn't exist..." | 404 |
| Login Error | "Login Failed" | "Unable to connect to authentication service..." | None |
| Custom Error | Custom | Custom from URL params | Optional |
| Generic Error | "Whoops!" | "Something went wrong..." | Optional |

---

## Browser Console Tips

Open DevTools (F12) and check:
- ❌ No red error messages
- ✅ Should see: "Login submitted with email: ..." when you try to login
- ✅ Router navigation logs from TanStack Router DevTools

---

Happy Testing! 🎉