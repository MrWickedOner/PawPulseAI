import api from './api';
import type { AnomalyAlert } from '../types';

export const getAlerts = async (petId: string): Promise<AnomalyAlert[]> => {
  const response = await api.get(`/anomalies`, { params: { pet_id: petId } });
  return response.data;
};

export const getAnomalies = async (): Promise<AnomalyAlert[]> => {
  const response = await api.get('/anomalies');
  return response.data;
};

export const acknowledgeAlert = async (alertId: string): Promise<void> => {
  await api.patch(`/anomalies/${alertId}/acknowledge`);
};

export const dismissAlert = async (alertId: string): Promise<void> => {
  await api.patch(`/anomalies/${alertId}/dismiss`);
};
