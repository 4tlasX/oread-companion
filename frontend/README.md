# Oread Frontend

Frontend for the Oread AI Companion application.

## SCSS Architecture

The styles are now organized using SCSS with webpack for compilation.

### Directory Structure

```
src/assets/scss/
├── base/
│   ├── _variables.scss  # Colors, fonts, spacing
│   ├── _mixins.scss     # Reusable mixins
│   └── _base.scss       # Global styles
├── layout/
│   └── _layout.scss     # Layout components
├── components/
│   ├── _buttons.scss    # Button styles
│   ├── _forms.scss      # Form elements
│   ├── _tabs.scss       # Tab navigation
│   ├── _toggles.scss    # Toggle switches
│   └── _tags.scss       # Tag selector
└── main.scss            # Main entry point (imports all)
```

## Development

### Install Dependencies

```bash
npm install
```

### Build Styles

**Production build:**
```bash
npm run build
```

**Development with watch mode:**
```bash
npm run dev
# or
npm run watch
```

This will watch for changes in SCSS files and automatically recompile to CSS.

### Output

Compiled CSS is output to: `src/assets/css/styles.css`

## Adding New Styles

1. Create a new partial in the appropriate directory
2. Import it in `main.scss`
3. Run `npm run dev` to watch for changes

### Example: Adding a new component

```scss
// src/assets/scss/components/_modal.scss
.modal {
  background: $card-bg;
  border-radius: $border-radius;
  padding: $spacing-xl;
  // ... more styles
}
```

Then in `main.scss`:
```scss
@import 'components/modal';
```

## Variables

Common variables are defined in `base/_variables.scss`:

- **Colors:** `$primary-color`, `$danger-color`, etc.
- **Spacing:** `$spacing-sm`, `$spacing-md`, etc.
- **Typography:** `$font-family`, `$font-size-base`, etc.
- **Borders:** `$border-radius`, `$border-radius-sm`, etc.

## Mixins

Reusable mixins in `base/_mixins.scss`:

- `@include flex-center` - Center content with flexbox
- `@include mobile { ... }` - Mobile breakpoint
- `@include gradient-purple` - Purple gradient background
- And more...

## Notes

- The original `styles.css` is now generated from SCSS
- Don't edit `styles.css` directly - edit the SCSS files instead
- Run `npm run build` before committing to ensure CSS is up to date
