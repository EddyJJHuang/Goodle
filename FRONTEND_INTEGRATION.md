# 前端集成后端 API 指南

## 📋 后端 API 状态

- **后端地址**: http://127.0.0.1:8001
- **API 前缀**: `/api`
- **完整 API 地址**: http://127.0.0.1:8001/api
- **API 文档**: http://127.0.0.1:8001/docs

## ✅ 已完成配置

### 环境变量
`.env` 文件已配置：
```env
VITE_API_BASE_URL=http://127.0.0.1:8001/api
```

### API Client
[src/api/client.ts](src/api/client.ts) 已配置好：
- ✅ 自动添加 Authorization header
- ✅ Token 从 localStorage 获取
- ✅ 统一的错误处理

---

## 🔧 需要前端确认的事项

### 1. Token 存储和使用

**登录成功后需要保存 Token**：

```typescript
// 在登录成功后
const response = await authService.login({ email, password });

// 后端返回格式
// {
//   "code": 200,
//   "message": "Login successful",
//   "data": {
//     "token": "eyJhbGci...",
//     "user": { ... }
//   }
// }

// 保存 token 到 localStorage
localStorage.setItem('token', response.data.token);

// 保存用户信息（可选）
localStorage.setItem('user', JSON.stringify(response.data.user));
```

### 2. API 响应格式

**所有 API 都遵循统一格式**：

```typescript
interface ApiResponse<T> {
  code: number;      // 200 成功，4xx/5xx 错误
  message: string;   // "success" 或错误信息
  data: T;           // 实际数据
}
```

**示例**：

```typescript
// 登录响应
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "token": "jwt_token",
    "user": { ... }
  }
}

// 获取宠物列表响应
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 20,
    "page": 1,
    "pageSize": 10
  }
}
```

### 3. 需要认证的接口

以下接口需要在 Header 中携带 Token：
```
Authorization: Bearer {token}
```

**需要认证的接口**：
- `GET /api/auth/me` - 获取当前用户
- `GET /api/pets` - 获取宠物列表
- `POST /api/pets` - 创建宠物
- `PUT /api/pets/{id}` - 更新宠物
- `DELETE /api/pets/{id}` - 删除宠物
- `GET /api/matches` - 获取推荐
- `POST /api/swipe` - Swipe 操作
- `GET /api/matches/list` - 获取匹配列表

**不需要认证的接口**：
- `POST /api/auth/login` - 登录
- `POST /api/auth/register` - 注册
- `GET /health` - 健康检查
- `GET /` - 根路径

---

## 🐛 常见问题排查

### 问题 1: 403 Forbidden 错误

**原因**：Token 未正确发送到后端

**检查**：
1. Token 是否保存到 localStorage？
   ```javascript
   console.log(localStorage.getItem('token'));
   ```

2. API Client 是否正确添加 Header？
   ```typescript
   // src/api/client.ts 中的 request interceptor
   const token = localStorage.getItem('token');
   if (token && config.headers) {
     config.headers.Authorization = `Bearer ${token}`;
   }
   ```

3. 检查网络请求：
   - 打开浏览器开发者工具 → Network
   - 查看请求的 Headers
   - 确认有 `Authorization: Bearer xxx`

### 问题 2: CORS 错误

**后端已配置 CORS**，允许的源：
```python
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
```

如果前端使用其他端口，需要更新后端配置：
```python
# backend/app/core/config.py
CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:YOUR_PORT"]
```

### 问题 3: 数据格式不匹配

**后端返回的 user.id 是字符串类型**：
```typescript
interface User {
  id: string;  // ← 注意是 string
  name: string;
  email: string;
  avatar: string | null;
}
```

**宠物 ID 是数字类型**：
```typescript
interface Pet {
  id: number;  // ← 注意是 number
  name: string;
  // ...
}
```

---

## 📝 完整的登录流程示例

```typescript
// 1. 登录
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await authService.login({ email, password });

    // 2. 保存 token
    localStorage.setItem('token', response.data.token);

    // 3. 保存用户信息（可选）
    localStorage.setItem('user', JSON.stringify(response.data.user));

    // 4. 跳转到主页或更新状态
    navigate('/home');

  } catch (error) {
    console.error('Login failed:', error);
  }
};

// 5. 后续请求会自动携带 token（通过 interceptor）
const loadPets = async () => {
  const response = await petService.getPets({ page: 1, limit: 10 });
  // 成功获取数据
};
```

---

## 🧪 测试账号

```
Email: alice@example.com
Password: password123

其他账号: bob, carol, david, emma @example.com
所有密码: password123
```

---

## 📚 API 端点快速参考

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取当前用户 🔒

### 宠物管理
- `GET /api/pets?page=1&limit=10` - 获取列表 🔒
- `GET /api/pets/{id}` - 获取详情 🔒
- `POST /api/pets` - 创建宠物 🔒
- `PUT /api/pets/{id}` - 更新宠物 🔒
- `DELETE /api/pets/{id}` - 删除宠物 🔒

### 匹配系统
- `GET /api/matches?pet_id={id}&limit=10` - 获取推荐 🔒
- `POST /api/swipe` - Swipe 操作 🔒
- `GET /api/matches/list?pet_id={id}` - 获取匹配列表 🔒

🔒 = 需要 Token 认证

---

## 🔗 相关文档

- **API 详细文档**: [docs/API.md](docs/API.md)
- **后端 README**: [backend/README.md](backend/README.md)
- **Swagger UI**: http://127.0.0.1:8001/docs （可在线测试）

---

## ✅ 集成检查清单

- [ ] 确认 `.env` 配置正确
- [ ] 登录成功后保存 token 到 localStorage
- [ ] API Client 的 interceptor 正确添加 Authorization header
- [ ] 测试登录功能
- [ ] 测试需要认证的接口（如获取宠物列表）
- [ ] 处理 401/403 错误（token 过期或无效时跳转到登录页）
- [ ] 处理 ApiResponse 格式（访问 response.data 获取实际数据）

---

有问题随时查看 Swagger UI 文档：http://127.0.0.1:8001/docs
