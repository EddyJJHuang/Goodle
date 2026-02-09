import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { ApiResponse } from '../types/api';

// Create Axios instance
const client: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // TODO: Add token to headers if available
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor
client.interceptors.response.use(
  (response: AxiosResponse) => {
    // Return direct data from response
    return response.data;
  },
  (error) => {
    // Handle global errors
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // TODO: redirect to login
          console.error('Unauthorized access');
          break;
        case 403:
          console.error('Access forbidden');
          break;
        case 500:
          console.error('Server error');
          break;
        default:
          console.error('An error occurred');
      }
    } else if (error.request) {
        console.error('No response received:', error.request);
    } else {
        console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// Generic GET method
export const get = <T>(url: string, params?: object): Promise<ApiResponse<T>> => {
  return client.get(url, { params });
};

// Generic POST method
export const post = <T>(url: string, data?: object): Promise<ApiResponse<T>> => {
  return client.post(url, data);
};

// Generic PUT method
export const put = <T>(url: string, data?: object): Promise<ApiResponse<T>> => {
  return client.put(url, data);
};

// Generic DELETE method
export const del = <T>(url: string): Promise<ApiResponse<T>> => {
  return client.delete(url);
};

export default client;
