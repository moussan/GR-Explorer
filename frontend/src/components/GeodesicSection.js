import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify'; // Import toast
import GeodesicInputForm from './GeodesicInputForm';
import Plot from 'react-plotly.js';
import { InlineMath } from 'react-katex'; // For title

const API_BASE_URL = '/api';

// Plotting helpers (can be moved outside if they become large)
// Helper function to generate plot data (example for r vs t)
const getRVSTPlotData = (geodesicResults) => {
    if (!geodesicResults?.position_coords) return [];
    const t = geodesicResults.position_coords['t'];
    const r = geodesicResults.position_coords['r'];
    if (!t || !r) return [];
    return [{ x: t, y: r, type: 'scatter', mode: 'lines', name: 'r(t)', marker: { color: 'blue' } }];
};

// Helper function to generate plot layout (example for r vs t)
const getRVSTPlotLayout = () => {
    return {
        title: 'Radial Coordinate vs Time',
        xaxis: { title: 'Coordinate Time (t)' },
        yaxis: { title: 'Radial Coordinate (r)', range: [0, undefined] },
        margin: { l: 50, r: 30, t: 50, b: 50 },
        hovermode: 'closest'
    };
};

const getXYPlotData = (geodesicResults) => {
    if (!geodesicResults?.position_coords) return [];
    const r = geodesicResults.position_coords['r'];
    const phi = geodesicResults.position_coords['phi'];
    if (!r || !phi) return [];
    const x = r.map((rad, i) => rad * Math.cos(phi[i]));
    const y = r.map((rad, i) => rad * Math.sin(phi[i]));
    return [{
        x: x,
        y: y,
        type: 'scatter',
        mode: 'lines',
        name: 'Path',
        marker: { color: 'green' }
    }];
};

const getXYPlotLayout = (currentGeodesicParams) => {
    const layout = {
        title: 'Equatorial Plane Projection',
        xaxis: { title: 'x', scaleanchor: "y", scaleratio: 1 },
        yaxis: { title: 'y' },
        margin: { l: 50, r: 30, t: 50, b: 50 },
        hovermode: 'closest',
        shapes: [{
            type: 'circle',
            xref: 'x',
            yref: 'y',
            x0: -0.1, y0: -0.1, x1: 0.1, y1: 0.1,
            fillcolor: 'black',
            line: { color: 'black' }
        }]
    };
    const M = currentGeodesicParams?.M;
    if (typeof M === 'number' && M > 0) {
        const eventHorizonRadius = 2 * M;
        layout.shapes.push({
            type: 'circle',
            xref: 'x',
            yref: 'y',
            x0: -eventHorizonRadius,
            y0: -eventHorizonRadius,
            x1: eventHorizonRadius,
            y1: eventHorizonRadius,
            line: { color: 'red', width: 2, dash: 'dash' },
            name: 'Event Horizon (r=2M)',
            opacity: 0.7
        });
    }
    return layout;
};


function GeodesicSection({ metricDef, onShowDefinition }) { // Receive metricDef and handler
    const [currentGeodesicParams, setCurrentGeodesicParams] = useState(null);
    const [geodesicResults, setGeodesicResults] = useState(null);
    const [geodesicLoading, setGeodesicLoading] = useState(false);
    const [geodesicError, setGeodesicError] = useState(null);
    const [formError, setFormError] = useState(null); // State for form input errors

    // Clear results if metric definition changes
    useEffect(() => {
        setGeodesicResults(null);
        setCurrentGeodesicParams(null);
        setGeodesicError(null);
        setFormError(null);
    }, [metricDef]);

    const handleCalculateGeodesic = useCallback((geodesicInputData) => {
        if (!metricDef) {
            setGeodesicError("Cannot calculate geodesic: Metric definition is missing."); 
            return;
        }
        console.log("Sending geodesic data:", geodesicInputData);
        setGeodesicLoading(true);
        setGeodesicError(null);
        setFormError(null); // Clear form error on new API submission
        setGeodesicResults(null);
        setCurrentGeodesicParams(null);

        const payload = {
            ...geodesicInputData,
            metric_components: metricDef.components,
            coords: metricDef.coords,
        };
        axios.post(`${API_BASE_URL}/calculate/geodesic`, payload)
            .then(response => {
                setGeodesicResults(response.data);
                setCurrentGeodesicParams(geodesicInputData.parameter_values);
                toast.success("Geodesic calculated successfully!");
            })
            .catch(err => {
                let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during geodesic calculation.';
                setGeodesicError(`Geodesic Error: ${errorMsg}`);
                toast.error(`Geodesic Error: ${errorMsg}`);
            })
            .finally(() => {
                setGeodesicLoading(false);
            });
    }, [metricDef]);

    // Handler for form input validation errors
    const handleFormError = useCallback((errorMessage) => {
        setFormError(errorMessage);
        setGeodesicError(null); // Clear API errors if there's a form error
        if(errorMessage) { // Only show toast if there is an error
             toast.warn(errorMessage); // Use warn for input errors
        }
    }, []);

    return (
        <div className="geodesic-section">
            <h5>
                <button className="definition-link" onClick={() => onShowDefinition('geodesic_equation')}>
                    Geodesic Calculation
                </button>
            </h5>
            <GeodesicInputForm
                onSubmit={handleCalculateGeodesic}
                onError={handleFormError} // Pass the handler for form errors
                currentCoords={metricDef?.coords} 
            />
            {/* Display form error if set */} 
            {formError && <div className="error-message">{formError}</div>}
            
            {geodesicLoading && <div className="loading-indicator">Calculating Geodesic...</div>}
            {/* Only show API error if there's no form error */} 
            {geodesicError && !formError && <div className="error-message">{geodesicError}</div>}

            {geodesicResults && !geodesicLoading && !geodesicError && !formError && (
                <div className="plot-container results-container">
                    <h3>Geodesic Plots</h3>
                    <div className="plot-grid">
                        <div className="plot-wrapper">
                            <Plot 
                                data={getRVSTPlotData(geodesicResults)} 
                                layout={getRVSTPlotLayout()} 
                                useResizeHandler={true} 
                                style={{ width: '100%', height: '400px' }} 
                            />
                        </div>
                        <div className="plot-wrapper">
                            <Plot 
                                data={getXYPlotData(geodesicResults)} 
                                layout={getXYPlotLayout(currentGeodesicParams)} 
                                useResizeHandler={true} 
                                style={{ width: '100%', height: '450px' }} 
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default GeodesicSection; 