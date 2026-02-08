import client from '../client';
import { ApiResponse } from '../../types/api';

interface LoginCredentials {
    email: string;
    password: string;
}

interface RegisterCredentials {
    email: string;
    password: string;
    name: string;
}

interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
}

interface AuthResponse {
    token: string;
    user: User;
}

export const authService = {
    login: (credentials: LoginCredentials) => client.post<AuthResponse>('/auth/login', credentials),
    register: (credentials: RegisterCredentials) => client.post<AuthResponse>('/auth/register', credentials),
    logout: () => client.post<void>('/auth/logout'),
    getCurrentUser: () => client.get<User>('/auth/me'),
};
