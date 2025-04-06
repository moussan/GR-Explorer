import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios'; // Import axios
import './App.css'; // Optional: for component-specific styles
import MetricInputForm, { initialMetricState } from './components/MetricInputForm';
// Import the results display component
import GeometryResultsDisplay from './components/GeometryResultsDisplay'; 
// Import the Stress-Energy form component
import StressEnergyInputForm, { initialStressEnergyState } from './components/StressEnergyInputForm';
// Import the Geodesic form component
import GeodesicInputForm from './components/GeodesicInputForm';
// Import plotting library
import Plot from 'react-plotly.js'; // Use Plotly for plotting
// Import KaTeX for rendering verification results
import 'katex/dist/katex.min.css'; 
import { InlineMath } from 'react-katex';
import ScenarioManager from './components/ScenarioManager'; // Import ScenarioManager

// Base URL for the backend API 
// Use the proxy defined in package.json for development, 
// or configure environment variables for production.
const API_BASE_URL = '/api'; // Relative path assumes proxy is set up

function App() {
  const [backendMessage, setBackendMessage] = useState('Connecting to backend...');
  
  // --- State for Inputs (now managed centrally) ---
  const [metricDef, setMetricDef] = useState(initialMetricState()); // Use initial state function
  const [stressEnergyDef, setStressEnergyDef] = useState(initialStressEnergyState()); // Use initial state function
  
  // State for Geometry Results
  const [geometryResults, setGeometryResults] = useState(null);
  const [geometryLoading, setGeometryLoading] = useState(false);
  const [geometryError, setGeometryError] = useState(null);

  // State for Stress-Energy Results
  const [stressEnergyResults, setStressEnergyResults] = useState(null);
  const [stressEnergyLoading, setStressEnergyLoading] = useState(false);
  const [stressEnergyError, setStressEnergyError] = useState(null);

  // State for EFE Verification
  const [efeVerificationResult, setEfeVerificationResult] = useState(null);
  const [efeLoading, setEfeLoading] = useState(false);
  const [efeError, setEfeError] = useState(null);

  // State for Geodesic Calculation
  const [currentGeodesicParams, setCurrentGeodesicParams] = useState(null);
  const [geodesicResults, setGeodesicResults] = useState(null);
  const [geodesicLoading, setGeodesicLoading] = useState(false);
  const [geodesicError, setGeodesicError] = useState(null);
  
   // State for Embedding Diagram
  const [embeddingResult, setEmbeddingResult] = useState(null);
  const [embeddingLoading, setEmbeddingLoading] = useState(false);
  const [embeddingError, setEmbeddingError] = useState(null);
  // Store params used for embedding calc if needed for plot titles etc.
  const [currentEmbeddingParams, setCurrentEmbeddingParams] = useState(null); 

  // Fetch initial welcome message from backend
  useEffect(() => {
    axios.get('/') // Assuming backend root provides a basic message
      .then(response => {
        // Check if the root endpoint returns a message structure
        if (response.data && response.data.message) {
            setBackendMessage(response.data.message);
        } else {
            // Fallback if the root response is different
            setBackendMessage('Backend connected.'); 
        }
      })
      .catch(err => {
        console.error('Error fetching root data from backend:', err);
        setBackendMessage('Failed to connect to backend.');
        setGeometryError('Could not reach the backend server. Is it running?'); // Use geometry error for initial connection issue
      });
  }, []);

  // --- Input Change Handlers for Controlled Components --- 

  const handleMetricComponentChange = useCallback((rowIndex, colIndex, value) => {
    setMetricDef(prev => ({ 
        ...prev,
        components: prev.components.map((row, rIdx) => 
            row.map((col, cIdx) => 
                (rIdx === rowIndex && cIdx === colIndex) ? value : col
            )
        )
    }));
  }, []);

  const handleMetricCoordChange = useCallback((index, value) => {
     setMetricDef(prev => ({ 
        ...prev,
        coords: prev.coords.map((coord, i) => (i === index ? value : coord))
    }));
  }, []);

  const handleMetricReset = useCallback(() => {
      setMetricDef(initialMetricState());
      // Clear results when resetting metric
      setGeometryResults(null);
      setGeometryError(null);
      setStressEnergyResults(null);
      setStressEnergyError(null);
      setEfeVerificationResult(null);
      setEfeError(null);
      setGeodesicResults(null);
      setGeodesicError(null);
      setEmbeddingResult(null);
      setEmbeddingError(null);
  }, []);

  // Handler for StressEnergyInputForm state changes
  const handleStressEnergyStateChange = useCallback((newStateChanges) => {
      setStressEnergyDef(prev => {
          const updatedState = { ...prev, ...newStateChanges };
          // Reset specific fields when method changes
          if ('definition_method' in newStateChanges) {
              if (newStateChanges.definition_method === 'preset') {
                  // Reset components to initial state when switching to preset
                  updatedState.components = initialStressEnergyState().components;
              } else {
                  // Reset preset name and params when switching to components
                  updatedState.preset_name = initialStressEnergyState().preset_name;
                  updatedState.params = initialStressEnergyState().params;
              }
          }
          return updatedState;
      });
  }, []);


  // --- Calculation Handlers (using state directly) --- 

  const handleCalculateGeometry = () => { // Now takes no args, uses metricDef state
    console.log("Sending metric data to backend:", metricDef);
    setGeometryLoading(true);
    setGeometryError(null);
    setGeometryResults(null); 
    // setCurrentMetricDef(metricData); // No longer needed, state is source of truth
    // Clear downstream results
    setStressEnergyResults(null);
    // setStressEnergyDef(initialStressEnergyState()); // Optionally reset Tmunu form?
    setEfeVerificationResult(null); 
    setGeodesicResults(null);
    setCurrentGeodesicParams(null); 
    setGeodesicError(null);
    setEmbeddingResult(null);
    setEmbeddingError(null);

    axios.post(`${API_BASE_URL}/calculate/geometry`, metricDef) // Send current metricDef state
      .then(response => {
        setGeometryResults(response.data);
      })
      .catch(err => {
        let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during geometry calculation.';
        setGeometryError(`Geometry Error: ${errorMsg}`);
      })
      .finally(() => {
        setGeometryLoading(false);
      });
  };

  const handleCalculateStressEnergy = () => { // No args, uses stressEnergyDef state
    console.log("Sending stress-energy data:", stressEnergyDef);
    setStressEnergyLoading(true);
    setStressEnergyError(null);
    setStressEnergyResults(null);
    setEfeVerificationResult(null); 

    let payload = { ...stressEnergyDef };
    if (payload.definition_method === 'preset' && payload.preset_name === 'perfect_fluid') {
      if (!metricDef) { // Check metricDef state directly
        setStressEnergyError("Metric must be defined before using the Perfect Fluid preset.");
        setStressEnergyLoading(false);
        return;
      }
      payload.metric_components = metricDef.components;
    }

    axios.post(`${API_BASE_URL}/calculate/stress-energy`, payload)
      .then(response => {
        setStressEnergyResults(response.data);
        // setCurrentStressEnergyInput(payload); // No longer need separate state for submitted input
      })
      .catch(err => {
        let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during T_munu calculation.';
        setStressEnergyError(`Stress-Energy Error: ${errorMsg}`);
      })
      .finally(() => {
        setStressEnergyLoading(false);
      });
  };

  const handleVerifyEFE = () => {
    if (!metricDef) {
      setEfeError("Cannot verify EFEs: Metric definition is missing."); return;
    }
    if (!stressEnergyDef || !stressEnergyResults) { // Check if Tmunu state/results exist
      setEfeError("Cannot verify EFEs: Stress-Energy tensor must be calculated first."); return;
    }
    console.log("Verifying EFEs with:", { metric: metricDef, stressEnergy: stressEnergyDef });
    setEfeLoading(true);
    setEfeError(null);
    setEfeVerificationResult(null);

    const verificationPayload = {
        metric_input: metricDef, // Use state
        stress_energy_input: stressEnergyDef, // Use state
    };
    axios.post(`${API_BASE_URL}/verify/efe`, verificationPayload)
      .then(response => {
          setEfeVerificationResult(response.data);
      })
      .catch(err => {
          let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during EFE verification.';
          setEfeError(`EFE Verification Error: ${errorMsg}`);
      })
      .finally(() => {
          setEfeLoading(false);
      });
  };

  const handleCalculateGeodesic = (geodesicInputData) => {
      if (!metricDef) {
        setGeodesicError("Cannot calculate geodesic: Metric definition is missing."); return;
      }
      console.log("Sending geodesic data:", geodesicInputData);
      setGeodesicLoading(true);
      setGeodesicError(null);
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
        })
        .catch(err => {
            let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during geodesic calculation.';
            setGeodesicError(`Geodesic Calculation Error: ${errorMsg}`);
        })
        .finally(() => {
            setGeodesicLoading(false);
        });
  };
  
   // --- Embedding Diagram Calculation --- 
   const handleCalculateEmbedding = () => {
        if (!metricDef) {
            setEmbeddingError("Metric must be defined to calculate embedding diagram."); return;
        }
        // Get parameters from Geodesic form - needs update if params differ
        // For now, assume relevant params (like M) are defined there
        // A better approach might be a dedicated parameter input section
        const paramsForEmbedding = currentGeodesicParams || {}; 
        console.log("Calculating embedding diagram for:", metricDef, "with params:", paramsForEmbedding);
        setEmbeddingLoading(true);
        setEmbeddingError(null);
        setEmbeddingResult(null);
        setCurrentEmbeddingParams(null);

        // TODO: Allow customizing r_min, r_max, num_points via UI?
        // Using defaults from backend model for now.
        const payload = {
             metric_input: metricDef, 
             parameter_values: paramsForEmbedding 
             // Add r_min, r_max etc. here if collected from UI
        };

        axios.post(`${API_BASE_URL}/calculate/embedding/flamm`, payload)
            .then(response => {
                setEmbeddingResult(response.data);
                setCurrentEmbeddingParams(paramsForEmbedding); // Store params used
            })
            .catch(err => {
                let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during embedding calculation.';
                setEmbeddingError(`Embedding Error: ${errorMsg}`);
            })
            .finally(() => {
                setEmbeddingLoading(false);
            });
   };
   
   // --- Scenario Management Handler --- 
   const handleLoadScenario = useCallback((loadedDefinition) => {
        console.log("Loading scenario definition:", loadedDefinition);
        // Update the state managed by App.js
        setMetricDef(loadedDefinition.metric_input);
        setStressEnergyDef(loadedDefinition.stress_energy_input);
        
        // Clear all results when loading a new scenario
        setGeometryResults(null);
        setGeometryError(null);
        setStressEnergyResults(null);
        setStressEnergyError(null);
        setEfeVerificationResult(null);
        setEfeError(null);
        setGeodesicResults(null);
        setGeodesicError(null);
        setCurrentGeodesicParams(null);
        setEmbeddingResult(null);
        setEmbeddingError(null);
        
        // Maybe automatically trigger geometry calculation after load?
        // handleCalculateGeometry(); // Uncomment to auto-calculate after load
        
   }, []); // Empty dependency array because it only uses setters

  // Helper function to generate plot data (example for r vs t)
  const getRVSTPlotData = () => {
    if (!geodesicResults?.position_coords) return [];
    const t = geodesicResults.position_coords['t'];
    const r = geodesicResults.position_coords['r'];
    if (!t || !r) return [];
    return [{ x: t, y: r, type: 'scatter', mode: 'lines', name: 'r(t)', marker: { color: 'blue' } }];
  };
  
  // Helper function to generate plot layout (example for r vs t)
  const getRVSTPlotLayout = () => {
      return {
          title: 'Geodesic: Radial Coordinate vs Time',
          xaxis: { title: 'Coordinate Time (t)' },
          yaxis: { title: 'Radial Coordinate (r)', range: [0, undefined] }, // Ensure r axis starts at 0
          margin: { l: 50, r: 30, t: 50, b: 50 },
          hovermode: 'closest'
      };
  };

  const getXYPlotData = () => {
    if (!geodesicResults?.position_coords) return [];
    const r = geodesicResults.position_coords['r'];
    const phi = geodesicResults.position_coords['phi'];
    // Ensure theta is present if needed for non-equatorial plots later
    // const theta = geodesicResults.position_coords['theta']; 
    if (!r || !phi) return [];
    
    // Assuming equatorial motion (theta=pi/2) for standard x, y projection
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

  const getXYPlotLayout = () => {
    const layout = {
      title: 'Geodesic: Equatorial Plane Projection',
      xaxis: { title: 'x', scaleanchor: "y", scaleratio: 1 }, // Ensure aspect ratio is 1:1
      yaxis: { title: 'y' },
      margin: { l: 50, r: 30, t: 50, b: 50 },
      hovermode: 'closest',
      shapes: [
        // Central mass/singularity representation
        {
          type: 'circle',
          xref: 'x',
          yref: 'y',
          x0: -0.1, y0: -0.1, x1: 0.1, y1: 0.1, // Small circle at origin
          fillcolor: 'black',
          line: { color: 'black' }
        }
      ]
    };

    // Add event horizon if M is defined
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
            name: 'Event Horizon (r=2M)', // Note: name doesn't appear directly on shape
            opacity: 0.7
        });
        // Add annotation for event horizon
        // layout.annotations = layout.annotations || [];
        // layout.annotations.push({ 
        //     x: 0, y: eventHorizonRadius, text: 'EH', showarrow: false 
        // });
    }

    return layout;
  };

  // Plotting functions for embedding diagram (z vs r, 3D surface)
  const getEmbeddingSurfaceData = () => {
    if (!embeddingResult?.x_surface) return [];
    return [{
      x: embeddingResult.x_surface,
      y: embeddingResult.y_surface,
      z: embeddingResult.z_surface,
      type: 'surface',
      colorscale: 'Viridis', // Example colorscale
      showscale: false, // Hide color bar
      contours: {
          z: { show: true, usecolormap: true, highlightcolor: "#42f462", project: { z: true } } // Add contours
      }
    }];
  };

  const getEmbeddingSurfaceLayout = () => {
     const M = currentEmbeddingParams?.M;
     const title = `Flamm's Paraboloid ${M ? `(M=${M})` : ''}`;
     return {
          title: title,
          scene: { // Use scene for 3D plots
              xaxis: { title: 'X = r cos(φ)' },
              yaxis: { title: 'Y = r sin(φ)' },
              zaxis: { title: 'Embedding z(r)' },
              aspectratio: { x: 1, y: 1, z: 0.4 } // Adjust aspect ratio
          },
          margin: { l: 10, r: 10, t: 50, b: 10 }
     };
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>GR Explorer</h1>
        <p>{backendMessage}</p>
      </header>
      
      {/* Add Scenario Manager at the top */} 
      <ScenarioManager 
            currentMetricDef={metricDef} 
            currentStressEnergyInput={stressEnergyDef} 
            onLoadScenario={handleLoadScenario} 
      />
      <hr className="section-divider" />

      <main className="App-content">
        {/* Metric Input - Now Controlled */} 
        <MetricInputForm 
            metricDef={metricDef} 
            onMetricChange={handleMetricComponentChange}
            onCoordChange={handleMetricCoordChange}
            onSubmit={handleCalculateGeometry} 
            onReset={handleMetricReset}
        />
        {geometryLoading && <div className="loading-indicator">Calculating Geometry...</div>}
        {geometryError && <div className="error-message">{geometryError}</div>}
        
        {/* Geometry Results Display */} 
        {geometryResults && !geometryLoading && !geometryError && (
            <div className="results-container">
                 <GeometryResultsDisplay results={geometryResults} /> 
                 {/* Button to calculate embedding diagram */} 
                 <div className="action-button-container">
                     <button onClick={handleCalculateEmbedding} disabled={embeddingLoading || !metricDef} className="secondary-action-button">
                         Calculate Flamm's Paraboloid
                     </button>
                     {embeddingLoading && <span className="inline-loader"> Loading...</span>}
                 </div>
                 {embeddingError && <div className="error-message">{embeddingError}</div>}
                 {embeddingResult && !embeddingLoading && !embeddingError && (
                     <div className="embedding-result-container results-container">
                         <h5>Flamm's Paraboloid</h5>
                         <p><i>Status: {embeddingResult.message}</i></p>
                         {embeddingResult.z_function_latex && (
                             <p><InlineMath math={`z(r) = ${embeddingResult.z_function_latex}`} /></p>
                         )}
                         {/* Embedding Plot */} 
                         {embeddingResult.x_surface && 
                            <div className="plot-wrapper">
                                <Plot 
                                    data={getEmbeddingSurfaceData()} 
                                    layout={getEmbeddingSurfaceLayout()} 
                                    useResizeHandler={true}
                                    style={{ width: '100%', height: '500px' }}
                                />
                            </div>
                         } 
                     </div>
                 )}
            </div>
        )}

        <hr className="section-divider" />

        {/* Stress-Energy Input - Now Controlled */} 
        {metricDef && (
          <>
            <StressEnergyInputForm 
                stressEnergyDef={stressEnergyDef}
                onStateChange={handleStressEnergyStateChange}
                onSubmit={handleCalculateStressEnergy} 
            />
            {stressEnergyLoading && <div className="loading-indicator">Calculating Stress-Energy Tensor...</div>}
            {stressEnergyError && <div className="error-message">{stressEnergyError}</div>}
            
            {stressEnergyResults && !stressEnergyLoading && !stressEnergyError && (
                <div className="results-container">
                    <h3>Calculated Stress-Energy Tensor (<InlineMath math="T_{\mu\nu}" />)</h3>
                    <GeometryResultsDisplay results={{ stress_energy_tensor: stressEnergyResults.stress_energy_tensor }} />
                </div>
            )}
            
            {/* EFE Verification */} 
            <div className="verification-section">
                <button 
                    onClick={handleVerifyEFE} 
                    disabled={!geometryResults || !stressEnergyResults || efeLoading}
                    className="verify-button"
                    title={(!geometryResults || !stressEnergyResults) ? "Calculate Geometry and Tmunu first" : "Verify Gmunu = kappa * Tmunu"}
                >
                    Verify Einstein Field Equations (G<sub>&mu;&nu;</sub> = T<sub>&mu;&nu;</sub>)
                </button>
                {efeLoading && <div className="loading-indicator">Verifying EFEs...</div>}
                {efeError && <div className="error-message">{efeError}</div>}
                {efeVerificationResult && !efeLoading && !efeError && (
                    <div className={`verification-result ${efeVerificationResult.verified ? 'verified-true' : 'verified-false'}`}>
                        <strong>Verification Result:</strong> {efeVerificationResult.message}
                    </div>
                )}
            </div>
          </>
        )}

         <hr className="section-divider" />

         {/* Geodesic Calculation Section */} 
         {metricDef && (
            <div className="geodesic-section">
                <GeodesicInputForm 
                    onSubmit={handleCalculateGeodesic} 
                    currentCoords={metricDef?.coords}
                />
                {geodesicLoading && <div className="loading-indicator">Calculating Geodesic...</div>}
                {geodesicError && <div className="error-message">{geodesicError}</div>}

                {/* Geodesic Plots */} 
                {geodesicResults && !geodesicLoading && !geodesicError && (
                    <div className="plot-container results-container">
                        <h3>Geodesic Plots</h3>
                        <div className="plot-wrapper">
                            <Plot data={getRVSTPlotData()} layout={getRVSTPlotLayout()} useResizeHandler={true} style={{ width: '100%', height: '400px' }}/>
                        </div>
                        <div className="plot-wrapper">
                            <Plot data={getXYPlotData()} layout={getXYPlotLayout()} useResizeHandler={true} style={{ width: '100%', height: '450px' }}/>
                        </div>
                    </div>
                )}
            </div>
         )}

      </main>
    </div>
  );
}

export default App; 