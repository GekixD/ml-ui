import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from '../components/Dashboard';

const App = () => {
  const [windowSize, setWindowSize] = useState(30);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');

  const handleAnalysis = async () => {
    try {
      return (
        <Router>
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </Router>
      );
    } catch (error) {
      console.error('Error:', error instanceof Error ? error.message : String(error));
    }
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  );
};

export default App;
