import { useRef } from 'react';
import '../styles/SummaryOutput.css'

function SummaryOutput({ summary }) {
  const summaryTextRef = useRef(null);

  const handleCopy = () => {
    if (summaryTextRef.current) {
      const textToCopy = summaryTextRef.current.innerText;
      navigator.clipboard.writeText(textToCopy)
        .then(() => {
          const copyBtn = document.getElementById('copyBtn');
          const originalText = copyBtn.innerText;
          copyBtn.innerText = 'Copied!';
          setTimeout(() => {
            copyBtn.innerText = originalText;
          }, 2000);
        })
        .catch(err => {
          console.error('Failed to copy text: ', err);
        });
    }
  };

  if (!summary) {
    return null;
  }

  return (
    <div className="summary-output-container">
      <div className="summary-output-card">
        <div className="summary-output-header">
          <h3>Summary Result</h3>
          <button 
            id="copyBtn"
            className="summary-copy-btn" 
            onClick={handleCopy}
          >
            Copy to Clipboard
          </button>
        </div>
        <div className="summary-output-body">
          <h5 className="summary-section-title">Original Text:</h5>
          <div className="summary-text-container summary-original-text">
            <p>{summary.input_text}</p>
          </div>
          
          <h5 className="summary-section-title">
            {summary.summary_type === 'short' ? 'Short Summary' : 'Detailed Summary'}:
          </h5>
          <div 
            ref={summaryTextRef}
            className="summary-text-container summary-result-text"
          >
            <p>{summary.summary}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SummaryOutput;