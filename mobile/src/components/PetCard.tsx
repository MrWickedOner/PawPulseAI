import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, AlertTriangle, Activity, Moon, Footprints, Loader2, ChevronRight } from 'lucide-react-native';
import { getAlerts } from '../services/alertService';

interface PetCardProps {
  pet: any;
  onPress: () => void;
}

const PetCard: React.FC<PetCardProps> = ({ pet, onPress }) => {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', pet.id],
    queryFn: () => getAlerts(pet.id),
  });

  const activeAlert = alerts?.find((a: any) => a.status === 'active');
  const hasCriticalAlert = activeAlert && activeAlert.severity === 'critical';

  return (
    <TouchableOpacity
      onPress={onPress}
      className={`bg-white border rounded-2xl p-5 mb-4 shadow-sm relative overflow-hidden ${
        activeAlert ? 'border-amber-200' : 'border-slate-200'
      }`}
    >
      {activeAlert && (
        <View className={`absolute top-0 left-0 right-0 h-1 ${
          hasCriticalAlert ? 'bg-rose-500' : 'bg-amber-500'
        }`} />
      )}

      <View className="flex-row justify-between items-start mb-4">
        <View className="flex-row items-center flex-1">
          <View className="w-14 h-14 rounded-full bg-slate-100 items-center justify-center border-2 border-slate-50 mr-4">
             <Text className="text-xl font-bold text-slate-400">{pet.name[0]}</Text>
          </View>
          <View className="flex-1">
            <Text className="text-lg font-bold text-slate-900">{pet.name}</Text>
            <Text className="text-sm text-slate-500">{pet.breed || 'Unknown Breed'}</Text>
          </View>
        </View>
        
        {isLoading ? (
          <Loader2 size={16} className="text-slate-300" />
        ) : activeAlert ? (
          <View className={`flex-row items-center px-3 py-1 rounded-full ${
            hasCriticalAlert ? 'bg-rose-50' : 'bg-amber-50'
          }`}>
            <AlertTriangle size={12} color={hasCriticalAlert ? '#e11d48' : '#d97706'} />
            <Text className={`ml-1.5 text-[10px] font-bold ${
              hasCriticalAlert ? 'text-rose-600' : 'text-amber-600'
            }`}>
              {activeAlert.type.toUpperCase()}
            </Text>
          </View>
        ) : (
          <View className="flex-row items-center bg-emerald-50 px-3 py-1 rounded-full">
            <CheckCircle2 size={12} color="#059669" />
            <Text className="ml-1.5 text-[10px] font-bold text-emerald-600">
              HEALTHY
            </Text>
          </View>
        )}
      </div>

      <View className="flex-row justify-around py-4 border-t border-b border-slate-50">
        <View className="items-center">
          <Activity size={18} color="#8b5cf6" />
          <Text className="text-base font-bold text-slate-800 mt-1">--%</Text>
          <Text className="text-[10px] text-slate-400 uppercase tracking-wider">Activity</Text>
        </View>
        <View className="items-center">
          <Moon size={18} color="#3b82f6" />
          <Text className="text-base font-bold text-slate-800 mt-1">--%</Text>
          <Text className="text-[10px] text-slate-400 uppercase tracking-wider">Sleep</Text>
        </View>
        <View className="items-center">
          <Footprints size={18} color="#f97316" />
          <Text className="text-base font-bold text-slate-800 mt-1">--</Text>
          <Text className="text-[10px] text-slate-400 uppercase tracking-wider">Steps</Text>
        </View>
      </View>
      
      <View className="mt-4 flex-row items-center justify-between">
        <View className="flex-1">
          {activeAlert ? (
            <Text className="text-xs text-amber-800" numberOfLines={1}>
              {activeAlert.description}
            </Text>
          ) : (
            <Text className="text-xs text-slate-400">View health details</Text>
          )}
        </View>
        <ChevronRight size={16} color="#94a3b8" />
      </View>
    </TouchableOpacity>
  );
};

export default PetCard;
