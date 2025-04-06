import sympy
from sympy import Array, Matrix, Symbol, diff, symbols, simplify
from typing import List

# Import necessary functions if running standalone for testing
# from .metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
# from .christoffel import calculate_christoffel_symbols

def calculate_riemann_tensor(
    christoffel: Array,
    coords: List[Symbol]
) -> Array:
    """
    Calculates the Riemann curvature tensor R^rho_sigma_mu_nu.

    Formula: 
    R^rho_sigma_mu_nu = d_mu(Gamma^rho_nu_sigma) - d_nu(Gamma^rho_mu_sigma) + 
                      Gamma^rho_mu_lambda * Gamma^lambda_nu_sigma - 
                      Gamma^rho_nu_lambda * Gamma^lambda_mu_sigma
    (Summation over lambda is implied)

    Args:
        christoffel: The Christoffel symbols of the second kind (Gamma^lambda_mu_nu) 
                     as a SymPy Array[lambda, mu, nu].
        coords: A list of 4 coordinate symbols (e.g., [t, r, theta, phi]).

    Returns:
        A SymPy Array representing the Riemann tensor R^rho_sigma_mu_nu.
        Indexed as riemann[rho, sigma, mu, nu].

    Raises:
        ValueError: If inputs are not the correct shape or type.
    """
    if not isinstance(christoffel, (Array, sympy.tensor.array.dense_ndim_array.ImmutableDenseNDimArray)) or christoffel.rank() != 3 or christoffel.shape != (4, 4, 4):
        raise ValueError("Christoffel symbols must be a 3-rank SymPy Array with shape (4, 4, 4).")
    if not isinstance(coords, list) or len(coords) != 4 or not all(isinstance(c, Symbol) for c in coords):
        raise ValueError("Coordinates must be a list of 4 SymPy symbols.")

    n = len(coords) # Dimension (should be 4)
    riemann = Array.zeros(n, n, n, n) # Initialize R^rho_sigma_mu_nu

    # Pre-calculate derivatives of Christoffel symbols: dGamma[mu, rho, nu, sigma] = d_mu(Gamma^rho_nu_sigma)
    # Note the index order might differ from formula notation depending on loop structure
    dGamma = Array.zeros(n, n, n, n)
    for mu in range(n):
        for rho in range(n):
            for nu in range(n):
                for sigma in range(n):
                    # Need to check if christoffel component is non-zero or non-constant before differentiating
                    if christoffel[rho, nu, sigma] != 0:
                       dGamma[mu, rho, nu, sigma] = simplify(diff(christoffel[rho, nu, sigma], coords[mu]))
                    else:
                       dGamma[mu, rho, nu, sigma] = 0

    # Calculate Riemann tensor components
    for rho in range(n):
        for sigma in range(n):
            for mu in range(n):
                for nu in range(n):
                    # Derivative terms
                    term1 = dGamma[mu, rho, nu, sigma]  # d_mu(Gamma^rho_nu_sigma)
                    term2 = dGamma[nu, rho, mu, sigma]  # d_nu(Gamma^rho_mu_sigma)
                    
                    # Product terms (sum over lambda)
                    term3 = 0
                    term4 = 0
                    for lam in range(n):
                        term3 += christoffel[rho, mu, lam] * christoffel[lam, nu, sigma]
                        term4 += christoffel[rho, nu, lam] * christoffel[lam, mu, sigma]

                    # Combine terms
                    riemann_component = term1 - term2 + term3 - term4
                    riemann[rho, sigma, mu, nu] = riemann_component # Simplify later if needed

    # Apply simplification to all components at the end (can be very slow)
    # riemann = riemann.applyfunc(simplify)

    return riemann

# Example Usage (requires imports from metric.py and christoffel.py)
if __name__ == '__main__':
    try:
        # Adjust imports based on how you run this
        from metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
        from christoffel import calculate_christoffel_symbols

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
        gamma = calculate_christoffel_symbols(g, g_inv, DEFAULT_COORDS)

        print("Calculating Riemann Tensor for Schwarzschild metric...")
        # This calculation can be very time-consuming!
        riemann_tensor = calculate_riemann_tensor(gamma, DEFAULT_COORDS)

        print("\nNon-zero Riemann Tensor Components (R^rho_sigma_mu_nu):")
        count = 0
        for rho in range(4):
            for sigma in range(4):
                for mu in range(4):
                    for nu in range(4):
                        # Simplify here for display
                        term = simplify(riemann_tensor[rho, sigma, mu, nu])
                        if term != 0:
                            count += 1
                            print(f"R^{DEFAULT_COORDS[rho]}_{{{DEFAULT_COORDS[sigma]},{DEFAULT_COORDS[mu]},{DEFAULT_COORDS[nu]}}} = {term}")
        
        if count == 0:
             print("All Riemann tensor components are zero (or calculation failed/simplified to zero).")
        else:
            print(f"\nFound {count} non-zero components (before potential further simplification).")
            # Note: Schwarzschild is Ricci-flat (R_munu = 0), but Riemann tensor is not zero.

    except ImportError:
        print("Could not import from metric.py or christoffel.py. Ensure they are accessible.")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        # Catch other potential errors during complex calculations
        print(f"An unexpected error occurred during calculation: {e}") 