import React from 'react';
import { Heatmap } from 'react-plotly.js';

export const CorrelationHeatmap = ({ data }) => {
    return (
        <Heatmap
            data={[{
                z: data.correlationMatrix,
                x: data.assets,
                y: data.assets,
                type: 'heatmap',
                colorscale: 'RdBu',
                zmin: -1,
                zmax: 1
            }]}
            layout={{
                title: 'Asset Correlation Heatmap',
                width: 800,
                height: 800,
                annotations: data.correlationMatrix.map((row, i) =>
                    row.map((val, j) => ({
                        text: val.toFixed(2),
                        x: data.assets[j],
                        y: data.assets[i],
                        xref: 'x',
                        yref: 'y',
                        showarrow: false,
                        font: {
                            color: Math.abs(val) > 0.5 ? 'white' : 'black'
                        }
                    }))
                ).flat()
            }}
        />
    );
};