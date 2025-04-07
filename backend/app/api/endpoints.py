import sympy
import numpy as np
from fastapi import APIRouter, HTTPException, Body
from sympy import symbols, Matrix, sympify, latex, Symbol, Array, lambdify
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import os
from pathlib import Path

# Import core calculation functions
from ..core import metric as metric_core
from ..core import christoffel as christoffel_core
from ..core import riemann as riemann_core
from ..core import ricci as ricci_core
from ..core import einstein_tensor as einstein_core
from ..core import stress_energy as stress_energy_core
from ..core import geodesic as geodesic_core
from ..core import embedding as embedding_core

# Import API models
from .models import (
    MetricInput, GeometryCalculationsResponse, SymbolicTensorOutput, SymbolicScalarOutput,
    StressEnergyInput, StressEnergyResponse,
    GeodesicInput, GeodesicOutput,
    EFEVerificationRequest, EFEVerificationResponse,
    EmbeddingInput, EmbeddingOutput,
    SaveScenarioInput, ScenarioListOutput, ScenarioLoadOutput,
    DefinitionItem, DefinitionsOutput
)

router = APIRouter()

# Define the path for saving scenarios within the container
SCENARIO_DIR = Path("/app/data/scenarios")
SCENARIO_DIR.mkdir(parents=True, exist_ok=True) # Ensure directory exists

# Load definitions once on startup
DEFINITIONS_FILE = Path("/app/data/definitions.json")
DEFINITIONS_DATA = {}
if DEFINITIONS_FILE.exists():
    try:
        with open(DEFINITIONS_FILE, "r") as f:
            DEFINITIONS_DATA = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load definitions file {DEFINITIONS_FILE}: {e}")

# Helper function to parse coordinate strings to SymPy symbols
def parse_coords(coord_names: List[str]) -> List[Symbol]:
    return [symbols(name) for name in coord_names]

