export type SubscriptionTier = 'free' | 'basic' | 'premium' | 'pro';

export interface User {
  email: string;
  id: string;
  tier: SubscriptionTier;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password?: string;
}

export interface Pet {
  name: string;
  species: string;
  breed?: string | null;
  birth_date?: string | null;
  weight?: number | null;
  id: string;
  owner_id: string;
  created_at: string;
}

export interface PetCreate {
  name: string;
  species: string;
  breed?: string | null;
  birth_date?: string | null;
  weight?: number | null;
}

export interface Device {
  type: string;
  external_id: string;
  id: string;
  pet_id: string;
  access_token: string;
  refresh_token?: string | null;
  token_expires_at?: string | null;
  token_type?: string | null;
  created_at: string;
}

export interface DeviceCreate {
  type: string;
  external_id: string;
  pet_id: string;
  access_token: string;
  refresh_token?: string | null;
}

export interface HealthData {
  type: string;
  value: number;
  unit: string;
  timestamp: string;
  id: string;
  pet_id: string;
  device_id: string;
}

export interface AnomalyAlert {
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'acknowledged' | 'dismissed';
  id: string;
  pet_id: string;
  created_at: string;
  confidence?: number;
  recommendation?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Subscription {
  tier: SubscriptionTier;
  status: string;
  id: string;
  user_id: string;
  stripe_customer_id?: string | null;
  stripe_subscription_id?: string | null;
  current_period_start?: string | null;
  current_period_end?: string | null;
  created_at: string;
}

export interface CheckoutSession {
  checkout_url: string;
}

export interface CheckoutSessionCreate {
  tier: SubscriptionTier;
  success_url: string;
  cancel_url: string;
}

export interface Practice {
  name: string;
  address: string;
  license_info: string;
  id: string;
  owner_id: string;
  created_at: string;
}

export interface PracticeCreate {
  name: string;
  address: string;
  license_info: string;
}
