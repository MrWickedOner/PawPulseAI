import React, { useMemo } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, Linking, Share, Platform } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Activity, Moon, Heart, Share2, AlertTriangle, Lock } from 'lucide-react-native';
import { VictoryBar, VictoryChart, VictoryAxis, VictoryArea, VictoryTheme, VictoryTooltip, VictoryVoronoiContainer } from 'victory-native';
import { getPet } from '../services/petService';
import { getHealthData } from '../services/healthService';
import { getAlerts, acknowledgeAlert } from '../services/alertService';
import { useFeatures } from '../hooks/useFeatures';

const PetDetailScreen = ({ route, navigation }: any) => {
  const { id } = route.params;
  const queryClient = useQueryClient();
  const { flags } = useFeatures();

  const { data: pet, isLoading: petLoading, error: petError } = useQuery({
    queryKey: ['pet', id],
    queryFn: () => getPet(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health', id],
    queryFn: () => getHealthData(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts', id],
    queryFn: () => getAlerts(id),
    enabled: !!id,
    staleTime: 1000 * 30, // 30 seconds
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: string) => acknowledgeAlert(id, alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts', id] });
    },
  });

  const activeAlert = alerts?.find((a: any) => a.status === 'active');

  const contactVet = () => {
    const subject = encodeURIComponent(`Health Alert: ${pet.name}`);
    const body = encodeURIComponent(`Hello,\n\nI am contacting you regarding a health alert for my pet, ${pet.name} (${pet.breed || 'Unknown Breed'}).\n\nPawPulse detected: ${activeAlert?.type}\nDescription: ${activeAlert?.description}\n\nPlease let me know if we should schedule a visit.\n\nBest regards,\nUser`);
    Linking.openURL(`mailto:vet@example.com?subject=${subject}&body=${body}`);
  };

  const handleShare = async () => {
    if (!flags.canShareVetReports) {
      navigation.navigate('Subscription');
      return;
    }

    try {
      await Share.share({
        message: `PawPulse Health Report for ${pet.name}\nStatus: ${activeAlert ? 'Alert Detected' : 'Healthy'}\nBreed: ${pet.breed || 'Unknown'}`,
        title: `Health Report: ${pet.name}`,
      });
    } catch (error) {
      console.error(error);
    }
  };

  // Score calculations (logic from web)
  const activityScore = useMemo(() => {
    const data = healthData?.filter((d: any) => d.type === 'activity');
    if (!data || data.length === 0) return 75;
    const avg = data.reduce((acc: number, curr: any) => acc + curr.value, 0) / data.length;
    return Math.round(Math.min(100, (avg / 500) * 100));
  }, [healthData]);

  const sleepScore = useMemo(() => {
    const data = healthData?.filter((d: any) => d.type === 'sleep');
    if (!data || data.length === 0) return 80;
    const avg = data.reduce((acc: number, curr: any) => acc + curr.value, 0) / data.length;
    return Math.round(Math.min(100, (avg / 8) * 100));
  }, [healthData]);

  const vitalsScore = useMemo(() => 98, []);

  if (petLoading || healthLoading || alertsLoading) {
    return (
      <View className="flex-1 items-center justify-center bg-slate-50">
        <ActivityIndicator size="large" color="#7c3aed" />
      </View>
    );
  }

  if (petError || !pet) {
    return (
      <View className="flex-1 items-center justify-center p-6 bg-slate-50">
        <Text className="text-red-500 text-center mb-4">Error loading pet details.</Text>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text className="text-violet-600 font-bold">Back to Pack</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const activityChartData = healthData?.filter((d: any) => d.type === 'activity').slice(-7).map((d: any) => ({
    x: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    y: d.value
  }));

  const heartRateData = healthData?.filter((d: any) => d.type === 'heart_rate').slice(-10).map((d: any) => ({
    x: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    y: d.value
  }));

  return (
    <ScrollView className="flex-1 bg-slate-50">
      <View className="px-6 py-4">
        <TouchableOpacity 
          onPress={() => navigation.goBack()}
          className="flex-row items-center mb-6"
        >
          <ArrowLeft size={20} color="#64748b" />
          <Text className="ml-2 text-slate-500 font-medium">Back to Pack</Text>
        </TouchableOpacity>

        <View className="flex-row items-start mb-8">
          <View className="w-24 h-24 rounded-2xl bg-slate-200 items-center justify-center border-2 border-slate-100 shadow-sm">
            <Text className="text-3xl font-bold text-slate-400">{pet.name[0]}</Text>
          </View>
          <View className="flex-1 ml-4 justify-center h-24">
            <View className="flex-row justify-between items-start">
              <View>
                <Text className="text-2xl font-bold text-slate-900">{pet.name}</Text>
                <Text className="text-slate-500">
                  {pet.breed || 'Unknown Breed'} • {pet.species}
                </Text>
              </View>
              <TouchableOpacity 
                onPress={handleShare}
                className="bg-white border border-slate-200 p-2 rounded-lg"
              >
                {flags.canShareVetReports ? <Share2 size={18} color="#475569" /> : <Lock size={16} color="#94a3b8" />}
              </TouchableOpacity>
            </View>
          </View>
        </View>

        <View className="flex-row justify-between mb-8">
          <View className="bg-white border border-slate-200 p-3 rounded-xl items-center flex-1 mr-2">
            <View className="w-8 h-8 bg-violet-50 rounded-full items-center justify-center mb-1">
              <Activity size={16} color="#7c3aed" />
            </View>
            <Text className="text-[10px] text-slate-500 font-bold uppercase">Activity</Text>
            <Text className="text-lg font-bold">{activityScore}%</Text>
          </View>
          <View className="bg-white border border-slate-200 p-3 rounded-xl items-center flex-1 mx-1">
            <View className="w-8 h-8 bg-blue-50 rounded-full items-center justify-center mb-1">
              <Moon size={16} color="#3b82f6" />
            </View>
            <Text className="text-[10px] text-slate-500 font-bold uppercase">Sleep</Text>
            <Text className="text-lg font-bold">{sleepScore}%</Text>
          </View>
          <View className="bg-white border border-slate-200 p-3 rounded-xl items-center flex-1 ml-2">
            <View className="w-8 h-8 bg-rose-50 rounded-full items-center justify-center mb-1">
              <Heart size={16} color="#e11d48" />
            </View>
            <Text className="text-[10px] text-slate-500 font-bold uppercase">Vitals</Text>
            <Text className="text-lg font-bold">{vitalsScore}%</Text>
          </View>
        </View>

        {activeAlert && (
          <View className="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-8">
            <View className="flex-row items-center mb-3">
              <View className="w-10 h-10 bg-amber-100 rounded-full items-center justify-center mr-3">
                <AlertTriangle size={20} color="#d97706" />
              </View>
              <Text className="text-lg font-bold text-amber-900">{activeAlert.type}</Text>
            </View>
            <Text className="text-amber-800 mb-5">{activeAlert.description}</Text>
            <View className="flex-row">
              <TouchableOpacity 
                onPress={contactVet}
                className="bg-amber-600 px-4 py-2 rounded-lg mr-3"
              >
                <Text className="text-white font-bold">Contact Vet</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                onPress={() => acknowledgeMutation.mutate(activeAlert.id)}
                disabled={acknowledgeMutation.isPending}
                className="bg-white border border-amber-200 px-4 py-2 rounded-lg"
              >
                <Text className="text-amber-800 font-bold">
                  {acknowledgeMutation.isPending ? 'Dismissing...' : 'Dismiss'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        <View className="bg-white border border-slate-200 rounded-2xl p-4 mb-6">
          <Text className="text-lg font-bold text-slate-900 mb-4">Activity History</Text>
          <View className="items-center">
            <VictoryChart 
              theme={VictoryTheme.material} 
              height={220} 
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
              <VictoryBar 
                data={activityChartData} 
                style={{ data: { fill: '#7c3aed', width: 12 } }}
                cornerRadius={{ top: 4 }}
              />
            </VictoryChart>
          </View>
        </View>

        <View className="bg-white border border-slate-200 rounded-2xl p-4 mb-10">
          <Text className="text-lg font-bold text-slate-900 mb-4">Resting Heart Rate</Text>
          <View className="items-center">
            <VictoryChart 
              theme={VictoryTheme.material} 
              height={220} 
              padding={{ top: 20, bottom: 40, left: 40, right: 20 }}
              containerComponent={<VictoryVoronoiContainer />}
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
              <VictoryArea 
                data={heartRateData} 
                style={{ 
                  data: { fill: '#3b82f6', fillOpacity: 0.1, stroke: '#3b82f6', strokeWidth: 2 } 
                }}
                interpolation="monotone"
              />
            </VictoryChart>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

export default PetDetailScreen;
