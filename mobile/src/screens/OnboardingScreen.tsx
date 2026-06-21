import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dog, Smartphone, CheckCircle2, ChevronRight, ChevronLeft } from 'lucide-react-native';
import { createPet } from '../services/petService';

const OnboardingScreen = ({ navigation }: any) => {
  const [step, setStep] = useState(1);
  const [petData, setPetData] = useState({
    name: '',
    species: 'Dog',
    breed: '',
    weight: '',
  });
  
  const queryClient = useQueryClient();

  const createPetMutation = useMutation({
    mutationFn: createPet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pets'] });
      setStep(2);
    },
  });

  const handleNext = () => {
    if (step === 1) {
      if (!petData.name) return;
      createPetMutation.mutate({
        name: petData.name,
        species: petData.species,
        breed: petData.breed,
        weight: petData.weight ? parseFloat(petData.weight) : undefined,
      });
    } else if (step < 3) {
      setStep(step + 1);
    } else {
      navigation.replace('MainTabs');
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-slate-50"
    >
      <ScrollView contentContainerStyle={{ flexGrow: 1 }} className="px-6 py-10">
        <View className="mb-10 flex-row justify-between items-center px-2">
          {[1, 2, 3].map((s) => (
            <View 
              key={s}
              className={`flex-1 h-1.5 rounded-full mx-1 ${
                s <= step ? 'bg-violet-600' : 'bg-slate-200'
              }`}
            />
          ))}
        </View>
        <Text className="text-center text-slate-400 font-bold mb-8 uppercase tracking-widest text-xs">Step {step} of 3</Text>

        <View className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm flex-1">
          {step === 1 && (
            <View>
              <View className="w-20 h-20 bg-violet-100 rounded-3xl items-center justify-center self-center mb-8">
                <Dog size={40} color="#7c3aed" />
              </View>
              <Text className="text-2xl font-bold text-center text-slate-900 mb-8">Tell us about your pet</Text>
              
              <View className="space-y-5">
                <View>
                  <Text className="text-sm font-bold text-slate-700 mb-2 ml-1">Pet Name</Text>
                  <TextInput 
                    className="bg-slate-50 px-4 py-4 rounded-2xl border border-slate-200 text-slate-900 focus:border-violet-500"
                    placeholder="e.g. Luna"
                    value={petData.name}
                    onChangeText={(val) => setPetData({...petData, name: val})}
                  />
                </View>

                <View className="flex-row">
                  <View className="flex-1 mr-2">
                    <Text className="text-sm font-bold text-slate-700 mb-2 ml-1">Species</Text>
                    <View className="flex-row bg-slate-50 rounded-2xl p-1 border border-slate-200">
                      <TouchableOpacity 
                        onPress={() => setPetData({...petData, species: 'Dog'})}
                        className={`flex-1 py-2 rounded-xl items-center ${petData.species === 'Dog' ? 'bg-white shadow-sm' : ''}`}
                      >
                        <Text className={`font-bold ${petData.species === 'Dog' ? 'text-violet-600' : 'text-slate-500'}`}>Dog</Text>
                      </TouchableOpacity>
                      <TouchableOpacity 
                        onPress={() => setPetData({...petData, species: 'Cat'})}
                        className={`flex-1 py-2 rounded-xl items-center ${petData.species === 'Cat' ? 'bg-white shadow-sm' : ''}`}
                      >
                        <Text className={`font-bold ${petData.species === 'Cat' ? 'text-violet-600' : 'text-slate-500'}`}>Cat</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                  <View className="flex-1 ml-2">
                    <Text className="text-sm font-bold text-slate-700 mb-2 ml-1">Weight (lbs)</Text>
                    <TextInput 
                      className="bg-slate-50 px-4 py-4 rounded-2xl border border-slate-200 text-slate-900 focus:border-violet-500"
                      placeholder="e.g. 25"
                      keyboardType="numeric"
                      value={petData.weight}
                      onChangeText={(val) => setPetData({...petData, weight: val})}
                    />
                  </View>
                </View>

                <View>
                  <Text className="text-sm font-bold text-slate-700 mb-2 ml-1">Breed</Text>
                  <TextInput 
                    className="bg-slate-50 px-4 py-4 rounded-2xl border border-slate-200 text-slate-900 focus:border-violet-500"
                    placeholder="e.g. Beagle"
                    value={petData.breed}
                    onChangeText={(val) => setPetData({...petData, breed: val})}
                  />
                </View>
              </View>
            </View>
          )}

          {step === 2 && (
            <View>
              <View className="w-20 h-20 bg-blue-100 rounded-3xl items-center justify-center self-center mb-8">
                <Smartphone size={40} color="#3b82f6" />
              </View>
              <Text className="text-2xl font-bold text-center text-slate-900 mb-2">Connect Device</Text>
              <Text className="text-center text-slate-500 mb-8">Choose your pet's smart collar provider</Text>
              
              <View className="space-y-3 mt-4">
                {['FitBark', 'Whistle', 'Tractive'].map((device) => (
                  <TouchableOpacity 
                    key={device}
                    onPress={() => setStep(3)}
                    className="flex-row items-center justify-between p-5 rounded-2xl border border-slate-100 bg-slate-50"
                  >
                    <Text className="font-bold text-slate-800 text-lg">{device}</Text>
                    <ChevronRight size={20} color="#94a3b8" />
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}

          {step === 3 && (
            <View>
              <View className="w-20 h-20 bg-emerald-100 rounded-3xl items-center justify-center self-center mb-8">
                <CheckCircle2 size={40} color="#10b981" />
              </View>
              <Text className="text-2xl font-bold text-center text-slate-900 mb-2">All Set!</Text>
              <Text className="text-center text-slate-500 mb-8">We've started learning {petData.name}'s baseline.</Text>
              
              <View className="bg-slate-50 p-6 rounded-2xl mt-4">
                <Text className="font-bold text-slate-800 mb-4">What happens next?</Text>
                {[
                  'We ingest historical data from your tracker',
                  'AI builds a personalized behavioral model',
                  'Real-time monitoring begins for anomalies'
                ].map((item, idx) => (
                  <View key={idx} className="flex-row mb-4 items-start">
                    <View className="w-5 h-5 bg-emerald-500 rounded-full items-center justify-center mr-3 mt-0.5">
                      <Text className="text-white text-[10px] font-bold">{idx + 1}</Text>
                    </View>
                    <Text className="text-sm text-slate-600 flex-1">{item}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          <View className="mt-auto pt-10">
            <View className="flex-row gap-3">
              {(step === 1 || step === 2) && (
                <TouchableOpacity 
                  onPress={step === 1 ? () => navigation.goBack() : handleBack}
                  className="flex-1 py-4 rounded-2xl border border-slate-200 items-center justify-center"
                >
                  <Text className="text-slate-600 font-bold text-lg">{step === 1 ? 'Cancel' : 'Back'}</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity 
                onPress={handleNext}
                disabled={createPetMutation.isPending || (step === 1 && !petData.name)}
                className={`flex-[2] py-4 rounded-2xl items-center justify-center shadow-sm ${
                  (step === 1 && !petData.name) || createPetMutation.isPending ? 'bg-violet-400' : 'bg-violet-600'
                }`}
              >
                {createPetMutation.isPending ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text className="text-white font-bold text-lg">
                    {step === 3 ? 'Dashboard' : 'Continue'}
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default OnboardingScreen;
