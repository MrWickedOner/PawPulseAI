import api from './api';
import type { Token, User, UserCreate } from '../types';

export const login = async (username: string, password: string): Promise<Token> => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  
  const response = await api.post('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const register = async (userData: UserCreate): Promise<User> => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

export const getMe = async (): Promise<User> => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
};
