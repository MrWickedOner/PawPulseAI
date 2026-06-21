import apiClient from '../api/client';
import * as SecureStore from 'expo-secure-store';

export const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  
  const response = await apiClient.post('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  if (response.data.access_token) {
    await SecureStore.setItemAsync('userToken', response.data.access_token);
  }
  
  return response.data;
};

export const logout = async () => {
  await SecureStore.deleteItemAsync('userToken');
};

export const getMe = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};
