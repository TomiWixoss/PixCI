# PixCI Backend

FastAPI backend for PixCI - AI-powered pixel art editor.

## Features

- **PXVG Encoding/Decoding**: Convert images to/from PXVG format
- **Image Processing**: Smart encoding with auto-detection
- **RESTful API**: Clean API design with FastAPI
- **Docker Support**: Easy deployment with Docker
- **CORS Enabled**: Ready for frontend integration

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/          # API endpoints
│   ├── core/            # Core configs
│   ├── models/          # Pydantic models
│   └── services/        # Business logic
├── pixci/               # Core pixci module
│   └── core/
│       ├── pxvg_engine.py
│       └── ...
├── logs/                # Application logs
├── uploads/             # Temporary uploads
├── temp/                # Temporary files
├── Dockerfile
├── requirements.txt
└── main.py
```

## Quick Start

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python main.py
# or
uvicorn app.main:app --reload
```

3. **Access API**:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/api/v1/health

### Docker

```bash
# Build
docker build -t pixci-backend .

# Run
docker run -p 8000:8000 pixci-backend
```

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
- file: Image file (PNG, JPG, GIF, WebP)
- block_size: int (default: 1)
- auto_detect: bool (default: true)

Response:
{
  "pxvg_code": "<pxvg>...</pxvg>",
  "message": "Encoded successfully"
}
```

### Decode PXVG to Image
```
POST /api/v1/decode
Content-Type: application/json

Body:
{
  "pxvg_code": "<pxvg>...</pxvg>",
  "scale": 1
}

Response:
{
  "image_base64": "data:image/png;base64,...",
  "message": "Decoded successfully"
}
```

## Environment Variables

```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=https://your-frontend.vercel.app
MAX_UPLOAD_SIZE=10485760
MAX_IMAGE_DIMENSION=512
```

## Deployment

See [DEPLOY.md](./DEPLOY.md) for detailed deployment instructions.

Quick deploy to Render:
1. Push to GitHub
2. Connect to Render
3. Deploy with `render.yaml`

## Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black .
```

### Lint
```bash
flake8 .
```

## Tech Stack

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pillow**: Image processing
- **OpenCV**: Computer vision
- **scikit-image**: Image analysis
- **NumPy/SciPy**: Numerical computing

## License

MIT
