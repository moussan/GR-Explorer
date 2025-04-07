import React, { useState, useEffect } from 'react';
import './GeodesicInputForm.css'; // Create CSS file next

// Default initial state example (corresponds to Schwarzschild radial infall from r=10)
// Note: Proper initial velocity often depends on normalization with the *specific* metric.
// This form provides the fields; calculation of correct u^mu might happen externally or need guidance.
// const defaultInitialPosition = ["0.0", "10.0", "1.570796", "0.0"]; // t, r, theta=pi/2, phi
// const defaultInitialVelocity = ["1.118", "0.0", "0.0", "0.0"]; // dt/dtau, dr/dtau, dtheta/dtau, dphi/dtau (example for M=1, r=10)
// const defaultTimeSpan = ["0.0", "50.0"];
// const defaultNumPoints = "200";
// const defaultParams = [{ name: 'M', value: '1.0' }];

// Helper to check if a string represents a valid number
const isValidNumber = (value) => !isNaN(parseFloat(value)) && isFinite(value);

function GeodesicInputForm({ onSubmit, onError, currentCoords = ["t", "r", "theta", "phi"] }) {
    const numCoords = currentCoords?.length || 4; // Default to 4 if not provided
    const initialArray = Array(numCoords).fill('');

    const [initialPosition, setInitialPosition] = useState(initialArray);
    const [initialVelocity, setInitialVelocity] = useState(initialArray);
    const [timeSpan, setTimeSpan] = useState(["0.0", "50.0"]); // [tau_min, tau_max]
    const [numPoints, setNumPoints] = useState("200");
    const [parameters, setParameters] = useState([{ name: 'M', value: '1.0' }]); // Array of {name: string, value: string}
    const [isFormValid, setIsFormValid] = useState(false); // State for validity

    // Default coordinate names
    const coordNames = currentCoords || ['t', 'r', 'θ', 'φ'];

    // --- Validation Effect --- 
    useEffect(() => {
        const posValid = initialPosition.every(isValidNumber);
        const velValid = initialVelocity.every(isValidNumber);
        const spanValid = isValidNumber(timeSpan[0]) && isValidNumber(timeSpan[1]) && parseFloat(timeSpan[0]) < parseFloat(timeSpan[1]);
        const pointsValid = isValidNumber(numPoints) && parseInt(numPoints, 10) > 0 && Number.isInteger(Number(numPoints));
        const paramValuesValid = parameters.every(param => isValidNumber(param.value));
        
        setIsFormValid(posValid && velValid && spanValid && pointsValid && paramValuesValid);

        // Clear previous form errors when inputs change
        if (onError) {
            onError(null);
        }
    }, [initialPosition, initialVelocity, timeSpan, numPoints, parameters, onError]);

    const handleInputChange = (setter) => (event, index) => {
        const newValue = event.target.value;
        setter(prev => {
            const updated = [...prev];
            updated[index] = newValue;
            return updated;
        });
    };

    const handleParamChange = (event, index, field) => {
        const newValue = event.target.value;
        setParameters(prev => 
            prev.map((param, i) => (i === index ? { ...param, [field]: newValue } : param))
        );
    };

    const addParameter = () => {
        setParameters(prev => [...prev, { name: '', value: '' }]);
    };

    const removeParameter = (index) => {
        setParameters(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        if (!isFormValid) {
            if (onError) {
                onError("Please fill in all fields with valid numbers. Time span must be valid and positive, and number of points must be an integer greater than 0.");
            }
            return;
        }
        onError(null); // Clear previous form errors on submit

        // Convert numeric fields from string to number, handle potential errors
        try {
            const pos = initialPosition.map(Number);
            const vel = initialVelocity.map(Number);
            const span = timeSpan.map(Number);
            const points = parseInt(numPoints, 10);
            const paramValues = parameters.reduce((acc, param) => {
                if (param.name && param.value) { // Only include if both name and value are present
                    acc[param.name] = parseFloat(param.value);
                    if (isNaN(acc[param.name])) throw new Error(`Invalid number for parameter ${param.name}`);
                }
                return acc;
            }, {});

            if (isNaN(points) || points <= 1) {
                throw new Error("Number of points must be an integer greater than 1.");
            }
            if (span.length !== 2 || isNaN(span[0]) || isNaN(span[1]) || span[0] >= span[1]) {
                throw new Error("Invalid time span [τ_min, τ_max]. Ensure τ_min < τ_max.");
            }
            if (pos.some(isNaN) || vel.some(isNaN)) {
                 throw new Error("Initial position and velocity must contain valid numbers.");
            }

            const payload = {
                initial_position: pos,
                initial_velocity: vel,
                t_span: span,
                num_points: points,
                parameter_values: paramValues,
                // Assumes the App component will add metric_components and coords
            };
            onSubmit(payload);

        } catch (error) {
            console.error("Input validation error:", error);
            onError(`Input Error: ${error.message}`); // Use onError prop
        }
    };

    return (
        <form onSubmit={handleSubmit} className="geodesic-form">
            <h3>Calculate Geodesic Path</h3>
            
            <div className="form-section">
                <h4>Initial Position (x<sup>&mu;</sup> at &tau;=0)</h4>
                <div className="vector-input">
                    {coordNames.map((coord, index) => (
                        <div key={`pos-${index}`} className="input-group">
                            <label htmlFor={`pos-${index}`}>{coord}:</label>
                            <input 
                                id={`pos-${index}`}
                                type="text" 
                                value={initialPosition[index]}
                                onChange={(e) => handleInputChange(setInitialPosition)(e, index)}
                                placeholder={`${coord}₀`}
                                aria-label={`Initial position ${coord}`}
                                className={!isValidNumber(initialPosition[index]) && initialPosition[index] !== '' ? 'input-error' : ''}
                            />
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <h4>Initial 4-Velocity (u<sup>&mu;</sup> = dx<sup>&mu;</sup>/d&tau; at &tau;=0)</h4>
                 <p className="info-text">Note: Ensure velocity satisfies normalization (g<sub>&mu;&nu;</sub>u<sup>&mu;</sup>u<sup>&nu;</sup> = -1 for timelike, 0 for null) for the chosen metric.</p>
                <div className="vector-input">
                    {coordNames.map((coord, index) => (
                        <div key={`vel-${index}`} className="input-group">
                            <label htmlFor={`vel-${index}`}>d{coord}/d&tau;:</label>
                            <input 
                                id={`vel-${index}`}
                                type="text" 
                                value={initialVelocity[index]}
                                onChange={(e) => handleInputChange(setInitialVelocity)(e, index)}
                                placeholder={`d${coord}/dtau₀`}
                                aria-label={`Initial velocity d${coord}/dtau`}
                                className={!isValidNumber(initialVelocity[index]) && initialVelocity[index] !== '' ? 'input-error' : ''}
                            />
                        </div>
                    ))}
                </div>
            </div>

            <div className="form-section">
                <h4>Integration Parameters</h4>
                <div className="integration-params">
                    <div className="input-group">
                        <label htmlFor="tau-min">Min Affine Param. (&tau;<sub>min</sub>):</label>
                        <input 
                            id="tau-min"
                            type="text" 
                            value={timeSpan[0]}
                            onChange={(e) => handleInputChange(setTimeSpan)(e, 0)}
                            className={(!isValidNumber(timeSpan[0]) || parseFloat(timeSpan[0]) >= parseFloat(timeSpan[1])) && timeSpan[0] !== '' ? 'input-error' : ''}
                        />
                    </div>
                    <div className="input-group">
                        <label htmlFor="tau-max">Max Affine Param. (&tau;<sub>max</sub>):</label>
                        <input 
                            id="tau-max"
                            type="text" 
                            value={timeSpan[1]}
                            onChange={(e) => handleInputChange(setTimeSpan)(e, 1)}
                            className={(!isValidNumber(timeSpan[1]) || parseFloat(timeSpan[1]) <= parseFloat(timeSpan[0])) && timeSpan[1] !== '' ? 'input-error' : ''}
                        />
                    </div>
                     <div className="input-group">
                        <label htmlFor="num-points">Number of Points:</label>
                        <input 
                            id="num-points"
                            type="number" 
                            value={numPoints}
                            onChange={(e) => setNumPoints(e.target.value)}
                            min="2" 
                            step="1"
                            className={(!isValidNumber(numPoints) || parseInt(numPoints, 10) <= 1) && numPoints !== '' ? 'input-error' : ''}
                        />
                    </div>
                </div>
            </div>

            <div className="form-section">
                <h4>Parameter Values (Numerical)</h4>
                <p className="info-text">Provide numerical values for symbolic constants in the metric (e.g., M, a, Q).</p>
                {parameters.map((param, index) => (
                    <div key={index} className="parameter-entry">
                        <input 
                            type="text"
                            placeholder="Symbol (e.g., M)"
                            value={param.name}
                            onChange={(e) => handleParamChange(e, index, 'name')}
                            className="param-name-input"
                        />
                        <span className="param-equals">=</span>
                        <input 
                             type="text"
                             placeholder="Value (e.g., 1.0)"
                             value={param.value}
                             onChange={(e) => handleParamChange(e, index, 'value')}
                             className="param-value-input"
                        />
                        <button type="button" onClick={() => removeParameter(index)} className="remove-param-button">
                            &times;
                        </button>
                    </div>
                ))}
                <button type="button" onClick={addParameter} className="add-param-button">
                    + Add Parameter
                </button>
            </div>

            <div className="button-group">
                <button 
                    type="submit" 
                    disabled={!isFormValid}
                    className="primary-button"
                    title={!isFormValid ? "Fill in all fields with valid positive numbers." : "Calculate geodesic path"}
                >
                    Calculate Geodesic
                </button>
                 {/* Optionally add a reset button here */}
                 {/* <button type="button" onClick={handleReset} className="secondary-button">Reset Fields</button> */}
            </div>
        </form>
    );
}

export default GeodesicInputForm; 