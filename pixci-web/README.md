# PixCI Web - Full Stack Application

Enterprise-grade web application for pixel art conversion using PXVG format.

## Architecture

```
pixci-web/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration & utilities
│   │   ├── models/   # Data models
│   │   └── services/ # Business logic
│   └── requirements.txt
└── frontend/         # Next.js TypeScript frontend
    ├── app/          # Next.js app router
    ├── components/   # React components
    ├── lib/          # Utilities & hooks
    └── package.json
```

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Backend runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/api/docs`

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at: `http://localhost:3000`

## Features

### Backend (FastAPI)
- ✅ RESTful API with OpenAPI docs
- ✅ Image to PXVG encoding
- ✅ PXVG to Image decoding
- ✅ File upload handling
- ✅ Input validation (Pydantic)
- ✅ Error handling & logging
- ✅ CORS support
- ✅ Environment-based config

### Frontend (Next.js)
- ✅ Modern React with TypeScript
- ✅ Responsive UI with Tailwind CSS
- ✅ Drag & drop file upload
- ✅ Monaco code editor
- ✅ Real-time preview
- ✅ State management (Zustand)
- ✅ API integration (React Query)
- ✅ Toast notifications

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Image Processing**: Pillow
- **Validation**: Pydantic
- **Server**: Uvicorn

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Data Fetching**: TanStack Query
- **HTTP**: Axios
- **Editor**: Monaco Editor

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Encode Image to PXVG
```
POST /api/v1/encode
Content-Type: multipart/form-data

Parameters:
- file: Image file
- block_size: int (1-16)
- auto_detect: bool
```

### Decode PXVG to Image
```
POST /api/v1/decode
Content-Type: application/json

Body:
{
  "pxvg_code": "<pxvg>...</pxvg>",
  "scale": 10
}
```

## Development

### Backend Development
```bash
cd backend
python run.py  # Auto-reload enabled
```

### Frontend Development
```bash
cd frontend
npm run dev  # Hot reload enabled
```

### Run Both Simultaneously
```bash
# Terminal 1
cd backend && python run.py

# Terminal 2
cd frontend && npm run dev
```

## Production Deployment

### Backend
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
npm run start
```

### Docker Compose
```bash
docker-compose up -d
```

## Environment Variables

### Backend (.env)
```env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000
MAX_UPLOAD_SIZE=10485760
MAX_IMAGE_DIMENSION=512
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Project Structure

### Backend
- `app/api/` - API route handlers
- `app/core/` - Config, logging, exceptions
- `app/models/` - Pydantic schemas
- `app/services/` - Business logic

### Frontend
- `app/` - Next.js pages & layouts
- `components/` - React components
- `lib/api/` - API client & services
- `lib/hooks/` - Custom React hooks
- `lib/store/` - Zustand state management

## License

MIT License

## Contributors

Built with ❤️ for the pixel art community
