import React from 'react';
import { AlertTriangle, RefreshCw, SearchX, Compass } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ErrorState({ type = 'error', message, onRetry }) {
  const navigate = useNavigate();

  if (type === 'no-results') {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh] px-4">
        <div className="glass-panel p-8 md:p-12 text-center max-w-md w-full border-amber-500/20">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto mb-6 text-amber-500">
            <SearchX size={32} />
          </div>
          <h3 className="text-xl font-bold text-white mb-3">No matching courses found</h3>
          <p className="text-gray-400 text-sm mb-8 leading-relaxed">
            {message || 'Try broadening your filter selections (e.g. switching from Paid to All) or adjusting your target career focus.'}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            {onRetry && (
              <button 
                className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium transition-colors flex items-center justify-center gap-2"
                onClick={onRetry}
              >
                <RefreshCw size={16} />
                <span>Reset Filters</span>
              </button>
            )}
            <button 
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-medium transition-colors flex items-center justify-center gap-2"
              onClick={() => navigate('/onboarding')}
            >
              <Compass size={16} />
              <span>Adjust Target</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex items-center justify-center min-h-[60vh] px-4">
      <div className="glass-panel p-8 md:p-12 text-center max-w-md w-full border-red-500/20">
        <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-6 text-red-500">
          <AlertTriangle size={32} />
        </div>
        <h3 className="text-xl font-bold text-white mb-3">Unable to generate recommendations</h3>
        <p className="text-gray-400 text-sm mb-8 leading-relaxed">
          {message || 'The recommendation service encountered an unexpected error. Please verify your internet connection or local API server and retry.'}
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          {onRetry ? (
            <button 
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-red-600/90 hover:bg-red-500 text-white font-semibold transition-all flex items-center justify-center gap-2"
              onClick={onRetry}
            >
              <RefreshCw size={18} />
              <span>Retry Recommendations</span>
            </button>
          ) : (
            <button 
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 border border-white/10 text-white font-semibold transition-all flex items-center justify-center gap-2"
              onClick={() => window.location.reload()}
            >
              <RefreshCw size={18} />
              <span>Reload Page</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
