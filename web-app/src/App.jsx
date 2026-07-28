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
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1>Log Filter AI Portal</h1>
        <p style={{ marginBottom: '2rem' }}>Intelligent dumpstate retrieval and automated root cause analysis.</p>
        
        {/* Top Navigation */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
          <button 
            className={`btn ${currentView === 'fetcher' ? '' : 'btn-secondary'}`}
            onClick={() => setCurrentView('fetcher')}
          >
            Issue Fetcher
          </button>
          <button 
            className={`btn ${currentView === 'analytics' ? '' : 'btn-secondary'}`}
            onClick={() => setCurrentView('analytics')}
          >
            Analytics Dashboard
          </button>
        </div>
      </header>

      {currentView === 'fetcher' && (
        <>
          <main className="glass-panel" style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
              <button 
                className={`btn ${activeTab === 'issueId' ? '' : 'btn-secondary'}`}
                onClick={() => {setActiveTab('issueId'); setQuery('');}}
                style={{ borderRadius: '20px' }}
              >
                Single Issue ID
              </button>
              <button 
                className={`btn ${activeTab === 'username' ? '' : 'btn-secondary'}`}
                onClick={() => {setActiveTab('username'); setQuery('');}}
                style={{ borderRadius: '20px' }}
              >
                Username
              </button>
              <button 
                className={`btn ${activeTab === 'group' ? '' : 'btn-secondary'}`}
                onClick={() => {setActiveTab('group'); setQuery('');}}
                style={{ borderRadius: '20px' }}
              >
                Group
              </button>
            </div>

            <form onSubmit={handleFetch} style={{ display: 'flex', gap: '1rem' }}>
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
              <h2>Fetched Issues</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.map(issue => (
                  <div key={issue.id} className="glass-panel" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem' }}>
                    <div>
                      <h3 style={{ marginBottom: '0.25rem' }}>{issue.id}: {issue.title}</h3>
                      <p style={{ fontSize: '0.875rem' }}>Component: {issue.component} | Status: {issue.status}</p>
                    </div>
                    <button 
                      className="btn" 
                      onClick={() => handleAnalyze(issue.id)}
                      style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '0.5rem'}}><path d="M2 12h4l3-9 5 18 3-9h5"/></svg>
                      Analyze with AI
                    </button>
                  </div>
                ))}
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

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
