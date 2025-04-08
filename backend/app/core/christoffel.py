import sympy
from sympy import Matrix, Array, zeros, simplify, diff, N, Symbol
from sympy.tensor.array import MutableDenseNDimArray
from typing import List, Tuple, Any

# Import coordinate symbols and metric functions if needed for examples/tests
# from .metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric

def calculate_christoffel_symbols(
    metric: Matrix,
    inverse_metric: Matrix,
    coords: List[Symbol]
) -> Tuple[List[List[List[Any]]], str]:
    """
    Calculates the Christoffel symbols of the second kind (Gamma^lambda_mu_nu).
    Gamma^lambda_mu_nu = 1/2 * g^lambda_rho * (d_mu(g_rho_nu) + d_nu(g_rho_mu) - d_rho(g_mu_nu))
    where d_mu is the partial derivative with respect to the coordinate coords[mu].

    Args:
        metric: The metric tensor g_munu (4x4 SymPy Matrix).
        inverse_metric: The inverse metric tensor g^munu (4x4 SymPy Matrix).
        coords: A list of 4 coordinate symbols (e.g., [t, r, theta, phi]).

    Returns:
        A tuple containing:
        - A nested list representing the Christoffel symbols Gamma^lambda_mu_nu.
          Indexed as christoffel[lambda][mu][nu].
        - An error message string if calculation fails, otherwise None.

    Raises:
        ValueError: If inputs are not the correct shape or type.
    """
    
    if not isinstance(metric, Matrix) or metric.shape != (4, 4):
        raise ValueError("Metric must be a 4x4 SymPy Matrix.")
    if not isinstance(inverse_metric, Matrix) or inverse_metric.shape != (4, 4):
        # Add logging here if needed: print(f"Invalid inverse metric type: {type(inverse_metric)}")
        raise ValueError("Inverse metric must be a 4x4 SymPy Matrix.")
    if len(coords) != 4:
        raise ValueError("Must provide 4 coordinate symbols.")
        
    n_dim = 4
    # Initialize mutable N-dim arrays directly with shape
    dg = MutableDenseNDimArray.zeros(n_dim, n_dim, n_dim)
    christoffel = MutableDenseNDimArray.zeros(n_dim, n_dim, n_dim)

    try:
        # 1. Calculate derivatives
        for rho in range(n_dim):
            coord_symbol = coords[rho]
            for mu in range(n_dim):
                for nu in range(n_dim):
                    metric_comp = metric[mu, nu]
                    # If component is zero, derivative is zero
                    if metric_comp == sympy.S.Zero:
                        dg[rho, mu, nu] = sympy.S.Zero
                        continue # Skip to next iteration
                    
                    # Check if the component depends on the coordinate being differentiated
                    if coord_symbol in metric_comp.free_symbols:
                        # Calculate derivative only if there's dependency
                        derivative = diff(metric_comp, coord_symbol)
                        # Only simplify if the derivative is non-zero. 
                        # If diff correctly returns S.Zero, simplify is not needed.
                        if derivative != sympy.S.Zero:
                            print(f"[DEBUG Christoffel] Calculated non-zero derivative for g[{mu},{nu}] w.r.t {coord_symbol}: {derivative}") # DEBUG
                            dg[rho, mu, nu] = simplify(derivative)
                        else:
                            dg[rho, mu, nu] = sympy.S.Zero # Assign zero directly if diff resulted in zero
                    else:
                        # No dependency, derivative is zero
                        dg[rho, mu, nu] = sympy.S.Zero

        # --- !!! DEBUG Check dg array (Keep for one more test) !!! --- 
        try:
            dg_is_zero = all(element == sympy.S.Zero for element in dg)
            print(f"[DEBUG Christoffel] Is dg array all zeros after calculation? {dg_is_zero}")
            if not dg_is_zero:
                 found_non_zero = False
                 for i in range(n_dim):
                     for j in range(n_dim):
                         for k in range(n_dim):
                             if dg[i,j,k] != sympy.S.Zero:
                                 print(f"[DEBUG Christoffel] Non-zero dg element dg[{i},{j},{k}] = {dg[i,j,k]} (type: {type(dg[i,j,k])})")
                                 found_non_zero = True; break
                         if found_non_zero: break
                     if found_non_zero: break
        except Exception as dg_err:
            print(f"[DEBUG Christoffel] Error checking dg array: {dg_err}")
        # --- !!! END DEBUG !!! ---

        # 2. Calculate Christoffel symbols
        for lam in range(n_dim):
            for mu in range(n_dim):
                for nu in range(n_dim):
                    sum_val = sympy.S.Zero # Initialize with SymPy Zero
                    for rho in range(n_dim):
                        term = dg[mu, rho, nu] + dg[nu, rho, mu] - dg[rho, mu, nu]
                        # Explicitly compare term and metric component with sympy.S.Zero
                        if term != sympy.S.Zero and inverse_metric[lam, rho] != sympy.S.Zero:
                            sum_val += inverse_metric[lam, rho] * term
                    
                    # Explicitly compare sum_val with sympy.S.Zero before simplifying
                    if sum_val != sympy.S.Zero: 
                         # Simplify the non-zero sum before assigning
                         simplified_sum = simplify(sympy.Rational(1, 2) * sum_val)
                         # Optional: Check if simplification resulted in zero?
                         # if simplified_sum != sympy.S.Zero:
                         christoffel[lam, mu, nu] = simplified_sum
                    # else: christoffel remains 0
                    
        christoffel_list = christoffel.tolist()
        return christoffel_list, None 

    except Exception as e:
        error_message = f"Error calculating Christoffel symbols: {e}"
        print(error_message) # Or use proper logging
        return None, error_message

# Example Usage (requires importing from metric.py)
if __name__ == '__main__':
    # Need to adjust imports if running this file directly
    # Assuming metric.py is in the same directory for standalone testing:
    try:
        from metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
        
        # Example: Schwarzschild metric
        t, r, theta, phi = DEFAULT_COORDS
        M = sympy.symbols('M')
        schwarzschild_components = [
            [-(1 - 2*M/r), 0, 0, 0],
            [0, 1/(1 - 2*M/r), 0, 0],
            [0, 0, r**2, 0],
            [0, 0, 0, r**2 * sympy.sin(theta)**2]
        ]

        g = create_metric_tensor(schwarzschild_components, DEFAULT_COORDS)
        g_inv = calculate_inverse_metric(g)

        print("Calculating Christoffel Symbols for Schwarzschild metric...")
        gamma, error = calculate_christoffel_symbols(g, g_inv, DEFAULT_COORDS)

        if gamma is not None:
            print("\nNon-zero Christoffel Symbols (Gamma^lambda_mu_nu):")
            count = 0
            for lam in range(4):
                for mu in range(4):
                    for nu in range(4):
                        # Simplify here for cleaner output display
                        term = simplify(gamma[lam][mu][nu]) 
                        if term != 0:
                            count += 1
                            print(f"Gamma^{DEFAULT_COORDS[lam]}_({DEFAULT_COORDS[mu]},{DEFAULT_COORDS[nu]}) = {term}")
                            # sympy.pprint(term, use_unicode=True)
            if count == 0:
                print("All Christoffel symbols are zero.")
        else:
            print(f"Error: {error}")

    except ImportError:
        print("Could not import from metric.py. Run this as part of the main application or ensure metric.py is accessible.")
    except ValueError as e:
        print(f"An error occurred: {e}") 