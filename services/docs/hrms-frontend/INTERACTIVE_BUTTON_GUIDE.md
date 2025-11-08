# Interactive Hover Button Guide 🎯

Complete guide for using the MagicUI Interactive Hover Button in HRMS.

## Overview

The Interactive Hover Button is a modern, animated button component from MagicUI that provides a smooth hover effect with an arrow transition.

## Current Usage

### Home Page (App.tsx)

The "Go to Login" button now uses the InteractiveHoverButton component:

```tsx
import { InteractiveHoverButton } from "@/components/ui/interactive-hover-button";
import { Link } from "@tanstack/react-router";

<Link to="/login" className="mt-4">
  <InteractiveHoverButton className="bg-black text-white hover:bg-black/90">
    Go to Login
  </InteractiveHoverButton>
</Link>
```

## How It Works

### Animation Breakdown

1. **Default State:**
   - Shows a small dot indicator on the left
   - Button text is visible and centered
   - Arrow icon is hidden (off-screen to the right)

2. **Hover State:**
   - The dot scales up dramatically
   - Button text slides to the right and fades out
   - Arrow icon slides in from the right with the text
   - Smooth transitions create a fluid effect

### Component Structure

```tsx
<InteractiveHoverButton>
  {/* Default view */}
  <div className="flex items-center gap-2">
    <div className="dot"></div>  {/* Small indicator */}
    <span>{children}</span>        {/* Button text */}
  </div>
  
  {/* Hover view (hidden by default) */}
  <div className="absolute">
    <span>{children}</span>        {/* Button text */}
    <ArrowRight />                 {/* Arrow icon */}
  </div>
</InteractiveHoverButton>
```

## Basic Usage

### Simple Button

```tsx
import { InteractiveHoverButton } from "@/components/ui/interactive-hover-button";

<InteractiveHoverButton>
  Click Me
</InteractiveHoverButton>
```

### With Link (Navigation)

```tsx
import { Link } from "@tanstack/react-router";
import { InteractiveHoverButton } from "@/components/ui/interactive-hover-button";

<Link to="/dashboard">
  <InteractiveHoverButton>
    Go to Dashboard
  </InteractiveHoverButton>
</Link>
```

### With Custom Styling

```tsx
<InteractiveHoverButton className="bg-blue-600 text-white hover:bg-blue-700">
  Custom Colors
</InteractiveHoverButton>
```

### With onClick Handler

```tsx
<InteractiveHoverButton 
  onClick={() => console.log('Clicked!')}
  className="bg-green-600 text-white"
>
  Submit Form
</InteractiveHoverButton>
```

## Styling Options

### Color Variants

#### Black Button (Current)
```tsx
<InteractiveHoverButton className="bg-black text-white hover:bg-black/90">
  Go to Login
</InteractiveHoverButton>
```

#### Primary Color
```tsx
<InteractiveHoverButton className="bg-primary text-primary-foreground">
  Primary Action
</InteractiveHoverButton>
```

#### Gradient
```tsx
<InteractiveHoverButton className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
  Gradient Button
</InteractiveHoverButton>
```

#### Outline Style
```tsx
<InteractiveHoverButton className="border-2 border-black bg-transparent text-black hover:bg-black hover:text-white">
  Outline Button
</InteractiveHoverButton>
```

### Size Variants

#### Large
```tsx
<InteractiveHoverButton className="p-3 px-8 text-lg">
  Large Button
</InteractiveHoverButton>
```

#### Small
```tsx
<InteractiveHoverButton className="p-1.5 px-4 text-sm">
  Small Button
</InteractiveHoverButton>
```

#### Full Width
```tsx
<InteractiveHoverButton className="w-full">
  Full Width Button
</InteractiveHoverButton>
```

## Advanced Usage

### Custom Icon

Replace the default ArrowRight icon by modifying the component:

```tsx
// Edit: src/components/ui/interactive-hover-button.tsx
import { ChevronRight } from "lucide-react"; // or any other icon

// Replace ArrowRight with ChevronRight in the component
```

### Disable Animation

```tsx
<InteractiveHoverButton className="[&>*]:!transition-none">
  No Animation
</InteractiveHoverButton>
```

### Different Animation Speed

```tsx
<InteractiveHoverButton className="[&>*]:duration-500">
  Slower Animation
</InteractiveHoverButton>
```

## Real-World Examples

### Example 1: Call-to-Action Section

```tsx
export function CTASection() {
  return (
    <section className="bg-gray-50 py-20 text-center">
      <h2 className="mb-4 text-3xl font-bold">Ready to Get Started?</h2>
      <p className="text-muted-foreground mb-8 text-lg">
        Join thousands of companies using HRMS
      </p>
      <Link to="/signup">
        <InteractiveHoverButton className="bg-black text-white">
          Start Free Trial
        </InteractiveHoverButton>
      </Link>
    </section>
  );
}
```

### Example 2: Card with Action Button

```tsx
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export function FeatureCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Employee Management</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Manage your team efficiently with our tools.</p>
      </CardContent>
      <CardFooter>
        <InteractiveHoverButton className="bg-blue-600 text-white">
          Learn More
        </InteractiveHoverButton>
      </CardFooter>
    </Card>
  );
}
```

### Example 3: Form Submit Button

