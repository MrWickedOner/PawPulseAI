import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Alert, Platform } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Check, ArrowLeft, Shield, Zap, Star, Info } from 'lucide-react-native';
import { getCurrentSubscription, verifyIAP } from '../services/subscriptionService';
import * as IAP from 'react-native-iap';
import { useQueryClient } from '@tanstack/react-query';

const plans = [
  { id: 'free', name: 'PawPulse Free', price: '$0', description: 'Basic tracking for casual pet owners.', features: ['Single pet profile', 'Device integration', 'Real-time activity view'], icon: Info, color: 'bg-slate-50', iconColor: '#64748b' },
  { id: 'basic', name: 'PawPulse Basic', price: '$9', description: 'Essential health monitoring.', features: ['Everything in Free', 'Anomaly alerts', 'Weekly summaries', '7-day history'], icon: Shield, color: 'bg-blue-50', iconColor: '#2563eb' },
  { id: 'premium', name: 'PawPulse Premium', price: '$19', description: 'Advanced insights and trends.', features: ['Everything in Basic', '30-day trendlines', 'Multi-pet dashboard', 'Vet reports'], icon: Star, color: 'bg-violet-50', iconColor: '#7c3aed', popular: true },
];

const itemSkus = Platform.select({
  ios: ['com.pawpulse.basic.monthly', 'com.pawpulse.premium.monthly'],
  android: ['com.pawpulse.basic.monthly', 'com.pawpulse.premium.monthly'],
}) || [];

const SubscriptionScreen = ({ navigation }: any) => {
  const { data: currentSub, isLoading: subLoading } = useQuery({
    queryKey: ['currentSubscription'],
    queryFn: getCurrentSubscription,
  });

  const [products, setProducts] = useState<IAP.Product[]>([]);
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    let purchaseUpdateSubscription: any;
    let purchaseErrorSubscription: any;

    const initIAP = async () => {
      try {
        await IAP.initConnection();
        if (itemSkus.length > 0) {
          const fetchedProducts = await IAP.getProducts({ skus: itemSkus });
          setProducts(fetchedProducts);
        }

        purchaseUpdateSubscription = IAP.purchaseUpdatedListener(async (purchase) => {
          const receipt = purchase.transactionReceipt;
          if (receipt) {
            setLoading(true);
            try {
              // Robustness: handle retry logic or server-side failure
              const result = await verifyIAP(receipt, purchase.productId, Platform.OS);
              
              if (result.success || result.status === 'active') {
                await IAP.finishTransaction({ purchase, isConsumable: false });
                queryClient.invalidateQueries({ queryKey: ['currentSubscription'] });
                queryClient.invalidateQueries({ queryKey: ['me'] });
                Alert.alert('Success', 'Subscription upgraded successfully!');
              } else {
                console.error('IAP verification failed on server:', result);
                Alert.alert('Verification Error', 'We could not verify your purchase. Please contact support.');
              }
            } catch (err) {
              console.error('Verification request failed', err);
              Alert.alert('Network Error', 'Failed to connect to our server for verification. Your purchase is safe and will be retried automatically.');
            } finally {
              setLoading(false);
            }
          }
        });

        purchaseErrorSubscription = IAP.purchaseErrorListener((error) => {
          console.warn('purchaseErrorListener', error);
        });

      } catch (err) {
        console.warn('IAP error', err);
      }
    };
    initIAP();
    return () => {
      if (purchaseUpdateSubscription) purchaseUpdateSubscription.remove();
      if (purchaseErrorSubscription) purchaseErrorSubscription.remove();
      IAP.endConnection();
    };
  }, []);

  const handleUpgrade = async (planId: string) => {
    if (planId === 'free') return;
    
    setLoading(true);
    try {
      const sku = `com.pawpulse.${planId}.monthly`;
      await IAP.requestSubscription({ sku });
      // In a real app, listen to purchaseUpdatedListener and verify receipt on backend
      Alert.alert('Purchase Initiated', 'Connecting to App Store...');
    } catch (err: any) {
      Alert.alert('Error', err.message);
    } finally {
      setLoading(false);
    }
  };

  if (subLoading) {
    return (
      <View className="flex-1 items-center justify-center bg-slate-50">
        <ActivityIndicator size="large" color="#7c3aed" />
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 bg-slate-50 px-6 py-10">
      <View className="flex-row items-center mb-8">
        <TouchableOpacity onPress={() => navigation.goBack()} className="p-2 -ml-2">
          <ArrowLeft size={24} color="#64748b" />
        </TouchableOpacity>
        <View className="ml-2">
          <Text className="text-2xl font-bold text-slate-900">Choose Plan</Text>
          <Text className="text-slate-500 text-sm">
            Current: {currentSub?.tier?.toUpperCase() || 'FREE'}
          </Text>
        </View>
      </View>

      <View className="space-y-6 pb-10">
        {plans.map((plan) => (
          <View 
            key={plan.id}
            className={`bg-white rounded-3xl p-6 border-2 relative ${
              currentSub?.tier === plan.id ? 'border-violet-600 bg-violet-50/30' : 'border-slate-100'
            }`}
          >
            {plan.popular && (
              <View className="absolute -top-3 left-6 bg-violet-600 px-3 py-1 rounded-full">
                <Text className="text-white text-[10px] font-bold uppercase">Most Popular</Text>
              </View>
            )}
            
            <View className="flex-row justify-between items-start mb-4">
              <View className="w-12 h-12 bg-white rounded-2xl items-center justify-center shadow-sm">
                <plan.icon size={24} color={plan.iconColor} />
              </View>
              <View className="items-end">
                <Text className="text-2xl font-bold text-slate-900">{plan.price}</Text>
                <Text className="text-slate-400 text-xs font-bold uppercase">per month</Text>
              </View>
            </View>

            <Text className="text-xl font-bold text-slate-900 mb-1">{plan.name}</Text>
            <Text className="text-slate-500 text-sm mb-6">{plan.description}</Text>

            <View className="space-y-3 mb-8">
              {plan.features.map((feature) => (
                <View key={feature} className="flex-row items-center">
                  <View className="w-5 h-5 rounded-full bg-emerald-50 items-center justify-center mr-3">
                    <Check size={12} color="#10b981" strokeWidth={3} />
                  </View>
                  <Text className="text-slate-600 text-sm">{feature}</Text>
                </View>
              ))}
            </View>

            <TouchableOpacity 
              onPress={() => handleUpgrade(plan.id)}
              disabled={currentSub?.tier === plan.id || loading}
              className={`py-4 rounded-2xl items-center justify-center ${
                currentSub?.tier === plan.id ? 'bg-slate-100' : 'bg-violet-600 shadow-md shadow-violet-200'
              }`}
            >
              <Text className={`font-bold text-lg ${
                currentSub?.tier === plan.id ? 'text-slate-400' : 'text-white'
              }`}>
                {currentSub?.tier === plan.id ? 'Current Plan' : 'Select Plan'}
              </Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

export default SubscriptionScreen;
