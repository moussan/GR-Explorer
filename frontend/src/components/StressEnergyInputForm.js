import React from 'react';
import { InlineMath } from 'react-katex';
import './StressEnergyInputForm.css';

// Define initial state structure (can be used in App.js)
export const initialStressEnergyState = () => ({
    definition_method: 'preset', // 'preset' or 'components'
    preset_name: 'vacuum', // 'vacuum', 'dust', 'perfect_fluid'
    components: [
        ['0', '0', '0', '0'],
        ['0', '0', '0', '0'],
        ['0', '0', '0', '0'],
        ['0', '0', '0', '0']
    ],
    params: { density: 'rho', pressure: 'p' },
});

const presetOptions = [
    { value: 'vacuum', label: 'Vacuum (Tμν = 0)' },
    { value: 'dust', label: 'Dust' },
    { value: 'perfect_fluid', label: 'Perfect Fluid' },
];

function StressEnergyInputForm({ stressEnergyDef, onStateChange, onSubmit }) {
    // Destructure props for easier access
    const {
        definition_method = 'preset',
        preset_name = 'vacuum',
        components = initialStressEnergyState().components, // Default if not provided
        params = initialStressEnergyState().params,
    } = stressEnergyDef || {}; // Handle case where stressEnergyDef might be initially null

    // --- Event Handlers --- 
    // These now call the onStateChange prop passed from App.js
    const handleMethodChange = (event) => {
        const newMethod = event.target.value;
        // Reset fields when method changes - logic moved to App.js reducer/handler
        onStateChange({ definition_method: newMethod }); 
    };

    const handlePresetChange = (event) => {
        onStateChange({ preset_name: event.target.value });
    };

    const handleComponentChange = (event, rowIndex, colIndex) => {
        const newValue = event.target.value;
        // Need a way to update nested state in App.js
        // Pass necessary info to the handler
        onStateChange({ 
            components: components.map((row, rIdx) =>
                row.map((col, cIdx) =>
                    (rIdx === rowIndex && cIdx === colIndex) ? newValue : col
                )
            )
        });
    };

    const handleParamChange = (event) => {
        const { name, value } = event.target;
        onStateChange({ 
            params: { ...params, [name]: value } 
        });
    };

    // Submit handler just calls the onSubmit from props
    const handleSubmit = (event) => {
        event.preventDefault();
        onSubmit(); // App.js uses its own state (stressEnergyDef)
    };

    // Ensure definition exists before rendering
    if (!stressEnergyDef) {
        return <p>Loading stress-energy form...</p>;
    }

    return (
        <form onSubmit={handleSubmit} className="stress-energy-form">
            <h3>Define Stress-Energy Tensor (T<sub>&mu;&nu;</sub>)</h3>

            <div className="method-selection">
                <label>
                    <input 
                        type="radio" 
                        name="definitionMethod"
                        value="preset"
                        checked={definition_method === 'preset'} // Use prop value
                        onChange={handleMethodChange} // Use handler
                    />
                    Use Preset
                </label>
                <label>
                    <input 
                        type="radio" 
                        name="definitionMethod"
                        value="components"
                        checked={definition_method === 'components'} // Use prop value
                        onChange={handleMethodChange} // Use handler
                    />
                    Manual Components
                </label>
            </div>

            {definition_method === 'preset' && (
                <div className="preset-options">
                    <label htmlFor="preset-select">Select Preset:</label>
                    <select 
                        id="preset-select"
                        value={preset_name} // Use prop value
                        onChange={handlePresetChange} // Use handler
                    >
                        {presetOptions.map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>

                    {preset_name === 'dust' && (
                        <div className="parameter-input">
                            <label htmlFor="density">Density (&rho;):</label>
                            <input 
                                type="text"
                                id="density"
                                name="density"
                                value={params.density} // Use prop value
                                onChange={handleParamChange} // Use handler
                            />
                        </div>
                    )}

                    {preset_name === 'perfect_fluid' && (
                        <> 
                            <div className="parameter-input">
                                <label htmlFor="density">Density (&rho;):</label>
                                <input 
                                    type="text"
                                    id="density"
                                    name="density"
                                    value={params.density} // Use prop value
                                    onChange={handleParamChange} // Use handler
                                />
                            </div>
                            <div className="parameter-input">
                                <label htmlFor="pressure">Pressure (p):</label>
                                <input 
                                    type="text"
                                    id="pressure"
                                    name="pressure"
                                    value={params.pressure} // Use prop value
                                    onChange={handleParamChange} // Use handler
                                />
                            </div>
                            <p className="info-text">Note: Perfect Fluid calculation requires the current Metric definition.</p>
                        </>
                    )}
                </div>
            )}

            {definition_method === 'components' && (
                <div className="components-grid">
                     {components.map((row, rowIndex) => (
                        <div key={rowIndex} className="component-row">
                            {row.map((component, colIndex) => (
                                <input 
                                    key={`${rowIndex}-${colIndex}`}
                                    type="text"
                                    value={component} // Use prop value
                                    onChange={(e) => handleComponentChange(e, rowIndex, colIndex)} // Use handler
                                    className="component-input-field"
                                    aria-label={`Tensor component T_${rowIndex}${colIndex}`}
                                />
                            ))}
                        </div>
                    ))}
                </div>
            )}

            <div className="button-group">
                 <button type="submit" className="primary-button">Calculate <InlineMath math="T_{\mu\nu}" /></button>
            </div>
        </form>
    );
}

export default StressEnergyInputForm; 