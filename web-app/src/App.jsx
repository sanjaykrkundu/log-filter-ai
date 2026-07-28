import { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [currentView, setCurrentView] = useState('fetcher'); // 'fetcher' or 'analytics'
  const [activeTab, setActiveTab] = useState(() => localStorage.getItem('activeTab') || 'issueId');
  const [query, setQuery] = useState(() => localStorage.getItem('query') || '');
  const [isFetching, setIsFetching] = useState(false);
  const [results, setResults] = useState([]);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const [textSize, setTextSize] = useState(() => localStorage.getItem('textSize') || 'medium');

  // Apply theme and persist to localStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Apply text size and persist
  useEffect(() => {
    document.documentElement.setAttribute('data-text-size', textSize);
    localStorage.setItem('textSize', textSize);
  }, [textSize]);

  // Persist search preferences
  useEffect(() => {
    localStorage.setItem('activeTab', activeTab);
  }, [activeTab]);

  useEffect(() => {
    localStorage.setItem('query', query);
  }, [query]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // Mock Analytics Data
  const stats = {
    totalAnalyzed: 1248,
    successRate: 94.2,
    categories: [
      { name: 'CameraService Crashes', count: 450, percentage: 36 },
      { name: 'ISP Hardware Timeouts', count: 320, percentage: 25 },
      { name: 'Memory Leaks', count: 280, percentage: 22 },
      { name: 'Unknown/Other', count: 198, percentage: 17 }
    ]
  };
  const hoursSaved = (stats.totalAnalyzed * 1.5).toLocaleString(); // 1.5 hours per issue

  const handleFetch = async (e) => {
    e.preventDefault();
    if (!query) return;
    
    setIsFetching(true);
    setResults([]);
    
    try {
      const response = await fetch('http://localhost:8000/api/issues/fetch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: activeTab, query })
      });
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error("Failed to fetch issues", err);
      alert("Failed to connect to backend server.");
    } finally {
      setIsFetching(false);
    }
  };

  const handleAnalyze = async (id) => {
    try {
      const response = await fetch('http://localhost:8000/api/issues/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue_id: id })
      });
      const data = await response.json();
      alert(data.message);
    } catch (err) {
      console.error("Failed to analyze issue", err);
      alert("Failed to connect to backend server.");
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* 1. Navbar */}
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '0.75rem 2rem', 
        backgroundColor: 'var(--card-bg)',
        borderBottom: '1px solid var(--border-color)',
        backdropFilter: 'blur(12px)'
      }}>
        {/* Left: Logo */}
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '1.25rem', margin: 0, background: 'linear-gradient(135deg, var(--text-primary), var(--text-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Log Filter AI
          </h1>
        </div>

        {/* Middle: Fetch Form */}
        <div style={{ flex: 2, display: 'flex', justifyContent: 'center' }}>
          <form onSubmit={handleFetch} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', width: '100%', maxWidth: '600px' }}>
            <div style={{ width: '150px' }}>
              <select 
                className="input-field" 
                style={{ padding: '0.5rem' }}
                value={activeTab} 
                onChange={(e) => {setActiveTab(e.target.value); setQuery('');}}
              >
                <option value="issueId">Issue ID</option>
                <option value="username">Username</option>
                <option value="group">Group</option>
              </select>
            </div>
            <div style={{ flex: 1 }}>
              <input 
                type="text" 
                className="input-field" 
                style={{ padding: '0.5rem' }}
                placeholder={
                  activeTab === 'issueId' ? 'e.g. ISSUE-8492' : 
                  activeTab === 'username' ? 'e.g. jdoe' : 'e.g. Camera-Framework'
                }
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
            <button type="submit" className="btn" disabled={isFetching || !query} style={{ padding: '0.5rem 1rem', minWidth: '100px' }}>
              {isFetching ? 'Fetching...' : 'Fetch'}
            </button>
          </form>
        </div>

        {/* Right: Theme Toggle & Text Size */}
        <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '1rem' }}>
          
          {/* Text Size Controller */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', background: 'rgba(0,0,0,0.05)', padding: '0.25rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '0.25rem', marginRight: '0.25rem' }}>Size:</span>
            <button className={`nav-tab ${textSize === 'small' ? 'active' : ''}`} onClick={() => setTextSize('small')} style={{ padding: '0.25rem 0.5rem', minWidth: '28px', fontSize: '0.7rem' }}>S</button>
            <button className={`nav-tab ${textSize === 'medium' ? 'active' : ''}`} onClick={() => setTextSize('medium')} style={{ padding: '0.25rem 0.5rem', minWidth: '28px', fontSize: '0.8rem' }}>M</button>
            <button className={`nav-tab ${textSize === 'large' ? 'active' : ''}`} onClick={() => setTextSize('large')} style={{ padding: '0.25rem 0.5rem', minWidth: '28px', fontSize: '0.9rem' }}>L</button>
          </div>

          <button onClick={toggleTheme} className="btn btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.875rem' }}>
            {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>
      </header>

      {/* 2. Statusbar */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0.5rem 2rem', 
        backgroundColor: 'var(--status-bar-bg)', 
        borderBottom: '1px solid var(--border-color)',
        fontSize: '0.75rem',
      }}>
        {/* Left: Navigation */}
        <div style={{ display: 'flex', gap: '0.25rem', background: 'rgba(0,0,0,0.05)', padding: '0.25rem', borderRadius: '8px' }}>
          <button 
            className={`nav-tab ${currentView === 'fetcher' ? 'active' : ''}`}
            onClick={() => setCurrentView('fetcher')}
          >
            Issue Fetcher
          </button>
          <button 
            className={`nav-tab ${currentView === 'analytics' ? 'active' : ''}`}
            onClick={() => setCurrentView('analytics')}
          >
            Analytics Data
          </button>
        </div>

        {/* Right: Stats */}
        <div style={{ display: 'flex', gap: '2rem' }}>
          <div><span style={{ color: 'var(--text-secondary)' }}>Total Analyzed: </span><strong style={{ color: 'var(--accent-color)' }}>{stats.totalAnalyzed.toLocaleString()}</strong></div>
          <div><span style={{ color: 'var(--text-secondary)' }}>Success Rate: </span><strong>{stats.successRate}%</strong></div>
          <div><span style={{ color: 'var(--text-secondary)' }}>Man Hours Saved: </span><strong style={{ color: '#10b981' }}>{hoursSaved}h</strong></div>
        </div>
      </div>

      {/* 3. Container */}
      <div className="container" style={{ flex: 1 }}>
        {currentView === 'fetcher' && (
          <section>
            {results.length > 0 ? (
              <div className="data-table-container glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Issue ID</th>
                      <th>Title</th>
                      <th>Component</th>
                      <th>Status</th>
                      <th style={{ textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map(issue => (
                      <tr key={issue.id}>
                        <td style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{issue.id}</td>
                        <td>{issue.title}</td>
                        <td>{issue.component}</td>
                        <td>
                          <span style={{ 
                            padding: '0.25rem 0.5rem', 
                            borderRadius: '4px', 
                            fontSize: '0.75rem',
                            backgroundColor: issue.status === 'Open' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                            color: issue.status === 'Open' ? '#ef4444' : '#3b82f6'
                          }}>
                            {issue.status}
                          </span>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <button 
                            className="btn" 
                            onClick={() => handleAnalyze(issue.id)}
                            style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', background: 'linear-gradient(135deg, #10b981, #059669)' }}
                          >
                            Analyze
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ textAlign: 'center', marginTop: '4rem', color: 'var(--text-secondary)' }}>
                <p>No issues fetched yet. Use the search bar in the navbar to begin.</p>
              </div>
            )}
          </section>
        )}

        {currentView === 'analytics' && (
          <section>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
              <div className="glass-panel metric-card">
                <span className="metric-label">Total Analyzed</span>
                <span className="metric-value">{stats.totalAnalyzed.toLocaleString()}</span>
              </div>
              <div className="glass-panel metric-card">
                <span className="metric-label">Success Rate</span>
                <span className="metric-value">{stats.successRate}%</span>
              </div>
              <div className="glass-panel metric-card" style={{ border: '1px solid var(--accent-color)' }}>
                <span className="metric-label">Man Hours Saved</span>
                <span className="metric-value" style={{ color: '#10b981' }}>{hoursSaved}h</span>
              </div>
            </div>

            <div className="glass-panel">
              <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-primary)' }}>Top Issue Categories</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {stats.categories.map(cat => (
                  <div key={cat.name}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{cat.name}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>{cat.count} ({cat.percentage}%)</span>
                    </div>
                    <div className="progress-track">
                      <div className="progress-fill" style={{ width: `${cat.percentage}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
