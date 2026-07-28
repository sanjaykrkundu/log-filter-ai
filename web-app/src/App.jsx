import { useState } from 'react';
import './index.css';

function App() {
  const [currentView, setCurrentView] = useState('fetcher'); // 'fetcher' or 'analytics'
  const [activeTab, setActiveTab] = useState('issueId');
  const [query, setQuery] = useState('');
  const [isFetching, setIsFetching] = useState(false);
  const [results, setResults] = useState([]);

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
        padding: '1rem 2rem', 
        backgroundColor: 'rgba(15, 23, 42, 0.8)',
        borderBottom: '1px solid var(--border-color)',
        backdropFilter: 'blur(12px)'
      }}>
        <h1 style={{ fontSize: '1.5rem', margin: 0 }}>Log Filter AI</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            className={`btn ${currentView === 'fetcher' ? '' : 'btn-secondary'}`}
            onClick={() => setCurrentView('fetcher')}
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          >
            Issue Fetcher
          </button>
          <button 
            className={`btn ${currentView === 'analytics' ? '' : 'btn-secondary'}`}
            onClick={() => setCurrentView('analytics')}
            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          >
            Analytics
          </button>
        </div>
      </header>

      {/* 2. Statusbar */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '3rem', 
        padding: '0.75rem 2rem', 
        backgroundColor: 'rgba(30, 41, 59, 0.5)', 
        borderBottom: '1px solid var(--border-color)',
        fontSize: '0.875rem',
      }}>
        <div><span style={{ color: 'var(--text-secondary)' }}>Total Analyzed: </span><strong style={{ color: 'var(--accent-color)' }}>{stats.totalAnalyzed.toLocaleString()}</strong></div>
        <div><span style={{ color: 'var(--text-secondary)' }}>Success Rate: </span><strong>{stats.successRate}%</strong></div>
        <div><span style={{ color: 'var(--text-secondary)' }}>Man Hours Saved: </span><strong style={{ color: '#10b981' }}>{hoursSaved}h</strong></div>
      </div>

      {/* 3. Container */}
      <div className="container" style={{ flex: 1, paddingTop: '2rem' }}>
        {currentView === 'fetcher' && (
          <>
            <main className="glass-panel" style={{ marginBottom: '2rem' }}>
              <form onSubmit={handleFetch} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <div style={{ width: '200px' }}>
                  <select 
                    className="input-field" 
                    value={activeTab} 
                    onChange={(e) => {setActiveTab(e.target.value); setQuery('');}}
                  >
                    <option value="issueId">Single Issue ID</option>
                    <option value="username">Username</option>
                    <option value="group">Group</option>
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <input 
                    type="text" 
                    className="input-field" 
                    placeholder={
                      activeTab === 'issueId' ? 'e.g. ISSUE-8492' : 
                      activeTab === 'username' ? 'e.g. jdoe' : 'e.g. Camera-Framework'
                    }
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </div>
                <button type="submit" className="btn" disabled={isFetching || !query} style={{ minWidth: '150px' }}>
                  {isFetching ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: '16px', height: '16px', border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                      Fetching...
                    </span>
                  ) : (
                    'Fetch Data'
                  )}
                </button>
              </form>
            </main>

            {results.length > 0 && (
              <section>
                <h2 style={{ marginBottom: '1rem' }}>Fetched Issues</h2>
                <div className="data-table-container">
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
                              color: issue.status === 'Open' ? '#fca5a5' : '#93c5fd'
                            }}>
                              {issue.status}
                            </span>
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            <button 
                              className="btn" 
                              onClick={() => handleAnalyze(issue.id)}
                              style={{ padding: '0.5rem 1rem', fontSize: '0.875rem', background: 'linear-gradient(135deg, #10b981, #059669)' }}
                            >
                              Analyze
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </>
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
              <h3 style={{ marginBottom: '1.5rem' }}>Top Issue Categories</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {stats.categories.map(cat => (
                  <div key={cat.name}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: '500' }}>{cat.name}</span>
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

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
