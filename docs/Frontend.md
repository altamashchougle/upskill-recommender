# Frontend Architecture

UpskillAI's frontend is built with **React** (Vite) and styled exclusively with **Tailwind CSS**.

## Core Structure
*   `src/components/`: Reusable UI elements.
    *   `common/`: Shared UI (ErrorState, LoadingState).
    *   `dashboard/`: The main results view components.
    *   `onboarding/`: The multi-step career wizard.
*   `src/context/`: Global state management (`AppContext.jsx`).
*   `src/pages/`: Route-level container components.

## State Management
We use a centralized `AppContext` for all global state (User Profile, Recommendations, Filters). The Context automatically synchronizes with `localStorage` to allow users to refresh the page without losing their generated career roadmap.

## Styling
The application uses a dark-mode premium SaaS aesthetic. All styling relies strictly on Tailwind CSS utility classes. Custom animations and dynamic entry effects are powered by `framer-motion`.
