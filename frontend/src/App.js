import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios'; // Import axios
import './App.css'; // Optional: for component-specific styles
import { ToastContainer, toast } from 'react-toastify'; // Import toast
import 'react-toastify/dist/ReactToastify.css'; // Import CSS
import MetricInputForm, { initialMetricState } from './components/MetricInputForm';
// Import the results display component
import GeometryResultsDisplay from './components/GeometryResultsDisplay'; 
// Import the Stress-Energy form component
import StressEnergyInputForm, { initialStressEnergyState } from './components/StressEnergyInputForm';
// Import the Geodesic form component
import GeodesicSection from './components/GeodesicSection';
// Import KaTeX for rendering verification results
import 'katex/dist/katex.min.css'; 
import { InlineMath } from 'react-katex';
import ScenarioManager from './components/ScenarioManager'; // Import ScenarioManager
import DefinitionDisplay from './components/DefinitionDisplay'; // Import DefinitionDisplay
import EmbeddingSection from './components/EmbeddingSection'; // Import new component

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

  // State for definition popup
  const [definitionKeyToShow, setDefinitionKeyToShow] = useState(null);

  // Fetch initial welcome message from backend
  useEffect(() => {
    axios.get('/') // Assuming backend root provides a basic message
      .then(response => {
        // Check if the root endpoint returns a message structure
        if (response.data && response.data.message) {
            setBackendMessage(response.data.message);
            toast.info("Connected to backend."); // Optional: Initial connection toast
        } else {
            // Fallback if the root response is different
            setBackendMessage('Backend connected.'); 
        }
      })
      .catch(err => {
        console.error('Error fetching root data from backend:', err);
        const errorMsg = 'Could not reach the backend server. Is it running?';
        setBackendMessage('Failed to connect to backend.');
        setGeometryError(errorMsg); 
        toast.error(errorMsg); // Show error toast
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
      // Clear geodesic params as they depend on metric parameters
      // setCurrentGeodesicParams(null); // No longer needed
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
    // setGeodesicResults(null); // No longer needed
    // setCurrentGeodesicParams(null); // No longer needed
    // setGeodesicError(null); // No longer needed
    // setEmbeddingResult(null); // No longer needed
    // setEmbeddingError(null); // No longer needed

    axios.post(`${API_BASE_URL}/calculate/geometry`, metricDef) // Send current metricDef state
      .then(response => {
        setGeometryResults(response.data);
        toast.success("Geometry calculated successfully!");
      })
      .catch(err => {
        let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during geometry calculation.';
        setGeometryError(`Geometry Error: ${errorMsg}`);
        toast.error(`Geometry Error: ${errorMsg}`);
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
        toast.success("Stress-Energy tensor calculated!");
      })
      .catch(err => {
        let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during T_munu calculation.';
        setStressEnergyError(`Stress-Energy Error: ${errorMsg}`);
        toast.error(`Stress-Energy Error: ${errorMsg}`);
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
          if (response.data.verified) {
              toast.success("EFE Verification: Equations satisfied!");
          } else {
              toast.warn("EFE Verification: Equations NOT satisfied.");
          }
      })
      .catch(err => {
          let errorMsg = err.response?.data?.detail || err.message || 'An error occurred during EFE verification.';
          setEfeError(`EFE Verification Error: ${errorMsg}`);
          toast.error(`EFE Verification Error: ${errorMsg}`);
      })
      .finally(() => {
          setEfeLoading(false);
      });
  };

  // --- Scenario Management Handler --- 
  const handleLoadScenario = useCallback((loadedDefinition) => {
        console.log("Loading scenario definition:", loadedDefinition);
        setMetricDef(loadedDefinition.metric_input);
        setStressEnergyDef(loadedDefinition.stress_energy_input);
        
        // Clear results, including previously tracked geodesic/embedding state
        setGeometryResults(null);
        setGeometryError(null);
        setStressEnergyResults(null);
        setStressEnergyError(null);
        setEfeVerificationResult(null);
        setEfeError(null);
        // setCurrentGeodesicParams(null); // Clear if kept
        // setGeodesicResults(null); // No longer needed
        // setGeodesicError(null); // No longer needed
        // setEmbeddingResult(null); // No longer needed
        // setEmbeddingError(null); // No longer needed
        setDefinitionKeyToShow(null); 
        
        toast.success("Scenario loaded successfully!"); 
   }, []);

   // --- Definition Display Handler ---
   const handleShowDefinition = useCallback((key) => {
       setDefinitionKeyToShow(key);
   }, []);

   const handleCloseDefinition = useCallback(() => {
       setDefinitionKeyToShow(null);
   }, []);

  return (
    <div className="App">
      <ToastContainer 
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
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
        {/* --- Metric Section --- */}
        <section className="content-section metric-section">
            {/* Use h4 for section title */} 
            <h4>Metric Definition (<InlineMath math="g_{\mu\nu}" />)</h4>
            <MetricInputForm 
                metricDef={metricDef} 
                onMetricChange={handleMetricComponentChange}
                onCoordChange={handleMetricCoordChange}
                onSubmit={handleCalculateGeometry} 
                onReset={handleMetricReset}
            />
            {geometryLoading && <div className="loading-indicator">Calculating Geometry...</div>}
        </section>
        
        {/* --- Geometry Results & Embedding Section --- */} 
        {geometryResults && !geometryLoading && !geometryError && (
            <section className="content-section results-section">
                 {/* Title now inside GeometryResultsDisplay */} 
                 {/* <h4>Geometry Results</h4> */} 
                <div className="results-container">
                    <GeometryResultsDisplay 
                        results={geometryResults} 
                        onShowDefinition={handleShowDefinition}
                    /> 
                    <EmbeddingSection 
                        metricDef={metricDef}
                        // currentGeodesicParams={currentGeodesicParams} // Only if needed
                        onShowDefinition={handleShowDefinition}
                    />
                </div>
            </section>
        )}

        <hr className="section-divider" />

        {/* --- Stress-Energy & EFE Section --- */} 
        {metricDef && (
          <section className="content-section stress-energy-section">
             {/* Use h4 for section title */} 
             <h4>Stress-Energy Tensor (<InlineMath math="T_{\mu\nu}" />) & EFE</h4>
            <StressEnergyInputForm 
                stressEnergyDef={stressEnergyDef}
                onStateChange={handleStressEnergyStateChange}
                onSubmit={handleCalculateStressEnergy} 
            />
            {stressEnergyLoading && <div className="loading-indicator">Calculating Stress-Energy Tensor...</div>}
            
            {stressEnergyResults && !stressEnergyLoading && !stressEnergyError && (
                <div className="results-container tmunu-results">
                    <h5>Calculated Stress-Energy Tensor</h5>
                    <GeometryResultsDisplay 
                        results={{ stress_energy_tensor: stressEnergyResults.stress_energy_tensor }} 
                        onShowDefinition={handleShowDefinition} 
                    />
                </div>
            )}
            
            {/* EFE Verification subsection */} 
            <div className="subsection verification-section">
                <h5>Einstein Field Equation Verification</h5>
                <button 
                    onClick={handleVerifyEFE} 
                    disabled={!geometryResults || !stressEnergyResults || efeLoading}
                    className="secondary-button verify-button" // Apply button style later
                    title={(!geometryResults || !stressEnergyResults) ? "Calculate Geometry and Tmunu first" : "Verify Gmunu = kappa * Tmunu"}
                >
                    Verify <InlineMath math="G_{\mu\nu} = \kappa T_{\mu\nu}"/> 
                    <button className="definition-link-inline" onClick={(e) => { e.stopPropagation(); handleShowDefinition('efe'); }}> 
                         (?)
                    </button>
                </button>
                {efeLoading && <div className="loading-indicator">Verifying EFEs...</div>}
                {efeVerificationResult && !efeLoading && !efeError && (
                    <div className={`verification-result ${efeVerificationResult.verified ? 'verified-true' : 'verified-false'}`}>
                        <strong>Result:</strong> {efeVerificationResult.message}
                    </div>
                )}
            </div>
          </section>
        )}

         <hr className="section-divider" />

         {/* --- Geodesic Section --- */} 
         {metricDef && (
             <section className="content-section geodesic-section-wrapper">
                 {/* GeodesicSection component handles its own title */} 
                 <GeodesicSection 
                    metricDef={metricDef} 
                    onShowDefinition={handleShowDefinition}
                    // Optional: Pass setter if EmbeddingSection needs updated geodesic params
                    // onParamsCalculated={setCurrentGeodesicParams} 
                 />
             </section>
         )}

      </main>
      
      {/* Render Definition Popup Conditionally */} 
      {definitionKeyToShow && (
         <DefinitionDisplay 
             itemKey={definitionKeyToShow} 
             onClose={handleCloseDefinition} 
         />
      )}
    </div>
  );
}

export default App; 