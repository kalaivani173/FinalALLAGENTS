# NPCI AI Agent Frontend

React frontend for the NPCI AI Agent Portal with Admin, Product Owner, and Developer roles.

## Features

- **Admin Portal** with three main tabs:
  - Change Requests: Create and submit change requests
  - Publish Changes: Publish changes to bank endpoints
  - Status Center: Track publication status

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- shadcn/ui components
- React Router

## Setup

1. Install dependencies:
```bash
npm install
```

2. Install additional dependencies for shadcn/ui:
```bash
npm install class-variance-authority tailwindcss-animate
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

## Backend Integration

Make sure the backend server is running on http://localhost:8000

The frontend is configured to proxy API requests to the backend.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/          # shadcn/ui components
│   │   └── AdminPortal.jsx
│   ├── lib/
│   │   ├── api.js      # API integration
│   │   └── utils.js    # Utility functions
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```
