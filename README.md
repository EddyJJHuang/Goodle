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