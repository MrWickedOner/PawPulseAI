import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Alert, Switch } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { User, Bell, CreditCard, Shield, LogOut, ChevronRight, CheckCircle2, Clock, FileText, Zap, Fingerprint } from 'lucide-react-native';
import { logout, getMe } from '../services/authService';
import { getCurrentSubscription, cancelSubscription } from '../services/subscriptionService';
import { getPets } from '../services/petService';
import { isBiometricAvailable, authenticateWithBiometrics, getBiometricsEnabled, setBiometricsEnabled } from '../services/securityService';

const SettingsScreen = ({ navigation }: any) => {
  const { signOut } = useAuth();
  const queryClient = useQueryClient();
  const [biometricsAvailable, setBiometricsAvailable] = useState(false);
  const [biometricsEnabled, setBiometricsEnabledState] = useState(false);
  
  useEffect(() => {
    const checkBiometrics = async () => {
      const available = await isBiometricAvailable();
      setBiometricsAvailable(available);
      const enabled = await getBiometricsEnabled();
      setBiometricsEnabledState(enabled);
    };
    checkBiometrics();
  }, []);

  const toggleBiometrics = async () => {
    if (!biometricsEnabled) {
      const success = await authenticateWithBiometrics();
      if (success) {
        await setBiometricsEnabled(true);
        setBiometricsEnabledState(true);
      }
    } else {
      await setBiometricsEnabled(false);
      setBiometricsEnabledState(false);
    }
  };

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  });

  const { data: subscription, isLoading: subLoading } = useQuery({
    queryKey: ['currentSubscription'],
    queryFn: getCurrentSubscription,
  });

  const { data: pets } = useQuery({
    queryKey: ['pets'],
    queryFn: getPets,
  });

  const cancelMutation = useMutation({
    mutationFn: cancelSubscription,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentSubscription'] });
      Alert.alert('Success', 'Subscription cancelled successfully.');
    },
  });

  const handleLogout = async () => {
    await signOut();
    // navigation.replace('Login'); // AuthContext state change will trigger this
  };

  if (userLoading || subLoading) {
    return (
      <View className="flex-1 items-center justify-center bg-slate-50">
        <ActivityIndicator size="large" color="#7c3aed" />
      </View>
    );
  }

  const petLimit = user?.tier === 'free' ? 1 : user?.tier === 'basic' ? 1 : user?.tier === 'premium' ? 5 : 100;
  const petCount = pets?.length || 0;

  const sections = [
    { name: 'Account', icon: User, desc: user?.email || 'Manage profile' },
    { name: 'Notifications', icon: Bell, desc: 'Alerts & summaries' },
    { name: 'Privacy & Security', icon: Shield, desc: 'Data & access' },
  ];

  return (
    <ScrollView className="flex-1 bg-slate-50 px-6 py-10">
      <View className="flex-row justify-between items-center mb-8">
        <View>
          <Text className="text-2xl font-bold text-slate-900">Settings</Text>
          <Text className="text-slate-500 text-sm">Manage your experience</Text>
        </View>
        <TouchableOpacity 
          onPress={handleLogout}
          className="flex-row items-center bg-white border border-slate-200 px-4 py-2 rounded-xl"
        >
          <LogOut size={16} color="#64748b" />
          <Text className="ml-2 text-slate-600 font-bold">Sign Out</Text>
        </TouchableOpacity>
      </View>

      {/* Subscription Card */}
      <View className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm mb-8">
        <View className="p-6 border-b border-slate-50">
          <View className="flex-row justify-between items-center mb-4">
            <View className="flex-row items-center">
              <Text className="text-lg font-bold text-slate-900 mr-2">Current Plan</Text>
              <View className={`px-2 py-0.5 rounded-full ${
                user?.tier === 'free' ? 'bg-slate-100' : 'bg-violet-100'
              }`}>
                <Text className={`text-[10px] font-bold uppercase tracking-wider ${
                  user?.tier === 'free' ? 'text-slate-600' : 'text-violet-700'
                }`}>
                  {user?.tier}
                </Text>
              </View>
            </View>
          </View>
          <Text className="text-slate-500 text-xs italic mb-4">
            {subscription?.status === 'active' 
              ? `Renews on ${new Date(subscription.current_period_end).toLocaleDateString()}` 
              : 'Free Tier'}
          </Text>
          <TouchableOpacity 
            onPress={() => navigation.navigate('Subscription')} // Navigate to Upgrade/Subscription Screen
            className="bg-violet-600 py-3 rounded-xl items-center px-6"
          >
            <Text className="text-white font-bold">
              {user?.tier === 'free' ? 'Upgrade Now' : 'Change Plan'}
            </Text>
          </TouchableOpacity>
        </View>
        
        <View className="p-6 bg-slate-50/50">
          <View className="flex-row items-center mb-2">
            <Zap size={14} color="#94a3b8" />
            <Text className="ml-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Usage</Text>
          </View>
          <View className="flex-row justify-between mb-2">
            <Text className="text-sm text-slate-600">Pets Tracked</Text>
            <Text className="text-sm font-bold text-slate-900">{petCount} of {petLimit}</Text>
          </View>
          <View className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
            <View 
              className="bg-violet-500 h-full rounded-full" 
              style={{ width: `${Math.min((petCount / petLimit) * 100, 100)}%` }}
            />
          </View>

          <View className="mt-6 flex-row items-center mb-2">
            <Clock size={14} color="#94a3b8" />
            <Text className="ml-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Billing</Text>
          </View>
          <View className="flex-row items-center justify-between">
            <View className="flex-row items-center">
              <View className="w-10 h-10 bg-white rounded-xl border border-slate-100 items-center justify-center mr-3">
                <CreditCard size={20} color="#94a3b8" />
              </View>
              <View>
                <Text className="font-bold text-slate-800 text-sm">Visa •••• 4242</Text>
                <Text className="text-slate-500 text-xs">Exp 12/28</Text>
              </View>
            </View>
            <TouchableOpacity>
              <Text className="text-sm font-bold text-violet-600">Edit</Text>
            </TouchableOpacity>
          </View>
        </View>

        {user?.tier !== 'free' && (
          <View className="px-6 py-4 border-t border-slate-50 flex-row justify-between items-center">
            <TouchableOpacity 
              onPress={() => {
                Alert.alert(
                  'Cancel Subscription',
                  'Are you sure you want to cancel?',
                  [
                    { text: 'No', style: 'cancel' },
                    { text: 'Yes', onPress: () => cancelMutation.mutate() }
                  ]
                );
              }}
              disabled={cancelMutation.isPending}
            >
              <Text className="text-xs font-bold text-rose-600">
                {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Subscription'}
              </Text>
            </TouchableOpacity>
            <TouchableOpacity className="flex-row items-center">
              <FileText size={14} color="#94a3b8" />
              <Text className="ml-1 text-xs font-bold text-slate-400">Invoices</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      <View className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm mb-6">
        {sections.map((section, idx) => (
          <TouchableOpacity 
            key={section.name}
            className={`flex-row items-center p-5 ${
              idx !== sections.length - 1 ? 'border-b border-slate-50' : ''
            }`}
          >
            <View className="w-10 h-10 bg-slate-50 rounded-xl items-center justify-center mr-4">
              <section.icon size={20} color="#94a3b8" />
            </View>
            <View className="flex-1">
              <Text className="font-bold text-slate-800 text-base">{section.name}</Text>
              <Text className="text-xs text-slate-500">{section.desc}</Text>
            </View>
            <ChevronRight size={18} color="#cbd5e1" />
          </TouchableOpacity>
        ))}
      </View>

      {biometricsAvailable && (
        <View className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm mb-10">
          <View className="flex-row items-center p-5">
            <View className="w-10 h-10 bg-violet-50 rounded-xl items-center justify-center mr-4">
              <Fingerprint size={20} color="#7c3aed" />
            </View>
            <View className="flex-1">
              <Text className="font-bold text-slate-800 text-base">Biometric Unlock</Text>
              <Text className="text-xs text-slate-500">Require fingerprint or Face ID</Text>
            </View>
            <Switch
              value={biometricsEnabled}
              onValueChange={toggleBiometrics}
              trackColor={{ false: '#e2e8f0', true: '#c4b5fd' }}
              thumbColor={biometricsEnabled ? '#7c3aed' : '#f8fafc'}
            />
          </View>
        </View>
      )}
    </ScrollView>
  );
};

export default SettingsScreen;
