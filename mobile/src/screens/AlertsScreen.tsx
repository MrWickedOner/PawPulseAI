import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { Bell, AlertTriangle, ChevronRight, CheckCircle2 } from 'lucide-react-native';
import { getPets } from '../services/petService';
import { getAlerts } from '../services/alertService';

const AlertsScreen = ({ navigation }: any) => {
  const { data: pets, isLoading: petsLoading, refetch: refetchPets, isRefetching: isRefetchingPets } = useQuery({
    queryKey: ['pets'],
    queryFn: getPets,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const petIds = pets?.map((p: any) => p.id) || [];

  const { data: allAlerts, isLoading: alertsLoading, refetch: refetchAlerts, isRefetching: isRefetchingAlerts } = useQuery({
    queryKey: ['all-alerts-tab', petIds],
    queryFn: async () => {
      const alertPromises = petIds.map((id: string) => getAlerts(id));
      const alertResults = await Promise.all(alertPromises);
      return alertResults.flat().filter((a: any) => a.status === 'active');
    },
    enabled: petIds.length > 0,
    staleTime: 1000 * 60, // 1 minute
  });

  const onRefresh = () => {
    refetchPets();
    refetchAlerts();
  };

  const isLoading = petsLoading || (alertsLoading && petIds.length > 0);
  const isRefetching = isRefetchingPets || isRefetchingAlerts;

  if (isLoading) {
    return (
      <View className="flex-1 items-center justify-center bg-slate-50">
        <ActivityIndicator size="large" color="#7c3aed" />
      </View>
    );
  }

  return (
    <ScrollView 
      className="flex-1 bg-slate-50"
      contentContainerStyle={{ padding: 20 }}
      refreshControl={
        <RefreshControl refreshing={isRefetching} onRefresh={onRefresh} />
      }
    >
      <View className="mb-8">
        <Text className="text-2xl font-bold text-slate-900">Health Alerts</Text>
        <Text className="text-slate-500 text-sm">Stay informed about your pack's health</Text>
      </View>

      {!allAlerts || allAlerts.length === 0 ? (
        <View className="bg-white border border-slate-200 rounded-3xl p-10 items-center shadow-sm">
          <View className="w-20 h-20 bg-emerald-50 rounded-full items-center justify-center mb-6">
            <CheckCircle2 size={40} color="#10b981" />
          </View>
          <Text className="text-xl font-bold text-slate-900 mb-2">No Active Alerts</Text>
          <Text className="text-slate-500 text-center">Your pack is currently healthy and no anomalies have been detected.</Text>
        </View>
      ) : (
        <View className="space-y-4">
          {allAlerts.map((alert: any) => {
            const pet = pets?.find((p: any) => p.id === alert.pet_id);
            const isCritical = alert.severity === 'critical';
            
            return (
              <TouchableOpacity 
                key={alert.id}
                onPress={() => navigation.navigate('PackTab', { screen: 'PetDetail', params: { id: alert.pet_id } })}
                className={`bg-white border rounded-2xl p-5 shadow-sm flex-row items-center ${
                  isCritical ? 'border-rose-200' : 'border-amber-200'
                }`}
              >
                <View className={`w-12 h-12 rounded-full items-center justify-center mr-4 ${
                  isCritical ? 'bg-rose-100' : 'bg-amber-100'
                }`}>
                  <AlertTriangle size={24} color={isCritical ? '#e11d48' : '#d97706'} />
                </View>
                <View className="flex-1">
                  <View className="flex-row justify-between items-start mb-1">
                    <Text className="font-bold text-slate-900 text-lg" numberOfLines={1}>
                      {pet?.name || 'Unknown'}
                    </Text>
                    <Text className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                      isCritical ? 'bg-rose-100 text-rose-600' : 'bg-amber-100 text-amber-600'
                    }`}>
                      {alert.type}
                    </Text>
                  </View>
                  <Text className="text-slate-600 text-sm" numberOfLines={2}>
                    {alert.description}
                  </Text>
                </View>
                <ChevronRight size={20} color="#cbd5e1" />
              </TouchableOpacity>
            );
          })}
        </View>
      )}
    </ScrollView>
  );
};

export default AlertsScreen;
