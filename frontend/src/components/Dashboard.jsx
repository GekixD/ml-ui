import React, { useState } from 'react';
import DatasetSelector from './data/DatasetSelector';

const Dashboard = () => {
  const [windowSize, setWindowSize] = useState(30);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');

  const handleAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          window_size: windowSize,
          features: selectedFeatures,
        }),
      });
      const data = await response.json();
      // TODO: Handle the response
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : String(error));
    }
  };

  return (
    <div className="mw8 center ph3 ph5-ns">
      <h1 className="f2 lh-title mb4 mt4 dark-gray">ML Correlation Dashboard</h1>
      <div className="mb4">
        <DatasetSelector onSelect={setSelectedDataset} />
      </div>
      <div className="mb4">
        <label className="f5 db mb2">
          Window Size:
          <input
            type="number"
            value={windowSize}
            onChange={(e) => setWindowSize(Number(e.target.value))}
            className="input-reset ba b--black-20 pa2 mb2 db w-100 w-auto-ns"
          />
        </label>
      </div>
      <button 
        onClick={handleAnalysis}
        className="f6 link dim br2 ph3 pv2 mb2 dib white bg-blue bn pointer"
      >
        Run Analysis
      </button>
    </div>
  );
};

export default Dashboard;