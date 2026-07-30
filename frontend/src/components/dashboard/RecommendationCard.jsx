import React, { useState } from 'react';
import { ExternalLink, Star, Clock, BarChart, Sparkles, Building2, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function RecommendationCard({ recommendation }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const title = recommendation.title || 'Untitled Course';
  const provider = recommendation.provider || recommendation.platform || 'Online Provider';
  const url = recommendation.url || '#';
  const rating = Number(recommendation.rating || 0);
  const duration = recommendation.duration || 'Flexible';
  const level = recommendation.level || 'All Levels';
  const price = recommendation.is_paid && recommendation.price > 0 ? `$${Number(recommendation.price).toFixed(2).replace(/\.00$/, '')}` : 'Free';
  const university = recommendation.university || '';

  const whyText = recommendation.why_recommended || recommendation.ai_why_fit || recommendation.ai_gap_solved || 'Fills critical gaps in your target career.';
  const score = recommendation.score ? Math.round(recommendation.score * 100) : null;
  const skillsCovered = recommendation.skills_covered || recommendation.skills_gained || [];

  return (
    <div className="glass-panel h-full flex flex-col hover:border-purple-500/50 hover:shadow-[0_8px_30px_rgb(0,0,0,0.5)] transition-all duration-300 relative group overflow-hidden bg-black/60 p-0">
      
      {/* Top Banner / Match Percentage */}
      <div className="px-6 pt-6 pb-4 border-b border-white/5 relative z-10 flex justify-between items-start">
        <div className="flex flex-col gap-1.5">
          <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-widest rounded bg-white/5 border border-white/10 text-gray-400 w-fit">
            {provider}
          </span>
          {university && (
            <div className="flex items-center gap-1.5 text-xs text-gray-500 mt-1">
              <Building2 size={12} /> {university}
            </div>
          )}
        </div>

        {score && (
          <div className="flex flex-col items-end">
            <span className="text-2xl font-bold text-emerald-400 leading-none drop-shadow-md">
              {score}%
            </span>
            <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-500/70 mt-1">Match</span>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="p-6 flex-grow flex flex-col relative z-10">
        <a href={url} target="_blank" rel="noopener noreferrer" className="block group/link mb-3">
          <h3 className="text-xl font-bold text-white leading-snug group-hover/link:text-purple-400 transition-colors">
            {title}
            <ExternalLink size={16} className="inline-block ml-2 opacity-0 group-hover/link:opacity-100 transition-opacity -mt-1" />
          </h3>
        </a>

        {/* Skill Badges */}
        {skillsCovered.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-5">
            {skillsCovered.slice(0, 3).map((s, i) => (
              <span key={i} className="text-[10px] font-semibold tracking-wide text-gray-300 bg-purple-900/20 border border-purple-500/20 px-2 py-1 rounded">
                {s}
              </span>
            ))}
            {skillsCovered.length > 3 && (
              <span className="text-[10px] font-semibold tracking-wide text-gray-500 bg-white/5 border border-white/10 px-2 py-1 rounded">
                +{skillsCovered.length - 3}
              </span>
            )}
          </div>
        )}

        <div className="grid grid-cols-2 gap-y-3 gap-x-4 mb-6">
          <div className="flex items-center gap-2 text-xs font-medium text-gray-400">
            <BarChart size={14} className="text-gray-500" /> {level}
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-gray-400">
            <Clock size={14} className="text-gray-500" /> {duration}
          </div>
          {rating > 0 && (
            <div className="flex items-center gap-2 text-xs font-medium text-gray-400">
              <Star size={14} className="text-amber-400 fill-amber-400" /> {rating.toFixed(1)}
            </div>
          )}
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
            {price}
          </div>
        </div>

        {/* Expandable Explanation */}
        <div className="mt-auto border-t border-white/5 pt-4">
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center justify-between w-full text-xs font-bold uppercase tracking-widest text-purple-400 hover:text-purple-300 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Sparkles size={12} /> Why Recommended
            </div>
            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
          
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0, marginTop: 0 }}
                animate={{ height: 'auto', opacity: 1, marginTop: 12 }}
                exit={{ height: 0, opacity: 0, marginTop: 0 }}
                className="overflow-hidden"
              >
                <p className="text-sm text-gray-400 leading-relaxed italic border-l-2 border-purple-500/30 pl-3">
                  "{whyText}"
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
