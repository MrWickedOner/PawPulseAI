import React, { useMemo } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { PlusCircle, Lock, AlertTriangle, ChevronRight, LayoutDashboard } from 'lucide-react-native';
import { getPets } from '../services/petService';
import { getAlerts } from '../services/alertService';
import { getHealthData } from '../services/healthService';
import { useFeatures } from '../hooks/useFeatures';
import PetCard from '../components/PetCard';
import { VictoryBar, VictoryChart, VictoryAxis, VictoryTheme, VictoryGroup } from 'victory-native';

const DashboardScreen = ({ navigation }: any) => {
  const { data: pets, isLoading: petsLoading, error, refetch, isRefetching, isStale: petsStale, dataUpdatedAt: petsUpdatedAt } = useQuery({
    queryKey: ['pets'],
    queryFn: getPets,
    staleTime: 1000 * 60 * 1, // 1 minute
  });

  const { flags, isLoading: featuresLoading } = useFeatures();

  const petIds = useMemo(() => pets?.map((p: any) => p.id) || [], [pets]);
  
  const { data: allAlertsData, isLoading: alertsLoading, isStale: alertsStale } = useQuery({
    queryKey: ['all-alerts', petIds],
    queryFn: async () => {
      const alertPromises = petIds.map((id: string) => getAlerts(id));
      const alertResults = await Promise.all(alertPromises);
      return alertResults.flat().filter((a: any) => a.status === 'active');
    },
    enabled: petIds.length > 0,
    staleTime: 1000 * 30, // 30 seconds
  });

  const { data: packHealthData, isLoading: healthLoading, isStale: healthStale } = useQuery({
    queryKey: ['pack-health', petIds],
    queryFn: async () => {
      const healthPromises = petIds.map((id: string) => getHealthData(id));
      const healthResults = await Promise.all(healthPromises);
      return healthResults;
    },
    enabled: petIds.length > 0,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const isDataStale = petsStale || alertsStale || healthStale;

  const chartData = useMemo(() => {
    if (!packHealthData || !pets) return [];
    
    // Last 7 days labels
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    return pets.map((pet: any, index: number) => {
      const petHealth = packHealthData[index] || [];
      const activityData = petHealth.filter((d: any) => d.type === 'activity').slice(-7);
      
      return activityData.map((d: any, i: number) => ({
        x: days[i % 7],
        y: d.value,
        petName: pet.name
      }));
    });
  }, [packHealthData, pets]);

  const isLoading = petsLoading || featuresLoading;

  const onRefresh = () => {
    refetch();
  };

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
      <View className="flex-row justify-between items-end mb-6">
        <View>
          <Text className="text-2xl font-bold text-slate-900">Your Pack</Text>
          <View className="flex-row items-center">
            <Text className="text-slate-500 mr-2">Real-time health status</Text>
            {petsUpdatedAt > 0 && (
              <Text className="text-[10px] text-slate-400">
                Synced {new Date(petsUpdatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Text>
            )}
          </View>
        </View>
        
        {pets && pets.length >= flags.petLimit ? (
          <TouchableOpacity
            className="bg-slate-100 flex-row items-center px-4 py-2 rounded-xl border border-slate-200"
            onPress={() => {}}
          >
            <Lock size={14} color="#64748b" />
            <Text className="ml-2 text-slate-500 font-medium text-sm">Limit Reached</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity
            className="bg-violet-600 flex-row items-center px-4 py-2 rounded-xl shadow-sm"
            onPress={() => navigation.navigate('Onboarding')}
          >
            <PlusCircle size={14} color="white" />
            <Text className="ml-2 text-white font-medium text-sm">Add Pet</Text>
          </TouchableOpacity>
        )}
      </View>

      {allAlertsData && allAlertsData.length > 0 && (
        <View className="bg-rose-50 border border-rose-100 rounded-2xl overflow-hidden mb-8 shadow-sm">
          <View className="bg-rose-100 px-4 py-3 border-b border-rose-100 flex-row items-center justify-between">
            <View className="flex-row items-center">
              <AlertTriangle size={16} color="#e11d48" />
              <Text className="ml-2 text-rose-700 font-bold">
                Health Alerts ({allAlertsData.length})
              </Text>
            </View>
            <Text className="text-[10px] text-rose-600 font-bold uppercase">Action Required</Text>
          </View>
          <View>
            {allAlertsData.map((alert: any) => {
              const pet = pets?.find((p: any) => p.id === alert.pet_id);
              return (
                <TouchableOpacity 
                  key={alert.id}
                  className="flex-row items-center justify-between p-4 border-b border-rose-100 last:border-0"
                  onPress={() => navigation.navigate('PackTab', { screen: 'PetDetail', params: { id: alert.pet_id } })}
                >
                  <View className="flex-row items-center flex-1">
                    <View className="w-10 h-10 rounded-full bg-rose-200 items-center justify-center mr-3">
                      <Text className="text-rose-600 font-bold">{pet?.name[0] || '?'}</Text>
                    </View>
                    <View className="flex-1">
                      <Text className="font-bold text-rose-900 text-sm">{alert.type}</Text>
                      <Text className="text-xs text-rose-700" numberOfLines={1}>
                        {pet?.name}: {alert.description}
                      </Text>
                    </View>
                  </View>
                  <ChevronRight size={18} color="#fda4af" />
                </TouchableOpacity>
              );
            })}
          </View>
        </View>
      )}

      {pets?.length === 0 ? (
        <View className="bg-white border border-slate-200 rounded-2xl p-10 items-center shadow-sm">
          <LayoutDashboard size={48} color="#cbd5e1" />
          <Text className="text-slate-500 mt-4 text-center">You haven't added any pets yet.</Text>
          <TouchableOpacity className="mt-4">
            <Text className="text-violet-600 font-bold">Add your first pet</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View>
          {pets?.map((pet: any) => (
            <PetCard 
              key={pet.id} 
              pet={pet} 
              onPress={() => navigation.navigate('PackTab', { screen: 'PetDetail', params: { id: pet.id } })} 
            />
          ))}
        </View>
      )}

      {/* Weekly Pack Activity */}
      <View className="bg-white border border-slate-200 rounded-2xl p-5 mt-4 shadow-sm mb-6">
        <Text className="text-lg font-bold text-slate-900 mb-4">Weekly Pack Activity</Text>
        <View className="items-center">
          {healthLoading ? (
            <ActivityIndicator size="small" color="#7c3aed" className="h-40" />
          ) : chartData.length > 0 ? (
            <VictoryChart 
              theme={VictoryTheme.material} 
              height={200} 
              padding={{ top: 20, bottom: 40, left: 40, right: 20 }}
            >
              <VictoryAxis 
                style={{ 
                  tickLabels: { fontSize: 8, fill: '#94a3b8' },
                  axis: { stroke: 'none' },
                  grid: { stroke: '#f1f5f9' }
                }} 
              />
              <VictoryAxis dependentAxis 
                style={{ 
                  tickLabels: { fontSize: 8, fill: '#94a3b8' },
                  axis: { stroke: 'none' },
                  grid: { stroke: '#f1f5f9' }
                }} 
              />
              <VictoryGroup offset={10}>
                {chartData.map((data: any, i: number) => (
                  <VictoryBar 
                    key={i}
                    data={data} 
                    style={{ data: { fill: i === 0 ? '#7c3aed' : '#3b82f6', width: 8 } }}
                    cornerRadius={{ top: 2 }}
                  />
                ))}
              </VictoryGroup>
            </VictoryChart>
          ) : (
            <View className="h-40 items-center justify-center">
              <Text className="text-slate-400 text-xs italic">No activity data available yet</Text>
            </View>
          )}
        </View>
      </View>
    </ScrollView>
  );
};

export default DashboardScreen;
