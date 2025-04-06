import sympy
from sympy import Matrix, Symbol, sqrt, integrate, symbols, simplify, oo, lambdify
from typing import List, Tuple, Optional, Callable

# Define symbols if needed for standalone testing
# t, r, theta, phi = symbols('t r theta phi')
# M = symbols('M')

def calculate_flamms_paraboloid(
    metric: Matrix,
    coords: List[Symbol]
) -> Tuple[Optional[sympy.Expr], Optional[str]]:
    """
    Attempts to calculate the embedding function z(r) for Flamm's paraboloid.

    This applies specifically to static, spherically symmetric metrics in 
    standard Schwarzschild-like coordinates (t, r, theta, phi) where the 
    equatorial plane (t=const, theta=pi/2) has a metric of the form:
    ds^2 = g_rr(r) dr^2 + g_phiphi(r) dphi^2 
    (We expect g_phiphi(r) = r^2 for standard coordinates, but check g_rr).
    
    The embedding function z(r) satisfies: dz/dr = sqrt(g_rr(r) - 1).

    Args:
        metric: The 4x4 metric tensor (SymPy Matrix).
        coords: List of 4 coordinate symbols (must contain r, theta).

    Returns:
        A tuple (z_function, error_message):
        - z_function: The calculated sympy expression for z(r) if successful, else None.
                   Integration constant is chosen such that z -> 0 as r -> oo (if possible).
        - error_message: A string containing an error message if calculation fails or 
                         metric is unsuitable, else None.
    """
    
    # Basic validation
    if not isinstance(metric, Matrix) or metric.shape != (4, 4):
        return None, "Input must be a 4x4 SymPy Matrix."
    if len(coords) != 4:
        return None, "Must provide 4 coordinate symbols."
        
    # Identify indices for r, theta
    try:
        r_idx = coords.index(symbols('r'))
        theta_idx = coords.index(symbols('theta'))
        # Assume t is 0, phi is 3 if needed, but we primarily need r and theta
    except ValueError:
        return None, "Coordinates must include 'r' and 'theta'."

    # --- Check Metric Suitability --- 
    # 1. Check for static and diagonal (simplified check)
    #    More robust checks would involve Killing vectors etc.
    t_idx = 0 # Assume t is the first coordinate
    if any(metric[t_idx, i] != 0 for i in range(1, 4)) or \
       any(metric[i, t_idx] != 0 for i in range(1, 4)):
           # Check off-diagonal terms involving time
           pass # Allow non-diagonal static metrics for now, focus on g_rr
           
    # 2. Extract g_rr component
    g_rr = metric[r_idx, r_idx]
    
    # 3. Check if g_rr depends only on r
    variables_in_grr = g_rr.free_symbols
    r_symbol = symbols('r')
    if not variables_in_grr.issubset({r_symbol, *metric.free_symbols} - set(coords)): # Allow parameters like M
         # Check if symbols in g_rr are only 'r' or parameters not in coords list itself.
        other_coord_deps = variables_in_grr.intersection(set(coords)) - {r_symbol}
        if other_coord_deps:
             return None, f"Metric component g_rr depends on coordinates other than r: {other_coord_deps}. Cannot compute Flamm's paraboloid simply."

    # --- Calculate Embedding --- 
    try:
        # Calculate the integrand for dz/dr
        integrand = sqrt(g_rr - 1)
        integrand_simplified = simplify(integrand)
        
        # Perform indefinite integration wrt r
        # Note: Symbolic integration can fail or be very slow
        print(f"Attempting integration of: {integrand_simplified}") # Logging
        z_integrated = integrate(integrand_simplified, r_symbol)
        print(f"Integration result (before constant): {z_integrated}") # Logging

        # Check for integration failure (returns Integral object)
        if isinstance(z_integrated, sympy.Integral):
            return None, f"Symbolic integration failed for sqrt(g_rr - 1) = {integrand_simplified}. Cannot determine z(r)."
            
        # Determine integration constant C such that z(r) -> 0 as r -> oo
        # This assumes the integral converges to a constant C_inf at infinity
        try:
             limit_at_inf = sympy.limit(z_integrated, r_symbol, oo)
             print(f"Limit at infinity: {limit_at_inf}") # Logging
             if limit_at_inf.is_finite:
                 integration_constant = -limit_at_inf
             else:
                  print("Warning: Limit of integral at infinity is not finite. Setting constant to 0.")
                  integration_constant = 0
        except Exception as lim_e: # Catch potential errors in limit calculation
             print(f"Warning: Could not compute limit at infinity ({lim_e}). Setting constant to 0.")
             integration_constant = 0
             
        z_function = simplify(z_integrated + integration_constant)
        
        return z_function, None
        
    except (ValueError, TypeError, Exception) as e:
        # Catch errors during sqrt, integrate, simplify, limit
        import traceback
        print(f"Error during Flamm's paraboloid calculation: {e}\n{traceback.format_exc()}")
        return None, f"Could not calculate embedding function z(r): {e}"


# Example Usage (for testing)
if __name__ == '__main__':
    t, r, theta, phi = symbols('t r theta phi')
    M = symbols('M')
    coords_list = [t, r, theta, phi]

    # Schwarzschild metric components
    schwarzschild_components = [
        [-(1 - 2*M/r), 0, 0, 0],
        [0, 1/(1 - 2*M/r), 0, 0],
        [0, 0, r**2, 0],
        [0, 0, 0, r**2 * sympy.sin(theta)**2]
    ]
    
    from metric import create_metric_tensor # Assumes metric.py is accessible
    g_schw = create_metric_tensor(schwarzschild_components, coords_list)
    
    print("Calculating Flamm's Paraboloid for Schwarzschild...")
    z_func_schw, err_schw = calculate_flamms_paraboloid(g_schw, coords_list)

    if err_schw:
        print(f"Error: {err_schw}")
    else:
        print(f"\nEmbedding function z(r) = {z_func_schw}")
        sympy.pprint(z_func_schw)
        
        # Verify for specific values (using lambdify)
        try:
            z_lambdified = lambdify((r, M), z_func_schw, 'numpy')
            r_vals = np.linspace(2.1, 10, 5) # Start outside horizon
            M_val = 1.0
            z_vals = z_lambdified(r_vals, M_val)
            print("\nNumerical values (M=1):")
            for rv, zv in zip(r_vals, z_vals):
                print(f"r = {rv:.2f}, z = {zv:.3f}")
        except Exception as e:
             print(f"Could not lambdify or evaluate numerically: {e}")

    # Example of unsuitable metric (e.g., depends on t)
    # g_unsuitable = Matrix([[-(1 - 2*M/r)*t, 0, 0, 0], [0, 1/(1 - 2*M/r), 0, 0], [0, 0, r**2, 0], [0, 0, 0, r**2]])
    # print("\nTesting unsuitable metric...")
    # z_func_uns, err_uns = calculate_flamms_paraboloid(g_unsuitable, coords_list)
    # print(f"Result: {z_func_uns}, Error: {err_uns}") 