import { useState } from 'react';
import SummaryInput from './SummaryInput';
import SummaryOutput from './SummaryOutput';
import History from './History';
import '../styles/Dashboard.css';

function Dashboard({ user }) {
  const [currentSummary, setCurrentSummary] = useState(null);

  const handleSummaryCreated = (summaryData) => {
    setCurrentSummary(summaryData);
  };

  const handleSelectSummary = (summary) => {
    setCurrentSummary({
      input_text: summary.input_text,
      summary: summary.summary_text,
      summary_type: summary.summary_type,
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="dashboard-fullscreen">
      <header className="dashboard-header">
        <h2>Welcome, {user.name}!</h2>
        <p>Use this application to create summaries of texts. Enter your content below to get started.</p>
      </header>

      <main className="dashboard-main">
        <section className="dashboard-main-left">
          <SummaryInput onSummaryCreated={handleSummaryCreated} />
          <SummaryOutput summary={currentSummary} />
        </section>

        <aside className="dashboard-main-right">
          <History onSelectSummary={handleSelectSummary} />
        </aside>
      </main>
    </div>
  );
}

export default Dashboard;
