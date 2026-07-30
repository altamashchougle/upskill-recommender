import React from 'react';
import { Calendar, CheckCircle2, ChevronRight, Award } from 'lucide-react';
import { motion } from 'framer-motion';

export default function RoadmapTimeline({ targetRole, skillGap = [], subjects = [], roadmap = null }) {
  
  const phases = roadmap && roadmap.length > 0
    ? roadmap.map((phase, idx) => ({
        id: `phase-${idx}`,
        month: phase.phase || `Phase ${idx + 1}`,
        title: phase.phase.includes(':') ? phase.phase.split(':')[1].trim() : phase.title || phase.phase,
        duration: phase.duration || '4 weeks',
        skills: phase.focus_skills || [],
        description: phase.description || `Master core domain competencies required.`,
      }))
    : [
        {
          id: 'phase-1',
          month: 'Phase 1',
          title: 'Domain Fundamentals',
          duration: '4 weeks',
          skills: skillGap.slice(0, 3),
          description: `Establish solid architectural and mathematical foundations.`,
        },
        {
          id: 'phase-2',
          month: 'Phase 2',
          title: 'Core Competency',
          duration: '4-6 weeks',
          skills: skillGap.slice(3, 6),
          description: `Dive deep into specialized frameworks and complex problem solving.`,
        },
        {
          id: 'phase-3',
          month: 'Phase 3',
          title: 'Production Infrastructure',
          duration: '4 weeks',
          skills: skillGap.slice(6, 9),
          description: `Bridge theory to production by building robust pipelines.`,
        }
      ];

  return (
    <div className="glass-panel w-full flex flex-col gap-8">
      <div className="flex justify-between items-start">
        <div className="flex gap-4">
          <div className="bg-emerald-900/30 p-3 rounded-lg">
            <Calendar size={24} className="text-emerald-400" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Execution Timeline</h3>
            <p className="text-sm text-gray-400">Structured progression phases</p>
          </div>
        </div>
      </div>

      <div className="relative pl-6 border-l border-white/10 ml-4 flex flex-col gap-10">
        {phases.map((phase, idx) => (
          <motion.div 
            key={phase.id} 
            className="relative"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + idx * 0.1 }}
          >
            <div className="absolute -left-[37px] top-1 w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-emerald-400" />
            </div>

            <div className="bg-black/40 border border-white/5 rounded-xl p-5 hover:border-emerald-500/30 transition-colors group">
              <div className="flex justify-between items-center mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-emerald-400 font-bold text-sm tracking-wider uppercase">
                    {phase.month}
                  </span>
                  <span className="text-xs text-gray-500 px-2 py-0.5 rounded bg-white/5 border border-white/10">
                    {phase.duration}
                  </span>
                </div>
              </div>

              <h4 className="text-lg font-bold text-white mb-2 group-hover:text-emerald-400 transition-colors">
                {phase.title}
              </h4>
              <p className="text-sm text-gray-400 mb-4 leading-relaxed">
                {phase.description}
              </p>

              {phase.skills && phase.skills.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {phase.skills.map((skill, sIdx) => (
                    <span key={sIdx} className="text-xs font-medium text-gray-300 px-2.5 py-1 rounded-md bg-white/5 border border-white/10 flex items-center gap-1.5">
                      <CheckCircle2 size={12} className="text-emerald-500" />
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