# Helper function to parse string components to SymPy expressions
def parse_components(components: List[List[str]]) -> List[List[sympy.Expr]]:
    try:
        return [[sympify(comp) for comp in row] for row in components]
    except (sympy.SympifyError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid symbolic expression found: {e}")

# Helper function to format a SymPy Matrix/Array into the output model format
def format_tensor_output(tensor: Union[Matrix, Array], indices: str) -> SymbolicTensorOutput:
    """Formats a tensor into LaTeX dictionary.
    Indices example: 'munu', 'Lmunu' (for lambda,mu,nu), 'Rrsmn' (for rho,sigma,mu,nu)
    """
    output = {}
    shape = tensor.shape
    num_indices = len(shape)

    if num_indices == 2: # Matrix (e.g., g_munu, R_munu, G_munu, T_munu)
        for i in range(shape[0]):
            for j in range(shape[1]):
                key = f"{i}{j}" # Simple index key
                # Simplify before converting to LaTeX for cleaner output
                simplified_expr = simplify(tensor[i, j])
                output[key] = latex(simplified_expr)
    elif num_indices == 3: # 3-rank Array (e.g., Christoffel Gamma^l_mn)
        for i in range(shape[0]): # lambda
            for j in range(shape[1]): # mu
                for k in range(shape[2]): # nu
                    key = f"{i}_{j}{k}" # Index key like "lambda_munu"
                    simplified_expr = simplify(tensor[i, j, k])
                    if simplified_expr != 0: # Often only non-zero components are interesting
                         output[key] = latex(simplified_expr)
    elif num_indices == 4: # 4-rank Array (e.g., Riemann R^r_smn)
         for i in range(shape[0]): # rho
            for j in range(shape[1]): # sigma
                for k in range(shape[2]): # mu
                    for l in range(shape[3]): # nu
                        key = f"{i}_{j}{k}{l}" # Index key like "rho_sigmamunu"
                        simplified_expr = simplify(tensor[i, j, k, l])
                        if simplified_expr != 0:
                            output[key] = latex(simplified_expr)
    else:
        raise NotImplementedError(f"Tensor formatting not implemented for rank {num_indices}")

    return SymbolicTensorOutput(components_latex=output)

# === API Endpoints ===

@router.post("/calculate/geometry", response_model=GeometryCalculationsResponse, tags=["Calculations"])
def calculate_all_geometry(metric_input: MetricInput = Body(...)):
    """
    Calculate all standard geometric tensors from a given metric.
    Takes metric components as strings and coordinate names.
    Returns calculated tensors with components as LaTeX strings.
    """
    try:
        coords = parse_coords(metric_input.coords)
        metric_components_sympy = parse_components(metric_input.components)
        
        # --- Perform Calculations (Core Logic) ---
        g = metric_core.create_metric_tensor(metric_components_sympy, coords)
        g_inv = metric_core.calculate_inverse_metric(g) # Raises if singular
        
        # Unpack the result and error from Christoffel calculation
        gamma_array, christoffel_error = christoffel_core.calculate_christoffel_symbols(g, g_inv, coords)
        
        # Check for errors from Christoffel calculation
        if christoffel_error:
            # Raise a 500 error as this is an internal calculation failure
            raise HTTPException(status_code=500, detail=f"Error calculating Christoffel symbols: {christoffel_error}")
        
        # Note: Riemann calculation can be very slow. Use the unpacked array.
        riemann = riemann_core.calculate_riemann_tensor(gamma_array, coords)
        ricci = ricci_core.calculate_ricci_tensor(riemann)
        ricci_s = ricci_core.calculate_ricci_scalar(ricci, g_inv)
        einstein = einstein_core.calculate_einstein_tensor(ricci, ricci_s, g)
        # --- End Calculations ---
        
        # --- Format Results --- 
        response = GeometryCalculationsResponse(
            metric=format_tensor_output(g, "munu"),
            inverse_metric=format_tensor_output(g_inv, "munu"),
            christoffel=format_tensor_output(gamma_array, "Lmunu"), # Use the unpacked array
            riemann=format_tensor_output(riemann, "Rrsmn"),
            ricci_tensor=format_tensor_output(ricci, "munu"),
            ricci_scalar=SymbolicScalarOutput(latex=latex(simplify(ricci_s))),
            einstein_tensor=format_tensor_output(einstein, "munu")
        )
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotImplementedError as e:
         raise HTTPException(status_code=501, detail=str(e)) # e.g., tensor rank issue
    except Exception as e:
        # Catch potential SymPy errors, calculation errors, etc.
        # Log the error server-side for debugging
        print(f"Error during geometry calculation: {e}") 
        raise HTTPException(status_code=500, detail=f"Internal server error during calculation: {e}")


@router.post("/calculate/stress-energy", response_model=StressEnergyResponse, tags=["Calculations"])
def calculate_stress_energy(input_data: StressEnergyInput = Body(...)):
    """
    Calculate the Stress-Energy tensor based on components or a preset.
    Returns the tensor with components as LaTeX strings.
    """
    try:
        coords = parse_coords(input_data.coords)
        T = None

        if input_data.definition_method == 'components':
            if not input_data.components:
                raise ValueError("Components must be provided for method 'components'.")
            components_sympy = parse_components(input_data.components)
            T = stress_energy_core.create_stress_energy_tensor_from_components(components_sympy)
        
        elif input_data.definition_method == 'preset':
            if not input_data.preset_name:
                raise ValueError("Preset name must be provided for method 'preset'.")
            
            preset_name = input_data.preset_name.lower()
            params_sympy = {k: sympify(v) for k, v in (input_data.params or {}).items()}

            if preset_name == 'vacuum':
                T = stress_energy_core.create_vacuum_tensor()
            elif preset_name == 'dust':
                density = params_sympy.get('density', symbols('rho'))
                # TODO: Allow specifying four-velocity? Defaulting for now.
                T = stress_energy_core.create_dust_tensor(density=density)
            elif preset_name == 'perfect_fluid':
                if not input_data.metric_components:
                    raise ValueError("Metric components are required for perfect fluid preset.")
                metric_components_sympy = parse_components(input_data.metric_components)
                g = metric_core.create_metric_tensor(metric_components_sympy, coords)
                density = params_sympy.get('density', symbols('rho'))
                pressure = params_sympy.get('pressure', symbols('p'))
                T = stress_energy_core.create_perfect_fluid_tensor(metric=g, density=density, pressure=pressure)
            else:
                raise ValueError(f"Unknown preset name: {input_data.preset_name}")
        else:
             # This case should be caught by Pydantic validator, but added defensively
             raise ValueError("Invalid definition_method.")

        if T is None:
             raise ValueError("Could not determine Stress-Energy tensor based on input.")

        return StressEnergyResponse(stress_energy_tensor=format_tensor_output(T, "munu"))

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sympy.SympifyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid symbolic expression in parameters: {e}")
    except Exception as e:
        print(f"Error during stress-energy calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during calculation: {e}")


@router.post("/calculate/embedding/flamm", response_model=EmbeddingOutput, tags=["Calculations", "Visualization"])
def calculate_flamm_embedding(input_data: EmbeddingInput = Body(...)):
    """
    Calculates the symbolic embedding function z(r) for Flamm's paraboloid,
    applicable to static, spherically symmetric metrics like Schwarzschild.
    Optionally evaluates the function numerically to return data for plotting.
    """
    try:
        metric_input = input_data.metric_input
        coords = parse_coords(metric_input.coords)
        metric_components_sympy = parse_components(metric_input.components)
        
        # Substitute numerical parameter values BEFORE calculation
        param_symbols = {symbols(k): float(v) for k, v in input_data.parameter_values.items()}
        metric_components_num = [[comp.subs(param_symbols) for comp in row]
                                 for row in metric_components_sympy]
        
        g = metric_core.create_metric_tensor(metric_components_num, coords)
        
        # Call the core calculation function
        z_function, error = embedding_core.calculate_flamms_paraboloid(g, coords)
        
        if error:
            return EmbeddingOutput(message=f"Failed: {error}")
        
        z_latex = None
        r_vals_list = None
        z_vals_list = None
        x_surf_list = None
        y_surf_list = None
        z_surf_list = None
        message = "Calculation successful, but no embedding function found (e.g., integrand was zero)."
        
        if z_function is not None:
            z_latex = latex(z_function)
            message = "Flamm's paraboloid embedding function z(r) calculated successfully."
            
            # --- Numerical Evaluation for Plotting ---
            try:
                r_sym = symbols('r')
                # Lambdify the symbolic function z(r)
                # Check free symbols - should only contain 'r' after parameter substitution
                free_syms = z_function.free_symbols
                if len(free_syms) > 1 or (len(free_syms) == 1 and r_sym not in free_syms):
                     print(f"Warning: z(r) contains unexpected symbols: {free_syms}. Cannot lambdify correctly.")
                     message += f" (Warning: Cannot evaluate numerically due to symbols: {free_syms})"
                else:
                    z_lambdified = lambdify(r_sym, z_function, 'numpy')
                    
                    # Determine r_min dynamically if not provided (e.g., event horizon)
                    r_min_val = input_data.r_min
                    if r_min_val is None:
                        M_val = input_data.parameter_values.get('M')
                        if M_val is not None and M_val > 0:
                             # Default to slightly outside event horizon
                             r_min_val = 2.0 * M_val * 1.01 
                        else:
                            r_min_val = 0.1 # Default small value if no M
                    
                    r_max_val = input_data.r_max
                    num_r = input_data.num_points_r
                    num_phi = input_data.num_points_phi
                    
                    if r_min_val >= r_max_val:
                         message += " (Numerical evaluation skipped: r_min >= r_max)"    
                    else:
                        r_vals = np.linspace(r_min_val, r_max_val, num_r)
                        z_vals = z_lambdified(r_vals)
                        
                        # Check for complex numbers (e.g., sqrt of negative inside horizon)
                        if np.iscomplexobj(z_vals):
                            # Keep only real part for plotting, or handle appropriately
                            print("Warning: Complex values encountered in z(r), taking real part.")
                            z_vals = np.real(z_vals)
                        
                        r_vals_list = r_vals.tolist()
                        z_vals_list = z_vals.tolist()
                        
                        # Generate surface data
                        phi_vals = np.linspace(0, 2 * np.pi, num_phi)
                        R_mesh, Phi_mesh = np.meshgrid(r_vals, phi_vals)
                        Z_mesh = z_lambdified(R_mesh) # Evaluate z on the R grid
                        if np.iscomplexobj(Z_mesh):
                             Z_mesh = np.real(Z_mesh)

                        X_mesh = R_mesh * np.cos(Phi_mesh)
                        Y_mesh = R_mesh * np.sin(Phi_mesh)
                        
                        x_surf_list = X_mesh.tolist()
                        y_surf_list = Y_mesh.tolist()
                        z_surf_list = Z_mesh.tolist()
                        message += f" Numerical data generated for r in [{r_min_val:.2f}, {r_max_val:.2f}]."

            except Exception as num_err:
                print(f"Error during numerical evaluation of z(r): {num_err}")
                message += f" (Numerical evaluation failed: {num_err})"

        # Return combined results
        return EmbeddingOutput(
            z_function_latex=z_latex,
            message=message,
            r_values=r_vals_list,
            z_values=z_vals_list,
            x_surface=x_surf_list,
            y_surface=y_surf_list,
            z_surface=z_surf_list
        )
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error during Flamm embedding calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during calculation: {e}")


@router.post("/calculate/geodesic", response_model=GeodesicOutput, tags=["Calculations"])
def calculate_single_geodesic(input_data: GeodesicInput = Body(...)):
    """
    Calculate a single geodesic path numerically.
    """
    try:
        coords = parse_coords(input_data.coords)
        metric_components_sympy = parse_components(input_data.metric_components)
        
        # Substitute numerical parameter values into the metric
        if input_data.parameter_values:
            param_symbols = {symbols(k): float(v) for k, v in input_data.parameter_values.items()}
            metric_components_sympy = [[comp.subs(param_symbols) for comp in row]
                                       for row in metric_components_sympy]
            # Check if substitution resulted in only numeric types (or handle errors)
            # This basic substitution assumes parameters are simple symbols

        # Calculate necessary geometric quantities numerically
        g = metric_core.create_metric_tensor(metric_components_sympy, coords)
        g_inv = metric_core.calculate_inverse_metric(g)
        gamma = christoffel_core.calculate_christoffel_symbols(g, g_inv, coords)
        
        # Simplify Christoffel symbols before lambdifying - IMPORTANT for performance/stability
        # This can still be slow for complex metrics
        print("Simplifying Christoffel symbols...") # Add logging
        gamma_simplified = gamma # gamma.applyfunc(simplify) # Option to simplify, can be very slow!
        print("Simplification complete (or skipped).")

        # Prepare time evaluation points
        t_eval = np.linspace(input_data.t_span[0], input_data.t_span[1], input_data.num_points)

        # Run geodesic calculation
        print("Starting numerical integration...") # Add logging
        tau_values, states = geodesic_core.calculate_geodesic(
            gamma_simplified,
            coords,
            input_data.initial_position,
            input_data.initial_velocity,
            input_data.t_span,
            t_eval,
            **(input_data.solver_options or {})
        )
        print("Numerical integration finished.") # Add logging

        # Format output
        pos_dict = {coord_name: states[:, i].tolist() for i, coord_name in enumerate(input_data.coords)}
        vel_dict = {coord_name: states[:, i + len(coords)].tolist() for i, coord_name in enumerate(input_data.coords)}

        return GeodesicOutput(
            tau_values=tau_values.tolist(),
            position_coords=pos_dict,
            velocity_coords=vel_dict
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Errors from calculate_geodesic (solver issues, Christoffel eval issues)
        print(f"Runtime error during geodesic calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Runtime error during numerical integration: {e}")
    except Exception as e:
        print(f"Error during geodesic calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during calculation: {e}")

# Placeholder for EFE Verification Endpoint (FR5)
@router.post("/verify/efe", response_model=EFEVerificationResponse, tags=["Verification"])
def verify_efe(request: EFEVerificationRequest = Body(...)):
    """Verify if G_munu = kappa * T_munu holds for the given inputs."""
    # 1. Calculate G_munu from metric_input
    # 2. Calculate T_munu from stress_energy_input
    # 3. Sympify kappa from coupling_constant_str
    # 4. Compare G_munu and kappa * T_munu element-wise using simplify(G - kappa*T) == 0
    # 5. Return verification result
    # Note: This requires careful handling of symbolic simplification and potential floating point issues if kappa is complex.
    try:
        # --- Step 1: Calculate Einstein Tensor G_munu --- 
        metric_coords = parse_coords(request.metric_input.coords)
        metric_comps_sympy = parse_components(request.metric_input.components)
        g = metric_core.create_metric_tensor(metric_comps_sympy, metric_coords)
        g_inv = metric_core.calculate_inverse_metric(g)
        gamma = christoffel_core.calculate_christoffel_symbols(g, g_inv, metric_coords)
        riemann = riemann_core.calculate_riemann_tensor(gamma, metric_coords)
        ricci = ricci_core.calculate_ricci_tensor(riemann)
        ricci_s = ricci_core.calculate_ricci_scalar(ricci, g_inv)
        G = einstein_core.calculate_einstein_tensor(ricci, ricci_s, g)
        
        # --- Step 2: Calculate Stress-Energy Tensor T_munu --- 
        T_coords = parse_coords(request.stress_energy_input.coords)
        # Ensure coordinates match (or handle transformation if necessary - currently assumes same coords)
        if metric_coords != T_coords:
             raise ValueError("Metric and Stress-Energy tensor must use the same coordinate names for verification.")
             
        T = None
        if request.stress_energy_input.definition_method == 'components':
            if not request.stress_energy_input.components:
                 raise ValueError("Components must be provided for T_munu if method is 'components'.")
            T_comps_sympy = parse_components(request.stress_energy_input.components)
            T = stress_energy_core.create_stress_energy_tensor_from_components(T_comps_sympy)
        elif request.stress_energy_input.definition_method == 'preset':
            # ... (logic to create T from preset, similar to /calculate/stress-energy endpoint) ...
            # Requires handling presets like vacuum, dust, perfect_fluid here as well.
             preset_name = request.stress_energy_input.preset_name.lower()
             params_sympy = {k: sympify(v) for k, v in (request.stress_energy_input.params or {}).items()}
             if preset_name == 'vacuum':
                 T = stress_energy_core.create_vacuum_tensor()
             elif preset_name == 'dust':
                 T = stress_energy_core.create_dust_tensor(density=params_sympy.get('density', symbols('rho')))
             elif preset_name == 'perfect_fluid':
                 # Perfect fluid requires the metric g calculated earlier
                 T = stress_energy_core.create_perfect_fluid_tensor(
                     metric=g, 
                     density=params_sympy.get('density', symbols('rho')),
                     pressure=params_sympy.get('pressure', symbols('p'))
                 )
             else:
                 raise ValueError(f"Unknown preset name for T_munu: {preset_name}")
        else:
            raise ValueError("Invalid definition_method for Stress-Energy tensor.")
            
        if T is None:
             raise ValueError("Could not determine Stress-Energy tensor T_munu.")

        # --- Step 3: Parse Coupling Constant --- 
        kappa = sympify(request.coupling_constant_str)

        # --- Step 4: Compare G_munu and kappa * T_munu --- 
        diff_tensor = G - kappa * T
        # Simplify the difference tensor
        diff_tensor_simplified = diff_tensor.applyfunc(simplify)
        
        is_verified = (diff_tensor_simplified == Matrix.zeros(4, 4))
        message = "EFEs satisfied." if is_verified else "EFEs NOT satisfied."
        
        # Find first non-zero component if not verified
        if not is_verified:
            for i in range(4):
                for j in range(4):
                    if diff_tensor_simplified[i,j] != 0:
                        message = f"EFEs NOT satisfied. Mismatch found in component ({i},{j}): {diff_tensor_simplified[i,j]}"
                        break
                if message != "EFEs NOT satisfied.": break # Exit outer loop too
                        
        # --- Step 5: Return Result --- 
        return EFEVerificationResponse(verified=is_verified, message=message)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except sympy.SympifyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid symbolic expression: {e}")
    except Exception as e:
        print(f"Error during EFE verification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during verification: {e}")

# --- Scenario Management Endpoints ---

@router.post("/scenarios", status_code=201, tags=["Scenarios"])
def save_scenario(scenario_input: SaveScenarioInput = Body(...)):
    """Saves a scenario definition (metric + Tmunu) to a file."""
    scenario_name = scenario_input.scenario_name
    file_path = SCENARIO_DIR / f"{scenario_name}.json"
    
    if file_path.exists():
        raise HTTPException(status_code=409, 
                            detail=f"Scenario '{scenario_name}' already exists.")
    
    try:
        # Pydantic models have .dict() method, use .model_dump() for v2+
        # Use model_dump_json for direct JSON serialization
        json_data = scenario_input.definition.model_dump_json(indent=2)
        with open(file_path, "w") as f:
            f.write(json_data)
        return {"message": f"Scenario '{scenario_name}' saved successfully."}
    except IOError as e:
        print(f"Error saving scenario {scenario_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not save scenario: {e}")
    except Exception as e:
        # Catch potential Pydantic serialization errors
        print(f"Error serializing scenario {scenario_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not serialize scenario data: {e}")

@router.get("/scenarios", response_model=ScenarioListOutput, tags=["Scenarios"])
def list_scenarios():
    """Lists the names of all saved scenarios."""
    try:
        scenario_files = [f.stem for f in SCENARIO_DIR.glob("*.json") if f.is_file()]
        return ScenarioListOutput(scenario_names=sorted(scenario_files))
    except Exception as e:
        print(f"Error listing scenarios: {e}")
        raise HTTPException(status_code=500, detail=f"Could not list scenarios: {e}")

@router.get("/scenarios/{scenario_name}", response_model=ScenarioLoadOutput, tags=["Scenarios"])
def load_scenario(scenario_name: str):
    """Loads a specific scenario definition by name."""
    file_path = SCENARIO_DIR / f"{scenario_name}.json"
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_name}' not found.")
        
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            # Validate data against the Pydantic model
            definition = ScenarioDefinition(**data) 
            return ScenarioLoadOutput(scenario_name=scenario_name, definition=definition)
    except json.JSONDecodeError as e:
        print(f"Error decoding scenario file {scenario_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not parse scenario file '{scenario_name}'.")
    except Exception as e: # Catch Pydantic validation errors or other issues
        print(f"Error loading scenario {scenario_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not load scenario '{scenario_name}': {e}")
        
# Optional: Add DELETE endpoint
# @router.delete("/scenarios/{scenario_name}", status_code=204, tags=["Scenarios"])
# def delete_scenario(scenario_name: str):
#     """Deletes a specific scenario."""
#     # ... implementation ...

# --- Educational Content Endpoint ---

@router.get("/definitions", response_model=DefinitionsOutput, tags=["Educational"])
def get_all_definitions():
    """Retrieves all available educational definitions."""
    if not DEFINITIONS_DATA:
        raise HTTPException(status_code=404, detail="Definitions data not found or failed to load.")
    # Validate loaded data against Pydantic model (optional but good practice)
    try:
        validated_data = {k: DefinitionItem(**v) for k, v in DEFINITIONS_DATA.items()}
        return DefinitionsOutput(definitions=validated_data)
    except Exception as e:
        print(f"Error validating definitions data: {e}")
        raise HTTPException(status_code=500, detail="Definitions data is invalid.")

@router.get("/definitions/{item_key}", response_model=DefinitionItem, tags=["Educational"])
def get_single_definition(item_key: str):
    """Retrieves the definition for a specific item key."""
    definition = DEFINITIONS_DATA.get(item_key.lower())
    if not definition:
        raise HTTPException(status_code=404, detail=f"Definition for '{item_key}' not found.")
    try:
        return DefinitionItem(**definition)
    except Exception as e:
         print(f"Error validating definition for {item_key}: {e}")
         raise HTTPException(status_code=500, detail="Definition data is invalid.")

# (End of file) 