import React from 'react';
import { Line } from 'react-plotly.js';

export const EffectTimeline = ({ data, type }) => {
    const effectPeriods = data.effects.reduce((acc, curr, idx) => {
        if (curr && (!acc.length || !acc[acc.length - 1].end)) {
            acc.push({ start: idx, end: null });
        } else if (!curr && acc.length && !acc[acc.length - 1].end) {
            acc[acc.length - 1].end = idx;
        }
        return acc;
    }, []);

    return (
        <Line
            data={[
                {
                    x: data.dates,
                    y: data.returns,
                    name: 'Returns',
                    type: 'scatter',
                    mode: 'lines'
                },
                {
                    x: data.dates,
                    y: data.thresholds,
                    name: 'Threshold',
                    type: 'scatter',
                    mode: 'lines',
                    line: { dash: 'dash' }
                },
                ...effectPeriods.map((period, i) => ({
                    x: data.dates.slice(period.start, period.end),
                    y: data.returns.slice(period.start, period.end),
                    name: `${type} Effect ${i + 1}`,
                    type: 'scatter',
                    mode: 'markers',
                    marker: { color: 'red' }
                }))
            ]}
            layout={{
                title: `${type === 'heat_wave' ? 'Heat Wave' : 'Meteor Shower'} Effect Timeline`,
                xaxis: { title: 'Date' },
                yaxis: { title: 'Returns' },
                showlegend: true,
                width: 1000,
                height: 500
            }}
        />
    );
};