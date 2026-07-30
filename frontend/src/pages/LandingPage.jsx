import React, { useEffect } from 'react';
import { useApp } from '../context/AppContext.jsx';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, BrainCircuit, Code, Network, Zap } from 'lucide-react';

const POPULAR_ROLES = [
  "AI Engineer", 
  "ML Engineer", 
  "Data Scientist", 
  "LLM Engineer", 
  "Robotics Engineer"
];

export default function LandingPage() {
  const { cancelPendingRequest, updateProfile } = useApp();
  const navigate = useNavigate();

  useEffect(() => {
    cancelPendingRequest();
  }, [cancelPendingRequest]);

  const handleRoleClick = (role) => {
    updateProfile({ learningGoal: role, step: 3 });
    navigate('/onboarding');
  };

  return (
    <div className="min-h-screen bg-[#000000] text-white relative overflow-hidden flex flex-col items-center">
      {/* Vercel-style Ambient Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-600/20 blur-[120px] rounded-full pointer-events-none opacity-50" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-purple-600/10 blur-[100px] rounded-full pointer-events-none" />

      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

      <main className="flex-1 w-full max-w-7xl mx-auto px-6 pt-32 pb-24 relative z-10 flex flex-col items-center">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="text-center flex flex-col items-center max-w-4xl w-full"
        >
          {/* Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md mb-8 hover:bg-white/10 transition-colors cursor-default">
            <Sparkles size={14} className="text-blue-400" />
            <span className="text-xs font-medium text-gray-300 tracking-wide">AI Career Intelligence Platform</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-400 mb-6 leading-tight">
            Build Your <br className="hidden md:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">AI Career Roadmap</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 mb-12 max-w-2xl font-light leading-relaxed">
            Stop guessing your next career move. We parse emerging AI roles and calculate the exact skills you need to land your dream job.
          </p>

          <button 
            className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-white text-black rounded-full font-semibold text-lg transition-transform hover:scale-105 active:scale-95"
            onClick={() => navigate('/onboarding')}
          >
            Start Building
            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

        {/* Popular Roles Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="mt-24 w-full"
        >
          <div className="text-center mb-8">
            <span className="text-sm font-semibold tracking-widest text-gray-500 uppercase">Explore Popular High-Growth Roles</span>
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            {POPULAR_ROLES.map((role, idx) => (
              <motion.button
                key={role}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleRoleClick(role)}
                className="flex items-center gap-3 px-6 py-4 rounded-2xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.08] hover:border-white/20 transition-all cursor-pointer backdrop-blur-sm"
              >
                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <Zap size={14} className="text-blue-400" />
                </div>
                <span className="text-gray-200 font-medium">{role}</span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32 w-full max-w-5xl">
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
          >
            <BrainCircuit size={24} className="text-purple-400 mb-6" />
            <h3 className="text-lg font-semibold text-white mb-3">AI Role Parsing</h3>
            <p className="text-gray-400 text-sm leading-relaxed">Our LLM breaks down ambiguous or emerging job titles into precise, verified production requirements.</p>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
            className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
          >
            <Network size={24} className="text-emerald-400 mb-6" />
            <h3 className="text-lg font-semibold text-white mb-3">Skill Gap Analysis</h3>
            <p className="text-gray-400 text-sm leading-relaxed">Instantly map your current toolbelt against target role expectations to reveal critical missing competencies.</p>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}
            className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
          >
            <Code size={24} className="text-blue-400 mb-6" />
            <h3 className="text-lg font-semibold text-white mb-3">Smart Curation</h3>
            <p className="text-gray-400 text-sm leading-relaxed">Hybrid ML ranking algorithms discover and sort the exact courses you need to close your knowledge gaps.</p>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
