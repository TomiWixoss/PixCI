# PixCI Web Frontend

Enterprise-grade Next.js frontend for pixel art conversion using PXVG format.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Code Editor**: Monaco Editor
- **File Upload**: React Dropzone
- **Notifications**: React Hot Toast
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Main page with tabs
│   └── globals.css          # Global styles
├── components/
│   ├── features/
│   │   ├── EncodeTab.tsx    # Image → PXVG tab
│   │   ├── DecodeTab.tsx    # PXVG → Image tab
│   │   ├── ImageUploader.tsx # Drag & drop uploader
│   │   └── CodeEditor.tsx   # Monaco code editor
│   ├── ui/
│   │   ├── Button.tsx       # Reusable button
│   │   ├── Input.tsx        # Reusable input
│   │   └── Card.tsx         # Reusable card
│   └── providers/
│       ├── QueryProvider.tsx # React Query setup
│       └── ToastProvider.tsx # Toast notifications
├── lib/
│   ├── api/
│   │   ├── client.ts        # Axios client with interceptors
│   │   ├── services.ts      # API service functions
│   │   └── types.ts         # TypeScript types
│   ├── hooks/
│   │   ├── useEncode.ts     # Encode mutation hook
│   │   └── useDecode.ts     # Decode mutation hook
│   ├── store/
│   │   └── useAppStore.ts   # Zustand global state
│   └── utils.ts             # Utility functions
└── public/                  # Static assets
```

## Features

### Encode Tab (Image → PXVG)
- ✅ Drag & drop image upload
- ✅ File validation (PNG, JPG, GIF)
- ✅ Image preview
- ✅ Configurable block size
- ✅ Auto-detect block size
- ✅ Real-time PXVG code display
- ✅ Syntax highlighting
- ✅ Copy to clipboard
- ✅ Download PXVG file

### Decode Tab (PXVG → Image)
- ✅ Monaco code editor for PXVG input
- ✅ Syntax highlighting
- ✅ Configurable scale factor
- ✅ Real-time image preview
- ✅ Download PNG image
- ✅ Pixelated rendering

### Global Features
- ✅ Responsive design
- ✅ Dark/Light theme support
- ✅ Loading states
- ✅ Error handling
- ✅ Toast notifications
- ✅ Persistent settings (localStorage)
- ✅ Type-safe API calls

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

3. **Run development server:**
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=PixCI Web
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler
```

## API Integration

The frontend communicates with the FastAPI backend through:

- **Encode**: `POST /api/v1/encode` (multipart/form-data)
- **Decode**: `POST /api/v1/decode` (application/json)
- **Health**: `GET /api/v1/health`

## State Management

### Zustand Store
- Encode settings (block size, auto-detect)
- Decode settings (scale)
- Current PXVG code
- Current image
- Active tab

### React Query
- Server state caching
- Automatic refetching
- Optimistic updates
- Error handling

## Styling

Tailwind CSS with custom utilities:
- Responsive breakpoints
- Custom animations
- Gradient backgrounds
- Shadow utilities

## Production Build

```bash
npm run build
npm run start
```

Or with Docker:
```bash
docker build -t pixci-frontend .
docker run -p 3000:3000 pixci-frontend
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
