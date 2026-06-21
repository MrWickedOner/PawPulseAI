import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Loader2, PlusCircle, Lock, AlertTriangle, ChevronRight, CheckCircle2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getPets } from '../services/petService';
import { getAnomalies } from '../services/alertService';
import { useFeatures } from '../hooks/useFeatures';
import PetCard from '../components/PetCard';

const mockTrendData = [
  { name: 'Mon', value: 400 },
  { name: 'Tue', value: 300 },
  { name: 'Wed', value: 500 },
  { name: 'Thu', value: 280 },
  { name: 'Fri', value: 590 },
  { name: 'Sat', value: 800 },
  { name: 'Sun', value: 750 },
];

const Dashboard: React.FC = () => {
  const { data: pets, isLoading: petsLoading, error } = useQuery({
    queryKey: ['pets'],
    queryFn: getPets,
  });

  const { flags, isLoading: featuresLoading } = useFeatures();

  const { data: activeAnomalies } = useQuery({
    queryKey: ['all-anomalies'],
    queryFn: getAnomalies,
    select: (data) => data.filter(a => a.status === 'active'),
    enabled: !!pets && pets.length > 0,
  });

  const isLoading = petsLoading || featuresLoading;

  const getAlertStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-rose-50 border-rose-100 text-rose-700';
      case 'high': return 'bg-amber-50 border-amber-100 text-amber-700';
      case 'medium': return 'bg-yellow-50 border-yellow-100 text-yellow-700';
      case 'low': return 'bg-blue-50 border-blue-100 text-blue-700';
      default: return 'bg-slate-50 border-slate-100 text-slate-700';
    }
  };

  const getPetName = (petId: string) => pets?.find(p => p.id === petId)?.name || 'Unknown Pet';

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Error loading pets. Please try again later.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {activeAnomalies && activeAnomalies.length > 0 && (
        <section className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
          <div className="bg-slate-50 px-6 py-3 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-800 font-bold text-sm uppercase tracking-wider">
              <AlertTriangle size={16} className="text-amber-500" />
              Active Health Alerts ({activeAnomalies.length})
            </div>
          </div>
          <div className="divide-y divide-slate-100">
            {activeAnomalies.map((alert) => (
              <Link 
                key={alert.id}
                to={`/pet/${alert.pet_id}`}
                className={`flex items-center justify-between p-4 hover:opacity-80 transition-opacity ${getAlertStyles(alert.severity)}`}
              >
                <div className="flex gap-4 items-center">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm uppercase">{alert.severity}</span>
                      <span className="text-slate-400">•</span>
                      <span className="font-bold">{alert.type}</span>
                    </div>
                    <p className="text-sm opacity-90">{getPetName(alert.pet_id)}: {alert.description}</p>
                    {alert.confidence && (
                      <div className="mt-1 flex items-center gap-1.5">
                        <div className="w-16 h-1 bg-black/10 rounded-full overflow-hidden">
                           <div className="h-full bg-current" style={{ width: `${alert.confidence * 100}%` }} />
                        </div>
                        <span className="text-[10px] font-bold">{(alert.confidence * 100).toFixed(0)}% confidence</span>
                      </div>
                    )}
                  </div>
                </div>
                <ChevronRight size={20} className="opacity-50" />
              </Link>
            ))}
          </div>
        </section>
      )}

      {activeAnomalies && activeAnomalies.length === 0 && pets && pets.length > 0 && (
        <section className="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 flex items-center gap-3 text-emerald-800">
          <CheckCircle2 size={20} className="text-emerald-500" />
          <div>
            <p className="font-bold">All clear!</p>
            <p className="text-sm">No health anomalies detected in your pack today.</p>
          </div>
        </section>
      )}

      <section>
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Your Pack</h2>
            <p className="text-slate-500">Real-time health status for your pets</p>
          </div>
          {pets && pets.length >= flags.petLimit ? (
            <Link
              to="/subscription"
              className="bg-slate-100 text-slate-500 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 border border-slate-200"
            >
              <Lock size={16} />
              Add Pet (Limit Reached)
            </Link>
          ) : (
            <Link
              to="/onboarding"
              className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <PlusCircle size={18} />
              Add Pet
            </Link>
          )}
        </div>

        {pets?.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center">
            <p className="text-slate-500 mb-4">You haven't added any pets yet.</p>
            <Link
              to="/onboarding"
              className="text-violet-600 font-medium hover:underline"
            >
              Get started by adding your first pet
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pets?.map((pet) => (
              <PetCard key={pet.id} pet={pet} />
            ))}
          </div>
        )}
      </section>

      <section className="bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="text-lg font-bold text-slate-900 mb-6">Weekly Pack Activity</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={mockTrendData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
              <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                dy={10}
              />
              <YAxis hide />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#7c3aed" 
                strokeWidth={3} 
                dot={{ fill: '#7c3aed', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
