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
