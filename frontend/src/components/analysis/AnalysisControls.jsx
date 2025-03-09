import React from 'react';
import { useAnalysisStore } from '../../store/analysisStore';
import { DateRangePicker, Select, Slider } from '../common';

export const AnalysisControls = ({ onAnalyze }) => {
    const [params, setParams] = React.useState({
        assets: [],
        startDate: '',
        endDate: '',
        analysisType: 'both',
        lambda: 2.0,
        windowSize: 30
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onAnalyze(params);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <Select
                label="Assets"
                multiple
                value={params.assets}
                onChange={(value) => setParams({ ...params, assets: value })}
                options={availableAssets}
            />
            
            <DateRangePicker
                startDate={params.startDate}
                endDate={params.endDate}
                onDateChange={(start, end) => 
                    setParams({ ...params, startDate: start, endDate: end })}
            />
            
            <Select
                label="Analysis Type"
                value={params.analysisType}
                onChange={(value) => setParams({ ...params, analysisType: value })}
                options={[
                    { value: 'both', label: 'Both Effects' },
                    { value: 'heat_wave', label: 'Heat Wave' },
                    { value: 'meteor_shower', label: 'Meteor Shower' }
                ]}
            />
            
            <Slider
                label="Lambda (Sensitivity)"
                min={1.0}
                max={3.0}
                step={0.1}
                value={params.lambda}
                onChange={(value) => setParams({ ...params, lambda: value })}
            />
            
            <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded"
            >
                Run Analysis
            </button>
        </form>
    );
};