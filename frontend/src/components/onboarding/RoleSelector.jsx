import React from 'react';
import { motion } from 'framer-motion';
import { Briefcase, ArrowRight, UserCircle } from 'lucide-react';
import { useApp } from '../../context/AppContext.jsx';

const COMMON_ROLES = [
  'Data Analyst',
  'Software Developer',
  'Python Developer',
  'Frontend Developer'
];

export default function RoleSelector({ onNext }) {
  const { userProfile, updateProfile } = useApp();
  const currentRole = userProfile.customRole;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (currentRole.trim()) onNext();
  };

  return (
    <motion.div 
      className="w-full"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="flex items-center gap-4 mb-6">
        <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
          <UserCircle size={24} className="text-blue-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">What is your current role?</h2>
          <p className="text-gray-400 text-sm mt-1">We use your starting baseline to identify precise skill gaps.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="space-y-2 relative group">
          <label className="text-sm font-medium text-gray-300 ml-1">Current Job Title or Background</label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Briefcase size={18} className="text-gray-500 group-focus-within:text-blue-400 transition-colors" />
            </div>
            <input
              type="text"
              value={currentRole}
              onChange={(e) => updateProfile({ customRole: e.target.value })}
              placeholder="e.g. Data Analyst, Software Engineer, Student"
              className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all text-lg"
              autoFocus
            />
          </div>
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-500 ml-1">Or select a common starting point:</label>
          <div className="flex flex-wrap gap-2">
            {COMMON_ROLES.map(role => (
              <button
                key={role}
                type="button"
                onClick={() => {
                  updateProfile({ customRole: role });
                  onNext();
                }}
                className="px-4 py-2 rounded-lg bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/20 text-gray-300 text-sm font-medium transition-all"
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={!currentRole.trim()}
          className="w-full flex items-center justify-center gap-2 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-white/5 disabled:text-gray-500 text-white font-semibold transition-all group mt-8"
        >
          Continue to Skills
          <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
        </button>
      </form>
    </motion.div>
  );
}
