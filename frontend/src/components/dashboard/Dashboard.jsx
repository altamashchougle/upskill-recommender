import React, { useMemo } from 'react';
import { useApp } from '../../context/AppContext.jsx';
import CareerTransitionCard from './CareerTransitionCard.jsx';
import SkillGapCard from './SkillGapCard.jsx';
import RoadmapTimeline from './RoadmapTimeline.jsx';
import RecommendationCard from './RecommendationCard.jsx';
import ErrorState from '../common/ErrorState.jsx';
import LoadingState from '../common/LoadingState.jsx';
import { motion } from 'framer-motion';
import { RefreshCcw } from 'lucide-react';

export default function Dashboard() {
  const { userProfile, recommendationData, filters, analyzeCareerPath } = useApp();

  const {
    allRecommendations,
    careerPath,
    skillGap,
    loading,
    error,
  } = recommendationData;

  const currentRole = userProfile.customRole || careerPath?.current_role || 'Beginner';
  const targetRole = userProfile.learningGoal || (careerPath?.next_roles && careerPath.next_roles[0]) || 'Professional';

  const filteredCourses = useMemo(() => {
    if (!allRecommendations) return [];
    return allRecommendations.filter((course) => {
      if (filters.searchTerm) {
        const term = filters.searchTerm.toLowerCase();
        if (!(course.title || '').toLowerCase().includes(term) &&
            !(course.description || '').toLowerCase().includes(term)) {
          return false;
        }
      }
      return true;
    }).slice(0, 6);
  }, [allRecommendations, filters.searchTerm]);

  const handleRetry = () => {
    analyzeCareerPath({
      jobRole: currentRole,
      userSkillsList: userProfile.userSkills,
      goal: targetRole,
      useAI: filters.useAI,
    });
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState type="error" message={error} onRetry={handleRetry} />;
  if (!allRecommendations.length && !careerPath) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-6">
            <RefreshCcw size={28} className="text-gray-600" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No Results Yet</h3>
          <p className="text-gray-500 text-sm mb-6">
            Head to the Career Roadmap builder to generate your personalized AI career analysis.
          </p>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="max-w-7xl mx-auto py-10 px-6"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-10 gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-white mb-1">AI Career Roadmap</h2>
          <p className="text-gray-500 font-medium">Your personalized path to becoming a <span className="text-gray-200">{targetRole}</span></p>
        </div>
        <button 
          onClick={handleRetry}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-gray-400 hover:text-white text-sm font-medium transition-colors cursor-pointer"
        >
          <RefreshCcw size={14} />
          Regenerate
        </button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 flex flex-col gap-8">
          <CareerTransitionCard 
            currentRole={currentRole} 
            targetRole={targetRole} 
            resolutionMeta={recommendationData.resolutionMeta}
          />
          <RoadmapTimeline roadmap={careerPath?.roadmap} skillGap={skillGap} />
        </div>
        <div className="lg:col-span-4 flex flex-col gap-8">
          <SkillGapCard 
            userSkills={userProfile.userSkills} 
            requiredSkills={careerPath?.required_skills || []} 
            skillGap={skillGap} 
          />
        </div>
      </div>

      {/* Courses */}
      {filteredCourses.length > 0 && (
        <div className="mt-14 pt-10 border-t border-white/5">
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-white mb-1">Recommended Curriculum</h3>
            <p className="text-gray-500 text-sm">Curated resources ranked to bridge your specific skill gap.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course, idx) => (
              <motion.div 
                key={course.course_id || idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 + 0.15 }}
                className="h-full"
              >
                <RecommendationCard recommendation={course} />
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
