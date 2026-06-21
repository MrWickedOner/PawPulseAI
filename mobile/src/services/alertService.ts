import apiClient from '../api/client';

export const getAlerts = async (petId: string) => {
  const response = await apiClient.get(`/pets/${petId}/alerts`);
  return response.data;
};

export const acknowledgeAlert = async (petId: string, alertId: string) => {
  const response = await apiClient.post(`/pets/${petId}/alerts/${alertId}/acknowledge`);
  return response.data;
};
