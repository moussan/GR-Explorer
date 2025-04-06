import React from 'react';
import 'katex/dist/katex.min.css'; // Import KaTeX CSS
import { BlockMath, InlineMath } from 'react-katex';
import './GeometryResultsDisplay.css'; // For styling

// Helper function to format tensor index strings (e.g., "0_12" -> "^0_{12}")
const formatIndex = (indexStr) => {
    if (indexStr.includes('_')) {
        const parts = indexStr.split('_');
        return `^{${parts[0]}}_{${parts[1]}}`;
    } else if (indexStr.length === 4) { // Assume R^rho_sigma_mu_nu format
         // TODO: Improve index formatting for Riemann if needed 
         // Example: "0_123" might need a specific structure
         // For now, just use the basic split
         const parts = indexStr.split('_');
         if(parts.length === 2) return `^{${parts[0]}}_{${parts[1]}}`;
         return `_{${indexStr}}`; // Fallback
    }
    // Default for 2 indices (e.g., "00", "12")
    return `_{${indexStr}}`;
};

// Helper to render a dictionary of tensor components
const renderTensorComponents = (components, tensorSymbol) => {
    if (!components || Object.keys(components).length === 0) {
        return <p>No non-zero components or not calculated.</p>;
    }
    
    // Sort keys for consistent display order (optional)
    const sortedKeys = Object.keys(components).sort();

    return (
        <div className="tensor-components">
            {sortedKeys.map(key => (
                <div key={key} className="tensor-component-item">
                    {/* Use index prop in InlineMath if available for better keying */} 
                    <InlineMath math={`${tensorSymbol}${formatIndex(key)} = `} />
                    <BlockMath math={components[key]} /> 
                </div>
            ))}
        </div>
    );
};

// Function to create a clickable title
const ClickableTitle = ({ title, definitionKey, onShowDefinition }) => (
    <button className="definition-link" onClick={() => onShowDefinition(definitionKey)}>
        {title}
    </button>
);

function GeometryResultsDisplay({ results, onShowDefinition }) {
    if (!results) {
        return null; // Don't render anything if there are no results
    }

    // Helper to create title component
    const InfoTitle = ({ title, definitionKey }) => (
        <ClickableTitle 
            title={title} 
            definitionKey={definitionKey} 
            onShowDefinition={onShowDefinition} 
        />
    );

    return (
        <div className="results-display">
            <h2>Geometric Quantities</h2>

            {results.metric && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Metric Tensor (<InlineMath math="g_{\mu\nu}" />)</>} definitionKey="metric" /></h3>
                    {renderTensorComponents(results.metric.components_latex, 'g')}
                </div>
            )}

            {results.inverse_metric && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Inverse Metric (<InlineMath math="g^{\mu\nu}" />)</>} definitionKey="inverse_metric" /></h3>
                    {renderTensorComponents(results.inverse_metric.components_latex, 'g')}
                </div>
            )}

            {results.christoffel && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Christoffel Symbols (<InlineMath math="\Gamma^{\lambda}_{\mu\nu}" />)</>} definitionKey="christoffel" /></h3>
                    {renderTensorComponents(results.christoffel.components_latex, '\Gamma')}
                </div>
            )}
            
            {results.riemann && (
                 <div className="result-section">
                    <h3><InfoTitle title={<>Riemann Tensor (<InlineMath math="R^{\rho}_{\sigma\mu\nu}" />)</>} definitionKey="riemann" /></h3>
                    {/* Note: Index formatting might need refinement for 4 indices */} 
                    {renderTensorComponents(results.riemann.components_latex, 'R')}
                </div>
            )}

            {results.ricci_tensor && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Ricci Tensor (<InlineMath math="R_{\mu\nu}" />)</>} definitionKey="ricci_tensor" /></h3>
                    {renderTensorComponents(results.ricci_tensor.components_latex, 'R')}
                </div>
            )}

            {results.ricci_scalar && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Ricci Scalar (<InlineMath math="R" />)</>} definitionKey="ricci_scalar" /></h3>
                    <BlockMath math={results.ricci_scalar.latex} />
                </div>
            )}

            {results.einstein_tensor && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Einstein Tensor (<InlineMath math="G_{\mu\nu}" />)</>} definitionKey="einstein_tensor" /></h3>
                    {renderTensorComponents(results.einstein_tensor.components_latex, 'G')}
                </div>
            )}
            
            {/* Added section for Stress-Energy if passed in */} 
            {results.stress_energy_tensor && (
                <div className="result-section">
                    <h3><InfoTitle title={<>Stress-Energy Tensor (<InlineMath math="T_{\mu\nu}" />)</>} definitionKey="stress_energy_tensor" /></h3>
                    {renderTensorComponents(results.stress_energy_tensor.components_latex, 'T')}
                </div>
            )}
        </div>
    );
}

export default GeometryResultsDisplay; 