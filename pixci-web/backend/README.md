# PixCI Web Backend

Enterprise-grade FastAPI backend for pixel art conversion using PXVG format.

## Features

- 🚀 FastAPI with async support
- 📝 Comprehensive API documentation (Swagger/ReDoc)
- 🔒 Input validation with Pydantic
- 📊 Structured logging
- 🎨 Image to PXVG encoding
- 🖼️ PXVG to Image decoding
- 🔄 CORS support
- 📁 File upload handling
- ⚙️ Environment-based configuration

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── encode.py      # Image → PXVG endpoints
│   │       ├── decode.py      # PXVG → Image endpoints
│   │       └── health.py      # Health check
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── logging.py         # Logging setup
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── file_service.py    # File operations
│   │   └── pixci_service.py   # PixCI integration
│   └── main.py                # FastAPI app
├── logs/                      # Application logs
├── uploads/                   # Uploaded files
├── temp/                      # Temporary files
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── run.py                     # Development server
```

## Setup

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run development server:**
```bash
python run.py
```

Server will start at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

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
- file: Image file (PNG, JPG, GIF)
- block_size: int (1-16, default: 1)
- auto_detect: bool (default: false)
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

## Configuration

Environment variables (`.env`):

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000

# Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif

# Processing
MAX_IMAGE_DIMENSION=512
```

## Development

Run with auto-reload:
```bash
python run.py
```

Run tests:
```bash
pytest
```

## Production Deployment

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

Or with Docker:
```bash
docker build -t pixci-backend .
docker run -p 8000:8000 pixci-backend
```
