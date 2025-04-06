import sympy
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Union, Tuple, Optional

# ==============================================================================
# Base Models & Common Types
# ==============================================================================

class SymbolicTensorInput(BaseModel):
    """Input for defining a tensor via its components as strings."""
    components: List[List[str]] = Field(..., description="4x4 list of lists containing strings representing tensor components.")
    coords: List[str] = Field(default=["t", "r", "theta", "phi"], description="List of 4 coordinate variable names used in components.")

    @validator('components')
    def check_components_shape(cls, v):
        if len(v) != 4 or not all(len(row) == 4 for row in v):
            raise ValueError("Tensor components must be a 4x4 list of lists.")
        # Further validation could check if strings are parseable by SymPy here or in the endpoint
        return v

    @validator('coords')
    def check_coords_len(cls, v):
        if len(v) != 4:
            raise ValueError("Coordinates list must contain 4 symbols.")
        return v

class SymbolicTensorOutput(BaseModel):
    """Output structure for a symbolic tensor (components as LaTeX strings)."""
    components_latex: Dict[str, str] = Field(..., description="Dictionary mapping index strings (e.g., '00', '12') to LaTeX strings.")
    # Optional: Could also include the raw SymPy string representation
    # components_sympy: Dict[str, str] = Field(..., description="Dictionary mapping index strings to SymPy string representations.")
    
class SymbolicScalarOutput(BaseModel):
    """Output structure for a symbolic scalar value."""
    latex: str = Field(..., description="LaTeX string representation of the scalar.")
    # sympy_str: str = Field(..., description="SymPy string representation of the scalar.")

# ==============================================================================
# Metric & Geometry Calculation Models
# ==============================================================================

class MetricInput(SymbolicTensorInput):
    """Input model specifically for defining the metric tensor g_munu."""
    pass # Inherits structure from SymbolicTensorInput

class GeometryCalculationsResponse(BaseModel):
    """Response model containing all calculated geometric quantities."""
    metric: Optional[SymbolicTensorOutput] = None
    inverse_metric: Optional[SymbolicTensorOutput] = None
    christoffel: Optional[SymbolicTensorOutput] = None # Note: This is 3-indexed, might need specific format
    riemann: Optional[SymbolicTensorOutput] = None    # Note: This is 4-indexed, might need specific format
    ricci_tensor: Optional[SymbolicTensorOutput] = None
    ricci_scalar: Optional[SymbolicScalarOutput] = None
    einstein_tensor: Optional[SymbolicTensorOutput] = None
    
    # We might represent multi-index tensors differently, e.g.,
    # christoffel_latex: Dict[str, str] # Keys like "0_12", "1_33" etc.
    # riemann_latex: Dict[str, str]     # Keys like "0_123", "3_010" etc.

# ==============================================================================
# Stress-Energy Tensor Models
# ==============================================================================

class StressEnergyPresetInput(BaseModel):
    """Input for selecting a preset Stress-Energy tensor."""
    preset_name: str = Field(..., description="Name of the preset ('vacuum', 'dust', 'perfect_fluid').")
    params: Dict[str, str] = Field(default={}, description="Parameters for the preset (e.g., {'density': 'rho_0', 'pressure': 'p_0'}).")
    # Metric components might be needed if the preset requires the metric (e.g., perfect fluid)
    metric_components: Optional[List[List[str]]] = Field(None, description="Metric components (needed for some presets like perfect fluid).")
    coords: List[str] = Field(default=["t", "r", "theta", "phi"], description="Coordinate variable names.")


class StressEnergyInput(BaseModel):
    """Input model allowing either direct components or a preset."""
    definition_method: str = Field(..., description="Method: 'components' or 'preset'.")
    components: Optional[List[List[str]]] = Field(None, description="4x4 tensor components (if method is 'components').")
    preset_name: Optional[str] = Field(None, description="Name of preset (if method is 'preset').")
    params: Optional[Dict[str, str]] = Field(default={}, description="Parameters for preset.")
    coords: List[str] = Field(default=["t", "r", "theta", "phi"], description="Coordinate variable names.")
     # Metric needed for perfect fluid preset calculation, passed alongside if needed
    metric_components: Optional[List[List[str]]] = Field(None, description="Metric components (needed for perfect fluid preset).")

    @validator('definition_method')
    def check_method(cls, v):
        if v not in ['components', 'preset']:
            raise ValueError("definition_method must be 'components' or 'preset'.")
        return v

    # Could add more complex validation logic here, e.g., ensure 'components' is provided
    # if method is 'components', and 'preset_name' if method is 'preset'.

class StressEnergyResponse(BaseModel):
    """Response containing the defined Stress-Energy tensor."""
    stress_energy_tensor: SymbolicTensorOutput


# ==============================================================================
# EFE Verification Models
# ==============================================================================

