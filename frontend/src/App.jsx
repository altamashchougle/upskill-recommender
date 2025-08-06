import { useEffect, useState } from 'react';
import './App.css';

// API base URL - will work for both development and production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function Spinner() {
  return <span className="spinner" aria-label="Loading" />;
}

function SuccessCheck() {
  return <span className="success-check" aria-label="Success">✓</span>;
}

function StarRating({ rating }) {
  const stars = [];
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  for (let i = 0; i < 5; i++) {
    if (i < fullStars) {
      stars.push(<span key={i} className="star filled">★</span>);
    } else if (i === fullStars && hasHalfStar) {
      stars.push(<span key={i} className="star half">★</span>);
    } else {
      stars.push(<span key={i} className="star">☆</span>);
    }
  }
  
  return <div className="rating">{stars} <span className="rating-text">({rating.toFixed(1)})</span></div>;
}

function CourseCard({ course }) {
  return (
    <div className="course-card">
      <div className="course-title">
        <a href={course.url} target="_blank" rel="noopener noreferrer">{course.title}</a>
        <span className={`course-provider ${course.provider.toLowerCase()}`}>{course.provider}</span>
        {course.ai_enhanced && <span className="ai-badge">🤖 AI</span>}
      </div>
      {course.description && <div className="course-desc">{course.description}</div>}
      <div className="course-meta">
        <span className="meta">{course.is_paid ? `Paid: $${course.price}` : 'Free'}</span>
        {course.duration && <span className="meta">⏱ {course.duration}</span>}
        {course.level && <span className="meta">Level: {course.level}</span>}
        {course.subject && <span className="meta">Subject: {course.subject}</span>}
        {course.rating && <span className="meta"><StarRating rating={course.rating} /></span>}
      </div>
    </div>
  );
}

function CareerPathCard({ careerPath }) {
  return (
    <div className="career-path-card">
      <h3>Career Path for {careerPath.current_role}</h3>
      <div className="career-progression">
        <div className="current-role">
          <span className="role-badge current">{careerPath.current_role}</span>
        </div>
        <div className="arrow">→</div>
        <div className="next-roles">
          {careerPath.next_roles && careerPath.next_roles.length > 0 ? (
            careerPath.next_roles.map((role, idx) => (
              <span key={idx} className="role-badge next">{role}</span>
            ))
          ) : (
            <span className="role-badge next">Senior {careerPath.current_role}</span>
          )}
        </div>
      </div>
      <div className="required-skills">
        <h4>Key Skills:</h4>
        <div className="skills-list">
          {careerPath.required_skills && careerPath.required_skills.length > 0 ? (
            careerPath.required_skills.map((skill, idx) => (
              <span key={idx} className="skill-tag">{skill}</span>
            ))
          ) : (
            <span className="skill-tag">Technical Skills</span>
          )}
        </div>
      </div>
    </div>
  );
}

function Pagination({ currentPage, totalPages, onPageChange }) {
  const pages = [];
  const maxVisiblePages = 5;
  
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
  
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  return (
    <div className="pagination">
      <button 
        className="pagination-btn"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        ← Previous
      </button>
      
      {startPage > 1 && (
        <>
          <button 
            className="pagination-btn"
            onClick={() => onPageChange(1)}
          >
            1
          </button>
          {startPage > 2 && <span className="pagination-ellipsis">...</span>}
        </>
      )}
      
      {pages.map(page => (
        <button
          key={page}
          className={`pagination-btn ${page === currentPage ? 'active' : ''}`}
          onClick={() => onPageChange(page)}
        >
          {page}
        </button>
      ))}
      
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="pagination-ellipsis">...</span>}
          <button 
            className="pagination-btn"
            onClick={() => onPageChange(totalPages)}
          >
            {totalPages}
          </button>
        </>
      )}
      
      <button 
        className="pagination-btn"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next →
      </button>
    </div>
  );
}

