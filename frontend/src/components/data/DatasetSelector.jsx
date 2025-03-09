import React, { useState, useEffect } from 'react';

const DatasetSelector = ({ onSelect }) => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleDatasetChange = (e, action) => {
    const selectedDataset = e.target.value;
    if (action === 'add') {
      setDatasets([...datasets, selectedDataset]);
    } else if (action === 'remove') {
      const newDatasets = datasets.filter(d => d !== selectedDataset);
      setDatasets(newDatasets);
    }
  };

  useEffect(() => {
    const fetchDatasets = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/datasets');
        const data = await response.json();
        setDatasets(data.datasets);
      } catch (err) {
        setError('Failed to load datasets');
      } finally {
        setLoading(false);
      }
    };

    fetchDatasets();
  }, []);

  if (loading) return (
    <div className="pa3 bg-light-blue black-70 br2">
      Loading datasets...
    </div>
  );
  
  if (error) return (
    <div className="pa3 bg-light-red dark-red br2">
      Error: {error}
    </div>
  );

  return (
    <div>
      <h3 className="f4 mb3 dark-gray">Select Dataset</h3>
      <select 
        onChange={(e) => handleDatasetChange(e, 'add')}
        className="input-reset ba b--black-20 pa2 mb2 db w-100 w-auto-ns"
      >
        <option value="">Choose a dataset...</option>
        {datasets.map((dataset) => (
          <option key={dataset} value={dataset}>
            {dataset}
          </option>
        ))}
      </select>
      <div className="mt3">
        {datasets.map((dataset) => (
          <div
            key={dataset}
            className="dib mr2 mb2 pa2 bg-light-gray br2 relative"
          >
            <button
              onClick={(e) => handleDatasetChange(e, 'remove')}
              className="bn bg-transparent pointer dark-red mr1 pa0"
              aria-label="Remove dataset"
            >
              ×
            </button>
            <span className="ml1">{dataset}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DatasetSelector; 