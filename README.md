# PixCI - AI Pixel Art Studio

Công cụ chỉnh sửa Pixel Art bằng AI với khả năng encoding/decoding PXVG.

## Cấu trúc dự án

```
PixCI/
├── pixci-web/           # Web application
│   ├── backend/         # FastAPI backend (bao gồm pixci module)
│   │   ├── app/         # FastAPI app
│   │   ├── pixci/       # Core pixci module
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── frontend/        # Next.js frontend
│       ├── app/
│       ├── components/
│       └── package.json
├── pixci_gui.py         # Desktop GUI application
├── llms.txt             # LLM documentation
└── README.md
```

## Tính năng

- **PXVG Encoding/Decoding**: Chuyển đổi ảnh sang/từ định dạng PXVG
- **AI Image Editing**: Chỉnh sửa ảnh bằng AI thông qua text prompts
- **Web Interface**: Giao diện web hiện đại với Next.js
- **RESTful API**: Backend FastAPI mạnh mẽ
- **Desktop GUI**: Ứng dụng desktop với Tkinter

## Quick Start

### Web Application

#### Backend
```bash
cd pixci-web/backend
pip install -r requirements.txt
python main.py
```

API sẽ chạy tại: http://localhost:8000
Docs: http://localhost:8000/api/docs

#### Frontend
```bash
cd pixci-web/frontend
npm install
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

### Desktop GUI
```bash
python pixci_gui.py
```

## Deployment

### Backend (Render)
Xem [pixci-web/backend/DEPLOY.md](pixci-web/backend/DEPLOY.md)

### Frontend (Vercel)
Xem [pixci-web/frontend/DEPLOY.md](pixci-web/frontend/DEPLOY.md)

## Tech Stack

### Backend
- FastAPI
- Uvicorn
- Pillow, OpenCV
- scikit-image
- NumPy, SciPy

### Frontend
- Next.js 16
- React 19
- TailwindCSS 4
- Framer Motion
- Monaco Editor

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Encode Image
```
POST /api/v1/encode
Content-Type: multipart/form-data
```

### Decode PXVG
```
POST /api/v1/decode
Content-Type: application/json
```

## Environment Variables

### Backend
```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app
MAX_UPLOAD_SIZE=10485760
MAX_IMAGE_DIMENSION=512
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Development

### Install dependencies
```bash
# Backend
cd pixci-web/backend
pip install -r requirements.txt

# Frontend
cd pixci-web/frontend
npm install
```

### Run development servers
```bash
# Backend
cd pixci-web/backend
uvicorn app.main:app --reload

# Frontend
cd pixci-web/frontend
npm run dev
```

## Docker

### Backend
```bash
cd pixci-web/backend
docker build -t pixci-backend .
docker run -p 8000:8000 pixci-backend
```

### Full Stack
```bash
cd pixci-web
docker-compose up
```

## License

MIT

## Documentation

- [Backend Deployment](pixci-web/backend/DEPLOY.md)
- [Frontend Deployment](pixci-web/frontend/DEPLOY.md)
- [LLM Documentation](llms.txt)
- [PXVG Workflow](llms-pxvg-workflow.txt)