function App() {
  const [platforms, setPlatforms] = useState([]);
  const [availableSkills, setAvailableSkills] = useState([]);
  const [customRole, setCustomRole] = useState('');
  const [userSkills, setUserSkills] = useState('');
  const [learningGoal, setLearningGoal] = useState('');
  const [allRecommendations, setAllRecommendations] = useState([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [careerPath, setCareerPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [paidFilter, setPaidFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [subjectFilter, setSubjectFilter] = useState('all');
  const [levelFilter, setLevelFilter] = useState('all');
  const [durationFilter, setDurationFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [useAI, setUseAI] = useState(false);
  const [aiCourses, setAiCourses] = useState([]);
  const [geminiAvailable, setGeminiAvailable] = useState(false);
  const [currentPage, setCurrentPage] = useState('home');
  const [currentPageNum, setCurrentPageNum] = useState(1);
  const [subjects, setSubjects] = useState([]);
  const [levels, setLevels] = useState([]);
  
  const RECOMMENDATIONS_PER_PAGE = 8;

  // Fetch data from backend
  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE_URL}/platforms`).then(res => res.json()),
      fetch(`${API_BASE_URL}/skills`).then(res => res.json()),
      fetch(`${API_BASE_URL}/`).then(res => res.json())
    ])
    .then(([platformsData, skillsData, apiInfo]) => {
      setPlatforms(platformsData.platforms);
      setAvailableSkills(skillsData.skills);
      setGeminiAvailable(apiInfo.gemini_available);
    })
    .catch(() => setError('Failed to load data. Please ensure the backend is running.'));
  }, []);

  // Dynamic filter updates
  useEffect(() => {
    if (allRecommendations.length === 0) {
      setFilteredRecommendations([]);
      setSubjects([]);
      setLevels([]);
      return;
    }

    let filtered = [...allRecommendations];

    // Apply search filter
    if (searchTerm.trim()) {
      filtered = filtered.filter(course =>
        course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply platform filter
    if (platformFilter !== 'all') {
      filtered = filtered.filter(course => course.provider === platformFilter);
    }

    // Apply paid filter
    if (paidFilter !== 'all') {
      filtered = filtered.filter(course => 
        paidFilter === 'paid' ? course.is_paid : !course.is_paid
      );
    }

    // Apply subject filter
    if (subjectFilter !== 'all') {
      filtered = filtered.filter(course => course.subject === subjectFilter);
    }

    // Apply level filter
    if (levelFilter !== 'all') {
      filtered = filtered.filter(course => course.level === levelFilter);
    }

    // Apply duration filter
    if (durationFilter !== 'all') {
      filtered = filtered.filter(course => {
        const durationHours = parseFloat(course.duration.split(' ')[0]);
        switch (durationFilter) {
          case 'short':
            return durationHours <= 2;
          case 'medium':
            return durationHours > 2 && durationHours <= 5;
          case 'long':
            return durationHours > 5;
          default:
            return true;
        }
      });
    }

    setFilteredRecommendations(filtered);
    setCurrentPageNum(1); // Reset to first page when filters change

    // Update available filter options based on filtered results
    const uniqueSubjects = [...new Set(filtered.map(course => course.subject))].sort();
    const uniqueLevels = [...new Set(filtered.map(course => course.level))].sort();
    
    setSubjects(uniqueSubjects);
    setLevels(uniqueLevels);
  }, [allRecommendations, searchTerm, platformFilter, paidFilter, subjectFilter, levelFilter, durationFilter]);

  // Get current page recommendations
  const getCurrentPageRecommendations = () => {
    const startIndex = (currentPageNum - 1) * RECOMMENDATIONS_PER_PAGE;
    const endIndex = startIndex + RECOMMENDATIONS_PER_PAGE;
    return filteredRecommendations.slice(startIndex, endIndex);
  };

  const totalPages = Math.ceil(filteredRecommendations.length / RECOMMENDATIONS_PER_PAGE);

  // Handle recommend button
  const handleRecommend = async () => {
    if (!customRole.trim()) {
      setError('Please enter a job role');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess(false);
    setAllRecommendations([]);
    setFilteredRecommendations([]);
    setCareerPath(null);
    setAiCourses([]);
    setCurrentPageNum(1);
    
    try {
      // Get career path
      const careerRes = await fetch(`${API_BASE_URL}/career_path/${encodeURIComponent(customRole.trim())}`);
      if (careerRes.ok) {
        const careerData = await careerRes.json();
        setCareerPath(careerData);
      }
      
      // Get AI courses if enabled
      if (useAI && geminiAvailable) {
        try {
          const aiRes = await fetch(`${API_BASE_URL}/ai_courses?job_role=${encodeURIComponent(customRole.trim())}&skills=${encodeURIComponent(userSkills)}`);
          if (aiRes.ok) {
            const aiData = await aiRes.json();
            if (aiData.courses && aiData.courses.length > 0) {
              setAiCourses(aiData.courses);
            }
          }
        } catch (e) {
          console.log("AI courses not available:", e);
        }
      }
      
      // Get recommendations
      let url = `${API_BASE_URL}/recommendations?job_role=${encodeURIComponent(customRole.trim())}`;
      if (paidFilter !== 'all') {
        url += `&paid=${paidFilter === 'paid' ? 'true' : 'false'}`;
      }
      if (platformFilter !== 'all') {
        url += `&platform=${platformFilter}`;
      }
      if (userSkills.trim()) {
        url += `&user_skills=${encodeURIComponent(userSkills)}`;
      }
      if (learningGoal.trim()) {
        url += `&goal=${encodeURIComponent(learningGoal)}`;
      }
      if (useAI) {
        url += `&use_ai=true`;
      }
      
      const res = await fetch(url);
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      
      setAllRecommendations(data.recommendations);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 1200);
    } catch (e) {
      setError('Failed to fetch recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle career card click
  const handleCareerClick = async (careerRole) => {
    setCustomRole(careerRole);
    setCurrentPage('form');
    
    // Auto-recommend courses for this career
    setLoading(true);
    setError('');
    setSuccess(false);
    setAllRecommendations([]);
    setFilteredRecommendations([]);
    setCareerPath(null);
    setAiCourses([]);
    setCurrentPageNum(1);
    
    try {
      // Get career path
      const careerRes = await fetch(`${API_BASE_URL}/career_path/${encodeURIComponent(careerRole)}`);
      if (careerRes.ok) {
        const careerData = await careerRes.json();
        setCareerPath(careerData);
      }
      
      // Get recommendations
      const res = await fetch(`${API_BASE_URL}/recommendations?job_role=${encodeURIComponent(careerRole)}`);
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      
      setAllRecommendations(data.recommendations);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 1200);
    } catch (e) {
      setError('Failed to fetch recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPageNum(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const emptyState = !loading && !error && filteredRecommendations.length === 0 && customRole.trim();
  const currentRecommendations = getCurrentPageRecommendations();

  // Render home page
  if (currentPage === 'home') {
    return (
      <div className="app">
        {/* Header */}
        <header className="app-header">
          <div className="container">
            <h1 className="app-title">Upskill Recommender</h1>
          </div>
        </header>

        {/* Hero Section */}
        <section className="hero">
          <div className="hero-background">
            <div className="gradient-overlay"></div>
          </div>
          <div className="hero-content">
            <div className="hero-left">
              <div className="hero-card">
                <h2>Skills that start careers</h2>
                <p>Introducing Upskill Recommender — focus on the skills and real-world experience that'll get you noticed.</p>
                {geminiAvailable && (
                  <div className="ai-status">
                    <span className="ai-indicator">🤖 AI-Powered with Gemini</span>
                  </div>
                )}
              </div>
            </div>
            <div className="hero-right">
              <div className="hero-people">
                <div className="person">
                  <div className="person-icon">☁️</div>
                  <div className="person-avatar">👩‍💻</div>
                </div>
                <div className="person">
                  <div className="person-icon">📊</div>
                  <div className="person-avatar">👨‍💼</div>
                </div>
                <div className="person">
                  <div className="person-icon">🎮</div>
                  <div className="person-avatar">👩‍🎨</div>
                </div>
                <div className="person">
                  <div className="person-icon">📱</div>
                  <div className="person-avatar">👨‍💻</div>
                </div>
                <div className="person">
                  <div className="person-icon">💼</div>
                  <div className="person-avatar">👩‍💼</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Career Paths Section */}
        <section className="career-paths">
          <div className="container">
            <h2>Ready to reimagine your career?</h2>
            <p>Get the skills and real-world experience employers want with Career Accelerators.</p>
            
            <div className="career-cards">
              <div className="career-card yellow" onClick={() => handleCareerClick("Full Stack Web Developer")}>
                <div className="career-icon">&lt; /&gt;</div>
                <div className="career-avatar">👨‍💻</div>
                <h3>Full Stack Web Developer</h3>
              </div>
              <div className="career-card purple" onClick={() => handleCareerClick("Digital Marketer")}>
                <div className="career-icon">📱</div>
                <div className="career-avatar">👩‍💼</div>
                <h3>Digital Marketer</h3>
              </div>
              <div className="career-card pink" onClick={() => handleCareerClick("Data Scientist")}>
                <div className="career-icon">📊</div>
                <div className="career-avatar">👨‍💼</div>
                <h3>Data Scientist</h3>
              </div>
            </div>
            
            <div className="get-started-section">
              <button 
                className="get-started-button"
                onClick={() => setCurrentPage('form')}
              >
                Get Started
              </button>
            </div>
          </div>
        </section>
      </div>
    );
  }

  // Render form page
  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="container">
          <div className="header-content">
            <button 
              className="nav-button back-button"
              onClick={() => setCurrentPage('home')}
            >
              ← Back
            </button>
            <h1 className="app-title">Upskill Recommender</h1>
            <div className="header-spacer"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <section className="main-content">
        <div className="container">
          <div className="main-card">
            <div className="card">
              <label htmlFor="job-role">Enter your current job role:</label>
              <input
                id="job-role"
                type="text"
                placeholder="e.g., Software Engineer, Data Scientist, Product Manager, etc."
                value={customRole}
                onChange={e => setCustomRole(e.target.value)}
              />
              
              <div className="skills-section">
                <label htmlFor="user-skills">Your current skills (comma-separated):</label>
                <input
                  id="user-skills"
                  type="text"
                  placeholder="e.g., Python, JavaScript, SQL, Leadership"
                  value={userSkills}
                  onChange={e => setUserSkills(e.target.value)}
                />
                <div className="skills-suggestions">
                  <small>Popular skills: {availableSkills.slice(0, 10).join(', ')}...</small>
                </div>
              </div>
              
              <div className="goal-section">
                <label htmlFor="learning-goal">Your learning goal:</label>
                <input
                  id="learning-goal"
                  type="text"
                  placeholder="e.g., become a data analyst, learn React, master Python"
                  value={learningGoal}
                  onChange={e => setLearningGoal(e.target.value)}
                />
              </div>
              
              <div className="search-section">
                <label htmlFor="search-courses">Search courses:</label>
                <input
                  id="search-courses"
                  type="text"
                  placeholder="Search by course title or description..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                />
              </div>
              
              {geminiAvailable && (
                <div className="ai-toggle-section">
                  <label className="ai-toggle">
                    <input
                      type="checkbox"
                      checked={useAI}
                      onChange={e => setUseAI(e.target.checked)}
                    />
                    <span className="ai-toggle-text">🤖 Use AI to enhance recommendations</span>
                  </label>
                  <small className="ai-note">AI will provide enhanced course descriptions and additional insights</small>
                </div>
              )}
              
              <div className="filter-row">
                <div className="filter-group">
                  <label htmlFor="platform-filter">Platform:</label>
                  <select
                    id="platform-filter"
                    value={platformFilter}
                    onChange={e => setPlatformFilter(e.target.value)}
                  >
                    <option value="all">All Platforms</option>
                    {platforms.map(platform => (
                      <option key={platform} value={platform}>{platform}</option>
                    ))}
                  </select>
                </div>
                
                <div className="filter-group">
                  <label htmlFor="paid-filter">Price:</label>
                  <select
                    id="paid-filter"
                    value={paidFilter}
                    onChange={e => setPaidFilter(e.target.value)}
                  >
                    <option value="all">All Courses</option>
                    <option value="free">Free Only</option>
                    <option value="paid">Paid Only</option>
                  </select>
                </div>
                
                {subjects.length > 0 && (
                  <div className="filter-group">
                    <label htmlFor="subject-filter">Subject:</label>
                    <select
                      id="subject-filter"
                      value={subjectFilter}
                      onChange={e => setSubjectFilter(e.target.value)}
                    >
                      <option value="all">All Subjects</option>
                      {subjects.map(subject => (
                        <option key={subject} value={subject}>{subject}</option>
                      ))}
                    </select>
                  </div>
                )}
                
                {levels.length > 0 && (
                  <div className="filter-group">
                    <label htmlFor="level-filter">Level:</label>
                    <select
                      id="level-filter"
                      value={levelFilter}
                      onChange={e => setLevelFilter(e.target.value)}
                    >
                      <option value="all">All Levels</option>
                      {levels.map(level => (
                        <option key={level} value={level}>{level}</option>
                      ))}
                    </select>
                  </div>
                )}
                
                <div className="filter-group">
                  <label htmlFor="duration-filter">Duration:</label>
                  <select
                    id="duration-filter"
                    value={durationFilter}
                    onChange={e => setDurationFilter(e.target.value)}
                  >
                    <option value="all">Any Duration</option>
                    <option value="short">Short (≤2 hours)</option>
                    <option value="medium">Medium (2-5 hours)</option>
                    <option value="long">Long (>5 hours)</option>
                  </select>
                </div>
              </div>
              
              <button onClick={handleRecommend} disabled={!customRole.trim() || loading}>
                {loading ? <Spinner /> : success ? <SuccessCheck /> : 'Get Smart Recommendations'}
              </button>
            </div>
            
            {error && <p className="error-msg">{error}</p>}
            
            <div className="results">
              {careerPath && (
                <div className="career-path-section">
                  <CareerPathCard careerPath={careerPath} />
                </div>
              )}
              
              {aiCourses.length > 0 && (
                <div className="ai-courses-section">
                  <h2>🤖 AI-Generated Course Suggestions</h2>
                  <div className="course-list">
                    {aiCourses.map((course, idx) => (
                      <CourseCard key={`ai-${idx}`} course={course} />
                    ))}
                  </div>
                </div>
              )}
              
              {emptyState && (
                <div className="empty-state">No recommendations yet. Click the button to get started!</div>
              )}
              
              {filteredRecommendations.length > 0 && (
                <>
                  <div className="results-header">
                    <h2>Recommended Courses ({filteredRecommendations.length})</h2>
                    <div className="results-info">
                      Showing {((currentPageNum - 1) * RECOMMENDATIONS_PER_PAGE) + 1} - {Math.min(currentPageNum * RECOMMENDATIONS_PER_PAGE, filteredRecommendations.length)} of {filteredRecommendations.length} courses
                    </div>
                  </div>
                  
                  <div className="course-list">
                    {currentRecommendations.map((course, idx) => (
                      <CourseCard key={idx} course={course} />
                    ))}
                  </div>
                  
                  {totalPages > 1 && (
                    <Pagination 
                      currentPage={currentPageNum}
                      totalPages={totalPages}
                      onPageChange={handlePageChange}
                    />
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
