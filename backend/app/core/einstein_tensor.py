import sympy
from sympy import Matrix, Symbol, Expr, simplify, symbols

# Import necessary functions if running standalone for testing
# from .metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
# from .christoffel import calculate_christoffel_symbols
# from .riemann import calculate_riemann_tensor
# from .ricci import calculate_ricci_tensor, calculate_ricci_scalar

def calculate_einstein_tensor(
    ricci_tensor: Matrix,
    ricci_scalar: Expr,
    metric: Matrix
) -> Matrix:
    """
    Calculates the Einstein tensor G_munu.

    Formula: G_munu = R_munu - (1/2) * g_munu * R

    Args:
        ricci_tensor: The Ricci tensor R_munu (4x4 SymPy Matrix).
        ricci_scalar: The Ricci scalar R (SymPy Expression).
        metric: The metric tensor g_munu (4x4 SymPy Matrix).

    Returns:
        A SymPy Matrix representing the Einstein tensor G_munu.

    Raises:
        ValueError: If inputs are not the correct shape or type.
    """
    if not isinstance(ricci_tensor, Matrix) or ricci_tensor.shape != (4, 4):
        raise ValueError("Ricci tensor must be a 4x4 SymPy Matrix.")
    if not isinstance(ricci_scalar, (sympy.Expr, sympy.Number)):
         # Allow for number type in case scalar simplifies to a constant
        raise ValueError("Ricci scalar must be a SymPy Expression or Number.")
    if not isinstance(metric, Matrix) or metric.shape != (4, 4):
        raise ValueError("Metric must be a 4x4 SymPy Matrix.")

    # Calculate the Einstein tensor using the formula
    einstein_tensor = ricci_tensor - (sympy.Rational(1, 2) * metric * ricci_scalar)

    # Apply simplification to all components (can be slow)
    # einstein_tensor = einstein_tensor.applyfunc(simplify)

    return einstein_tensor

# Example Usage (requires imports from other core modules)
if __name__ == '__main__':
    try:
        # Adjust imports based on execution context
        from metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
        from christoffel import calculate_christoffel_symbols
        from riemann import calculate_riemann_tensor
        from ricci import calculate_ricci_tensor, calculate_ricci_scalar

        # Example: Schwarzschild metric (Ricci flat, so Einstein tensor should also be zero)
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
        ricci = calculate_ricci_tensor(riemann)
        scalar_R = calculate_ricci_scalar(ricci, g_inv)

        # Simplify Ricci components before calculating Einstein tensor for this example
        ricci_simplified = ricci.applyfunc(simplify)
        scalar_R_simplified = simplify(scalar_R)

        print("Calculating Einstein Tensor for Schwarzschild metric...")
        einstein = calculate_einstein_tensor(ricci_simplified, scalar_R_simplified, g)
        
        print("Einstein Tensor G_munu:")
        # Simplify final result for display
        sympy.pprint(einstein.applyfunc(simplify))

        # Verify result for vacuum solution
        assert simplify(einstein) == Matrix.zeros(4,4), "Einstein tensor should be 0 for Schwarzschild (vacuum)"
        print("\nVerified: Einstein tensor is zero for Schwarzschild metric.")

    except ImportError:
        print("Could not import from core modules. Ensure they are accessible.")
    except ValueError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 