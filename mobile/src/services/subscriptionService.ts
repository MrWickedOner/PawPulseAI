import apiClient from '../api/client';

export const getCurrentSubscription = async () => {
  const response = await apiClient.get('/subscriptions/current');
  return response.data;
};

export const cancelSubscription = async () => {
  const response = await apiClient.post('/subscriptions/cancel');
  return response.data;
};

export const verifyIAP = async (receiptData: string, productId: string, platform: string) => {
  const response = await apiClient.post('/subscriptions/verify-iap', {
    receipt_data: receiptData,
    product_id: productId,
    platform: platform,
  });
  return response.data;
};
