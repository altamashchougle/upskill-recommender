import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Target, X, Plus, ArrowRight, ArrowLeft } from 'lucide-react';
import { useApp } from '../../context/AppContext.jsx';

const SUGGESTED_SKILLS = ['Python', 'SQL', 'Machine Learning', 'React', 'AWS', 'Docker', 'Git'];

export default function SkillInput({ onNext, onBack }) {
  const { userProfile, updateProfile } = useApp();
  const userSkills = userProfile.userSkills;
  const [inputValue, setInputValue] = useState('');

  const handleAddSkill = (e) => {
    e.preventDefault();
    const skill = inputValue.trim();
    if (skill && !userSkills.includes(skill)) {
      updateProfile({ userSkills: [...userSkills, skill] });
      setInputValue('');
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    updateProfile({ userSkills: userSkills.filter(skill => skill !== skillToRemove) });
  };

  const toggleSkill = (skill) => {
    if (userSkills.includes(skill)) {
      handleRemoveSkill(skill);
    } else {
      updateProfile({ userSkills: [...userSkills, skill] });
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
        <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
          <Target size={24} className="text-purple-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">What's in your current stack?</h2>
          <p className="text-gray-400 text-sm mt-1">List the tools and technologies you already know.</p>
        </div>
      </div>

      <div className="space-y-6">
        <form onSubmit={handleAddSkill} className="relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Plus size={18} className="text-gray-500 group-focus-within:text-purple-400 transition-colors" />
          </div>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="e.g. Python, React, SQL... (Press Enter to add)"
            className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all text-lg"
          />
        </form>

        <div className="min-h-[120px] p-6 rounded-2xl bg-white/[0.02] border border-white/5">
          {userSkills.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-600 text-sm font-medium">
              No skills added yet. Type above to add your first skill.
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              <AnimatePresence>
                {userSkills.map((skill) => (
                  <motion.div
                    key={skill}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-500/20 border border-purple-500/30 text-purple-200 text-sm font-medium"
                  >
                    {skill}
                    <button 
                      onClick={() => handleRemoveSkill(skill)}
                      className="hover:bg-purple-500/30 rounded-full p-0.5 transition-colors"
                    >
                      <X size={14} />
                    </button>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-500 ml-1">Suggested technical skills:</label>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_SKILLS.filter(s => !userSkills.includes(s)).map(skill => (
              <button
                key={skill}
                type="button"
                onClick={() => toggleSkill(skill)}
                className="px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/20 text-gray-400 text-sm transition-all"
              >
                + {skill}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-4 mt-8 pt-4">
          <button
            onClick={onBack}
            className="flex-1 flex items-center justify-center gap-2 py-4 rounded-xl bg-white/5 hover:bg-white/10 text-white font-medium transition-all"
          >
            <ArrowLeft size={18} />
            Back
          </button>
          <button
            onClick={onNext}
            className="flex-[2] flex items-center justify-center gap-2 py-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold transition-all group"
          >
            Continue to Target
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
