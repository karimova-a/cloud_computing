import React, { useState } from 'react';
import Calculator from './components/Calculator';
import ResultsDashboard from './components/ResultsDashboard';

function App() {
  const [inputs, setInputs] = useState({
    mau: 5000,
    messagesPerUser: 100,
    inputTokens: 150,
    outputTokens: 300,
    modelId: 'gpt-4o-mini',
    storagePerMessageKB: 2,
    bandwidthPerMessageKB: 1
  });

  return (
    <div className="app-container">
      <header className="header">
        <h1>CFO Bot</h1>
        <p>Intelligent Cloud Architecture Cost Estimator</p>
      </header>

      <div className="dashboard-layout">
        <Calculator inputs={inputs} setInputs={setInputs} />
        <ResultsDashboard inputs={inputs} />
      </div>
    </div>
  );
}

export default App;
