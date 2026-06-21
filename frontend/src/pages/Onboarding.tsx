import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dog, Smartphone, CheckCircle2, ChevronRight, ChevronLeft, Loader2 } from 'lucide-react';
import { createPet } from '../services/petService';

const Onboarding: React.FC = () => {
  const [step, setStep] = useState(1);
  const [petData, setPetData] = useState({
    name: '',
    species: 'Dog',
    breed: '',
    age: '',
    weight: '',
  });
  
  const navigate = useNavigate();
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
      navigate('/');
    }
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setPetData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="mb-12">
        <div className="flex justify-between items-center mb-4">
          {[1, 2, 3].map((s) => (
            <div 
              key={s}
              className={`flex-1 h-2 rounded-full mx-1 ${
                s <= step ? 'bg-violet-600' : 'bg-slate-200'
              }`}
            />
          ))}
        </div>
        <p className="text-center text-slate-500 font-medium">Step {step} of 3</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-3xl p-8 md:p-12 shadow-sm">
        {step === 1 && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-violet-100 rounded-2xl flex items-center justify-center text-violet-600 mx-auto mb-8">
              <Dog size={40} />
            </div>
            <h2 className="text-3xl font-bold text-center text-slate-900">Tell us about your pet</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Pet Name</label>
                <input 
                  type="text" 
                  name="name"
                  value={petData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition-all" 
                  placeholder="e.g. Luna" 
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Species</label>
                  <select
                    name="species"
                    value={petData.species}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition-all"
                  >
                    <option value="Dog">Dog</option>
                    <option value="Cat">Cat</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Breed</label>
                  <input 
                    type="text" 
                    name="breed"
                    value={petData.breed}
                    onChange={handleChange}
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition-all" 
                    placeholder="e.g. Beagle" 
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                 <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">Weight (lbs)</label>
                    <input 
                      type="number" 
                      name="weight"
                      value={petData.weight}
                      onChange={handleChange}
                      className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none transition-all" 
                      placeholder="e.g. 25" 
                    />
                  </div>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-blue-100 rounded-2xl flex items-center justify-center text-blue-600 mx-auto mb-8">
              <Smartphone size={40} />
            </div>
            <h2 className="text-3xl font-bold text-center text-slate-900">Connect Device</h2>
            <p className="text-center text-slate-500">Choose your pet's smart collar provider to sync data</p>
            <div className="grid grid-cols-1 gap-4 mt-8">
              {['FitBark', 'Whistle', 'Tractive'].map((device) => (
                <button 
                  key={device}
                  onClick={() => setStep(3)}
                  className="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:border-violet-500 hover:bg-violet-50 transition-all text-left group"
                >
                  <span className="font-bold text-slate-800">{device}</span>
                  <ChevronRight size={20} className="text-slate-400 group-hover:text-violet-600" />
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-emerald-100 rounded-2xl flex items-center justify-center text-emerald-600 mx-auto mb-8">
              <CheckCircle2 size={40} />
            </div>
            <h2 className="text-3xl font-bold text-center text-slate-900">All Set!</h2>
            <p className="text-center text-slate-500">We've started learning {petData.name}'s baseline. You'll receive your first health summary in 7 days.</p>
            <div className="bg-slate-50 p-6 rounded-2xl mt-8">
              <h4 className="font-bold text-slate-800 mb-2">What happens next?</h4>
              <ul className="space-y-3">
                <li className="flex gap-3 text-sm text-slate-600">
                  <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center text-white text-[10px] shrink-0 mt-0.5">1</div>
                  <span>We ingest historical data from your tracker</span>
                </li>
                <li className="flex gap-3 text-sm text-slate-600">
                  <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center text-white text-[10px] shrink-0 mt-0.5">2</div>
                  <span>AI builds a personalized behavioral model</span>
                </li>
                <li className="flex gap-3 text-sm text-slate-600">
                  <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center text-white text-[10px] shrink-0 mt-0.5">3</div>
                  <span>Real-time monitoring begins for anomalies</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        <div className="flex gap-4 mt-12">
          {step === 1 && (
            <button 
              onClick={() => navigate('/')}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl border border-slate-200 text-slate-600 font-bold hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
          )}
          {step > 1 && step < 3 && (
             <button 
                onClick={handleBack}
                className="flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl border border-slate-200 text-slate-600 font-bold hover:bg-slate-50 transition-colors"
              >
                <ChevronLeft size={20} />
                Back
              </button>
          )}
          {(step === 1 || step === 3) && (
            <button 
              onClick={handleNext}
              disabled={createPetMutation.isPending || (step === 1 && !petData.name)}
              className="flex-[2] bg-violet-600 text-white px-6 py-4 rounded-xl font-bold hover:bg-violet-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {createPetMutation.isPending && <Loader2 className="w-5 h-5 animate-spin" />}
              {step === 3 ? 'Go to Dashboard' : 'Continue'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
