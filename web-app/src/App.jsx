import { useState, useEffect } from 'react';
import config from '../../config/app_config.json';
import './index.css';

const API_BASE = config.frontend.api_base_url;
const WS_BASE = config.frontend.ws_base_url;

function App() {
  const [currentView, setCurrentView] = useState('fetcher'); // 'fetcher' or 'analytics'
  const [activeTab, setActiveTab] = useState(() => localStorage.getItem('activeTab') || 'issueId');
  const [query, setQuery] = useState(() => localStorage.getItem('query') || '');
  const [isFetching, setIsFetching] = useState(false);
  const [results, setResults] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalIssues, setTotalIssues] = useState(0);
  const issuesPerPage = 50;
  
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  const [textSize, setTextSize] = useState(() => localStorage.getItem('textSize') || 'medium');
  const [isAdmin, setIsAdmin] = useState(() => localStorage.getItem('isAdmin') === 'true');
  const [userRole, setUserRole] = useState(() => localStorage.getItem('userRole') || 'VIEWER');
  
  // Users State
  const [usersList, setUsersList] = useState([]);
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newUserRole, setNewUserRole] = useState('VIEWER');
  
  // Analytics State
  const [stats, setStats] = useState({
    totalAnalyzed: 0,
    successRate: 0,
    categories: []
  });

  // Training form states
  const [isNewIssue, setIsNewIssue] = useState(false);
  const [trainIssueId, setTrainIssueId] = useState('');
  const [trainTitle, setTrainTitle] = useState('');
  const [trainComponent, setTrainComponent] = useState('');
  const [trainSnippet, setTrainSnippet] = useState('');
  const [trainMeaning, setTrainMeaning] = useState('');
  const [trainFiles, setTrainFiles] = useState(null);
  const [isTraining, setIsTraining] = useState(false);

  // Analysis states
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzingId, setAnalyzingId] = useState(null);

  // WebSocket for Live Analytics Sync
  useEffect(() => {
    const ws = new WebSocket(WS_BASE);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'analytics_update') {
          fetchAnalytics(); // Silently refresh data
        }
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    };
    return () => ws.close();
  }, []);

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

  // Persist admin state
  useEffect(() => {
    localStorage.setItem('isAdmin', isAdmin);
  }, [isAdmin]);

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

  const handleAdminToggle = async () => {
    if (isAdmin) {
      setIsAdmin(false);
      setUserRole('VIEWER');
      localStorage.removeItem('adminToken');
      localStorage.removeItem('userRole');
      if (currentView === 'training' || currentView === 'users') setCurrentView('fetcher');
    } else {
      const uname = prompt("Enter username (defaults to 'admin'):", "admin");
      if (uname === null) return;
      const pwd = prompt("Enter password:");
      if (pwd !== null) {
        try {
          const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: uname, password: pwd })
          });
          const data = await res.json();
          if (data.status === 'success') {
             localStorage.setItem('adminToken', data.token);
             localStorage.setItem('userRole', data.role);
             setIsAdmin(true);
             setUserRole(data.role);
          } else {
             alert(data.message);
          }
        } catch (e) {
          alert("Failed to connect to login server.");
        }
      }
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_BASE}/users`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` }
      });
      const data = await res.json();
      if (data.status === 'success') {
        setUsersList(data.users);
      }
    } catch (err) {
      console.error("Failed to fetch users");
    }
  };

  useEffect(() => {
    if (currentView === 'users' && userRole === 'SUPER_ADMIN') {
      fetchUsers();
    }
  }, [currentView, userRole]);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({ username: newUsername, password: newPassword, role: newUserRole })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setNewUsername('');
        setNewPassword('');
        fetchUsers();
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Failed to create user");
    }
  };

  const handleDeleteUser = async (id) => {
    if (!window.confirm("Delete this user?")) return;
    try {
      const res = await fetch(`${API_BASE}/users/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('adminToken')}` }
      });
      const data = await res.json();
      if (data.status === 'success') {
        fetchUsers();
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Failed to delete user");
    }
  };

  // Fetch real analytics data
  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/analytics`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch analytics", err);
    }
  };

  useEffect(() => {
    // Refresh analytics when switching views or after an analysis completes
    fetchAnalytics();
  }, [currentView, analysisResult]);

  const hoursSaved = (stats.totalAnalyzed * 1.5).toLocaleString(); // 1.5 hours per issue

  const handleFetch = async (e, pageOverride = 1) => {
    if (e) e.preventDefault();
    if (!query) return;
    
    setIsFetching(true);
    setResults([]);
    
    try {
      const response = await fetch(`${API_BASE}/issues/fetch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: activeTab, query, page: pageOverride, limit: issuesPerPage })
      });
      const data = await response.json();
      setResults(data.issues || []);
      setTotalIssues(data.total || 0);
      setCurrentPage(data.page || 1);
    } catch (err) {
      console.error("Failed to fetch issues", err);
      alert("Failed to connect to backend server.");
    } finally {
      setIsFetching(false);
    }
  };

  const handleAnalyze = async (id) => {
    setAnalyzingId(id);
    try {
      const response = await fetch(`${API_BASE}/issues/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue_id: id })
      });
      const data = await response.json();
      if (data.status === 'success') {
        setAnalysisResult(data.data);
      } else {
        alert(data.message);
      }
    } catch (err) {
      console.error("Failed to analyze issue", err);
      alert("Failed to connect to backend server.");
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleTrainSubmit = async (e) => {
    e.preventDefault();
    if (!trainSnippet || !trainMeaning) {
      alert("Please provide the log snippet and meaning.");
      return;
    }
    if (isNewIssue && (!trainTitle || !trainComponent)) {
      alert("Please provide a title and component for the new issue.");
      return;
    }
    if (!isNewIssue && !trainIssueId) {
      alert("Please provide the target Issue ID.");
      return;
    }
    
    setIsTraining(true);
    try {
      const formData = new FormData();
      formData.append('issue_id', trainIssueId || "AUTO-GENERATE");
      formData.append('is_new_issue', isNewIssue);
      formData.append('title', trainTitle || "");
      formData.append('component', trainComponent || "");
      formData.append('snippet', trainSnippet);
      formData.append('meaning', trainMeaning);
      
      if (trainFiles) {
        for (let i = 0; i < trainFiles.length; i++) {
          formData.append('files', trainFiles[i]);
        }
      }

      const token = localStorage.getItem('adminToken');
      const response = await fetch(`${API_BASE}/train`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      
      if (response.status === 401) {
          alert("Session expired or invalid token. Please log in again.");
          setIsAdmin(false);
          localStorage.removeItem('adminToken');
          setCurrentView('fetcher');
          return;
      }
      
      const data = await response.json();
      if (data.status === 'success') {
          alert(data.message);
          setTrainSnippet('');
          setTrainMeaning('');
          setTrainTitle('');
          setTrainFiles(null);
      } else {
          alert(data.message);
      }
    } catch (err) {
      console.error("Failed to submit training data", err);
      alert("Failed to connect to backend server.");
    } finally {
      setIsTraining(false);
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
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <img src="/logo.svg" alt="Log Filter AI Logo" style={{ width: '32px', height: '32px', borderRadius: '6px' }} />
          <h1 style={{ fontSize: '1.25rem', margin: 0, background: 'linear-gradient(135deg, var(--text-primary), var(--text-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Log Filter AI
          </h1>
        </div>

        {/* Middle: Fetch Form */}
        <div style={{ flex: 2, display: 'flex', justifyContent: 'center' }}>
          <form onSubmit={(e) => handleFetch(e, 1)} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', width: '100%', maxWidth: '600px' }}>
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
            <button className={`nav-tab ${textSize === 'small' ? 'active' : ''}`} onClick={() => setTextSize('small')} style={{ padding: '0.25rem 0.5rem', minWidth: '28px', fontSize: '0.7rem' }}>S</button>
            <button className={`nav-tab ${textSize === 'medium' ? 'active' : ''}`} onClick={() => setTextSize('medium')} style={{ padding: '0.25rem 0.5rem', minWidth: '28px', fontSize: '0.8rem' }}>M</button>
            <button className={`nav-tab ${textSize === 'large' ? 'active' : ''}`} onClick={() => setTextSize('large')} style={{ padding: '0.25rem 0.5rem', minWidth: '28px', fontSize: '0.9rem' }}>L</button>
          </div>

          <button onClick={toggleTheme} className="btn btn-secondary" style={{ padding: '0.4rem 0.6rem', fontSize: '1rem', border: 'none' }} title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
          
          {/* Admin Lock */}
          <button 
            onClick={handleAdminToggle} 
            className="btn btn-secondary" 
            style={{ padding: '0.4rem 0.6rem', fontSize: '1rem', border: 'none' }}
            title={isAdmin ? "Logout Admin" : "Admin Login"}
          >
            {isAdmin ? '🔓' : '🔒'}
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
          {isAdmin && (userRole === 'SUPER_ADMIN' || userRole === 'EDITOR') && (
            <button 
              className={`nav-tab ${currentView === 'training' ? 'active' : ''}`}
              onClick={() => setCurrentView('training')}
              style={{ color: 'var(--accent-color)', fontWeight: 'bold' }}
            >
              ⚙️ Training Console
            </button>
          )}
          {isAdmin && userRole === 'SUPER_ADMIN' && (
            <button 
              className={`nav-tab ${currentView === 'users' ? 'active' : ''}`}
              onClick={() => setCurrentView('users')}
              style={{ color: '#8b5cf6', fontWeight: 'bold' }}
            >
              👥 Users
            </button>
          )}
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
              <>
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
                            disabled={analyzingId === issue.id}
                            style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem', background: 'linear-gradient(135deg, #10b981, #059669)' }}
                          >
                            {analyzingId === issue.id ? 'Analyzing...' : 'Analyze'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Pagination Controls */}
              {totalIssues > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', padding: '0 1rem' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                    Showing {(currentPage - 1) * issuesPerPage + 1} - {Math.min(currentPage * issuesPerPage, totalIssues)} of {totalIssues} issues
                  </span>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      className="btn btn-secondary" 
                      disabled={currentPage === 1 || isFetching}
                      onClick={() => handleFetch(null, currentPage - 1)}
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                    >
                      Previous
                    </button>
                    <button 
                      className="btn btn-secondary" 
                      disabled={currentPage * issuesPerPage >= totalIssues || isFetching}
                      onClick={() => handleFetch(null, currentPage + 1)}
                      style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
              </>
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

        {currentView === 'training' && isAdmin && (
          <section>
            <div className="glass-panel" style={{ maxWidth: '800px', margin: '0 auto' }}>
              <h2 style={{ marginBottom: '0.5rem', color: 'var(--accent-color)' }}>Admin Training Console</h2>
              <p style={{ marginBottom: '2rem' }}>Feed manual log snippets and their root cause meanings to continuously improve the AI agent.</p>
              
              <form onSubmit={handleTrainSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input 
                    type="checkbox" 
                    id="newIssueToggle"
                    checked={isNewIssue}
                    onChange={(e) => setIsNewIssue(e.target.checked)}
                    style={{ width: '1.2rem', height: '1.2rem', cursor: 'pointer' }}
                  />
                  <label htmlFor="newIssueToggle" style={{ fontWeight: '500', cursor: 'pointer' }}>Define a New Issue Type</label>
                </div>

                {!isNewIssue ? (
                  <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Target Issue ID</label>
                    <input 
                      type="text" 
                      className="input-field" 
                      placeholder="e.g. ISSUE-8492"
                      value={trainIssueId}
                      onChange={(e) => setTrainIssueId(e.target.value)}
                    />
                  </div>
                ) : (
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <div style={{ flex: 2 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>New Issue Title</label>
                      <input 
                        type="text" 
                        className="input-field" 
                        placeholder="e.g. Memory Leak in ISP node"
                        value={trainTitle}
                        onChange={(e) => setTrainTitle(e.target.value)}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Component</label>
                      <input 
                        type="text" 
                        className="input-field" 
                        placeholder="e.g. Camera"
                        value={trainComponent}
                        onChange={(e) => setTrainComponent(e.target.value)}
                      />
                    </div>
                  </div>
                )}
                
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Raw Log Snippet</label>
                  <textarea 
                    className="input-field" 
                    style={{ minHeight: '150px', fontFamily: 'monospace', fontSize: '0.875rem', resize: 'vertical' }}
                    placeholder="Paste the confusing logcat lines here..."
                    value={trainSnippet}
                    onChange={(e) => setTrainSnippet(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Meaning / Root Cause</label>
                  <textarea 
                    className="input-field" 
                    style={{ minHeight: '100px', resize: 'vertical' }}
                    placeholder="Explain what this log snippet actually means to train the AI..."
                    value={trainMeaning}
                    onChange={(e) => setTrainMeaning(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>Attach Files (Optional)</label>
                  <input 
                    type="file" 
                    multiple
                    className="input-field" 
                    onChange={(e) => setTrainFiles(e.target.files)}
                  />
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Upload full logcats, bugreports, or dumpstates</p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                  <button type="submit" className="btn" disabled={isTraining} style={{ padding: '0.75rem 2rem' }}>
                    {isTraining ? 'Training AI...' : 'Submit to AI Agent'}
                  </button>
                </div>
              </form>
            </div>
          </section>
        )}
        
        {currentView === 'users' && isAdmin && userRole === 'SUPER_ADMIN' && (
          <section>
            <div className="glass-panel" style={{ maxWidth: '800px', margin: '0 auto' }}>
              <h2 style={{ marginBottom: '1.5rem', color: '#8b5cf6' }}>User Management</h2>
              
              <form onSubmit={handleCreateUser} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', alignItems: 'flex-end' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Username</label>
                  <input type="text" className="input-field" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} required />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Password</label>
                  <input type="password" className="input-field" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Role</label>
                  <select className="input-field" value={newUserRole} onChange={(e) => setNewUserRole(e.target.value)}>
                    <option value="VIEWER">VIEWER</option>
                    <option value="EDITOR">EDITOR</option>
                    <option value="SUPER_ADMIN">SUPER_ADMIN</option>
                  </select>
                </div>
                <button type="submit" className="btn" style={{ padding: '0.75rem 1.5rem', background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }}>Add User</button>
              </form>

              <table className="data-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Role</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {usersList.map(u => (
                    <tr key={u.id}>
                      <td style={{ fontWeight: 'bold' }}>{u.username}</td>
                      <td>
                        <span style={{ 
                          padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem',
                          background: u.role === 'SUPER_ADMIN' ? 'rgba(139, 92, 246, 0.2)' : u.role === 'EDITOR' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                          color: u.role === 'SUPER_ADMIN' ? '#8b5cf6' : u.role === 'EDITOR' ? '#10b981' : '#9ca3af'
                        }}>{u.role}</span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {u.username !== 'admin' && (
                          <button onClick={() => handleDeleteUser(u.id)} className="btn btn-secondary" style={{ padding: '0.3rem 0.6rem', color: '#ef4444' }}>Delete</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>

      {/* AI Analysis Modal */}
      {analysisResult && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel" style={{ width: '90%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ margin: 0, color: 'var(--text-primary)' }}>AI Root Cause Analysis</h2>
              <button className="btn btn-secondary" onClick={() => setAnalysisResult(null)} style={{ padding: '0.4rem 0.8rem' }}>Close</button>
            </div>
            
            {(!analysisResult.findings || analysisResult.findings.length === 0) ? (
              <p style={{ color: 'var(--text-secondary)' }}>No actionable errors found in the dumpstate.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {analysisResult.findings.map((finding, idx) => (
                  <div key={idx} style={{ padding: '1rem', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'rgba(0,0,0,0.02)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                      <span style={{ 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '4px', 
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        backgroundColor: finding.analysis?.classification === 'KNOWN' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                        color: finding.analysis?.classification === 'KNOWN' ? '#10b981' : '#ef4444'
                      }}>
                        {finding.analysis?.classification || 'UNKNOWN'}
                      </span>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Confidence: <strong>{finding.analysis?.confidence_score || '0'}</strong></span>
                    </div>
                    
                    <h3 style={{ marginBottom: '0.5rem', fontSize: '1.1rem', color: 'var(--accent-color)' }}>{finding.analysis?.issue_name || 'Unidentified Issue'}</h3>
                    
                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Root Cause:</strong>
                      <p style={{ margin: '0.25rem 0 0 0', lineHeight: 1.5, color: 'var(--text-primary)' }}>{finding.analysis?.root_cause || 'N/A'}</p>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Suggested Fix:</strong>
                      <p style={{ margin: '0.25rem 0 0 0', lineHeight: 1.5, color: 'var(--text-primary)' }}>{finding.analysis?.suggested_fix || 'N/A'}</p>
                    </div>
                    
                    <div>
                      <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Raw Log Line:</strong>
                      <div style={{ marginTop: '0.25rem', padding: '0.5rem', background: 'rgba(0,0,0,0.1)', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.75rem', overflowX: 'auto', whiteSpace: 'pre', color: 'var(--text-secondary)' }}>
                        L{finding.line_number}: {finding.error_line}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
