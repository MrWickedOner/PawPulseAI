import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, AlertTriangle, Activity, Moon, Footprints, Loader2 } from 'lucide-react';
import { getAlerts } from '../services/alertService';
import type { Pet } from '../types';

interface PetCardProps {
  pet: Pet;
}

const PetCard: React.FC<PetCardProps> = ({ pet }) => {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', pet.id],
    queryFn: () => getAlerts(pet.id),
  });

  const activeAlert = alerts?.find(a => a.status === 'active');
  
  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-rose-600 bg-rose-50 border-rose-100';
      case 'high': return 'text-amber-600 bg-amber-50 border-amber-100';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-100';
      default: return 'text-slate-600 bg-slate-50 border-slate-100';
    }
  };

  const getSeverityBar = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-rose-500';
      case 'high': return 'bg-amber-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <Link
      to={`/pet/${pet.id}`}
      className={`bg-white border rounded-xl p-6 hover:shadow-md transition-shadow group relative overflow-hidden ${
        activeAlert ? 'border-amber-100 shadow-sm' : 'border-slate-200'
      }`}
    >
      {activeAlert && (
        <div className={`absolute top-0 left-0 right-0 h-1 ${getSeverityBar(activeAlert.severity)}`} />
      )}

      <div className="flex justify-between items-start mb-4">
        <div className="flex gap-4">
          <div className="w-16 h-16 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden border-2 border-slate-100">
             <span className="text-2xl font-bold text-slate-400">{pet.name[0]}</span>
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-800">{pet.name}</h3>
            <p className="text-sm text-slate-500">{pet.breed || 'Unknown Breed'}</p>
          </div>
        </div>
        
        {isLoading ? (
          <Loader2 size={14} className="animate-spin text-slate-300" />
        ) : activeAlert ? (
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${getSeverityStyles(activeAlert.severity)}`}>
            <AlertTriangle size={14} />
            {activeAlert.type.toUpperCase()}
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full text-xs font-bold border border-emerald-100">
            <CheckCircle2 size={14} />
            HEALTHY
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4 py-4 border-t border-b border-slate-50">
        <div className="text-center">
          <div className="flex justify-center text-violet-500 mb-1">
            <Activity size={18} />
          </div>
          <div className="text-lg font-bold text-slate-800">--%</div>
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Activity</div>
        </div>
        <div className="text-center">
          <div className="flex justify-center text-blue-500 mb-1">
            <Moon size={18} />
          </div>
          <div className="text-lg font-bold text-slate-800">--%</div>
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Sleep</div>
        </div>
        <div className="text-center">
          <div className="flex justify-center text-orange-500 mb-1">
            <Footprints size={18} />
          </div>
          <div className="text-lg font-bold text-slate-800">--</div>
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">Steps</div>
        </div>
      </div>
      
      {activeAlert && (
        <div className="mt-4 text-xs text-amber-800 bg-amber-50/50 p-2 rounded-lg border border-amber-100 line-clamp-2">
          {activeAlert.description}
        </div>
      )}
    </Link>
  );
};

export default PetCard;
