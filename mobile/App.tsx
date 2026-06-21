import "./src/global.css";
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import AsyncStorage from '@react-native-async-storage/async-storage';
import AppNavigator from './src/navigation/AppNavigator';
import { registerForPushNotificationsAsync, sendPushTokenToBackend } from './src/services/notificationService';
import { AuthProvider } from './src/context/AuthContext';
import { setOnUnauthorized } from './src/api/client';
import OfflineIndicator from './src/components/OfflineIndicator';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as Notifications from 'expo-notifications';

import * as Linking from 'expo-linking';

const prefix = Linking.createURL('/');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 60 * 24, // 24 hours
    },
  },
});

const asyncStoragePersister = createAsyncStoragePersister({
  storage: AsyncStorage,
});

export default function App() {
  const linking = {
    prefixes: [prefix],
    config: {
      screens: {
        MainTabs: {
          screens: {
            PackTab: {
              screens: {
                PetDetail: 'pet/:id',
              },
            },
            Alerts: 'alerts',
            Profile: 'settings',
          },
        },
      },
    },
  };

  useEffect(() => {
    registerForPushNotificationsAsync().then(token => {
      if (token) {
        sendPushTokenToBackend(token);
      }
    });

    // Handle notifications received while the app is foregrounded
    const subscription = Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received:', notification);
    });

    // Handle notifications tapped by the user
    const responseSubscription = Notifications.addNotificationResponseReceivedListener(response => {
      const url = response.notification.request.content.data.url;
      if (url) {
        Linking.openURL(url);
      }
    });

    return () => {
      subscription.remove();
      responseSubscription.remove();
    };
  }, []);

  return (
    <SafeAreaProvider>
      <PersistQueryClientProvider
        client={queryClient}
        persistOptions={{ persister: asyncStoragePersister }}
      >
        <AuthProvider>
          <OfflineIndicator />
          <NavigationContainer linking={linking}>
            <AppNavigator />
            <StatusBar style="auto" />
          </NavigationContainer>
        </AuthProvider>
      </PersistQueryClientProvider>
    </SafeAreaProvider>
  );
}
