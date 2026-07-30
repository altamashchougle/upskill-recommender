import React, { useEffect } from 'react';
import OnboardingWizard from '../components/onboarding/OnboardingWizard.jsx';
import { useApp } from '../context/AppContext.jsx';

export default function OnboardingPage() {
  const { cancelPendingRequest } = useApp();

  useEffect(() => {
    cancelPendingRequest();
  }, [cancelPendingRequest]);

  return (
    <div className="flex-1 w-full">
      <OnboardingWizard />
    </div>
  );
}
