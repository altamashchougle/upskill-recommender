import React from 'react';
import { Sparkles, ShieldCheck, User, Compass, ArrowDown, Award, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

export default function CareerTransitionCard({ currentRole, targetRole, resolutionMeta }) {
  const confidence = resolutionMeta?.confidence || 'high';
  
  const confidenceConfig = {
    high: { label: 'Verified Career Path', color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-500/30' },
    'medium-high': { label: 'AI Validated Career Path', color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-500/30' },
    medium: { label: 'Emerging Role', color: 'text-purple-400', bg: 'bg-purple-400/10', border: 'border-purple-500/30' },
    low: { label: 'Experimental Path', color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-500/30' }
  };
  
  const conf = confidenceConfig[confidence] || confidenceConfig.medium;

  return (
    <div className="glass-panel w-full relative overflow-hidden flex flex-col items-center">
      <div className="absolute top-0 right-0 p-40 bg-purple-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none" />
      
      {/* Premium Header */}
      <div className="w-full flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-4 relative z-10 border-b border-white/5 pb-6">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-purple-900/40 to-blue-900/40 p-3 rounded-lg border border-white/10">
            <Compass size={24} className="text-purple-400" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white tracking-wide">Career Identity</h3>
            <p className="text-sm text-gray-400">Strategic progression mapping</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${conf.border} ${conf.bg} shadow-lg`}>
          <ShieldCheck size={16} className={conf.color} />
          <span className={`text-sm font-semibold tracking-wide uppercase ${conf.color}`}>{conf.label}</span>
        </div>
      </div>

      {/* Vertical Career Journey */}
      <div className="flex flex-col items-center w-full max-w-lg relative z-10">
        
        {/* Node 1: Current Status */}
        <motion.div 
          className="w-full bg-black/40 border border-white/10 p-4 rounded-xl flex items-center gap-4 hover:border-gray-500/50 transition-colors"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="w-12 h-12 rounded-full bg-gray-800/80 flex items-center justify-center border border-gray-600 shrink-0">
            <User size={20} className="text-gray-400" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1 block">Starting Baseline</span>
            <h4 className="text-lg font-bold text-white leading-none">{currentRole}</h4>
          </div>
        </motion.div>

        {/* Animated Progress Line */}
        <div className="flex flex-col items-center py-2 h-16 w-full">
          <div className="w-[2px] h-full bg-gradient-to-b from-gray-600 via-purple-500 to-purple-500 relative overflow-hidden">
            <motion.div 
              className="absolute top-0 left-0 w-full h-1/2 bg-white/50 blur-[2px]"
              animate={{ y: ['-100%', '200%'] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
            />
          </div>
        </div>

        {/* Node 2: Target Role */}
        <motion.div 
          className="w-full bg-gradient-to-r from-purple-900/30 to-black/40 border border-purple-500/30 p-5 rounded-xl flex items-center gap-4 hover:border-purple-400/50 hover:shadow-[0_0_30px_rgba(168,85,247,0.15)] transition-all relative overflow-hidden"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="absolute right-0 top-0 h-full w-1 bg-purple-500" />
          <div className="w-14 h-14 rounded-full bg-purple-900/50 flex items-center justify-center border border-purple-400 shrink-0 shadow-[0_0_15px_rgba(168,85,247,0.4)]">
            <Sparkles size={24} className="text-purple-300" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-purple-400 mb-1 block flex items-center gap-1">
              Target Destination <Award size={10} />
            </span>
            <h4 className="text-2xl font-bold text-white leading-none drop-shadow-md">{targetRole}</h4>
          </div>
        </motion.div>

        {/* Animated Progress Line 2 */}
        <div className="flex flex-col items-center py-2 h-12 w-full opacity-50">
          <div className="w-[2px] h-full bg-gradient-to-b from-purple-500 to-transparent relative overflow-hidden line-dashed" style={{ backgroundImage: 'linear-gradient(to bottom, #a855f7 50%, transparent 50%)', backgroundSize: '100% 8px' }} />
        </div>

        {/* Node 3: Next Career Level */}
        <motion.div 
          className="w-3/4 bg-black/20 border border-white/5 p-3 rounded-lg flex items-center gap-3 opacity-60"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center border border-gray-800 shrink-0">
            <TrendingUp size={14} className="text-gray-500" />
          </div>
          <div>
            <span className="text-[9px] font-bold uppercase tracking-widest text-gray-600 block">Future Trajectory</span>
            <h4 className="text-sm font-semibold text-gray-400">Senior {targetRole}</h4>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
