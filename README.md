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
- npm or yarn

### 2. Installation
```bash
npm install
```

### 3. Run Frontend (Development)
```bash
npm run dev
# Server will start at http://localhost:5173
```

---

## 🤝 Backend Development Guide

### 1. Project Setup
- **Frontend Port**: 5173
- **Backend Port**: 3000 (Expected)
- **Proxy**: All requests to `/api/*` are automatically forwarded to `http://localhost:3000`.

### 2. Where to write backend code?
Please create a **new folder** (`backend/` or `server/`) in the root. Do not modify `src/`.

### 3. API Contract
Refer to [docs/API.md](docs/API.md) for the detailed API specification.
