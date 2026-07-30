import React, { useEffect } from 'react';
import Dashboard from '../components/dashboard/Dashboard.jsx';
import { useApp } from '../context/AppContext.jsx';

export default function DashboardPage() {
  const { userProfile, recommendationData, resetRecommendations } = useApp();

  useEffect(() => {
    // If the user modified their target role but hasn't searched, prevent old dashboard from showing
    if (
      !recommendationData.loading &&
      recommendationData.lastSearchedGoal &&
      recommendationData.lastSearchedGoal !== userProfile.learningGoal
    ) {
      resetRecommendations();
    }
  }, [userProfile.learningGoal, recommendationData.lastSearchedGoal, recommendationData.loading, resetRecommendations]);

  return (
    <div className="flex-1 w-full">
      <Dashboard />
    </div>
  );
}
