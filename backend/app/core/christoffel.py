import sympy
from sympy import Matrix, Array, zeros, simplify, diff, N, Symbol
from sympy.tensor.array import MutableDenseNDimArray
from typing import List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                        continue
                    
                    # Check if the component depends on the coordinate being differentiated
                    if coord_symbol in metric_comp.free_symbols:
                        # Calculate derivative only if there's dependency
                        derivative = diff(metric_comp, coord_symbol)
                        if derivative != sympy.S.Zero:
                            dg[rho, mu, nu] = simplify(derivative)
                        else:
                            dg[rho, mu, nu] = sympy.S.Zero
                    else:
                        dg[rho, mu, nu] = sympy.S.Zero

        # 2. Calculate Christoffel symbols
        for lam in range(n_dim):
            for mu in range(n_dim):
                for nu in range(n_dim):
                    sum_val = sympy.S.Zero
                    for rho in range(n_dim):
                        term = dg[mu, rho, nu] + dg[nu, rho, mu] - dg[rho, mu, nu]
                        if term != sympy.S.Zero and inverse_metric[lam, rho] != sympy.S.Zero:
                            sum_val += inverse_metric[lam, rho] * term
                    
                    if sum_val != sympy.S.Zero:
                        christoffel[lam, mu, nu] = simplify(sympy.Rational(1, 2) * sum_val)
                    
        christoffel_list = christoffel.tolist()
        return christoffel_list, None

    except Exception as e:
        error_message = f"Error calculating Christoffel symbols: {str(e)}"
        logger.error(error_message)
        return None, error_message

# Example Usage (requires importing from metric.py)
if __name__ == '__main__':
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

        logger.info("Calculating Christoffel Symbols for Schwarzschild metric...")
        gamma, error = calculate_christoffel_symbols(g, g_inv, DEFAULT_COORDS)

        if gamma is not None:
            logger.info("\nNon-zero Christoffel Symbols (Gamma^lambda_mu_nu):")
            count = 0
            for lam in range(4):
                for mu in range(4):
                    for nu in range(4):
                        term = simplify(gamma[lam][mu][nu]) 
                        if term != 0:
                            count += 1
                            logger.info(f"Gamma^{DEFAULT_COORDS[lam]}_({DEFAULT_COORDS[mu]},{DEFAULT_COORDS[nu]}) = {term}")
            if count == 0:
                logger.info("All Christoffel symbols are zero.")
        else:
            logger.error(f"Error: {error}")

    except ImportError:
        logger.error("Could not import from metric.py. Run this as part of the main application or ensure metric.py is accessible.")
    except ValueError as e:
        logger.error(f"An error occurred: {e}") 