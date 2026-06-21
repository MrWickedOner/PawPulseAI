import api from './api';
import type { HealthData } from '../types';

export const getHealthData = async (petId: string): Promise<HealthData[]> => {
  const response = await api.get(`/health/${petId}`);
  return response.data;
};