```tsx
export function ContactForm() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input type="text" placeholder="Name" className="w-full rounded border p-2" />
      <input type="email" placeholder="Email" className="w-full rounded border p-2" />
      
      <InteractiveHoverButton 
        type="submit"
        className="bg-green-600 text-white hover:bg-green-700"
      >
        Send Message
      </InteractiveHoverButton>
    </form>
  );
}
```

### Example 4: Multiple Buttons

```tsx
export function ActionButtons() {
  return (
    <div className="flex gap-4">
      <Link to="/login">
        <InteractiveHoverButton className="bg-black text-white">
          Log In
        </InteractiveHoverButton>
      </Link>
      
      <Link to="/signup">
        <InteractiveHoverButton className="border-2 border-black bg-transparent text-black hover:bg-black hover:text-white">
          Sign Up
        </InteractiveHoverButton>
      </Link>
    </div>
  );
}
```

## Customizing the Component

### Location
The component is located at: `src/components/ui/interactive-hover-button.tsx`

### Modify Default Styles

```tsx
export function InteractiveHoverButton({
  children,
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        // Change default styles here:
        "group relative w-auto cursor-pointer overflow-hidden rounded-full border p-2 px-6 text-center font-semibold",
        "bg-black text-white", // Add default colors
        className
      )}
      {...props}
    >
      {/* ... rest of component */}
    </button>
  );
}
```

### Change Animation Timing

```tsx
// Find these classes in the component:
"transition-all duration-300"

// Change to:
"transition-all duration-500" // Slower
"transition-all duration-150" // Faster
```

### Change Indicator Style

```tsx
// Find this line:
<div className="h-2 w-2 rounded-full ..."></div>

// Change to square:
<div className="h-2 w-2 rounded-sm ..."></div>

// Change size:
<div className="h-3 w-3 rounded-full ..."></div>
```

## Accessibility

The button component is fully accessible:
- ✅ Uses semantic `<button>` element
- ✅ Supports all standard button attributes
- ✅ Works with keyboard navigation (Tab, Enter, Space)
- ✅ Maintains focus states
- ✅ Screen reader compatible

### Add ARIA Labels

```tsx
<InteractiveHoverButton 
  aria-label="Navigate to login page"
  title="Go to Login"
>
  Go to Login
</InteractiveHoverButton>
```

## Performance Tips

1. **Avoid nesting interactive elements**
   ```tsx
   ❌ Bad: <button><InteractiveHoverButton>Text</InteractiveHoverButton></button>
   ✅ Good: <InteractiveHoverButton>Text</InteractiveHoverButton>
   ```

2. **Use with Link correctly**
   ```tsx
   ✅ Good: Wrap button with Link
   <Link to="/page">
     <InteractiveHoverButton>Go</InteractiveHoverButton>
   </Link>
   ```

3. **Don't use too many on one page**
   - Limit to 1-3 interactive buttons per view
   - Use regular buttons for secondary actions

## Common Issues

### Issue 1: Animation Not Working

**Cause:** CSS transitions might be disabled globally

**Solution:**
```tsx
// Make sure these classes are present:
transition-all duration-300 group-hover:...
```

### Issue 2: Button Too Wide/Narrow

**Solution:**
```tsx
// Adjust padding
<InteractiveHoverButton className="px-8"> {/* or any value */}
```

### Issue 3: Text Overflow

**Solution:**
```tsx
<InteractiveHoverButton className="whitespace-nowrap">
  Longer Button Text
</InteractiveHoverButton>
```

### Issue 4: Arrow Not Showing

**Cause:** Lucide icon not imported

**Solution:**
Check that `ArrowRight` is imported in the component file:
```tsx
import { ArrowRight } from "lucide-react"
```

## Testing

### Visual Test Checklist

- [ ] Button appears with correct styling
- [ ] Hover animation works smoothly
- [ ] Text slides out properly
- [ ] Arrow slides in from the right
- [ ] No layout shift during animation
- [ ] Works on mobile (touch devices)
- [ ] Keyboard navigation works (Tab + Enter)

### Browser Compatibility

| Browser | Support |
|---------|---------|
| Chrome  | ✅ Full |
| Firefox | ✅ Full |
| Safari  | ✅ Full |
| Edge    | ✅ Full |
| Mobile  | ✅ Full |

## Comparison with Standard Button

| Feature | Standard Button | Interactive Hover Button |
|---------|----------------|-------------------------|
| Animation | ❌ None | ✅ Smooth slide effect |
| Visual Interest | ⚠️ Basic | ✅ High |
| File Size | ✅ Smaller | ⚠️ Slightly larger |
| Use Case | General | CTA, Hero sections |
| Accessibility | ✅ Full | ✅ Full |

## When to Use

### ✅ Use Interactive Hover Button For:
- Primary call-to-action buttons
- Hero section buttons
- Important navigation links
- Form submit buttons (main forms)
- Landing page conversions

### ❌ Don't Use For:
- Small inline actions
- Repetitive list items
- Secondary/tertiary actions
- Dense UI sections
- Form cancel buttons

## Summary

✅ Installed and active in App.tsx
✅ Smooth hover animation with arrow
✅ Fully customizable styling
✅ Works with TanStack Router Link
✅ Accessible and performant

**Current Implementation:**
- Location: Home page (App.tsx)
- Button: "Go to Login"
- Style: Black background with white text
- Effect: Smooth slide-in arrow on hover

---

Enjoy your interactive button! 🚀