import api from './api';
import type { Pet, PetCreate } from '../types';

export const getPets = async (): Promise<Pet[]> => {
  const response = await api.get('/pets/');
  return response.data;
};

export const getPet = async (petId: string): Promise<Pet> => {
  const response = await api.get(`/pets/${petId}`);
  return response.data;
};

export const createPet = async (petData: PetCreate): Promise<Pet> => {
  const response = await api.post('/pets/', petData);
  return response.data;
};
