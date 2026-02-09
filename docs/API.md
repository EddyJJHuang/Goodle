# Goodle API Documentation

This document outlines the API contract expected by the Goodle frontend.
Base URL: `http://localhost:3000/api` (configurable via `VITE_API_BASE_URL`)

## Global Response Format

All API responses should follow this structure:

```typescript
interface ApiResponse<T> {
  code: number;      // 200 for success, 4xx/5xx for errors
  message: string;   // "success" or error message
  data: T;           // The actual payload
}
```

## Authentication

**Headers**: `Authorization: Bearer <token>` (Required for protected routes)

### 1. Login
- **Endpoint**: `POST /auth/login`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response (`data`)**:
  ```json
  {
    "token": "jwt_token_string",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "user@example.com",
      "avatar": "https://..."
    }
  }
  ```

### 2. Register
- **Endpoint**: `POST /auth/register`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }
  ```
- **Response**: Same as Login.

### 3. Get Current User
- **Endpoint**: `GET /auth/me`
- **Response**: User object only.

---

## Pets Service

### 1. Get Pets List
- **Endpoint**: `GET /pets`
- **Query Params**: `page`, `limit`, `type`, `status`
- **Response**:
  ```json
  {
    "items": [ { ...pet_object } ],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
  ```

### 2. Get Pet Details
- **Endpoint**: `GET /pets/:id`
- **Response**: Single Pet object.

### 3. Create Pet
- **Endpoint**: `POST /pets`
- **Body**: Pet object (without ID).
- **Response**: Created Pet object.

---

## 流浪狗上报 (Stray Report / Report Now)

- **Endpoint**: `POST /api/stray-report`
- **Body**: `multipart/form-data` — 照片 `photo`（可选）、文字描述 `description`、GPS 坐标 `lat`/`lng`、上报时间 `report_time`（ISO 或 datetime-local 格式）。服务端将坐标逆解析为地址（Geopy + Nominatim），照片存于 `uploads/stray/`。
- **Response**: 创建记录，含 `address`（逆解析结果）。

---

## 寻狗发布 (Lost Dog)

- **Endpoint**: `POST /api/lost-dog`
- **Body**: `multipart/form-data` — 狗狗照片 `photo`（可选）、品种 `breed`、特征描述 `description`、走失时间 `lost_time`（ISO）、走失地点 `address`、GPS `lat`/`lng`（可选）、联系方式 `contact`。
- **Response**: 创建记录，默认状态为待寻找（`pending`）。
- **状态更新**: `PATCH /api/lost-dog/:id/status?status=found` — 已找到时更新为 `found`。

---

## 地图数据接口 (Map Data)

用于地图标记点列表，支持**范围查询**（中心点 + 半径）与**时间过滤**（最近 N 天）。

### 1. 获取流浪狗地图标记点
- **Endpoint**: `GET /api/map/stray`
- **Query Params**（均可选）:
  - `lat` (float): 中心点纬度
  - `lng` (float): 中心点经度
  - `radius` (float): 半径（米），与 lat/lng 一起使用时只返回该范围内的数据
  - `days` (int): 只返回最近 N 天的上报数据
- **Response**: `data` 为数组，每项含 `id`, `description`, `lat`, `lng`, `address`, `report_time`, `photo_path` 等。

### 2. 获取寻狗地图标记点
- **Endpoint**: `GET /api/map/lost`
- **Query Params**: 同 `/api/map/stray`（`lat`, `lng`, `radius`, `days`）
- **Response**: `data` 为数组，每项含 `id`, `breed`, `description`, `lost_time`, `lat`, `lng`, `address`, `contact`, `photo_path`, `status` 等；仅含状态为待寻找的记录。
