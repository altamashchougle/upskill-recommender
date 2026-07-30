import React from 'react';
import { BrainCircuit, CheckCircle2, Zap, AlertTriangle, Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SkillGapCard({ userSkills = [], requiredSkills = [], skillGap = [] }) {
  const ownedList = Array.isArray(userSkills) ? userSkills : [];
  const requiredList = Array.isArray(requiredSkills) && requiredSkills.length > 0 ? requiredSkills : skillGap;
  const missingList = Array.isArray(skillGap) && skillGap.length > 0 ? skillGap : requiredList.filter(r => !ownedList.some(o => o.toLowerCase() === r.toLowerCase()));

  const totalRequiredCount = Math.max(requiredList.length, missingList.length + ownedList.length);
  const ownedCount = Math.min(ownedList.length, totalRequiredCount);
  const completionPercentage = totalRequiredCount > 0 ? Math.round((ownedCount / totalRequiredCount) * 100) : 0;

  // Determine mock priority based on index mapping for missing skills
  const getMissingSkillCard = (skill, index, total) => {
    const ratio = index / Math.max(1, total);
    let priorityConfig;
    
    if (ratio < 0.35) {
      priorityConfig = { label: 'High Priority', color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/30', fill: 'bg-rose-500', width: 'w-[90%]', icon: AlertTriangle };
    } else if (ratio < 0.7) {
      priorityConfig = { label: 'Medium Priority', color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30', fill: 'bg-amber-500', width: 'w-[60%]', icon: Zap };
    } else {
      priorityConfig = { label: 'Low Priority', color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30', fill: 'bg-blue-500', width: 'w-[30%]', icon: Lightbulb };
    }

    const Icon = priorityConfig.icon;

    return (
      <motion.div 
        key={skill}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }}
        className={`w-full p-4 rounded-xl border ${priorityConfig.bg} ${priorityConfig.border} hover:shadow-[0_0_15px_rgba(255,255,255,0.05)] transition-all`}
      >
        <div className="flex justify-between items-start mb-3">
          <h5 className="font-bold text-white text-sm">{skill}</h5>
          <span className={`text-[10px] uppercase tracking-widest font-bold px-2 py-1 rounded bg-black/50 ${priorityConfig.color} flex items-center gap-1`}>
            <Icon size={10} /> {priorityConfig.label}
          </span>
        </div>
        
        {/* Animated Progress indicator */}
        <div className="w-full h-1.5 bg-black/50 rounded-full overflow-hidden">
          <motion.div 
            className={`h-full ${priorityConfig.fill} rounded-full`} 
            initial={{ width: 0 }}
            animate={{ width: priorityConfig.width.replace('w-[', '').replace(']', '') }}
            transition={{ duration: 1, delay: 0.2 + index * 0.1, ease: "easeOut" }}
          />
        </div>
      </motion.div>
    );
  };

  return (
    <div className="glass-panel w-full flex flex-col gap-6 relative overflow-hidden">
      <div className="absolute -top-32 -left-32 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      
      <div className="flex justify-between items-start relative z-10 border-b border-white/5 pb-5">
        <div className="flex gap-3">
          <div className="bg-emerald-900/30 p-2.5 rounded-lg border border-emerald-500/20">
            <BrainCircuit size={20} className="text-emerald-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Visual Intelligence</h3>
            <p className="text-xs text-gray-400">Skill Gap Analysis</p>
          </div>
        </div>
        <div className="text-right flex flex-col items-end">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-emerald-400 leading-none">{completionPercentage}%</span>
            <div className="w-8 h-8 rounded-full border-2 border-emerald-500/30 flex items-center justify-center border-t-emerald-400 transform rotate-45" />
          </div>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Readiness</p>
        </div>
      </div>

      <div className="flex flex-col gap-8 relative z-10">
        
        {/* Missing Skills Section */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Zap size={16} className="text-rose-400" />
            <h4 className="text-sm font-bold tracking-wide text-white uppercase">Missing Competencies ({missingList.length})</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            {missingList.length > 0 ? (
              missingList.map((skill, index) => getMissingSkillCard(skill, index, missingList.length))
            ) : (
              <div className="col-span-full p-6 text-center border border-dashed border-emerald-500/30 rounded-xl bg-emerald-900/10">
                <p className="text-emerald-400 font-medium">You have all required baseline skills!</p>
              </div>
            )}
          </div>
        </div>

        {/* Owned Skills Section */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 size={16} className="text-emerald-400" />
            <h4 className="text-sm font-bold tracking-wide text-white uppercase">Verified Skills ({ownedList.length})</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {ownedList.length > 0 ? ownedList.map((skill, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.02 }}
                className="bg-emerald-900/20 border border-emerald-500/30 text-emerald-300 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 hover:bg-emerald-900/40 transition-colors"
              >
                <CheckCircle2 size={12} className="text-emerald-500" />
                {skill}
              </motion.div>
            )) : (
              <span className="text-xs text-gray-500 italic">No exact matching skills found in baseline.</span>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
