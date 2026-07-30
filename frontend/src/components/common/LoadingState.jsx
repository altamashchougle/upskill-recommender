import React, { useState, useEffect } from 'react';
import { BrainCircuit, CheckCircle2, Circle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const LOADING_STEPS = [
  "Understanding your background",
  "Validating career path",
  "Calculating skill gaps",
  "Ranking courses",
  "Building roadmap"
];

export default function LoadingState() {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev < LOADING_STEPS.length ? prev + 1 : prev));
    }, 1200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative w-full max-w-7xl mx-auto py-12 px-6 min-h-[80vh] flex items-center justify-center">
      
      {/* Skeleton Dashboard Background */}
      <div className="absolute inset-0 z-0 opacity-20 pointer-events-none overflow-hidden flex flex-col pt-12 px-6 gap-8">
        <div className="w-1/3 h-10 bg-white/10 rounded-lg animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 w-full">
          <div className="lg:col-span-8 flex flex-col gap-6">
            <div className="w-full h-48 bg-white/5 rounded-2xl animate-pulse" />
            <div className="w-full h-96 bg-white/5 rounded-2xl animate-pulse" />
          </div>
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="w-full h-[500px] bg-white/5 rounded-2xl animate-pulse" />
          </div>
        </div>
      </div>

      {/* Active Pipeline Modal */}
      <motion.div 
        className="relative z-10 glass-panel p-10 w-full max-w-xl flex flex-col items-center bg-black/80 shadow-[0_0_50px_rgba(0,0,0,0.8)]"
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="absolute top-0 right-0 p-32 bg-blue-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
        
        <motion.div 
          className="w-16 h-16 rounded-2xl bg-white/[0.03] flex items-center justify-center mb-6 border border-white/10"
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        >
          <BrainCircuit size={32} className="text-blue-400" />
        </motion.div>
        
        <h3 className="text-xl font-bold text-white mb-2 text-center tracking-wide">AI Career Intelligence</h3>
        <p className="text-sm text-gray-400 mb-10 text-center">Parsing production requirements...</p>

        <div className="flex flex-col gap-5 w-full relative">
          {/* Vertical progress line connecting steps */}
          <div className="absolute left-[11px] top-4 bottom-4 w-0.5 bg-white/10 z-0" />
          
          <motion.div 
            className="absolute left-[11px] top-4 w-0.5 bg-blue-500 z-0 origin-top"
            initial={{ scaleY: 0 }}
            animate={{ scaleY: Math.min(stepIndex / (LOADING_STEPS.length - 1), 1) }}
            transition={{ duration: 0.5 }}
          />

          {LOADING_STEPS.map((step, idx) => {
            const isCompleted = idx < stepIndex;
            const isActive = idx === stepIndex;

            return (
              <div key={idx} className="flex items-center gap-4 relative z-10">
                <div className="shrink-0 bg-black">
                  {isCompleted ? (
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                      <CheckCircle2 size={24} className="text-blue-400" />
                    </motion.div>
                  ) : isActive ? (
                    <motion.div 
                      animate={{ rotate: 360 }} 
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Circle size={24} className="text-gray-400 border-t-blue-400 border-2 rounded-full" />
                    </motion.div>
                  ) : (
                    <Circle size={24} className="text-gray-700" />
                  )}
                </div>
                <span className={`text-sm font-medium transition-colors duration-300 ${
                  isCompleted ? 'text-gray-300' : 
                  isActive ? 'text-white font-bold' : 
                  'text-gray-600'
                }`}>
                  {step}
                </span>
                
                <AnimatePresence>
                  {isActive && (
                    <motion.span 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="ml-auto text-xs font-bold text-blue-400 uppercase tracking-widest"
                    >
                      Processing
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
