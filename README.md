Everyone Googles for information, but who Goodles for love? Introducing Goodle—The Gemini-powered search engine for pets.


### Directory Structure
- **`src/api`**: Contains all network logic.
  - `client.ts`: Axial instance with interceptors (handles Auth tokens automatically).
  - `services/`: API endpoints grouped by domain (e.g., `auth.ts`, `pets.ts`).
- **`src/types/api.ts`**: Defines the standard API response structure (`ApiResponse<T>`).
- **`src/context`**: Global state (e.g., `AuthContext` for user session).

### Environment Variables
Configure your `.env` file with:
```bash
VITE_API_BASE_URL=http://localhost:3000/api
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

---

## 部署 (Deployment)

### 前置条件
- Node.js 18+
- 后端服务已部署并可访问（或本地运行在 3000 端口）

### 1. 环境变量
复制环境变量示例并按环境修改：
```bash
cp .env.example .env
```
- **开发**：`VITE_API_BASE_URL=http://localhost:3000/api`（与 Vite 代理一致即可）
- **生产**：改为真实后端地址，如 `VITE_API_BASE_URL=https://api.yourdomain.com/api`

### 2. 构建前端
```bash
npm install
npm run build
```
产物在 `dist/` 目录，可部署到任意静态托管。

### 3. 本地预览构建结果
```bash
npm run preview
# 默认 http://localhost:4173，用于验证生产构建
```

### 4. 部署方式示例
- **Vercel / Netlify**：连接仓库后，Build 命令填 `npm run build`，输出目录填 `dist`，在项目设置中配置 `VITE_API_BASE_URL` 为生产 API 地址。
- **自有服务器 / Nginx**：将 `dist/` 内容放到站点根目录，并配置 SPA 回退（所有路径回退到 `index.html`）。
- **Docker**：在项目根目录执行 `docker build -t goodle-front .`，运行容器后访问对应端口即可（见下方 Docker 说明）。

### 5. 后端说明
当前仓库仅包含前端。规范中的后端（如流浪狗上报、寻狗、地图、匹配通知等）需在 `backend/` 或独立服务中实现，并保证 [docs/API.md](docs/API.md) 中的接口可用。部署时确保前端 `VITE_API_BASE_URL` 指向该后端。