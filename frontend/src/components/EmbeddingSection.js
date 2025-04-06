import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import Plot from 'react-plotly.js';
import { InlineMath } from 'react-katex';
import './EmbeddingSection.css'; // Import the CSS file

const API_BASE_URL = '/api';

// Plotting helpers for Embedding Diagram
const getEmbeddingSurfaceData = (embeddingResult) => {
    if (!embeddingResult?.x_surface) return [];
    return [{
        x: embeddingResult.x_surface,
        y: embeddingResult.y_surface,
        z: embeddingResult.z_surface,
        type: 'surface',
        colorscale: 'Viridis',
        showscale: false,
        contours: {
            z: { show: true, usecolormap: true, highlightcolor: "#42f462", project: { z: true } }
        }
    }];
};

const getEmbeddingSurfaceLayout = (currentEmbeddingParams) => {
    const M = currentEmbeddingParams?.M;
    const title = `Flamm's Paraboloid ${M ? `(M=${M})` : ''}`;
    return {
        title: title,
        scene: {
            xaxis: { title: 'X = r cos(φ)' },
            yaxis: { title: 'Y = r sin(φ)' },
            zaxis: { title: 'Embedding z(r)' },
            aspectratio: { x: 1, y: 1, z: 0.4 }
        },
        margin: { l: 10, r: 10, t: 50, b: 10 }
    };
};

const getEmbeddingZRData = (embeddingResult) => {
    if (!embeddingResult?.r_values || !embeddingResult?.z_values) return [];
    return [{
        x: embeddingResult.r_values,
        y: embeddingResult.z_values,
        type: 'scatter',
        mode: 'lines',
        name: 'z(r)',
        marker: { color: 'purple' }
    }];
};

const getEmbeddingZRLayout = (currentEmbeddingParams) => {
    const M = currentEmbeddingParams?.M;
    const title = `Embedding Function z(r) ${M ? `(M=${M})` : ''}`;
    return {
        title: title,
        xaxis: { title: 'Radial Coordinate (r)' },
        yaxis: { title: 'Embedding Coordinate z' },
        margin: { l: 50, r: 30, t: 50, b: 50 },
        hovermode: 'closest'
    };
};

