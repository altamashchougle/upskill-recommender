import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Sparkles, Compass, LayoutDashboard, Menu, X, Activity, Cpu } from 'lucide-react';
import { useApp } from '../context/AppContext.jsx';

export default function Navbar() {
  const { apiStatus, recommendationData } = useApp();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const hasRecommendations = recommendationData.allRecommendations.length > 0 || recommendationData.careerPath;
  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-black/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 no-underline">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600">
            <Sparkles size={16} className="text-white" />
          </div>
          <span className="text-lg font-bold text-white">
            Upskill<span className="text-indigo-400">AI</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          <Link
            to="/"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors no-underline ${
              isActive('/') ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            Home
          </Link>
          <Link
            to="/onboarding"
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors no-underline ${
              isActive('/onboarding') ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Compass size={15} />
            Career Roadmap
          </Link>
          <Link
            to="/dashboard"
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors no-underline ${
              isActive('/dashboard')
                ? 'bg-white/10 text-white'
                : hasRecommendations
                ? 'text-gray-400 hover:text-white hover:bg-white/5'
                : 'text-gray-600 hover:text-gray-400 hover:bg-white/5'
            }`}
          >
            <LayoutDashboard size={15} />
            Dashboard
            {hasRecommendations && (
              <span className="ml-1 h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            )}
          </Link>
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <div
            className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border ${
              apiStatus.healthy
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                : 'border-amber-500/30 bg-amber-500/10 text-amber-400'
            }`}
            title={`API: ${apiStatus.url}`}
          >
            <Activity size={12} />
            {apiStatus.healthy ? 'System Online' : 'Connecting...'}
          </div>

          <button
            onClick={() => navigate('/onboarding')}
            className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition-colors cursor-pointer border-none"
          >
            Build Roadmap
          </button>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden flex items-center justify-center w-9 h-9 rounded-lg bg-white/5 text-gray-400 hover:text-white transition-colors cursor-pointer border-none"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-white/5 bg-black/95 backdrop-blur-xl px-6 py-4 flex flex-col gap-2">
          <Link
            to="/"
            className={`px-4 py-3 rounded-lg text-sm font-medium no-underline ${isActive('/') ? 'bg-white/10 text-white' : 'text-gray-400'}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            Home
          </Link>
          <Link
            to="/onboarding"
            className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium no-underline ${isActive('/onboarding') ? 'bg-white/10 text-white' : 'text-gray-400'}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <Compass size={16} />
            Career Roadmap
          </Link>
          <Link
            to="/dashboard"
            className={`flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium no-underline ${isActive('/dashboard') ? 'bg-white/10 text-white' : 'text-gray-400'}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            <LayoutDashboard size={16} />
            Dashboard
          </Link>
        </div>
      )}
    </header>
  );
}
