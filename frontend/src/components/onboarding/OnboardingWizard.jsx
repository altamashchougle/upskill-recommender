import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Code2, Target, CheckCircle2 } from 'lucide-react';
import { useApp } from '../../context/AppContext.jsx';
import RoleSelector from './RoleSelector.jsx';
import SkillInput from './SkillInput.jsx';
import TargetCareer from './TargetCareer.jsx';
import { motion, AnimatePresence } from 'framer-motion';

export default function OnboardingWizard() {
  const navigate = useNavigate();
  const { userProfile, updateProfile, analyzeCareerPath, filters } = useApp();
  const [step, setStep] = useState(userProfile.step || 1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const goToStep = (newStep) => {
    setStep(newStep);
    updateProfile({ step: newStep });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubmitWizard = () => {
    setIsSubmitting(true);
    analyzeCareerPath({
      jobRole: userProfile.customRole,
      userSkillsList: userProfile.userSkills,
      goal: userProfile.learningGoal,
      useAI: filters.useAI,
    });
    // Immediately hand over loading state to dashboard
    navigate('/dashboard');
  };

  const variants = {
    enter: (direction) => ({
      x: direction > 0 ? 50 : -50,
      opacity: 0
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: (direction) => ({
      zIndex: 0,
      x: direction < 0 ? 50 : -50,
      opacity: 0
    })
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center py-12 px-4 max-w-3xl mx-auto w-full">
      {/* Stepper Header Bar */}
      <div className="w-full mb-12">
        <div className="flex items-center justify-between relative">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-[2px] bg-white/10 -z-10" />
          
          <div
            className={`flex flex-col items-center gap-3 cursor-pointer transition-all ${step === 1 ? 'opacity-100' : step > 1 ? 'opacity-70 hover:opacity-100' : 'opacity-40 pointer-events-none'}`}
            onClick={() => step > 1 && goToStep(1)}
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${step >= 1 ? 'bg-purple-900 border-purple-400 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.3)]' : 'bg-black border-gray-600 text-gray-500'}`}>
              {step > 1 ? <CheckCircle2 size={20} className="text-emerald-400" /> : <Briefcase size={18} />}
            </div>
            <span className={`text-sm font-semibold tracking-wide uppercase ${step >= 1 ? 'text-purple-300' : 'text-gray-500'}`}>Current Role</span>
          </div>

          <div
            className={`flex flex-col items-center gap-3 cursor-pointer transition-all ${step === 2 ? 'opacity-100' : step > 2 ? 'opacity-70 hover:opacity-100' : 'opacity-40 pointer-events-none'}`}
            onClick={() => (step > 2 || userProfile.customRole) && goToStep(2)}
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${step >= 2 ? 'bg-purple-900 border-purple-400 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.3)]' : 'bg-black border-gray-600 text-gray-500'}`}>
              {step > 2 ? <CheckCircle2 size={20} className="text-emerald-400" /> : <Code2 size={18} />}
            </div>
            <span className={`text-sm font-semibold tracking-wide uppercase ${step >= 2 ? 'text-purple-300' : 'text-gray-500'}`}>Skills</span>
          </div>

          <div className={`flex flex-col items-center gap-3 transition-all ${step === 3 ? 'opacity-100' : 'opacity-40'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${step >= 3 ? 'bg-purple-900 border-purple-400 text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.3)]' : 'bg-black border-gray-600 text-gray-500'}`}>
              <Target size={18} />
            </div>
            <span className={`text-sm font-semibold tracking-wide uppercase ${step >= 3 ? 'text-purple-300' : 'text-gray-500'}`}>Target</span>
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="w-full relative min-h-[400px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial="enter"
            animate="center"
            exit="exit"
            variants={variants}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="w-full absolute inset-0"
          >
            {step === 1 && <RoleSelector onNext={() => goToStep(2)} />}
            {step === 2 && <SkillInput onBack={() => goToStep(1)} onNext={() => goToStep(3)} />}
            {step === 3 && (
              <TargetCareer
                onBack={() => goToStep(2)}
                onSubmit={handleSubmitWizard}
                isSubmitting={isSubmitting}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
