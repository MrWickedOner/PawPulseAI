import { useQuery } from '@tanstack/react-query';
import { getMe } from '../services/authService';

export interface FeatureFlags {
  canAddMultiplePets: boolean;
  canViewLongHistory: boolean;
  canShareVetReports: boolean;
  canAccessProPortal: boolean;
  petLimit: number;
}

export type SubscriptionTier = 'free' | 'basic' | 'premium' | 'pro';

export const useFeatures = () => {
  const { data: user, isLoading: userLoading, isStale } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
    retry: 2,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const tier: SubscriptionTier = (user?.tier as SubscriptionTier) || 'free';

  const flags: FeatureFlags = {
    canAddMultiplePets: tier === 'premium' || tier === 'pro',
    canViewLongHistory: tier === 'premium' || tier === 'pro',
    canShareVetReports: tier === 'premium' || tier === 'pro',
    canAccessProPortal: tier === 'pro',
    petLimit: tier === 'premium' ? 5 : tier === 'pro' ? 100 : 1,
  };

  return { flags, tier, isLoading: userLoading };
};
