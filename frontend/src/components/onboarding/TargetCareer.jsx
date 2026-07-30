import React from 'react';
import { motion } from 'framer-motion';
import { Rocket, ArrowLeft, Bot, Zap } from 'lucide-react';
import { useApp } from '../../context/AppContext.jsx';

const COMMON_TARGETS = [
  'Data Scientist',
  'Machine Learning Engineer',
  'AI Engineer',
  'Senior Developer'
];

export default function TargetCareer({ onBack, onSubmit, isSubmitting }) {
  const { userProfile, updateProfile, filters, updateFilters } = useApp();
  const learningGoal = userProfile.learningGoal;
  const useAI = filters.useAI;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (learningGoal.trim() && !isSubmitting) {
      onSubmit();
    }
  };

  return (
    <motion.div 
      className="w-full"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="flex items-center gap-4 mb-6">
        <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
          <Rocket size={24} className="text-emerald-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">Where are you heading?</h2>
          <p className="text-gray-400 text-sm mt-1">Set your target role and let our AI calculate the exact gap.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="space-y-2 relative group">
          <label className="text-sm font-medium text-gray-300 ml-1">Target Job Title</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Zap size={18} className="text-gray-500 group-focus-within:text-emerald-400 transition-colors" />
            </div>
            <input
              type="text"
              value={learningGoal}
              onChange={(e) => updateProfile({ learningGoal: e.target.value })}
              placeholder="e.g. AI Product Manager, Staff Engineer"
              className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all text-lg"
              autoFocus
            />
          </div>
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-500 ml-1">Popular Targets:</label>
          <div className="flex flex-wrap gap-2">
            {COMMON_TARGETS.map(role => (
              <button
                key={role}
                type="button"
                onClick={() => updateProfile({ learningGoal: role })}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  learningGoal === role 
                  ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 border'
                  : 'bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/20 text-gray-300'
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        {/* AI Analysis Toggle */}
        <div 
          onClick={() => updateFilters({ useAI: !useAI })}
          className={`mt-6 flex items-start gap-4 p-4 rounded-xl cursor-pointer border transition-all ${
            useAI ? 'bg-blue-900/20 border-blue-500/50' : 'bg-white/[0.02] border-white/10 hover:bg-white/[0.04]'
          }`}
        >
          <div className={`shrink-0 p-2 rounded-lg ${useAI ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-800 text-gray-400'}`}>
            <Bot size={20} />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h4 className={`font-semibold ${useAI ? 'text-blue-100' : 'text-gray-300'}`}>Deep AI Analysis</h4>
              
              {/* Custom Toggle Switch */}
              <div className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${useAI ? 'bg-blue-600' : 'bg-gray-700'}`}>
                <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${useAI ? 'translate-x-4.5' : 'translate-x-1'}`} />
              </div>
            </div>
            <p className={`text-xs mt-1 leading-relaxed ${useAI ? 'text-blue-200/70' : 'text-gray-500'}`}>
              Enable Gemini LLM to deeply parse niche or ambiguous career titles and extract hidden production requirements. Recommended for emerging fields.
            </p>
          </div>
        </div>

        <div className="flex gap-4 pt-4">
          <button
            type="button"
            onClick={onBack}
            className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium transition-all"
          >
            <ArrowLeft size={18} />
            Back
          </button>
          <button
            type="submit"
            disabled={!learningGoal.trim() || isSubmitting}
            className="flex-[2] flex items-center justify-center gap-2 py-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:bg-white/5 disabled:text-gray-500 text-white font-bold transition-all relative overflow-hidden"
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Initializing...
              </span>
            ) : (
              <>
                Generate Roadmap
                <Rocket size={18} />
              </>
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
}
