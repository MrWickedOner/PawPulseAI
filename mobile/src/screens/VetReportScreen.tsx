import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { FileText, Download, Mail, Calendar } from 'lucide-react-native';

const VetReportScreen = () => {
  const reports = [
    { id: 1, pet: 'Luna', date: 'June 5, 2026', type: 'Anomaly Follow-up' },
    { id: 2, pet: 'Luna', date: 'May 30, 2026', type: 'Monthly Summary' },
    { id: 3, pet: 'Cooper', date: 'May 15, 2026', type: 'Monthly Summary' },
  ];

  return (
    <ScrollView className="flex-1 bg-slate-50 px-6 py-10">
      <View className="mb-8">
        <Text className="text-2xl font-bold text-slate-900">Vet Reports</Text>
        <Text className="text-slate-500 text-sm">Detailed health insights for your veterinarian</Text>
      </View>

      <View className="bg-violet-600 rounded-3xl p-8 mb-8 shadow-md shadow-violet-200">
        <Text className="text-2xl font-bold text-white mb-3">Need a new report?</Text>
        <Text className="text-white opacity-80 mb-8 leading-5">
          Select a pet and date range to generate a comprehensive health PDF.
        </Text>
        <TouchableOpacity className="bg-white py-3 rounded-2xl items-center">
          <Text className="text-violet-600 font-bold text-base">Generate Report</Text>
        </TouchableOpacity>
      </View>

      <View>
        <Text className="text-lg font-bold text-slate-900 mb-4">Recent Reports</Text>
        <View className="space-y-4">
          {reports.map((report) => (
            <View 
              key={report.id}
              className="bg-white border border-slate-100 rounded-2xl p-4 flex-row items-center justify-between"
            >
              <View className="flex-row items-center flex-1">
                <View className="w-12 h-12 bg-slate-50 rounded-xl items-center justify-center mr-4">
                  <FileText size={24} color="#94a3b8" />
                </View>
                <View className="flex-1">
                  <Text className="font-bold text-slate-800 text-base">{report.pet} - {report.type}</Text>
                  <View className="flex-row items-center mt-1">
                    <Calendar size={12} color="#94a3b8" />
                    <Text className="ml-1 text-xs text-slate-400">{report.date}</Text>
                  </View>
                </View>
              </View>
              <View className="flex-row">
                <TouchableOpacity className="p-2 ml-2">
                  <Download size={20} color="#cbd5e1" />
                </TouchableOpacity>
                <TouchableOpacity className="p-2 ml-1">
                  <Mail size={20} color="#cbd5e1" />
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

export default VetReportScreen;
