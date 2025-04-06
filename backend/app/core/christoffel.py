import sympy
from sympy import Matrix, diff, symbols, simplify, Array, Mul
from typing import List

# Import coordinate symbols and metric functions if needed for examples/tests
# from .metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric

def calculate_christoffel_symbols(
    metric: Matrix,
    inverse_metric: Matrix,
    coords: List[sympy.Symbol]
) -> Array:
    """
    Calculates the Christoffel symbols of the second kind (Gamma^lambda_mu_nu).

    Formula: Gamma^lambda_mu_nu = 1/2 * g^lambda_rho * (d_mu(g_rho_nu) + d_nu(g_rho_mu) - d_rho(g_mu_nu))
    where d_mu is the partial derivative with respect to the coordinate coords[mu].

    Args:
        metric: The metric tensor g_munu (4x4 SymPy Matrix).
        inverse_metric: The inverse metric tensor g^munu (4x4 SymPy Matrix).
        coords: A list of 4 coordinate symbols (e.g., [t, r, theta, phi]).

    Returns:
        A SymPy Array representing the Christoffel symbols Gamma^lambda_mu_nu.
        Indexed as christoffel[lambda, mu, nu].

    Raises:
        ValueError: If inputs are not the correct shape or type.
    """
    if not isinstance(metric, Matrix) or metric.shape != (4, 4):
        raise ValueError("Metric must be a 4x4 SymPy Matrix.")
    if not isinstance(inverse_metric, Matrix) or inverse_metric.shape != (4, 4):
        raise ValueError("Inverse metric must be a 4x4 SymPy Matrix.")
    if not isinstance(coords, list) or len(coords) != 4 or not all(isinstance(c, sympy.Symbol) for c in coords):
        raise ValueError("Coordinates must be a list of 4 SymPy symbols.")

    n = metric.shape[0] # Dimension (should be 4)
    christoffel = Array.zeros(n, n, n) # Initialize Gamma^lambda_mu_nu

    # Pre-calculate all first derivatives of the metric: dg[rho, mu, nu] = d_rho(g_mu_nu)
    dg = Array.zeros(n, n, n)
    for rho in range(n):
        for mu in range(n):
            for nu in range(n):
                dg[rho, mu, nu] = simplify(diff(metric[mu, nu], coords[rho]))

    # Calculate Christoffel symbols using the formula
    # Summation over index 'sigma' is implied by matrix multiplication logic later,
    # but let's write the loops explicitly for clarity matching the formula first.
    for lam in range(n):
        for mu in range(n):
            for nu in range(n):
                sum_val = 0
                for rho in range(n):
                    term1 = dg[mu, rho, nu] # d_mu(g_rho_nu)
                    term2 = dg[nu, rho, mu] # d_nu(g_rho_mu)
                    term3 = dg[rho, mu, nu] # d_rho(g_mu_nu)
                    sum_val += inverse_metric[lam, rho] * (term1 + term2 - term3)
                
                # christoffel[lam, mu, nu] = simplify(sum_val / 2) # Original explicit sum
                # Using applyfunc for simplification after creation might be better
                christoffel[lam, mu, nu] = sum_val / 2

    # Apply simplification to all components at the end (can be slow)
    # christoffel = christoffel.applyfunc(simplify)

    return christoffel

# Example Usage (requires importing from metric.py)
if __name__ == '__main__':
    # Need to adjust imports if running this file directly
    # Assuming metric.py is in the same directory for standalone testing:
    try:
        from metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
        
        # Example: Schwarzschild metric
        t, r, theta, phi = DEFAULT_COORDS
        M = symbols('M')
        schwarzschild_components = [
            [-(1 - 2*M/r), 0, 0, 0],
            [0, 1/(1 - 2*M/r), 0, 0],
            [0, 0, r**2, 0],
            [0, 0, 0, r**2 * sympy.sin(theta)**2]
        ]

        g = create_metric_tensor(schwarzschild_components, DEFAULT_COORDS)
        g_inv = calculate_inverse_metric(g)

        print("Calculating Christoffel Symbols for Schwarzschild metric...")
        gamma = calculate_christoffel_symbols(g, g_inv, DEFAULT_COORDS)

        print("\nNon-zero Christoffel Symbols (Gamma^lambda_mu_nu):")
        count = 0
        for lam in range(4):
            for mu in range(4):
                for nu in range(4):
                    # Simplify here for cleaner output display
                    term = simplify(gamma[lam, mu, nu]) 
                    if term != 0:
                        count += 1
                        print(f"Gamma^{DEFAULT_COORDS[lam]}_({DEFAULT_COORDS[mu]},{DEFAULT_COORDS[nu]}) = {term}")
                        # sympy.pprint(term, use_unicode=True)
        if count == 0:
            print("All Christoffel symbols are zero.")

    except ImportError:
        print("Could not import from metric.py. Run this as part of the main application or ensure metric.py is accessible.")
    except ValueError as e:
        print(f"An error occurred: {e}") 