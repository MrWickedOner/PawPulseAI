import React from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { User, Bell, CreditCard, Shield, LogOut, ChevronRight, CheckCircle2, Loader2, Clock, FileText, Zap } from 'lucide-react';
import { logout, getMe } from '../services/authService';
import { getCurrentSubscription, cancelSubscription } from '../services/subscriptionService';
import { getPets } from '../services/petService';

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const upgradeSuccess = searchParams.get('upgrade') === 'success';
  
  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
  });

  const { data: subscription, isLoading: subLoading } = useQuery({
    queryKey: ['currentSubscription'],
    queryFn: getCurrentSubscription,
  });

  const { data: pets } = useQuery({
    queryKey: ['pets'],
    queryFn: getPets,
  });

  const cancelMutation = useMutation({
    mutationFn: cancelSubscription,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentSubscription'] });
      alert('Subscription cancelled successfully.');
    },
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (userLoading || subLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    );
  }

  const petLimit = user?.tier === 'free' ? 1 : user?.tier === 'basic' ? 1 : user?.tier === 'premium' ? 5 : 100;
  const petCount = pets?.length || 0;

  const sections = [
    { name: 'Account', icon: User, desc: user?.email || 'Manage profile', path: '#' },
    { name: 'Notifications', icon: Bell, desc: 'Alerts & summaries', path: '#' },
    { name: 'Privacy & Security', icon: Shield, desc: 'Data & access', path: '#' },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Settings</h2>
          <p className="text-slate-500">Manage your PawPulse experience</p>
        </div>
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 px-4 py-2 text-slate-600 font-bold hover:bg-slate-100 rounded-xl transition-colors border border-slate-200"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>

      {upgradeSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 flex items-center gap-3 text-emerald-800">
          <CheckCircle2 className="text-emerald-500" size={20} />
          <p className="font-medium">Success! Your subscription has been updated.</p>
        </div>
      )}

      {/* Subscription Card */}
      <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm">
        <div className="p-8 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
               <h3 className="text-xl font-bold text-slate-900">Current Plan</h3>
               <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                 user?.tier === 'free' ? 'bg-slate-100 text-slate-600' : 
                 user?.tier === 'premium' ? 'bg-violet-100 text-violet-700' : 'bg-blue-100 text-blue-700'
               }`}>
                 {user?.tier}
               </span>
            </div>
            <p className="text-slate-500 text-sm italic">
              {subscription?.status === 'active' ? 'Renews on ' + new Date(subscription.current_period_end!).toLocaleDateString() : 'Free Tier'}
            </p>
          </div>
          <Link 
            to="/subscription"
            className="bg-violet-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-violet-700 transition-all text-center"
          >
            {user?.tier === 'free' ? 'Upgrade Now' : 'Change Plan'}
          </Link>
        </div>
        
        <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8 bg-slate-50/50">
          <div className="space-y-4">
             <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
               <Zap size={14} />
               Usage
             </h4>
             <div className="space-y-2">
                <div className="flex justify-between text-sm">
                   <span className="text-slate-600">Pets Tracked</span>
                   <span className="font-bold text-slate-900">{petCount} of {petLimit}</span>
                </div>
                <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                   <div 
                     className="bg-violet-500 h-full rounded-full transition-all" 
                     style={{ width: `${Math.min((petCount / petLimit) * 100, 100)}%` }}
                   />
                </div>
             </div>
          </div>

          <div className="space-y-4">
             <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
               <Clock size={14} />
               Billing
             </h4>
             <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                   <div className="w-10 h-10 bg-white rounded-xl border border-slate-200 flex items-center justify-center">
                      <CreditCard size={20} className="text-slate-400" />
                   </div>
                   <div className="text-sm">
                      <p className="font-bold text-slate-800">Visa •••• 4242</p>
                      <p className="text-slate-500">Exp 12/28</p>
                   </div>
                </div>
                <button className="text-sm font-bold text-violet-600 hover:text-violet-700">Edit</button>
             </div>
          </div>
        </div>

        {user?.tier !== 'free' && (
          <div className="px-8 py-4 bg-white border-t border-slate-100 flex justify-between items-center">
             <button 
               onClick={() => {
                 if (confirm('Are you sure you want to cancel your subscription?')) {
                   cancelMutation.mutate();
                 }
               }}
               disabled={cancelMutation.isPending}
               className="text-sm font-bold text-rose-600 hover:text-rose-700 disabled:opacity-50"
             >
               {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Subscription'}
             </button>
             <button className="text-sm font-bold text-slate-400 hover:text-slate-600 flex items-center gap-1">
               <FileText size={14} />
               View Invoices
             </button>
          </div>
        )}
      </div>

      <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-sm">
        {sections.map((section, idx) => (
          <Link 
            key={section.name}
            to={section.path}
            className={`w-full flex items-center gap-6 p-6 text-left hover:bg-slate-50 transition-colors ${
              idx !== sections.length - 1 ? 'border-b border-slate-100' : ''
            }`}
          >
            <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400">
              <section.icon size={24} />
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-slate-800">{section.name}</h4>
              <p className="text-sm text-slate-500">{section.desc}</p>
            </div>
            <ChevronRight className="text-slate-300" size={20} />
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Settings;
