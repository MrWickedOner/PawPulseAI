import { useQuery } from '@tanstack/react-query';
import { getMe } from '../services/authService';
import type { SubscriptionTier } from '../types';

export interface FeatureFlags {
  canAddMultiplePets: boolean;
  canViewLongHistory: boolean;
  canShareVetReports: boolean;
  canAccessProPortal: boolean;
  petLimit: number;
}

export const useFeatures = () => {
  const { data: user } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  });

  const tier: SubscriptionTier = user?.tier || 'free';

  const flags: FeatureFlags = {
    canAddMultiplePets: tier === 'premium' || tier === 'pro',
    canViewLongHistory: tier === 'premium' || tier === 'pro',
    canShareVetReports: tier === 'premium' || tier === 'pro',
    canAccessProPortal: tier === 'pro',
    petLimit: tier === 'premium' ? 5 : tier === 'pro' ? 100 : 1,
  };

  return { flags, tier, isLoading: !user };
};
