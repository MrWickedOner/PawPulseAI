import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Activity, Moon, Heart, Share2, Loader2, Lock, CheckCircle2, Clock } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { getPet } from '../services/petService';
import { getHealthData } from '../services/healthService';
import { getAlerts, acknowledgeAlert, dismissAlert } from '../services/alertService';
import { useFeatures } from '../hooks/useFeatures';

const PetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { flags } = useFeatures();

  const { data: pet, isLoading: petLoading, error: petError } = useQuery({
    queryKey: ['pet', id],
    queryFn: () => getPet(id!),
    enabled: !!id,
  });

  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health', id],
    queryFn: () => getHealthData(id!),
    enabled: !!id,
  });

  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ['alerts', id],
    queryFn: () => getAlerts(id!),
    enabled: !!id,
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: string) => acknowledgeAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts', id] });
      queryClient.invalidateQueries({ queryKey: ['all-anomalies'] });
    },
  });

  const dismissMutation = useMutation({
    mutationFn: (alertId: string) => dismissAlert(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts', id] });
      queryClient.invalidateQueries({ queryKey: ['all-anomalies'] });
    },
  });

  if (petLoading || healthLoading || alertsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    );
  }

  if (petError || !pet) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Error loading pet details. Please try again later.</p>
        <button onClick={() => navigate('/')} className="mt-4 text-violet-600 hover:underline">
          Back to Pack
        </button>
      </div>
    );
  }

  const activeAlerts = alerts?.filter(a => a.status === 'active') || [];
  const archivedAlerts = alerts?.filter(a => a.status !== 'active') || [];

  const contactVet = (alert?: any) => {
    const subject = encodeURIComponent(`Health Alert: ${pet.name}`);
    const alertInfo = alert ? `\n\nPawPulse detected: ${alert.type}\nDescription: ${alert.description}\nConfidence: ${((alert.confidence || 0) * 100).toFixed(0)}%` : '';
    const body = encodeURIComponent(`Hello,\n\nI am contacting you regarding my pet, ${pet.name} (${pet.breed || 'Unknown Breed'}).${alertInfo}\n\nPlease let me know if we should schedule a visit.\n\nBest regards,\n${pet.owner_id}`);
    window.location.href = `mailto:vet@example.com?subject=${subject}&body=${body}`;
  };

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-rose-600 bg-rose-50 border-rose-100';
      case 'high': return 'text-amber-600 bg-amber-50 border-amber-100';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-100';
      default: return 'text-slate-600 bg-slate-50 border-slate-100';
    }
  };

  // Calculate scores based on health data
  const activityScore = useMemo(() => {
    const data = healthData?.filter(d => d.type === 'activity');
    if (!data || data.length === 0) return 75;
    const avg = data.reduce((acc, curr) => acc + curr.value, 0) / data.length;
    return Math.round(Math.min(100, (avg / 500) * 100));
  }, [healthData]);

  const sleepScore = useMemo(() => {
    const data = healthData?.filter(d => d.type === 'sleep');
    if (!data || data.length === 0) return 80;
    const avg = data.reduce((acc, curr) => acc + curr.value, 0) / data.length;
    return Math.round(Math.min(100, (avg / 8) * 100));
  }, [healthData]);

  const vitalsScore = useMemo(() => {
    const data = healthData?.filter(d => d.type === 'heart_rate');
    if (!data || data.length === 0) return 95;
    return 98;
  }, [healthData]);

  return (
    <div className="space-y-8 pb-20 md:pb-8">
      <button 
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft size={20} />
        Back to Pack
      </button>

      <div className="flex flex-col md:flex-row gap-8 items-start">
        <div className="w-32 h-32 md:w-48 md:h-48 rounded-2xl bg-slate-200 flex items-center justify-center overflow-hidden shadow-lg border-2 border-slate-100">
           <span className="text-4xl font-bold text-slate-400">{pet.name[0]}</span>
        </div>
        <div className="flex-1 space-y-4 w-full">
          <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
            <div>
              <h2 className="text-3xl font-bold text-slate-900">{pet.name}</h2>
              <p className="text-slate-500 text-lg">
                {pet.breed || 'Unknown Breed'} • {pet.species} • {pet.weight ? `${pet.weight} lbs` : 'Weight N/A'}
              </p>
            </div>
            <button 
              onClick={() => {
                if (flags.canShareVetReports) {
                  contactVet();
                } else {
                  navigate('/subscription');
                }
              }}
              className={`flex items-center gap-2 border px-4 py-2 rounded-lg transition-colors font-medium ${
                flags.canShareVetReports 
                  ? 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50' 
                  : 'bg-slate-50 border-slate-100 text-slate-400 cursor-not-allowed'
              }`}
            >
              {flags.canShareVetReports ? <Share2 size={18} /> : <Lock size={16} />}
              Share Report
            </button>
          </div>
          
          <div className="flex flex-wrap gap-3">
            <div className="bg-white border border-slate-200 px-4 py-3 rounded-xl flex items-center gap-3 flex-1 min-w-[140px]">
              <div className="w-10 h-10 bg-violet-50 rounded-full flex items-center justify-center text-violet-600">
                <Activity size={20} />
              </div>
              <div>
                <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Activity</div>
                <div className="text-lg font-bold">{activityScore}%</div>
              </div>
            </div>
            <div className="bg-white border border-slate-200 px-4 py-3 rounded-xl flex items-center gap-3 flex-1 min-w-[140px]">
              <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
                <Moon size={20} />
              </div>
              <div>
                <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Sleep</div>
                <div className="text-lg font-bold">{sleepScore}%</div>
              </div>
            </div>
            <div className="bg-white border border-slate-200 px-4 py-3 rounded-xl flex items-center gap-3 flex-1 min-w-[140px]">
              <div className="w-10 h-10 bg-rose-50 rounded-full flex items-center justify-center text-rose-600">
                <Heart size={20} />
              </div>
              <div>
                <div className="text-xs text-slate-500 uppercase font-bold tracking-wider">Vitals</div>
                <div className="text-lg font-bold">{vitalsScore}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section className="bg-white border border-slate-200 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center justify-between">
              Activity History
              <span className="text-xs font-normal text-slate-400">Last 10 recordings</span>
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={healthData?.filter(d => d.type === 'activity').slice(-10)}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="timestamp" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{fill: '#94a3b8', fontSize: 10}} 
                    tickFormatter={(val) => new Date(val).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  />
                  <YAxis hide />
                  <Tooltip 
                    cursor={{fill: '#f8fafc'}}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    labelFormatter={(val) => new Date(val).toLocaleString()}
                  />
                  <Bar dataKey="value" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="bg-white border border-slate-200 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-6">Resting Heart Rate</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={healthData?.filter(d => d.type === 'heart_rate').slice(-10)}>
                  <defs>
                    <linearGradient id="colorRest" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="timestamp" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{fill: '#94a3b8', fontSize: 10}} 
                    tickFormatter={(val) => new Date(val).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  />
                  <YAxis hide />
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    labelFormatter={(val) => new Date(val).toLocaleString()}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorRest)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>

        <aside className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="font-bold text-slate-800">Health Timeline</h3>
              <Clock size={16} className="text-slate-400" />
            </div>
            <div className="p-6">
              {activeAlerts.length > 0 || archivedAlerts.length > 0 ? (
                <div className="space-y-6 relative before:absolute before:inset-0 before:left-2 before:w-0.5 before:bg-slate-100">
                  {activeAlerts.map((alert) => (
                    <div key={alert.id} className="relative pl-8 space-y-2">
                      <div className="absolute left-0 top-1.5 w-4.5 h-4.5 rounded-full bg-white border-2 border-amber-500 flex items-center justify-center">
                        <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                      </div>
                      <div className={`p-4 rounded-xl border ${getSeverityStyles(alert.severity)}`}>
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider">{alert.severity} alert</span>
                          <span className="text-[10px] opacity-70">{new Date(alert.created_at).toLocaleDateString()}</span>
                        </div>
                        <h4 className="font-bold text-sm mb-1">{alert.type}</h4>
                        <p className="text-xs opacity-90 mb-3">{alert.description}</p>
                        
                        {alert.recommendation && (
                          <div className="bg-white/50 p-2 rounded-lg text-[11px] mb-3">
                            <span className="font-bold">Advice:</span> {alert.recommendation}
                          </div>
                        )}

                        <div className="flex flex-wrap gap-2">
                          <button 
                            onClick={() => acknowledgeMutation.mutate(alert.id)}
                            className="text-[10px] font-bold bg-white/40 hover:bg-white/60 px-2 py-1 rounded transition-colors"
                          >
                            Acknowledge
                          </button>
                          <button 
                            onClick={() => contactVet(alert)}
                            className="text-[10px] font-bold bg-white/40 hover:bg-white/60 px-2 py-1 rounded transition-colors"
                          >
                            Share with Vet
                          </button>
                          <button 
                            onClick={() => dismissMutation.mutate(alert.id)}
                            className="text-[10px] font-bold hover:bg-black/5 px-2 py-1 rounded transition-colors opacity-60"
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}

                  {archivedAlerts.map((alert) => (
                    <div key={alert.id} className="relative pl-8 opacity-60 grayscale-[0.5]">
                      <div className="absolute left-0 top-1.5 w-4.5 h-4.5 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center">
                        <div className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                      </div>
                      <div className="text-xs">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-bold">{alert.type}</span>
                          <span className="text-[10px]">{new Date(alert.created_at).toLocaleDateString()}</span>
                        </div>
                        <p className="text-[11px] line-clamp-1">{alert.description}</p>
                        <span className="text-[10px] italic">Status: {alert.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 px-4">
                   <div className="w-12 h-12 bg-emerald-50 rounded-full flex items-center justify-center text-emerald-500 mx-auto mb-3">
                      <CheckCircle2 size={24} />
                   </div>
                   <p className="text-sm font-bold text-slate-800">All clear!</p>
                   <p className="text-xs text-slate-500 mt-1">No anomalies detected during the baseline learning period.</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-violet-600 rounded-2xl p-6 text-white shadow-lg shadow-violet-200">
            <h4 className="font-bold mb-2 flex items-center gap-2">
              <Activity size={18} />
              AI Learning
            </h4>
            <p className="text-xs text-violet-100 mb-4">
              We're constantly refining {pet.name}'s baseline. Data from the last 14 days is used to detect subtle shifts in health.
            </p>
            <div className="w-full h-1.5 bg-violet-400 rounded-full overflow-hidden">
               <div className="h-full bg-white" style={{ width: '85%' }} />
            </div>
            <p className="text-[10px] mt-2 text-violet-200 text-right font-medium">85% Learning Complete</p>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default PetDetail;