class EFEVerificationRequest(BaseModel):
    """Request to verify the Einstein Field Equations for a given setup."""
    metric_input: MetricInput
    stress_energy_input: StressEnergyInput
    coupling_constant_str: str = Field(default="1", description="String representation of the coupling constant kappa (e.g., '1', '8*pi*G').")
    
class EFEVerificationResponse(BaseModel):
    """Response indicating whether the EFEs are satisfied."""
    verified: bool = Field(..., description="True if G_munu = kappa * T_munu holds (symbolically), False otherwise.")
    message: str = Field(..., description="Details about the verification result (e.g., 'EFEs satisfied', 'Mismatch found in component G_00').")
    # Optional: could include the calculated G and T tensors for debugging
    # einstein_tensor: Optional[SymbolicTensorOutput] = None
    # stress_energy_tensor: Optional[SymbolicTensorOutput] = None


# ==============================================================================
# Geodesic Calculation Models
# ==============================================================================

class GeodesicInput(BaseModel):
    """Input for calculating a geodesic path."""
    metric_components: List[List[str]] = Field(..., description="Metric components defining the spacetime.")
    coords: List[str] = Field(default=["t", "r", "theta", "phi"], description="Coordinate variable names.")
    initial_position: List[float] = Field(..., description="Initial position [x0, x1, x2, x3].")
    initial_velocity: List[float] = Field(..., description="Initial 4-velocity [u0, u1, u2, u3].")
    t_span: Tuple[float, float] = Field(..., description="Integration interval [tau_min, tau_max].")
    num_points: int = Field(default=200, description="Number of points to evaluate the solution at.")
    # Optional: allow passing solver options
    solver_options: Optional[Dict[str, Any]] = Field(default={}, description="Optional arguments for scipy.integrate.solve_ivp.")
    # Optional: specify parameter values (like M=1.0)
    parameter_values: Optional[Dict[str, float]] = Field(default={}, description="Numerical values for symbolic constants in the metric.")


class GeodesicOutput(BaseModel):
    """Output for a calculated geodesic path."""
    tau_values: List[float] = Field(..., description="List of proper time/affine parameter values.")
    position_coords: Dict[str, List[float]] = Field(..., description="Dictionary mapping coordinate names to lists of position values.")
    velocity_coords: Dict[str, List[float]] = Field(..., description="Dictionary mapping coordinate names to lists of 4-velocity values.")
    message: str = Field(default="Geodesic calculated successfully.", description="Status message.")

# ==============================================================================
# Embedding Diagram Models
# ==============================================================================

class EmbeddingInput(BaseModel):
    """Input for calculating embedding diagrams (initially Flamm's)."""
    metric_input: MetricInput # Reuse metric input model
    # Add fields for numerical evaluation parameters
    parameter_values: Optional[Dict[str, float]] = Field(default={}, description="Numerical values for symbolic constants (e.g., M=1.0).")
    r_min: Optional[float] = Field(None, description="Minimum r value for numerical evaluation (defaults to event horizon if M is given, else e.g., 0.1).")
    r_max: Optional[float] = Field(default=10.0, description="Maximum r value for numerical evaluation.")
    num_points_r: Optional[int] = Field(default=50, description="Number of points for r dimension.")
    num_points_phi: Optional[int] = Field(default=60, description="Number of points for phi dimension (for 3D plot).")

class EmbeddingOutput(BaseModel):
    """Output for Flamm's paraboloid calculation."""
    z_function_latex: Optional[str] = Field(None, description="LaTeX string for the embedding function z(r).")
    message: str = Field(..., description="Status message, includes error if calculation failed.")
    # Add fields for numerical data
    r_values: Optional[List[float]] = None
    z_values: Optional[List[float]] = None 
    # For 3D surface plot
    x_surface: Optional[List[List[float]]] = None
    y_surface: Optional[List[List[float]]] = None
    z_surface: Optional[List[List[float]]] = None


# ==============================================================================
# Scenario Management Models
# ==============================================================================

class ScenarioDefinition(BaseModel):
    """Structure representing a saved scenario."""
    metric_input: MetricInput
    stress_energy_input: StressEnergyInput
    # Optional: Could add description, geodesic defaults, etc. later
    # description: Optional[str] = None

class SaveScenarioInput(BaseModel):
    """Input for saving a scenario."""
    scenario_name: str = Field(..., description="Unique name for the scenario.")
    definition: ScenarioDefinition
    
    @validator('scenario_name')
    def validate_name(cls, v):
        # Basic validation: prevent empty names and potentially harmful characters
        if not v or '/' in v or '\\' in v or '.' in v:
             raise ValueError("Scenario name cannot be empty or contain '/', '\\', '.'")
        return v

class ScenarioListOutput(BaseModel):
    """Output listing available scenario names."""
    scenario_names: List[str]

class ScenarioLoadOutput(BaseModel):
    """Output when loading a scenario."""
    scenario_name: str
    definition: ScenarioDefinition

# ==============================================================================
# Geodesic Calculation Models
# ==============================================================================
# ... rest of models ... 