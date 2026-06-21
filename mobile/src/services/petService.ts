import apiClient from '../api/client';

export const getPets = async () => {
  const response = await apiClient.get('/pets');
  return response.data;
};

export const getPet = async (id: string) => {
  const response = await apiClient.get(`/pets/${id}`);
  return response.data;
};

export const createPet = async (petData: any) => {
  const response = await apiClient.post('/pets', petData);
  return response.data;
};
