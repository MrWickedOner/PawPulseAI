import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { login } from '../services/authService';
import { useAuth } from '../context/AuthContext';

const LoginScreen = ({ navigation }: any) => {
  const { signIn } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await login(username, password);
      await signIn(response.access_token);
      // navigation.replace('MainTabs'); // AuthContext state change will trigger this in AppNavigator
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-slate-50"
    >
      <ScrollView contentContainerStyle={{ flexGrow: 1 }} className="px-6">
        <View className="flex-1 justify-center py-12">
          <View className="items-center mb-8">
            <View className="w-16 h-16 bg-violet-600 rounded-2xl items-center justify-center shadow-lg">
              <Text className="text-white font-bold text-4xl">P</Text>
            </View>
            <Text className="mt-6 text-3xl font-extrabold text-slate-900 text-center">
              Sign in to PawPulse
            </Text>
          </View>

          <View className="space-y-4">
            <View>
              <Text className="text-sm font-medium text-slate-700 mb-1 ml-1">Username</Text>
              <TextInput
                className="bg-white px-4 py-3 border border-slate-300 rounded-xl text-slate-900 focus:border-violet-500"
                placeholder="Username"
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
              />
            </View>

            <View className="mt-4">
              <Text className="text-sm font-medium text-slate-700 mb-1 ml-1">Password</Text>
              <TextInput
                className="bg-white px-4 py-3 border border-slate-300 rounded-xl text-slate-900 focus:border-violet-500"
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
              />
            </View>
          </View>

          {error ? (
            <Text className="text-red-500 text-sm text-center mt-4">{error}</Text>
          ) : null}

          <TouchableOpacity
            onPress={handleSubmit}
            disabled={loading}
            className={`mt-8 py-4 rounded-xl items-center justify-center shadow-sm ${
              loading ? 'bg-violet-400' : 'bg-violet-600'
            }`}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text className="text-white font-bold text-lg">Sign in</Text>
            )}
          </TouchableOpacity>

          <View className="mt-8 flex-row justify-center">
            <Text className="text-slate-600">Don't have an account? </Text>
            <TouchableOpacity onPress={() => {}}>
              <Text className="text-violet-600 font-semibold">Sign up</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default LoginScreen;
