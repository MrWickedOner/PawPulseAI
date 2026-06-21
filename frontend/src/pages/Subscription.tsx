import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Check, ArrowLeft, Shield, Zap, Star, Loader2, Info } from 'lucide-react';
import { getCurrentSubscription, createCheckoutSession } from '../services/subscriptionService';
import type { SubscriptionTier } from '../types';

const plans = [
  {
    id: 'free' as SubscriptionTier,
    name: 'PawPulse Free',
    price: '$0',
    interval: '/mo',
    description: 'Basic tracking for casual pet owners.',
    features: [
      'Single pet profile',
      'Device integration',
      'Real-time activity view',
    ],
    color: 'bg-slate-50',
    borderColor: 'border-slate-200',
    icon: Info,
    iconColor: 'text-slate-500',
  },
  {
    id: 'basic' as SubscriptionTier,
    name: 'PawPulse Basic',
    price: '$9',
    interval: '/mo',
    description: 'Essential health monitoring for your pet.',
    features: [
      'Everything in Free',
      'Anomaly alerts',
      'Weekly health summaries',
      '7-day data history',
    ],
    color: 'bg-blue-50',
    borderColor: 'border-blue-200',
    icon: Shield,
    iconColor: 'text-blue-600',
  },
  {
    id: 'premium' as SubscriptionTier,
    name: 'PawPulse Premium',
    price: '$19',
    interval: '/mo',
    description: 'Advanced insights and predictive trends.',
    features: [
      'Everything in Basic',
      '30-day predictive trendlines',
      'Multi-pet dashboard (up to 5)',
      'Shareable vet reports',
      'Priority support',
    ],
    color: 'bg-violet-50',
    borderColor: 'border-violet-200',
    icon: Star,
    iconColor: 'text-violet-600',
    popular: true,
  },
];

const Subscription: React.FC = () => {
  const navigate = useNavigate();
  const [showProOnboarding, setShowProOnboarding] = useState(false);

  const { data: currentSub, isLoading } = useQuery({
    queryKey: ['currentSubscription'],
    queryFn: getCurrentSubscription,
  });

  const checkoutMutation = useMutation({
    mutationFn: (tier: SubscriptionTier) => 
      createCheckoutSession({
        tier,
        success_url: window.location.origin + '/settings?upgrade=success',
        cancel_url: window.location.origin + '/subscription',
      }),
    onSuccess: (data) => {
      window.location.href = data.checkout_url;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-12 pb-12">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate('/settings')}
          className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-600"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Manage Subscription</h2>
          <p className="text-slate-500">
            {currentSub ? `Current Plan: ${currentSub.tier.toUpperCase()}` : 'Select a plan to get started'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <div 
            key={plan.id}
            className={`relative flex flex-col p-8 rounded-3xl border-2 transition-all ${
              currentSub?.tier === plan.id 
                ? `${plan.borderColor} ${plan.color} shadow-lg scale-105 z-10` 
                : 'border-white bg-white hover:border-slate-100 shadow-sm'
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-violet-600 text-white text-xs font-bold px-3 py-1 rounded-full tracking-wider uppercase">
                Most Popular
              </div>
            )}
            
            <div className={`w-12 h-12 ${plan.iconColor} mb-6 flex items-center justify-center rounded-2xl bg-white shadow-sm`}>
              <plan.icon size={24} />
            </div>

            <h3 className="text-xl font-bold text-slate-900 mb-2">{plan.name}</h3>
            <div className="flex items-baseline gap-1 mb-4">
              <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
              <span className="text-slate-500 font-medium">{plan.interval}</span>
            </div>
            <p className="text-slate-600 text-sm mb-8 leading-relaxed h-12">
              {plan.description}
            </p>

            <ul className="space-y-4 mb-8 flex-1">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-3 text-sm text-slate-600">
                  <div className={`mt-0.5 rounded-full p-0.5 ${currentSub?.tier === plan.id ? 'bg-violet-100 text-violet-600' : 'bg-slate-100 text-slate-400'}`}>
                    <Check size={12} strokeWidth={3} />
                  </div>
                  {feature}
                </li>
              ))}
            </ul>

            <button 
              disabled={currentSub?.tier === plan.id || checkoutMutation.isPending}
              onClick={() => checkoutMutation.mutate(plan.id)}
              className={`w-full py-3 px-4 rounded-xl font-bold transition-all flex items-center justify-center gap-2 ${
                currentSub?.tier === plan.id
                  ? 'bg-slate-100 text-slate-400 cursor-default'
                  : 'bg-violet-600 text-white shadow-md hover:bg-violet-700'
              }`}
            >
              {checkoutMutation.isPending && <Loader2 size={16} className="animate-spin" />}
              {currentSub?.tier === plan.id ? 'Current Plan' : 'Upgrade'}
            </button>
          </div>
        ))}
      </div>

      <div className="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-3xl p-8 text-white flex flex-col md:flex-row items-center justify-between gap-8">
        <div className="space-y-4 text-center md:text-left">
          <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center mb-4 mx-auto md:mx-0">
            <Zap size={24} />
          </div>
          <h3 className="text-2xl font-bold">PawPulse Pro for Veterinarians</h3>
          <p className="opacity-90 max-w-md text-indigo-100">
            White-labeled monitoring for your practice, multi-patient dashboards, and direct client management.
          </p>
        </div>
        <button 
          onClick={() => setShowProOnboarding(true)}
          className="bg-white text-indigo-600 px-8 py-4 rounded-2xl font-bold hover:bg-indigo-50 transition-all whitespace-nowrap shadow-xl shadow-indigo-900/20"
        >
          Explore Pro Tier
        </button>
      </div>

      {showProOnboarding && (
        <div className="bg-white border border-indigo-200 rounded-3xl p-8 shadow-sm space-y-6">
          <h3 className="text-xl font-bold text-slate-900">Register Your Practice</h3>
          <p className="text-slate-500 text-sm">Fill out the details below to request access to the PawPulse Pro portal.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Clinic Name</label>
              <input type="text" className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="e.g. City Veterinary Hospital" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">License Information</label>
              <input type="text" className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="License Number / Region" />
            </div>
            <div className="md:col-span-2 space-y-2">
              <label className="text-sm font-bold text-slate-700">Address</label>
              <input type="text" className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="Street, City, State, ZIP" />
            </div>
          </div>
          <div className="flex justify-end gap-4 pt-4">
            <button 
              onClick={() => setShowProOnboarding(false)}
              className="px-6 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button 
              className="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-indigo-700 transition-all"
              onClick={() => {
                alert('Practice registration request sent!');
                setShowProOnboarding(false);
              }}
            >
              Submit Request
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Subscription;
