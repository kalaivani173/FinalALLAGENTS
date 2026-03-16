# Frontend Setup Guide

## Quick Start

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Features Implemented

### Admin Portal

#### Tab 1: Change Requests
- ✅ API name search with autocomplete (ReqPay, ReqRegMob, ReqOtp, ReqChkTxn, ReqValAdd, ReqBalEnq, ReqBalChk)
- ✅ Change type dropdown (Api Addition, Field Addition, Field value changes)
- ✅ Description textarea
- ✅ Dump log file upload (optional)
- ✅ Submit button with API integration

#### Tab 2: Publish Changes
- ✅ Bank end URL input
- ✅ Manifest file upload
- ✅ Description textarea
- ✅ Publish button

#### Tab 3: Status Center
- ✅ Table displaying:
  - Org ID
  - Bank Name
  - Published Date
  - Status (with icons and colors)
  - Last Update

## API Integration

The frontend is configured to connect to the backend at `http://localhost:8000`.

### Endpoints Used:
- `POST /agent/artifact/upload` - Upload dump log
- `POST /agent/change/analyze` - Analyze change request
- `POST /agent/change/patch` - Generate patch
- `GET /health` - Health check

## Styling

- **Tailwind CSS** for utility-first styling
- **shadcn/ui** components for consistent UI
- Responsive design
- Modern, clean interface

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   │   ├── button.jsx
│   │   │   ├── input.jsx
│   │   │   ├── select.jsx
│   │   │   ├── tabs.jsx
│   │   │   ├── table.jsx
│   │   │   └── ...
│   │   └── AdminPortal.jsx  # Main admin component
│   ├── lib/
│   │   ├── api.js           # API client
│   │   └── utils.js         # Utility functions
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Troubleshooting

### Port 3000 already in use
```bash
# Use a different port
npm run dev -- --port 3001
```

### Backend not responding
- Ensure backend is running on http://localhost:8000
- Check CORS settings if needed
- Verify API endpoints in `src/lib/api.js`

### Build for production
```bash
npm run build
```

The built files will be in the `dist` directory.
