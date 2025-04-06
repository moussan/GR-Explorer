import sympy
from sympy import Matrix, symbols, simplify, diff

# Define common coordinate symbols
t, r, theta, phi = symbols('t r theta phi')
x, y, z = symbols('x y z')

# Default coordinate system (can be expanded)
DEFAULT_COORDS = [t, r, theta, phi]

def create_metric_tensor(components: list[list[sympy.Expr]], coords: list[sympy.Symbol] = DEFAULT_COORDS) -> Matrix:
    """
    Creates a SymPy Matrix representing the metric tensor g_munu.

    Args:
        components: A 4x4 list of lists containing SymPy expressions for each metric component.
        coords: A list of 4 coordinate symbols. Defaults to [t, r, theta, phi].

    Returns:
        A SymPy Matrix representing the metric tensor.

    Raises:
        ValueError: If the components list is not 4x4 or coordinates list is not 4.
    """
    if len(components) != 4 or not all(len(row) == 4 for row in components):
        raise ValueError("Metric components must be a 4x4 list of lists.")
    if len(coords) != 4:
        raise ValueError("Coordinates list must contain 4 symbols.")

    # TODO: Add validation that components are valid SymPy expressions?
    # Simplification might be desired here or later
    metric = Matrix(components)
    # Check symmetry (optional but good practice for metrics)
    # if not metric.is_symmetric():
    #     print("Warning: Provided metric components are not symmetric.")
    return metric

def calculate_inverse_metric(metric: Matrix) -> Matrix:
    """
    Calculates the inverse of the given metric tensor g^munu.

    Args:
        metric: A SymPy Matrix representing the metric tensor g_munu.

    Returns:
        A SymPy Matrix representing the inverse metric tensor g^munu.

    Raises:
        ValueError: If the input is not a 4x4 matrix.
        Exception: If the matrix is singular (determinant is zero).
    """
    if not isinstance(metric, Matrix) or metric.shape != (4, 4):
        raise ValueError("Input must be a 4x4 SymPy Matrix.")

    # Calculate the inverse
    determinant = metric.det()
    if simplify(determinant) == 0:
        raise ValueError("Metric is singular (determinant is zero), cannot compute inverse.")

    inverse_metric = metric.inv()
    # Apply simplification to the inverse metric components
    # inverse_metric = inverse_metric.applyfunc(simplify) # Be careful, simplify can be slow
    return inverse_metric

# Example Usage (can be removed or moved to tests later)
if __name__ == '__main__':
    # Example: Schwarzschild metric components
    M = symbols('M') # Mass parameter
    schwarzschild_components = [
        [-(1 - 2*M/r), 0, 0, 0],
        [0, 1/(1 - 2*M/r), 0, 0],
        [0, 0, r**2, 0],
        [0, 0, 0, r**2 * sympy.sin(theta)**2]
    ]

    try:
        g = create_metric_tensor(schwarzschild_components)
        print("Metric Tensor g_munu:")
        sympy.pprint(g)

        g_inv = calculate_inverse_metric(g)
        print("\nInverse Metric Tensor g^munu:")
        sympy.pprint(g_inv)

        # Test determinant check
        # singular_metric = Matrix([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        # calculate_inverse_metric(singular_metric)

    except ValueError as e:
        print(f"Error: {e}") 