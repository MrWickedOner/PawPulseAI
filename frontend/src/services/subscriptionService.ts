import api from './api';
import type { Subscription, CheckoutSession, CheckoutSessionCreate } from '../types';

export const getCurrentSubscription = async (): Promise<Subscription> => {
  const response = await api.get('/subscriptions/current');
  return response.data;
};

export const createCheckoutSession = async (data: CheckoutSessionCreate): Promise<CheckoutSession> => {
  const response = await api.post('/subscriptions/create-checkout', data);
  return response.data;
};

export const createPortalSession = async (returnUrl: string): Promise<CheckoutSession> => {
  const response = await api.post(`/subscriptions/portal?return_url=${encodeURIComponent(returnUrl)}`);
  return response.data;
};

export const cancelSubscription = async (): Promise<void> => {
  await api.post('/subscriptions/cancel');
};
