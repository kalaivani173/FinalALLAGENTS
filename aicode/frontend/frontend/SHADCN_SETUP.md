# shadcn/ui + Tailwind CSS Setup Guide

## ✅ Configuration Complete

Your project is fully configured with:
- **Tailwind CSS** v3.3.6
- **shadcn/ui** components (using Radix UI primitives)
- **PostCSS** with Autoprefixer
- **CSS Variables** for theming

## 📦 Installed Dependencies

### Core Dependencies
- `tailwindcss` - Utility-first CSS framework
- `autoprefixer` - CSS vendor prefixing
- `postcss` - CSS processing

### shadcn/ui Dependencies
- `@radix-ui/react-*` - Headless UI primitives
- `class-variance-authority` - Component variants
- `clsx` - Conditional className utility
- `tailwind-merge` - Merge Tailwind classes
- `tailwindcss-animate` - Animation utilities
- `lucide-react` - Icon library

## 🎨 Theme Configuration

The project uses CSS variables for theming, defined in `src/index.css`:

- **Light mode** (default)
- **Dark mode** (via `.dark` class)
- Custom color palette with HSL values
- Consistent border radius and spacing

## 📁 Component Structure

All shadcn/ui components are in `src/components/ui/`:

```
components/ui/
├── button.jsx      # Button component with variants
├── input.jsx       # Input field
├── label.jsx       # Form label
├── select.jsx      # Dropdown select
├── tabs.jsx        # Tab navigation
├── table.jsx       # Data table
├── textarea.jsx    # Multi-line input
└── card.jsx        # Card container
```

## 🚀 Usage Example

```jsx
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Title</CardTitle>
      </CardHeader>
      <CardContent>
        <Input placeholder="Enter text..." />
        <Button>Submit</Button>
      </CardContent>
    </Card>
  )
}
```

## 🎯 Tailwind Classes

You can use any Tailwind utility classes:

```jsx
<div className="flex items-center gap-4 p-6 bg-gray-50 rounded-lg">
  <h1 className="text-2xl font-bold text-gray-900">Title</h1>
</div>
```

## 🔧 Customization

### Change Colors
Edit CSS variables in `src/index.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%; /* Change primary color */
  --radius: 0.5rem; /* Change border radius */
}
```

### Add New Components
Follow shadcn/ui patterns:
1. Use Radix UI primitives
2. Apply Tailwind classes
3. Use `cn()` utility for className merging
4. Support variants with `class-variance-authority`

## 📝 Path Aliases

The project uses `@/` alias for imports:

```jsx
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
```

Configured in:
- `vite.config.js` - Vite alias
- `jsconfig.json` - JavaScript path mapping

## ✅ Verification

To verify everything works:

1. **Check Tailwind is processing:**
   - Add `className="bg-blue-500"` to any element
   - Should see blue background

2. **Check shadcn/ui components:**
   - Import and use any component
   - Should render with proper styling

3. **Check animations:**
   - Components should have smooth transitions
   - Hover states should work

## 🐛 Troubleshooting

### Styles not applying?
- Check `src/index.css` is imported in `main.jsx`
- Verify `tailwind.config.js` content paths include your files
- Clear build cache: `rm -rf node_modules/.vite`

### Components not rendering?
- Check all dependencies are installed: `npm install`
- Verify imports use `@/` alias correctly
- Check browser console for errors

### Dark mode not working?
- Add `dark` class to root element
- Verify CSS variables are defined for `.dark`

## 📚 Resources

- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Docs](https://ui.shadcn.com/)
- [Radix UI Docs](https://www.radix-ui.com/)
