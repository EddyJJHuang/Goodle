# AI Backend Setup and Testing

## 1. Install dependencies

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements-backend.txt
```

## 2. Configure environment

Create a local env file (gitignored):

```bash
copy .env.local.example .env.local
```

Then edit `.env.local` with your values. The backend auto-loads `.env`, `.env.local`, and `.env.backend.local`.

For local smoke testing without Gemini:

```bash
set AI_MOCK_MODE=1
```

For real Gemini calls:

```bash
set GEMINI_API_KEY=your_key_here
set GEMINI_IMAGE_MODEL=gemini-2.5-flash
set GEMINI_VIDEO_MODEL=gemini-2.5-flash
```

## 3. Run backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

Open Swagger UI:

- `http://localhost:3000/api/docs`

## 4. Test APIs with curl

### Health

```bash
curl http://localhost:3000/api/health
```

### Analyze photo (JSON)

```bash
curl -X POST http://localhost:3000/api/ai/analyze-photo ^
  -H "Content-Type: application/json" ^
  -d "{\"pet_id\":\"pet_001\",\"image_base64\":\"data:image/jpeg;base64,BASE64_IMAGE\"}"
```

### Analyze video (upload)

```bash
curl -X POST http://localhost:3000/api/ai/analyze-video/upload ^
  -F "pet_id=pet_001" ^
  -F "preprocess_seconds=10" ^
  -F "video=@C:/tmp/dog-social.mp4"
```

### Upsert stray report

```bash
curl -X POST http://localhost:3000/api/ai/stray-reports ^
  -H "Content-Type: application/json" ^
  -d "{\"report_id\":\"rep_101\",\"image_base64\":\"data:image/jpeg;base64,BASE64_IMAGE\"}"
```

### Match lost dog

```bash
curl -X POST http://localhost:3000/api/ai/match-lost-dog ^
  -H "Content-Type: application/json" ^
  -d "{\"owner_id\":\"owner_001\",\"notice_image_base64\":\"data:image/jpeg;base64,BASE64_IMAGE\",\"use_db_reports\":true}"
```

### Query notifications

```bash
curl http://localhost:3000/api/ai/notifications
```

## 5. Run automated tests

Tests use `AI_MOCK_MODE=1` and temporary SQLite DB:

```bash
pytest tests/test_ai_routes.py -q
```

## 6. Where to call these APIs in frontend

- `src/pages/PostPet.tsx`: call `aiService.analyzePhoto(...)` after user uploads pet image.
- `src/pages/Matching.tsx`: call `aiService.analyzeVideo(...)` or upload endpoint for behavior tags.
- `src/pages/LostFound.tsx`: call `aiService.upsertStrayReport(...)` and `aiService.matchLostDog(...)`.

The frontend service wrapper is already added at:

- `src/api/services/ai.ts`
