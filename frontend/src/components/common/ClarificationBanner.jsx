import React, { useState } from 'react';
import { AlertCircle, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';
import { useApp } from '../../context/AppContext.jsx';

export default function ClarificationBanner({ meta }) {
  const { clarifyRole } = useApp();
  const [loadingRole, setLoadingRole] = useState('');
  const [customInput, setCustomInput] = useState('');

  if (!meta || meta.confidence === 'high' || meta.confidence === 'medium-high' || meta.source === 'expansion' || meta.source === 'extracted') {
    return null;
  }

  const handleSelectRole = async (role) => {
    setLoadingRole(role);
    await clarifyRole(role);
    setLoadingRole('');
  };

  const handleSubmitCustom = async (e) => {
    e.preventDefault();
    if (customInput.trim()) {
      await handleSelectRole(customInput.trim());
    }
  };

  const confidenceTitle =
    meta.confidence === 'none'
      ? 'No exact match found — Please select a canonical career path:'
      : meta.confidence === 'low'
      ? 'Broad domain detected — Which specific engineering path do you mean?'
      : meta.source === 'dynamic_cache'
      ? 'Unverified Emerging Role — Select a canonical path or wait for AI validation:'
      : 'Typo Correction detected — Confirm your exact target career path:';

  return (
    <div className={`clarification-banner ${meta.confidence}`}>
      <div className="clarification-header">
        <div className="banner-icon-box">
          <AlertCircle size={20} className="banner-icon" />
        </div>
        <div>
          <h4 className="banner-title">{confidenceTitle}</h4>
          {meta.message && <p className="banner-message">{meta.message}</p>}
        </div>
      </div>

      <div className="clarification-suggestions">
        <span className="suggestions-label">Click to instantly recalculate recommendations:</span>
        <div className="suggestions-chips">
          {meta.suggestions && meta.suggestions.length > 0 ? (
            meta.suggestions.map((sugg, idx) => (
              <button
                key={idx}
                type="button"
                className={`sugg-chip ${loadingRole === sugg ? 'loading' : ''}`}
                onClick={() => handleSelectRole(sugg)}
                disabled={!!loadingRole}
              >
                {loadingRole === sugg ? (
                  <span className="spinner-sm" />
                ) : (
                  <Sparkles size={14} className="sugg-icon" />
                )}
                <span>{sugg}</span>
                <ArrowRight size={14} className="sugg-arrow" />
              </button>
            ))
          ) : (
            <div className="default-suggs">
              {['AI Engineer', 'Machine Learning Engineer', 'Data Scientist', 'Full Stack Developer'].map(
                (role, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="sugg-chip"
                    onClick={() => handleSelectRole(role)}
                    disabled={!!loadingRole}
                  >
                    <Sparkles size={14} className="sugg-icon" />
                    <span>{role}</span>
                  </button>
                )
              )}
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmitCustom} className="clarification-custom-form">
        <input
          type="text"
          className="form-input banner-input"
          placeholder="Or type another exact title (e.g. DevOps Engineer)..."
          value={customInput}
          onChange={(e) => setCustomInput(e.target.value)}
          disabled={!!loadingRole}
        />
        <button
          type="submit"
          className="btn btn-secondary btn-sm"
          disabled={!customInput.trim() || !!loadingRole}
        >
          Update
        </button>
      </form>
    </div>
  );
}
