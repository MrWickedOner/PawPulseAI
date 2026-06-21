import apiClient from '../api/client';

export const getHealthData = async (petId: string) => {
  const response = await apiClient.get(`/health/${petId}`);
  return response.data;
};
