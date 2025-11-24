# Components Readme

## Layout
- Description: Global shell that wraps all routes, contains navigation, toast system, footer, and mobile menu.
- Key files: `src/components/Layout.tsx`
- Responsibilities:
  - Provides HashRouter-compatible layout wrappers.
  - Manages toasts and route-loading indicator.
  - Hosts navigation links (Home, Search, Add Firm) and contact button.

## FirmCard
- Description: Card component that renders firm info from ANISA table.
- Key files: `src/components/FirmCard.tsx`
- Responsibilities:
  - Displays city/district, services, rating, contact buttons.
  - Handles navigation to `/firm/:id` and fallback images.
  - Enforces WhatsApp action button availability.

## Usage Notes
- All components are React functional components using TypeScript.
- Styling is Tailwind-first, with className-based design and fallback CSS in `src/index.css`.
- Components expect data shaped by `src/types.ts`, particularly `AnisaRecord`.
- To extend components, ensure new props are typed and update associated hooks/services for data.
