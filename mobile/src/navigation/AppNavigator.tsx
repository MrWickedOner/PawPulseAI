import React, { useEffect } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { LayoutDashboard, Bell, User } from 'lucide-react-native';
import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { setOnUnauthorized } from '../api/client';

import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen';
import PetDetailScreen from '../screens/PetDetailScreen';
import OnboardingScreen from '../screens/OnboardingScreen';
import SettingsScreen from '../screens/SettingsScreen';
import AlertsScreen from '../screens/AlertsScreen';
import VetReportScreen from '../screens/VetReportScreen';
import SubscriptionScreen from '../screens/SubscriptionScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const PackStack = createNativeStackNavigator();
const ProfileStack = createNativeStackNavigator();

function PackStackNavigator() {
  return (
    <PackStack.Navigator screenOptions={{ headerShown: false }}>
      <PackStack.Screen name="Dashboard" component={DashboardScreen} />
      <PackStack.Screen name="PetDetail" component={PetDetailScreen} />
      <PackStack.Screen name="Onboarding" component={OnboardingScreen} />
      <PackStack.Screen name="VetReport" component={VetReportScreen} />
    </PackStack.Navigator>
  );
}

function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
      <ProfileStack.Screen name="Settings" component={SettingsScreen} />
      <ProfileStack.Screen name="Subscription" component={SubscriptionScreen} />
    </ProfileStack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#7c3aed', // violet-600
        tabBarInactiveTintColor: '#64748b', // slate-500
        tabBarStyle: {
          borderTopWidth: 1,
          borderTopColor: '#e2e8f0', // slate-200
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        headerStyle: {
          backgroundColor: '#fff',
        },
        headerTitleStyle: {
          fontWeight: 'bold',
          color: '#0f172a', // slate-900
        },
      }}
    >
      <Tab.Screen
        name="PackTab"
        component={PackStackNavigator}
        options={{
          tabBarIcon: ({ color, size }) => <LayoutDashboard color={color} size={size} />,
          title: 'Pack',
          headerShown: false,
        }}
      />
      <Tab.Screen
        name="Alerts"
        component={AlertsScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Bell color={color} size={size} />,
          title: 'Alerts',
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStackNavigator}
        options={{
          tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
          title: 'Profile',
          headerShown: false,
        }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const { userToken, isLoading, signOut } = useAuth();

  useEffect(() => {
    setOnUnauthorized(signOut);
  }, [signOut]);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#7c3aed" />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {userToken == null ? (
        <Stack.Screen name="Login" component={LoginScreen} />
      ) : (
        <Stack.Screen name="MainTabs" component={MainTabs} />
      )}
      <Stack.Screen name="Auth" component={LoginScreen} />
    </Stack.Navigator>
  );
}
