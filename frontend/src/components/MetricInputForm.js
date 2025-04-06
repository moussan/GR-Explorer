import React from 'react';
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
        onSubmit(); // App.js will use its own state (`metricDef`)
    };

    const handleReset = () => {
        onReset(); // Trigger the reset logic in App.js
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
                        className="coord-input-field"
                        aria-label={`Coordinate ${index}`}
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
                                className="metric-input-field"
                                aria-label={`Metric component g_${rowIndex}${colIndex}`}
                            />
                        ))}
                    </div>
                ))}
            </div>
            {/* Group action buttons */} 
            <div className="button-group">
                <button 
                    type="submit" 
                    disabled={!isFormValid || hasEmptyCoords} // Check validity
                    className="primary-button" // Apply primary style
                    title={!isFormValid ? "Enter valid SymPy expressions for all components" : hasEmptyCoords ? "Enter non-empty coordinate symbols" : "Calculate geometric tensors"}
                >
                    Calculate Geometry
                </button>
                <button 
                    type="button" 
                    onClick={onReset} 
                    className="danger-button" // Apply danger style
                >
                    Reset Metric
                </button>
            </div>
        </form>
    );
}

export default MetricInputForm; 