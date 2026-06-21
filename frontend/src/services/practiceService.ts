import api from './api';
import type { Practice, PracticeCreate, Pet } from '../types';

export const registerPractice = async (data: PracticeCreate): Promise<Practice> => {
  const response = await api.post('/practices/', data);
  return response.data;
};

export const getMyPractices = async (): Promise<Practice[]> => {
  const response = await api.get('/practices/my');
  return response.data;
};

export const addPatientToPractice = async (practiceId: string, petId: string): Promise<void> => {
  await api.post(`/practices/${practiceId}/patients/${petId}`);
};

export const getPracticePatients = async (practiceId: string): Promise<Pet[]> => {
  const response = await api.get(`/practices/${practiceId}/patients`);
  return response.data;
};
