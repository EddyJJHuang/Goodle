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

## AI Service

### 1. Analyze Pet Photo (Feature 1a)
- **Endpoint**: `POST /ai/analyze-photo`
- **Body**:
  ```json
  {
    "pet_id": "pet_123",
    "image_base64": "data:image/jpeg;base64,..."
  }
  ```
  or
  ```json
  {
    "pet_id": "pet_123",
    "image_path": "C:/tmp/dog.jpg"
  }
  ```
- **Response (`data`)**:
  ```json
  {
    "breed": "mixed (labrador + border collie)",
    "size": "medium",
    "age_group": "adult",
    "appearance_tags": ["short_coat", "black_white"],
    "personality_guess": "friendly and energetic"
  }
  ```
- **Persistence**: Writes JSON into `pets.aitags`.

### 2. Analyze Pet Video (Feature 1b)
- **Endpoint**: `POST /ai/analyze-video`
- **Body**:
  ```json
  {
    "pet_id": "pet_123",
    "video_path": "C:/tmp/dog-social.mp4",
    "preprocess_seconds": 10
  }
  ```
- **Response (`data`)**:
  ```json
  {
    "activity_level": 7.2,
    "approach_speed": 6.8,
    "emotional_stability": 7.9,
    "play_preference": "chase",
    "body_language_score": 7.1
  }
  ```
- **Persistence**: Inserts into `pet_dynamic_info`.

### 3. Match Lost Dog (Feature 2b)
- **Endpoint**: `POST /ai/match-lost-dog`
- **Body**:
  ```json
  {
    "owner_id": "owner_001",
    "notice_image_base64": "data:image/jpeg;base64,...",
    "lost_at": "2026-02-09T10:00:00",
    "location": { "latitude": 31.23, "longitude": 121.47 },
    "use_db_reports": true
  }
  ```
- **Response (`data`)**:
  ```json
  {
    "is_match": true,
    "similarity_score": 82.5,
    "matched_report_ids": ["rep_101", "rep_102"],
    "candidate_count": 12
  }
  ```
- **Behavior**:
  - Candidate set = DB reports + request candidate reports.
  - Spatiotemporal filter: distance and time window.
  - Similarity threshold default: 70.
  - If matched and `owner_id` exists, notification is persisted.

### 4. Support Endpoints
- `POST /ai/stray-reports`: upsert stray report candidates.
- `GET /ai/stray-reports`: list candidate reports.
- `GET /ai/notifications`: list match notifications.
