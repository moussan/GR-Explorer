import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BlockMath, InlineMath } from 'react-katex';
import './DefinitionDisplay.css';

const API_BASE_URL = '/api'; // Assuming same base as App.js

function DefinitionDisplay({ itemKey, onClose }) {
    const [definition, setDefinition] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!itemKey) return;

        setIsLoading(true);
        setError(null);
        setDefinition(null);

        axios.get(`${API_BASE_URL}/definitions/${itemKey}`)
            .then(response => {
                setDefinition(response.data);
            })
            .catch(err => {
                console.error(`Error fetching definition for ${itemKey}:`, err);
                setError(`Could not load definition: ${err.response?.data?.detail || err.message}`);
            })
            .finally(() => {
                setIsLoading(false);
            });
    }, [itemKey]); // Re-fetch when itemKey changes

    if (!itemKey) return null; // Don't render if no key

    return (
        <div className="definition-popup-overlay" onClick={onClose}> 
            <div className="definition-popup-content" onClick={(e) => e.stopPropagation()}> 
                <button className="close-button" onClick={onClose}>&times;</button>
                {isLoading && <p>Loading definition...</p>}
                {error && <p className="error-text">{error}</p>}
                {definition && (
                    <>
                        <h3><InlineMath math={definition.title || itemKey} /></h3>
                        <p>{definition.definition}</p>
                        {definition.formula && (
                            <div className="formula-section">
                                <h4>Formula:</h4>
                                <BlockMath math={definition.formula} />
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

export default DefinitionDisplay; 