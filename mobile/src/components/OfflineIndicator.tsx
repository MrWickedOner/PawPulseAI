import React, { useEffect, useState } from 'react';
import { View, Text, SafeAreaView, Platform } from 'react-native';
import * as Network from 'expo-network';
import { WifiOff } from 'lucide-react-native';

const OfflineIndicator = () => {
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    const checkNetwork = async () => {
      const state = await Network.getNetworkStateAsync();
      setIsOffline(!state.isConnected || !state.isInternetReachable);
    };

    const interval = setInterval(checkNetwork, 5000);
    checkNetwork();

    return () => clearInterval(interval);
  }, []);

  if (!isOffline) return null;

  return (
    <View className="bg-amber-500 py-1 px-4 flex-row items-center justify-center">
      <WifiOff size={12} color="white" />
      <Text className="text-white text-[10px] font-bold ml-2 uppercase tracking-widest">
        Offline Mode • Viewing Cached Data
      </Text>
    </View>
  );
};

export default OfflineIndicator;
