import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, BrainCircuit, BookOpenCheck, GitFork, Bot, CheckCircle, TrendingUp, ShieldCheck } from 'lucide-react';
import { useApp } from '../context/AppContext.jsx';

export default function Hero() {
  const navigate = useNavigate();
  const { updateProfile } = useApp();

  const handleQuickLaunch = (currentRole, targetRole, skills) => {
    updateProfile({
      customRole: currentRole,
      userSkills: skills,
      learningGoal: targetRole,
      step: 3
    });
    navigate('/onboarding');
  };

  return (
    <section className="hero-section">
      {/* Subtle Background Glow Elements */}
      <div className="hero-glow hero-glow-primary" />
      <div className="hero-glow hero-glow-secondary" />

      <div className="hero-content">
        <div className="hero-badge">
          <Sparkles size={16} className="badge-icon" />
          <span>Next-Gen AI Career Transition Platform</span>
        </div>

        <h1 className="hero-title">
          Build your personalized <br />
          <span className="gradient-text">AI career roadmap</span>
        </h1>

        <p className="hero-subtitle">
          Discover the exact skills, verified courses, and step-by-step progression required to reach your dream technology role with explainable hybrid recommendation algorithms.
        </p>

        {/* CTA Buttons */}
        <div className="hero-cta-group">
          <button
            className="btn btn-primary btn-lg cta-btn"
            onClick={() => navigate('/onboarding')}
          >
            <span>Create My Career Roadmap</span>
            <ArrowRight size={18} />
          </button>
          <button
            className="btn btn-secondary btn-lg cta-btn-secondary"
            onClick={() => navigate('/dashboard')}
          >
            Explore Live Dashboard
          </button>
        </div>

        {/* Quick Transition Examples */}
        <div className="quick-transitions">
          <span className="quick-label">Popular Career Transitions:</span>
          <div className="transition-chips">
            <button
              className="transition-chip"
              onClick={() => handleQuickLaunch('Data Analyst', 'AI Engineer', ['Python', 'SQL', 'Data Visualization'])}
            >
              <span>Data Analyst</span>
              <ArrowRight size={14} className="chip-arrow" />
              <span className="chip-target">AI Engineer</span>
            </button>
            <button
              className="transition-chip"
              onClick={() => handleQuickLaunch('Software Developer', 'Machine Learning Engineer', ['Python', 'Git', 'REST APIs', 'Docker'])}
            >
              <span>Software Developer</span>
              <ArrowRight size={14} className="chip-arrow" />
              <span className="chip-target">ML Engineer</span>
            </button>
            <button
              className="transition-chip"
              onClick={() => handleQuickLaunch('Python Developer', 'Data Scientist', ['Python', 'SQL', 'Pandas'])}
            >
              <span>Python Dev</span>
              <ArrowRight size={14} className="chip-arrow" />
              <span className="chip-target">Data Scientist</span>
            </button>
          </div>
        </div>

        {/* Stats Strip */}
        <div className="hero-stats">
          <div className="stat-item">
            <TrendingUp size={18} className="stat-icon" />
            <div className="stat-info">
              <span className="stat-value">60+</span>
              <span className="stat-label">Canonical Tech Roles</span>
            </div>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <BrainCircuit size={18} className="stat-icon" />
            <div className="stat-info">
              <span className="stat-value">100%</span>
              <span className="stat-label">Explainable Scoring</span>
            </div>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <ShieldCheck size={18} className="stat-icon" />
            <div className="stat-info">
              <span className="stat-value">Zero</span>
              <span className="stat-label">Off-Domain Bias</span>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Cards Grid */}
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon-wrapper blue">
            <BrainCircuit size={24} />
          </div>
          <h3 className="feature-title">AI Skill Gap Analysis</h3>
          <p className="feature-desc">
            Instantly calculate precise skill deficits between your current engineering toolkit and real-world target industry requirements.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper purple">
            <BookOpenCheck size={24} />
          </div>
          <h3 className="feature-title">Personalized Course Matches</h3>
          <p className="feature-desc">
            Get hybrid-scored course recommendations from top platforms with transparent "Why recommended?" badges and skill mapping.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper emerald">
            <GitFork size={24} />
          </div>
          <h3 className="feature-title">Phased Career Roadmaps</h3>
          <p className="feature-desc">
            Follow structured 3-phase timelines moving systematically from foundational concepts to advanced production architectures.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon-wrapper amber">
            <Bot size={24} />
          </div>
          <h3 className="feature-title">Gemini AI Guidance</h3>
          <p className="feature-desc">
            Leverage Google Gemini LLM for deep explainability, adaptive learning outcomes, and customized career transition advice.
          </p>
        </div>
      </div>
    </section>
  );
}
