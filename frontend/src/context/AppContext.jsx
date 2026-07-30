/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AppContext = createContext();

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://upskill-backend-lynz.onrender.com';
const STORAGE_KEY = 'upskill_saas_session_v1';

const initialProfile = {
  customRole: '',
  userSkills: [],
  learningGoal: '',
  step: 1,
};

const initialRecommendations = {
  allRecommendations: [],
  careerPath: null,
  resolutionMeta: null,
  skillGap: [],
  aiCourses: [],
  loading: false,
  error: '',
  lastUpdated: null,
};

const initialFilters = {
  paidFilter: 'all',
  platformFilter: 'all',
  subjectFilter: 'all',
  levelFilter: 'all',
  durationFilter: 'all',
  searchTerm: '',
  useAI: false,
  currentPage: 1,
};

export function AppProvider({ children }) {
  // Load initial state from localStorage if present
  const loadStoredState = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          userProfile: initialProfile,
          filters: parsed.filters || initialFilters,
        };
      }
    } catch (err) {
      console.warn('Failed to load stored session:', err);
    }
    return {
      userProfile: initialProfile,
      filters: initialFilters,
    };
  };

  const stored = loadStoredState();
  const [userProfile, setUserProfile] = useState(stored.userProfile);
  const [recommendationData, setRecommendationData] = useState(initialRecommendations);
  const [filters, setFilters] = useState(stored.filters);
  
  // Purge local storage strictly
  useEffect(() => {
    // Purge old corrupt sessions strictly on load
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        // If it has userProfile saved, purge the whole thing
        if (parsed.userProfile) {
          localStorage.removeItem(STORAGE_KEY);
          console.warn('PURGED CORRUPTED SESSION DATA FROM LOCALSTORAGE');
        }
      }
    } catch(e) {}
  }, []);

  const activeRequestController = React.useRef(null);
  const currentRequestId = React.useRef(null);

  const [taxonomyData, setTaxonomyData] = useState({
    platforms: [],
    availableSkills: [],
    jobRoles: [],
    loading: true,
    error: null,
  });

  const [apiStatus, setApiStatus] = useState({
    healthy: true,
    geminiAvailable: false,
    url: API_BASE_URL,
  });

  // Sync state changes to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          filters,
        })
      );
    } catch (err) {
      console.warn('Failed to save state to localStorage:', err);
    }
  }, [filters]);

  // Fetch taxonomy and API health on initial load
  useEffect(() => {
    let isMounted = true;

    async function fetchInitialMetadata() {
      try {
        const [healthRes, platformsRes, skillsRes, rolesRes] = await Promise.all([
          fetch(`${API_BASE_URL}/health`).catch(() => null),
          fetch(`${API_BASE_URL}/platforms`).catch(() => null),
          fetch(`${API_BASE_URL}/skills`).catch(() => null),
          fetch(`${API_BASE_URL}/job_roles`).catch(() => null),
        ]);

        if (!isMounted) return;

        if (healthRes && healthRes.ok) {
          const health = await healthRes.json();
          setApiStatus(prev => ({ ...prev, healthy: true, geminiAvailable: health.gemini_available || false }));
        } else {
          setApiStatus(prev => ({ ...prev, healthy: false }));
        }

        const platformsList = platformsRes && platformsRes.ok ? (await platformsRes.json()).platforms || [] : [];
        const skillsList = skillsRes && skillsRes.ok ? (await skillsRes.json()).skills || [] : [];
        const rolesList = rolesRes && rolesRes.ok ? await rolesRes.json() : [];

        setTaxonomyData({
          platforms: platformsList,
          availableSkills: skillsList,
          jobRoles: Array.isArray(rolesList) ? rolesList : [],
          loading: false,
          error: null,
        });
      } catch (err) {
        if (isMounted) {
          setTaxonomyData(prev => ({ ...prev, loading: false, error: err.message }));
          setApiStatus(prev => ({ ...prev, healthy: false }));
        }
      }
    }

    fetchInitialMetadata();
    return () => { isMounted = false; };
  }, []);

  const updateProfile = useCallback((updates) => {
    setUserProfile(prev => ({ ...prev, ...updates }));
  }, []);

  const updateFilters = useCallback((updates) => {
    setFilters(prev => ({ ...prev, ...updates }));
  }, []);

  const clearAllData = useCallback(() => {
    setUserProfile(initialProfile);
    setRecommendationData(initialRecommendations);
    setFilters(initialFilters);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (err) {
      console.warn('Failed to clear storage:', err);
    }
  }, []);

  const resetRecommendations = useCallback(() => {
    setRecommendationData(initialRecommendations);
  }, []);

  const cancelPendingRequest = useCallback(() => {
    if (activeRequestController.current) {
      activeRequestController.current.abort();
      activeRequestController.current = null;
    }
  }, []);

  // Main recommendation engine trigger
  const analyzeCareerPath = useCallback(async ({ jobRole, userSkillsList, goal, useAI = false }) => {
    const targetRoleClean = (goal || jobRole || '').trim();
    if (!targetRoleClean) {
      setRecommendationData(prev => ({ ...prev, error: 'Please specify your target career role.' }));
      return { success: false, error: 'Please specify your target career role.' };
    }

    setRecommendationData({ ...initialRecommendations, loading: true, error: '' });

    try {
      if (activeRequestController.current) {
        activeRequestController.current.abort();
      }
      activeRequestController.current = new AbortController();
      const signal = activeRequestController.current.signal;
      
      const reqId = crypto.randomUUID();
      currentRequestId.current = reqId;

      const skillsParam = Array.isArray(userSkillsList)
        ? userSkillsList.join(',')
        : typeof userSkillsList === 'string'
        ? userSkillsList
        : '';

      // Prepare requests
      const params = new URLSearchParams({
        job_role: jobRole || targetRoleClean,
        user_skills: skillsParam,
        goal: goal || '',
        use_ai: String(useAI),
        top_n: '30',
      });

      const recUrl = `${API_BASE_URL}/recommendations?${params.toString()}`;
      const pathUrl = `${API_BASE_URL}/career_path/${encodeURIComponent(targetRoleClean)}`;

      const fetchOptions = {
        signal,
        headers: { 'Cache-Control': 'no-store' }
      };

      const [recResponse, pathResponse] = await Promise.all([
        fetch(recUrl, fetchOptions),
        fetch(pathUrl, fetchOptions),
      ]);

      if (currentRequestId.current !== reqId) return { success: false, error: 'Request aborted' };

      if (!recResponse.ok) {
        let errMsg = 'Failed to fetch course recommendations.';
        try {
          const errJson = await recResponse.json();
          errMsg = errJson.detail || errMsg;
        } catch { /* ignore */ }
        throw new Error(errMsg);
      }

      const recData = await recResponse.json();
      const pathData = pathResponse.ok ? await pathResponse.json() : null;

      if (currentRequestId.current !== reqId) return { success: false, error: 'Request aborted' };

      // Extract resolution metadata cleanly
      const meta = {
        confidence: recData.confidence || pathData?.confidence || 'high',
        source: recData.source || pathData?.source || 'exact',
        suggestions: recData.suggestions || pathData?.suggestions || [],
        message: recData.message || pathData?.message || '',
      };

      setRecommendationData({
        allRecommendations: recData.recommendations || [],
        careerPath: pathData,
        resolutionMeta: meta,
        skillGap: recData.skill_gap || [],
        aiCourses: [],
        loading: false,
        error: '',
        lastUpdated: new Date().toISOString(),
        lastSearchedGoal: targetRoleClean,
      });

      return { success: true, meta };
    } catch (err) {
      if (err.name === 'AbortError') {
        setRecommendationData(prev => ({ ...prev, loading: false }));
        return { success: false, error: 'Request aborted' };
      }
      console.error('Error analyzing career path:', err);
      
      let finalErrorMessage = err.message || 'An error occurred while generating recommendations.';
      if (finalErrorMessage.includes('Failed to fetch') || finalErrorMessage.includes('NetworkError')) {
        finalErrorMessage = 'Network error: Unable to connect to the backend server. Please check backend availability or CORS settings.';
      }

      setRecommendationData(prev => ({
        ...prev,
        loading: false,
        error: finalErrorMessage,
      }));
      return { success: false, error: err.message };
    }
  }, []);

  // Quick retry / clarification helper
  const clarifyRole = useCallback(async (canonicalRole) => {
    updateProfile({ customRole: canonicalRole, learningGoal: canonicalRole });
    return analyzeCareerPath({
      jobRole: canonicalRole,
      userSkillsList: userProfile.userSkills,
      goal: canonicalRole,
      useAI: filters.useAI,
    });
  }, [updateProfile, analyzeCareerPath, userProfile.userSkills, filters.useAI]);

  return (
    <AppContext.Provider
      value={{
        userProfile,
        updateProfile,
        recommendationData,
        filters,
        updateFilters,
        taxonomyData,
        apiStatus,
        analyzeCareerPath,
        clarifyRole,
        clearAllData,
        resetRecommendations,
        cancelPendingRequest,
        currentRequestId,
        API_BASE_URL,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
