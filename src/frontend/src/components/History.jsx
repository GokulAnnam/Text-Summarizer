import { useState, useEffect } from 'react';
import '../styles/History.css'

function History({ onSelectSummary }) {
  const [summaries, setSummaries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/api/history', {
        method: 'GET',
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to load history');
      }

      setSummaries(data);
    } catch (error) {
      setError('Failed to load history: ' + error.message);
      console.error('Error loading history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    
    const options = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

 
  const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (isLoading) {
    return (
      <div className="history-container">
        <div className="history-card">
          <div className="history-header">
            <h3>History</h3>
          </div>
          <div className="history-body history-loading">
            <div className="history-spinner"></div>
            <p>Loading your summary history...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-container">
        <div className="history-card">
          <div className="history-header">
            <h3>History</h3>
          </div>
          <div className="history-body">
            <div className="history-error">
              {error}
            </div>
            <button 
              className="history-retry-btn" 
              onClick={fetchHistory}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-card">
        <div className="history-header">
          <h3>Recent Summaries</h3>
          <button 
            className="history-refresh-btn" 
            onClick={fetchHistory}
          >
            Refresh
          </button>
        </div>
        <div className="history-body">
          {summaries.length === 0 ? (
            <p className="history-empty">No summary history yet. Create your first summary above!</p>
          ) : (
            <div className="history-list">
              {summaries.map((summary) => (
                <button
                  key={summary.id}
                  className="history-item"
                  onClick={() => onSelectSummary(summary)}
                >
                  <div className="history-item-header">
                    <h5 className="history-item-type">
                      {summary.summary_type === 'short' ? 'Short Summary' : 'Detailed Summary'}
                    </h5>
                    <span className="history-item-date">{formatDate(summary.created_at)}</span>
                  </div>
                  <p className="history-item-summary">{truncateText(summary.summary_text)}</p>
                  <p className="history-item-original">
                    Original text: {truncateText(summary.input_text, 50)}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default History;