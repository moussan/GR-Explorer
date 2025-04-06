import sympy
from sympy import Array, Matrix, Symbol, simplify, symbols, trace
from typing import List

# Import necessary functions if running standalone for testing
# from .metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
# from .christoffel import calculate_christoffel_symbols
# from .riemann import calculate_riemann_tensor

def calculate_ricci_tensor(riemann_tensor: Array) -> Matrix:
    """
    Calculates the Ricci tensor R_mu_nu by contracting the Riemann tensor.

    Formula: R_mu_nu = R^rho_mu_rho_nu (summation over rho)

    Args:
        riemann_tensor: The Riemann curvature tensor R^rho_sigma_mu_nu 
                        as a SymPy Array[rho, sigma, mu, nu].

    Returns:
        A SymPy Matrix representing the Ricci tensor R_mu_nu.

    Raises:
        ValueError: If the input is not the correct shape or type.
    """
    if not isinstance(riemann_tensor, (Array, sympy.tensor.array.dense_ndim_array.ImmutableDenseNDimArray)) or riemann_tensor.rank() != 4 or riemann_tensor.shape != (4, 4, 4, 4):
        raise ValueError("Riemann tensor must be a 4-rank SymPy Array with shape (4, 4, 4, 4).")

    n = riemann_tensor.shape[0]
    ricci_tensor = Matrix.zeros(n, n)

    for mu in range(n):
        for nu in range(n):
            sum_val = 0
            for rho in range(n):
                sum_val += riemann_tensor[rho, mu, rho, nu] # Contract first and third indices
            ricci_tensor[mu, nu] = sum_val # Simplify later if needed

    # Apply simplification to all components at the end (can be slow)
    # ricci_tensor = ricci_tensor.applyfunc(simplify)

    return ricci_tensor

def calculate_ricci_scalar(ricci_tensor: Matrix, inverse_metric: Matrix) -> sympy.Expr:
    """
    Calculates the Ricci scalar R by contracting the Ricci tensor with the inverse metric.

    Formula: R = g^mu_nu * R_mu_nu (summation over mu and nu)

    Args:
        ricci_tensor: The Ricci tensor R_mu_nu (4x4 SymPy Matrix).
        inverse_metric: The inverse metric tensor g^munu (4x4 SymPy Matrix).

    Returns:
        A SymPy expression representing the Ricci scalar R.

    Raises:
        ValueError: If inputs are not the correct shape or type.
    """
    if not isinstance(ricci_tensor, Matrix) or ricci_tensor.shape != (4, 4):
        raise ValueError("Ricci tensor must be a 4x4 SymPy Matrix.")
    if not isinstance(inverse_metric, Matrix) or inverse_metric.shape != (4, 4):
        raise ValueError("Inverse metric must be a 4x4 SymPy Matrix.")

    # Calculate the trace of the product of the inverse metric and the Ricci tensor
    # R = g^munu * R_munu = Trace(g_inv * R)
    # Ensure correct multiplication order if needed, but element-wise sum works directly:
    ricci_scalar = 0
    for mu in range(inverse_metric.shape[0]):
        for nu in range(inverse_metric.shape[1]):
            ricci_scalar += inverse_metric[mu, nu] * ricci_tensor[mu, nu]
            
    # Apply simplification
    # ricci_scalar = simplify(ricci_scalar)
    
    return ricci_scalar

# Example Usage (requires imports from other core modules)
if __name__ == '__main__':
    try:
        # Adjust imports based on execution context
        from metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
        from christoffel import calculate_christoffel_symbols
        from riemann import calculate_riemann_tensor

        # Example: Schwarzschild metric (known to be Ricci flat)
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
        riemann = calculate_riemann_tensor(gamma, DEFAULT_COORDS)

        print("Calculating Ricci Tensor for Schwarzschild metric...")
        ricci = calculate_ricci_tensor(riemann)
        print("Ricci Tensor R_munu:")
        # Simplify for display
        sympy.pprint(ricci.applyfunc(simplify))

        print("\nCalculating Ricci Scalar for Schwarzschild metric...")
        scalar_R = calculate_ricci_scalar(ricci, g_inv)
        print(f"Ricci Scalar R = {simplify(scalar_R)}")
        
        # Verify Schwarzschild is Ricci flat
        assert simplify(scalar_R) == 0, "Ricci scalar should be 0 for Schwarzschild"
        assert simplify(ricci) == Matrix.zeros(4, 4), "Ricci tensor should be 0 for Schwarzschild"
        print("\nVerified: Schwarzschild metric is Ricci-flat (R_munu = 0, R = 0).")

    except ImportError:
        print("Could not import from metric.py, christoffel.py, or riemann.py. Ensure they are accessible.")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 