import sympy
from sympy import Array, Matrix, Symbol, diff, symbols, simplify
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    try:
        # Pre-calculate derivatives of Christoffel symbols: dGamma[mu, rho, nu, sigma] = d_mu(Gamma^rho_nu_sigma)
        dGamma = Array.zeros(n, n, n, n)
        for mu in range(n):
            for rho in range(n):
                for nu in range(n):
                    for sigma in range(n):
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

                        # Combine terms and simplify
                        riemann_component = simplify(term1 - term2 + term3 - term4)
                        riemann[rho, sigma, mu, nu] = riemann_component

        return riemann

    except Exception as e:
        error_message = f"Error calculating Riemann tensor: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)

# Example Usage (requires imports from other core modules)
if __name__ == '__main__':
    try:
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
        gamma, error = calculate_christoffel_symbols(g, g_inv, DEFAULT_COORDS)

        if gamma is None:
            raise ValueError(f"Failed to calculate Christoffel symbols: {error}")

        logger.info("Calculating Riemann Tensor for Schwarzschild metric...")
        riemann_tensor = calculate_riemann_tensor(Array(gamma), DEFAULT_COORDS)

        logger.info("\nNon-zero Riemann Tensor Components (R^rho_sigma_mu_nu):")
        count = 0
        for rho in range(4):
            for sigma in range(4):
                for mu in range(4):
                    for nu in range(4):
                        term = riemann_tensor[rho, sigma, mu, nu]
                        if term != 0:
                            count += 1
                            logger.info(f"R^{DEFAULT_COORDS[rho]}_{{{DEFAULT_COORDS[sigma]},{DEFAULT_COORDS[mu]},{DEFAULT_COORDS[nu]}}} = {term}")
        
        if count == 0:
            logger.info("All Riemann tensor components are zero.")
        else:
            logger.info(f"\nFound {count} non-zero components.")

    except ImportError:
        logger.error("Could not import from metric.py or christoffel.py. Ensure they are accessible.")
    except ValueError as e:
        logger.error(f"An error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during calculation: {e}") 