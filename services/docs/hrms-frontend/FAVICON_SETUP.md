# Favicon & Page Title Setup 🎨

Complete guide for the custom building icon favicon and dynamic page titles in HRMS.

## What Was Changed

### ✅ Browser Tab Icon (Favicon)
- **Before:** React logo
- **After:** Building icon (Building2 from Lucide)
- **Color:** White building on dark background (#18181b)

### ✅ Page Titles
- **Before:** Static "Log in" on all pages
- **After:** Dynamic titles for each route
  - Home: "HRMS - Home"
  - Login: "Login - HRMS"
  - Error: "Error - HRMS"
  - 404: "404 Not Found - HRMS"

## Files Created

```
public/
├── favicon.svg          # SVG favicon (modern browsers)
├── favicon.ico          # Classic ICO format (older browsers)
├── favicon-32x32.png    # 32x32 PNG favicon
├── logo192.png          # 192x192 for Android/PWA
└── logo512.png          # 512x512 for Android/PWA
```

## How It Works

### Favicon Loading Order (Browser Compatibility)

The browser checks for favicons in this order:

1. **Modern browsers**: Use `favicon.svg` (scalable, looks sharp)
2. **Older browsers**: Use `favicon-32x32.png` or `favicon.ico`
3. **Apple devices**: Use `logo192.png` (apple-touch-icon)
4. **PWA/Android**: Use icons from `manifest.json`

### HTML Head Section

```html
<!-- Modern SVG favicon (best quality) -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />

<!-- PNG fallback for browsers that don't support SVG -->
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />

<!-- Classic ICO for older browsers -->
<link rel="alternate icon" href="/favicon.ico" />

<!-- Apple devices -->
<link rel="apple-touch-icon" href="/logo192.png" />

<!-- Theme color (matches favicon background) -->
<meta name="theme-color" content="#18181b" />
```

## Customizing the Favicon

### Option 1: Change Colors

Edit `public/favicon.svg`:

```svg
<!-- Change background color -->
<rect width="32" height="32" fill="#3b82f6" rx="4"/>

<!-- Change icon color -->
<g stroke="#ffffff">
```

**Popular color combinations:**
- Blue: `#3b82f6` (background) + `#ffffff` (icon)
- Green: `#10b981` (background) + `#ffffff` (icon)
- Purple: `#8b5cf6` (background) + `#ffffff` (icon)
- Red: `#ef4444` (background) + `#ffffff` (icon)

### Option 2: Use Different Lucide Icon

Replace the building icon paths with any other Lucide icon:

1. Visit: https://lucide.dev
2. Choose an icon
3. Copy the SVG paths
4. Replace the `<g>` content in `public/favicon.svg`

**Example with Briefcase icon:**

```svg
<g transform="translate(8, 6)" stroke="#ffffff" stroke-width="1.5" fill="none">
  <rect width="16" height="12" x="0" y="4" rx="2"/>
  <path d="M4 4V2a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  <line x1="0" y1="10" x2="16" y2="10"/>
</g>
```

### Option 3: Regenerate PNG Files After Changes

After editing `favicon.svg`, regenerate PNG versions:

```bash
cd hrms_v2

# Regenerate all PNG favicons
convert public/favicon.svg -resize 32x32 public/favicon-32x32.png
convert public/favicon.svg -resize 192x192 public/logo192.png
convert public/favicon.svg -resize 512x512 public/logo512.png
convert public/favicon.svg -resize 16x16 -define icon:auto-resize=16,32,48 public/favicon.ico
```

### Option 4: Use Custom Image/Logo

Replace with your company logo:

```bash
# Place your logo in public/ folder
cp /path/to/your-logo.png public/logo.png

# Update index.html
<link rel="icon" type="image/png" href="/logo.png" />
```

## Dynamic Page Titles

### How It Works

Each route in `src/main.tsx` has a `beforeLoad` hook that updates the document title:

```tsx
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/login",
  component: LoginPage,
  beforeLoad: () => {
    document.title = "Login - HRMS";
  },
});
```

### Adding Titles to New Routes

When you create a new route, add a title:

```tsx
const dashboardRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/dashboard",
  component: DashboardPage,
  beforeLoad: () => {
    document.title = "Dashboard - HRMS";
  },
});
```

### Dynamic Titles Based on Data

For pages with dynamic content (e.g., user profile):

```tsx
const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/profile/$userId",
  component: ProfilePage,
  beforeLoad: ({ params }) => {
    document.title = `Profile ${params.userId} - HRMS`;
  },
});
```

Or set it in the component:

```tsx
import { useEffect } from "react";

export default function ProfilePage({ userName }: { userName: string }) {
  useEffect(() => {
    document.title = `${userName} - Profile - HRMS`;
    
    // Cleanup: reset to default on unmount
    return () => {
      document.title = "HRMS";
    };
  }, [userName]);

  return <div>Profile content</div>;
}
```

## Manifest.json (PWA Support)

The `public/manifest.json` file defines how your app appears when installed as a PWA:

```json
{
  "short_name": "HRMS",
  "name": "HRMS - Human Resource Management System",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#18181b",
  "background_color": "#ffffff"
}
```

### Customizing Manifest

- **short_name**: Shown under icon on home screen (max 12 chars)
- **name**: Full app name
- **theme_color**: Browser UI color (status bar on mobile)
- **background_color**: Splash screen background
- **display**: "standalone", "fullscreen", or "browser"

## Testing Your Favicon

### 1. Clear Browser Cache

Sometimes browsers cache favicons aggressively:

**Chrome/Edge:**
```
Ctrl+Shift+Delete → Clear cache
```

**Firefox:**
```
Ctrl+Shift+Delete → Cookies and Site Data
```

**Safari:**
```
Safari → Clear History → All History
```

### 2. Hard Refresh

```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

### 3. Test Direct Access

Visit these URLs directly:
- http://localhost:3000/favicon.svg
- http://localhost:3000/favicon.ico
- http://localhost:3000/favicon-32x32.png

### 4. Test on Different Browsers

- ✅ Chrome/Edge (should use favicon.svg)
- ✅ Firefox (should use favicon.svg)
- ✅ Safari (should use apple-touch-icon)
- ✅ Mobile browsers

### 5. Check DevTools

Open DevTools → Network tab → Refresh page → Look for favicon requests

## Common Issues & Solutions

### Issue 1: Favicon Not Updating

**Solution:**
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Restart dev server
4. Check browser DevTools console for errors

### Issue 2: Favicon Shows on Some Pages but Not Others

**Solution:**
This shouldn't happen with our setup since the favicon is in `index.html`. Check that all routes use the same HTML entry point.

### Issue 3: Wrong Icon Shows on Mobile

**Solution:**
Make sure `logo192.png` and `logo512.png` exist and are referenced in `manifest.json`.

### Issue 4: Blurry Favicon

**Solution:**
- Ensure SVG is properly formed
- Regenerate PNG files at correct sizes
- Use even dimensions (16x16, 32x32, etc.)

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge | Mobile |
|---------|--------|---------|--------|------|--------|
| SVG Favicon | ✅ | ✅ | ⚠️ 14+ | ✅ | ⚠️ Varies |
| ICO Favicon | ✅ | ✅ | ✅ | ✅ | ✅ |
| PNG Favicon | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dynamic Title | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ = Full Support | ⚠️ = Partial Support

## Quick Reference

### Current Favicon Colors
- Background: `#18181b` (dark zinc)
- Icon: `#ffffff` (white)
- Matches HRMS dark theme

### Current Page Titles
- `/` → "HRMS - Home"
- `/login` → "Login - HRMS"
- `/error` → "Error - HRMS"
- `/*` (404) → "404 Not Found - HRMS"

### File Sizes
- favicon.svg: ~677 bytes
- favicon.ico: ~15 KB
- favicon-32x32.png: ~581 bytes
- logo192.png: ~12 KB
- logo512.png: ~60 KB

## Next Steps

1. ✅ Test favicon on all browsers
2. ✅ Verify page titles update correctly
3. ⬜ Add favicon to email templates (if needed)
4. ⬜ Create social media preview images (Open Graph)
5. ⬜ Add favicon to documentation site

---

**Pro Tip:** Bookmark this page for future favicon updates! 🔖