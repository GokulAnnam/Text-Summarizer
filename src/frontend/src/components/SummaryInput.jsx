import { useState } from 'react';
import './../styles/SummaryInput.css';

function SummaryInput({ onSummaryCreated }) {
  const [inputText, setInputText] = useState('');
  const [summaryType, setSummaryType] = useState('short');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputText.trim()) {
      setError('Please enter some text to summarize');
      return;
    }
    
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_text: inputText,
          summary_type: summaryType
        }),
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate summary');
      }

      onSummaryCreated(data);
      
      setInputText('');
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="summary-container">
      <div className="summary-card">
        <header className="summary-header">
          <h2>Create Summary</h2>
        </header>

        {error && <div className="summary-error">{error}</div>}

        <form onSubmit={handleSubmit} className="summary-form">
          <label htmlFor="inputText" className="summary-label">Text to Summarize</label>
          <textarea
            id="inputText"
            className="summary-textarea"
            rows="6"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste your text here..."
            required
          ></textarea>

          <div className="summary-type-group">
            <p className="summary-type-label">Summary Type</p>
            
            <div className="summary-radio-group">
              <div className="summary-radio-option">
                <input
                  type="radio"
                  name="summaryType"
                  id="shortSummary"
                  value="short"
                  checked={summaryType === 'short'}
                  onChange={() => setSummaryType('short')}
                  className="summary-radio-input"
                />
                <label className="summary-radio-label" htmlFor="shortSummary">
                  Short Summary
                </label>
              </div>

              <div className="summary-radio-option">
                <input
                  type="radio"
                  name="summaryType"
                  id="longSummary"
                  value="long"
                  checked={summaryType === 'long'}
                  onChange={() => setSummaryType('long')}
                  className="summary-radio-input"
                />
                <label className="summary-radio-label" htmlFor="longSummary">
                  Detailed Summary
                </label>
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="summary-button"
            disabled={isLoading}
          >
            {isLoading ? 'Generating Summary...' : 'Generate Summary'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default SummaryInput;