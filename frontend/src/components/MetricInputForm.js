import React, { useState, useEffect } from 'react';
import './MetricInputForm.css'; // We'll create this CSS file next

// Function to generate the initial state can still be useful in App.js
export const initialMetricState = () => ({
    components: [
        ["-(1 - 2*M/r)", "0", "0", "0"],
        ["0", "1/(1 - 2*M/r)", "0", "0"],
        ["0", "0", "r**2", "0"],
        ["0", "0", "0", "r**2*sin(theta)**2"]
    ],
    coords: ["t", "r", "theta", "phi"]
});

// Component now receives values and handlers as props
function MetricInputForm({ metricDef, onMetricChange, onCoordChange, onSubmit, onReset }) {

    // --- State for Validation Flags --- 
    const [isFormValid, setIsFormValid] = useState(false);
    const [hasEmptyCoords, setHasEmptyCoords] = useState(true);

    // --- Validation Effect --- 
    useEffect(() => {
        if (!metricDef) return; // Should not happen if used correctly, but safe check

        // Check coordinates
        const emptyCoords = metricDef.coords.some(coord => coord.trim() === '');
        setHasEmptyCoords(emptyCoords);

        // Check metric components (simple non-empty check)
        const emptyComponents = metricDef.components.flat().some(comp => comp.trim() === '');
        setIsFormValid(!emptyComponents && !emptyCoords); // Valid if no empty components AND no empty coords

    }, [metricDef]); // Re-run validation whenever metricDef changes

    const handleComponentChange = (event, rowIndex, colIndex) => {
        const newValue = event.target.value;
        // Call the handler passed from App.js to update the state there
        onMetricChange(rowIndex, colIndex, newValue);
    };

    const handleCoordChange = (event, index) => {
        const newValue = event.target.value;
        onCoordChange(index, newValue);
    };

    // Use the passed onSubmit and onReset handlers
    const handleSubmit = (event) => {
        event.preventDefault();
        // Although button is disabled, add extra check just in case
        if (!isFormValid || hasEmptyCoords) {
            console.warn("Submit attempted with invalid form state.");
            // Optionally, show a persistent error message or rely on button state
            return; 
        }
        onSubmit(); // Call the onSubmit passed from App.js
    };

    // Ensure metricDef and metricDef.components/coords exist before rendering
    if (!metricDef || !metricDef.components || !metricDef.coords) {
        // Or render a loading state, but returning null might be simplest if App.js guarantees it
        return <p>Loading metric form...</p>; 
    }

    return (
        <form onSubmit={handleSubmit} className="metric-form">
            <h3>Define Metric Tensor (g<sub>&mu;&nu;</sub>)</h3>
            
            <div className="coords-input">
                <label>Coordinates (&mu; = 0, 1, 2, 3):</label>
                {metricDef.coords.map((coord, index) => (
                    <input 
                        key={index}
                        type="text"
                        value={coord} // Value comes from props
                        onChange={(e) => handleCoordChange(e, index)} // Handler comes from props
                        aria-label={`Coordinate ${index}`}
                        placeholder={`x${index}`}
                        // Combine existing class (if any) with error class logic
                        className={`coord-input-field ${coord.trim() === '' ? 'input-error' : ''}`.trim()} 
                    />
                ))}
            </div>

            <div className="metric-grid">
                {metricDef.components.map((row, rowIndex) => (
                    <div key={rowIndex} className="metric-row">
                        {row.map((component, colIndex) => (
                            <input 
                                key={`${rowIndex}-${colIndex}`}
                                type="text"
                                value={component} // Value comes from props
                                onChange={(e) => handleComponentChange(e, rowIndex, colIndex)} // Handler comes from props
                                aria-label={`Metric component g_${rowIndex}${colIndex}`}
                                placeholder={`g_${rowIndex}${colIndex}`}
                                // Combine existing class (if any) with error class logic
                                className={`metric-input-field ${component.trim() === '' ? 'input-error' : ''}`.trim()} 
                            />
                        ))}
                    </div>
                ))}
            </div>
            {/* Group action buttons */} 
            <div className="button-group">
                <button 
                    type="submit" 
                    disabled={!isFormValid || hasEmptyCoords} // Use the calculated state variables
                    className="primary-button" 
                    title={
                        hasEmptyCoords ? "Enter non-empty coordinate symbols" : 
                        !isFormValid ? "Enter expressions for all metric components" : 
                        "Calculate geometric tensors"
                    } // Dynamic title
                >
                    Calculate Geometry
                </button>
                <button 
                    type="button" 
                    onClick={onReset} 
                    className="danger-button" 
                >
                    Reset Metric
                </button>
            </div>
        </form>
    );
}

export default MetricInputForm; 