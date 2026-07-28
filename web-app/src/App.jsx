import { useState } from 'react';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('issueId');
  const [query, setQuery] = useState('');
  const [isFetching, setIsFetching] = useState(false);
  const [results, setResults] = useState([]);

  const handleFetch = (e) => {
    e.preventDefault();
    if (!query) return;
    
    setIsFetching(true);
    setResults([]);
    
    // Mock network request
    setTimeout(() => {
      setIsFetching(false);
      
      // Mock results based on tab
      const mockData = [
        { id: 'ISSUE-8492', title: 'Camera Service Crash on Resume', component: 'Camera', status: 'Open' },
        { id: 'ISSUE-9103', title: 'NullPointerException in ISP Node 5', component: 'ISP', status: 'Investigating' }
      ];
      
      setResults(activeTab === 'issueId' ? [mockData[0]] : mockData);
    }, 1500);
  };

  const handleAnalyze = (id) => {
    alert(`Handing off ${id} to Python Log Filter AI backend... (Feature coming soon)`);
  };

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1>Log Filter AI Portal</h1>
        <p>Intelligent dumpstate retrieval and automated root cause analysis.</p>
      </header>

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
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h4l3-9 5 18 3-9h5"/></svg>
                  Analyze with AI
                </button>
              </div>
            ))}
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
