import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import './ScenarioManager.css';

const API_BASE_URL = '/api'; // Assuming same base as App.js

function ScenarioManager({ currentMetricDef, currentStressEnergyInput, onLoadScenario }) {
    const [scenarioList, setScenarioList] = useState([]);
    const [selectedScenario, setSelectedScenario] = useState('');
    const [newScenarioName, setNewScenarioName] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [saveMessage, setSaveMessage] = useState(null);

    // Fetch scenario list on component mount
    useEffect(() => {
        fetchScenarioList();
    }, []);

    const fetchScenarioList = () => {
        setIsLoading(true);
        setError(null);
        axios.get(`${API_BASE_URL}/scenarios`)
            .then(response => {
                setScenarioList(response.data.scenario_names || []);
            })
            .catch(err => {
                console.error("Error fetching scenario list:", err);
                const msg = "Could not load scenario list.";
                setError(msg);
                toast.error(msg);
                setScenarioList([]);
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    const handleLoad = () => {
        if (!selectedScenario) return;
        setIsLoading(true);
        setError(null);
        axios.get(`${API_BASE_URL}/scenarios/${selectedScenario}`)
            .then(response => {
                console.log("Loaded scenario:", response.data);
                onLoadScenario(response.data.definition);
            })
            .catch(err => {
                const msg = `Failed to load scenario: ${err.response?.data?.detail || err.message}`;
                console.error(`Error loading scenario ${selectedScenario}:`, err);
                setError(msg);
                toast.error(msg);
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    const handleSave = () => {
        let errorMsg = null;
        if (!newScenarioName) {
            errorMsg = "Please enter a name for the new scenario.";
        } else if (!currentMetricDef || !currentStressEnergyInput) {
            errorMsg = "Both Metric and Stress-Energy must be defined to save a scenario.";
        }
        
        if (errorMsg) {
            setError(errorMsg);
            toast.warn(errorMsg);
            return;
        }

        setIsLoading(true);
        setError(null);
        setSaveMessage(null);

        const payload = {
            scenario_name: newScenarioName,
            definition: {
                metric_input: currentMetricDef,
                stress_energy_input: currentStressEnergyInput,
            }
        };

        axios.post(`${API_BASE_URL}/scenarios`, payload)
            .then(response => {
                const msg = response.data.message || "Scenario saved successfully!";
                setSaveMessage(msg);
                toast.success(msg);
                setNewScenarioName('');
                fetchScenarioList();
            })
            .catch(err => {
                const msg = `Failed to save scenario: ${err.response?.data?.detail || err.message}`;
                console.error(`Error saving scenario ${newScenarioName}:`, err);
                setError(msg);
                toast.error(msg);
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    const handleDeleteClick = () => {
        if (!selectedScenario) return;

        // Optional: Add a confirmation dialog
        if (!window.confirm(`Are you sure you want to delete the scenario "${selectedScenario}"?`)) {
            return;
        }

        setIsLoading(true);
        setError(null);
        axios.delete(`${API_BASE_URL}/scenarios/${selectedScenario}`)
            .then(response => {
                const msg = response.data.message || `Scenario "${selectedScenario}" deleted successfully.`;
                toast.success(msg);
                setSelectedScenario(''); // Clear selection after delete
                fetchScenarioList(); // Refresh the list
            })
            .catch(err => {
                const msg = `Failed to delete scenario: ${err.response?.data?.detail || err.message}`;
                console.error(`Error deleting scenario ${selectedScenario}:`, err);
                setError(msg);
                toast.error(msg);
            })
            .finally(() => {
                setIsLoading(false);
            });
    };

    return (
        <div className="scenario-manager content-section">
            <h4>Scenario Management</h4>
            {error && <p className="error-message">{error}</p>}
            {isLoading && <div className="loading-indicator small-loader">Updating scenarios...</div>}

            <div className="scenario-controls">
                <div className="scenario-group load-group">
                    <label htmlFor="scenario-select">Load Scenario:</label>
                    <select 
                        id="scenario-select"
                        value={selectedScenario}
                        onChange={(e) => setSelectedScenario(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="">-- Select --</option>
                        {scenarioList.map(name => (
                            <option key={name} value={name}>{name}</option>
                        ))}
                    </select>
                    <button 
                        onClick={handleLoad} 
                        disabled={!selectedScenario || isLoading} 
                        className="secondary-button" 
                    >
                        Load
                    </button>
                    <button 
                        onClick={handleDeleteClick}
                        disabled={!selectedScenario || isLoading} 
                        className="danger-button danger-button-small"
                        title="Delete selected scenario"
                    >
                        Delete
                    </button>
                </div>

                <div className="scenario-group save-group">
                    <label htmlFor="scenario-save-name">Save As:</label>
                    <input 
                        id="scenario-save-name"
                        type="text"
                        placeholder="New scenario name"
                        value={newScenarioName}
                        onChange={(e) => setNewScenarioName(e.target.value)}
                        disabled={isLoading}
                    />
                    <button 
                        onClick={handleSave} 
                        disabled={!newScenarioName || !currentMetricDef || isLoading}
                        className="primary-button"
                        title={!currentMetricDef ? "Define a metric first" : "Save current inputs as scenario"}
                    >
                        Save
                    </button>
                    {saveMessage && <span className="success-message">{saveMessage}</span>}
                </div>
            </div>
        </div>
    );
}

export default ScenarioManager; 