function EmbeddingSection({ metricDef, currentGeodesicParams, onShowDefinition }) {
    const [embeddingResult, setEmbeddingResult] = useState(null);
    const [embeddingLoading, setEmbeddingLoading] = useState(false);
    const [embeddingError, setEmbeddingError] = useState(null);
    const [currentEmbeddingParams, setCurrentEmbeddingParams] = useState(null);
    const [embeddingPlotParams, setEmbeddingPlotParams] = useState({
        r_min: '', 
        r_max: '10.0',
        num_points_r: '50',
        num_points_phi: '60'
    });

     // Clear results if metric definition changes
     useEffect(() => {
        setEmbeddingResult(null);
        setCurrentEmbeddingParams(null);
        setEmbeddingError(null);
    }, [metricDef]);

    const handleEmbeddingParamChange = useCallback((event) => {
        const { name, value } = event.target;
        setEmbeddingPlotParams(prev => ({ ...prev, [name]: value }));
    }, []);

    const handleCalculateEmbedding = useCallback(() => {
        if (!metricDef) {
            setEmbeddingError("Metric must be defined to calculate embedding diagram."); return;
        }
        // Use metric params passed down (e.g., from geodesic calc)
        const paramsForEmbedding = currentGeodesicParams || {}; 
        console.log("Calculating embedding diagram for:", metricDef, "with params:", paramsForEmbedding);
        setEmbeddingLoading(true);
        setEmbeddingError(null);
        setEmbeddingResult(null);
        setCurrentEmbeddingParams(null);

        let numParams = {};
        try {
            numParams.r_min = embeddingPlotParams.r_min ? parseFloat(embeddingPlotParams.r_min) : null;
            numParams.r_max = parseFloat(embeddingPlotParams.r_max);
            numParams.num_points_r = parseInt(embeddingPlotParams.num_points_r, 10);
            numParams.num_points_phi = parseInt(embeddingPlotParams.num_points_phi, 10);
            
            if (isNaN(numParams.r_max) || isNaN(numParams.num_points_r) || isNaN(numParams.num_points_phi)) {
                 throw new Error("r_max and num_points must be valid numbers.");
             }
             if (numParams.num_points_r <= 1 || numParams.num_points_phi <= 1) {
                 throw new Error("Number of points must be greater than 1.");
             }
             if (numParams.r_min !== null && isNaN(numParams.r_min)) {
                  throw new Error("r_min must be a valid number if provided.");
             }
             if (numParams.r_min !== null && numParams.r_min >= numParams.r_max) {
                 throw new Error("r_min must be less than r_max.");
             }

        } catch (err) {
            setEmbeddingError(`Invalid plot parameters: ${err.message}`);
            toast.warn(`Invalid plot parameters: ${err.message}`);
            setEmbeddingLoading(false);
            return;
        }

        const payload = {
            metric_input: metricDef,
            parameter_values: paramsForEmbedding,
            r_min: numParams.r_min,
            r_max: numParams.r_max,
            num_points_r: numParams.num_points_r,
            num_points_phi: numParams.num_points_phi
        };

        axios.post(`${API_BASE_URL}/calculate/embedding/flamm`, payload)
            .then(response => {
                setEmbeddingResult(response.data);
                setCurrentEmbeddingParams(paramsForEmbedding);
                toast.success("Embedding diagram calculated successfully!");
            })
            .catch(err => {
                let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during embedding calculation.';
                setEmbeddingError(`Embedding Error: ${errorMsg}`);
                toast.error(`Embedding Error: ${errorMsg}`);
            })
            .finally(() => {
                setEmbeddingLoading(false);
            });
    }, [metricDef, currentGeodesicParams, embeddingPlotParams]); // Dependencies

    return (
        <div className="embedding-section">
            <div className="embedding-controls-section">
                <h5><InlineMath math="z(r)" /> Plot Controls</h5>
                <div className="embedding-params-inputs">
                    <div className="input-group-inline">
                        <label htmlFor="r_min">r<sub>min</sub>:</label>
                        <input type="text" id="r_min" name="r_min" value={embeddingPlotParams.r_min} onChange={handleEmbeddingParamChange} placeholder="auto (e.g., 2M+)" />
                    </div>
                    <div className="input-group-inline">
                        <label htmlFor="r_max">r<sub>max</sub>:</label>
                        <input type="text" id="r_max" name="r_max" value={embeddingPlotParams.r_max} onChange={handleEmbeddingParamChange} required />
                    </div>
                    <div className="input-group-inline">
                        <label htmlFor="num_points_r"># r points:</label>
                        <input type="number" id="num_points_r" name="num_points_r" value={embeddingPlotParams.num_points_r} onChange={handleEmbeddingParamChange} min="2" required />
                    </div>
                    <div className="input-group-inline">
                        <label htmlFor="num_points_phi"># φ points:</label>
                        <input type="number" id="num_points_phi" name="num_points_phi" value={embeddingPlotParams.num_points_phi} onChange={handleEmbeddingParamChange} min="2" required />
                    </div>
                </div>
                <div className="action-button-container">
                    <button 
                        onClick={handleCalculateEmbedding} 
                        disabled={embeddingLoading || !metricDef} 
                        className="secondary-button"
                    >
                        Calculate Flamm's Paraboloid
                    </button>
                    {embeddingLoading && <span className="inline-loader"> Loading...</span>}
                </div>
            </div>

            {embeddingResult && !embeddingLoading && !embeddingError && (
                <div className="embedding-result-container results-container">
                    <h5>
                        <button className="definition-link" onClick={() => onShowDefinition('flamms_paraboloid')}>
                            Flamm's Paraboloid Result
                        </button>
                    </h5>
                    <p><i>Status: {embeddingResult.message}</i></p>
                    {embeddingResult.z_function_latex && (
                        <p><InlineMath math={`z(r) = ${embeddingResult.z_function_latex}`} /></p>
                    )}

                    {embeddingResult.x_surface &&
                        <div className="plot-grid">
                            <div className="plot-wrapper">
                                <h6>Embedding Function z(r)</h6>
                                <Plot
                                    data={getEmbeddingZRData(embeddingResult)}
                                    layout={getEmbeddingZRLayout(currentEmbeddingParams)}
                                    useResizeHandler={true}
                                    style={{ width: '100%', height: '350px' }}
                                />
                            </div>
                            <div className="plot-wrapper">
                                <h6>3D Surface Plot</h6>
                                <Plot
                                    data={getEmbeddingSurfaceData(embeddingResult)}
                                    layout={getEmbeddingSurfaceLayout(currentEmbeddingParams)}
                                    useResizeHandler={true}
                                    style={{ width: '100%', height: '500px' }}
                                />
                            </div>
                        </div>
                    }
                </div>
            )}
        </div>
    );
}

export default EmbeddingSection; 