Everyone Googles for information, but who Goodles for love? Introducing Goodle—The Gemini-powered search engine for pets.


### Directory Structure
- **`src/api`**: Contains all network logic.
  - `client.ts`: Axial instance with interceptors (handles Auth tokens automatically).
  - `services/`: API endpoints grouped by domain (e.g., `auth.ts`, `pets.ts`).
- **`src/types/api.ts`**: Defines the standard API response structure (`ApiResponse<T>`).
- **`src/context`**: Global state (e.g., `AuthContext` for user session).

### Environment Variables
Create a local env file (gitignored) from the template:
```bash
copy .env.local.example .env.local
```

Then set:
```bash
VITE_API_BASE_URL=http://localhost:3000/api
GEMINI_API_KEY=your_gemini_key_here
```

### Authentication
The `AuthContext` automatically handles JWT storage and injection. Ensure your login endpoint returns:
```json
{
  "token": "jwt_token",
  "user": { "id": "...", "name": "..." }
}
```


## 🚀 Getting Started

### 1. Prerequisites
- Node.js (v18+)
- Python 3.9+
- Gemini API Key

### 2. Installation

**Frontend:**
```bash
npm install
```

**Backend (Python):**
```bash
# Create and activate virtual environment (Python 3.9 recommended)
/usr/bin/python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-backend.txt
```

### 3. Running the Project (Requires 2 Terminals)

**Terminal 1: Backend**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
# Backend runs at http://localhost:8001
```

**Terminal 2: Frontend**
```bash
npm run dev
# Frontend runs at http://localhost:5173
```


## Probabilistic Long-Term Forecasting (New)

A lightweight, model-agnostic forecasting extension now lives in `app/forecasting/`.
It upgrades a point-forecasting backbone to:

- multi-quantile forecasts (`[B, pred_len, D, Q]`)
- split conformal interval calibration (horizon-wise and joint)
- optional adaptive online conformal updates

### Quick demo

```bash
python scripts/forecasting_example.py
```

### Example command patterns

```bash
# 1) Point forecasting only
python scripts/forecasting_example.py

# 2) Quantile forecasting without conformal
python -c "from app.forecasting.pipeline import ForecastConfig; print(ForecastConfig(use_quantile_head=True, use_conformal=False))"

# 3) Quantile + horizon-wise conformal
python -c "from app.forecasting.pipeline import ForecastConfig; print(ForecastConfig(use_quantile_head=True, use_conformal=True, conformal_mode='horizon'))"

# 4) Quantile + adaptive conformal
python -c "from app.forecasting.pipeline import ForecastConfig; print(ForecastConfig(use_quantile_head=True, use_conformal=True, conformal_mode='horizon', adaptive_conformal=True))"
```
