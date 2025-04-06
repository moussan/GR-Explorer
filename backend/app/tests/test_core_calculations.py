import pytest
import sympy
from sympy import symbols, sin, cos, Rational, simplify, zeros, Matrix

# Adjust imports to be relative to the 'app' directory when running pytest from 'backend'
from app.core.metric import create_metric_tensor
from app.core.christoffel import calculate_christoffel_symbols

# Define symbols globally for tests
t, r, theta, phi = symbols('t r theta phi')
M = symbols('M')
coords_list = [t, r, theta, phi]

# Schwarzschild metric components (symbolic)
schwarzschild_components = [
    [-(1 - 2*M/r), 0, 0, 0],
    [0, 1/(1 - 2*M/r), 0, 0],
    [0, 0, r**2, 0],
    [0, 0, 0, r**2 * sin(theta)**2]
]

@pytest.fixture
def schwarzschild_metric():
    """Provides the Schwarzschild metric tensor as a fixture."""
    return create_metric_tensor(schwarzschild_components, coords_list)

@pytest.fixture
def schwarzschild_inverse_metric(schwarzschild_metric):
     """Provides the inverse Schwarzschild metric tensor."""
     # Calculate inverse (or define known result)
     g_inv = schwarzschild_metric.inv()
     # Ensure it remains a Matrix object after simplification if necessary
     # Simplification might return different types depending on structure
     simplified_inv = simplify(g_inv)
     # Check if simplification changed type, if so, cast back (less likely needed)
     # if not isinstance(simplified_inv, Matrix):
     #     simplified_inv = Matrix(simplified_inv)
     return simplified_inv # Pass the simplified result, assuming it's still a Matrix

def test_create_schwarzschild_metric(schwarzschild_metric):
    """Test the creation and basic properties of the Schwarzschild metric."""
    g = schwarzschild_metric
    assert g.shape == (4, 4)
    # Compare simplified difference to zero for robustness
    expected_g00 = -(1 - 2*M/r)
    assert simplify(g[0, 0] - expected_g00) == 0
    # assert simplify(g[0, 0]) == expected_g00 # Original assertion
    assert simplify(g[1, 1] - (1 / (1 - 2*M/r))) == 0
    assert simplify(g[2, 2] - r**2) == 0
    assert simplify(g[3, 3] - (r**2 * sin(theta)**2)) == 0
    assert g[0, 1] == 0 # Check an off-diagonal term

def test_schwarzschild_christoffel_known_values(schwarzschild_metric, schwarzschild_inverse_metric):
    """Test some known non-zero Christoffel symbols for Schwarzschild."""
    # Ensure the inverse metric passed is explicitly a Matrix
    g_inv_matrix = Matrix(schwarzschild_inverse_metric)
    christoffel, _ = calculate_christoffel_symbols(schwarzschild_metric, g_inv_matrix, coords_list)
    
    # Use simplify(expr1 - expr2) == 0 for robust comparison
    assert simplify(christoffel[0, 1, 0] - (M / (r**2 * (1 - 2*M/r)))) == 0
    assert simplify(christoffel[0, 0, 1] - (M / (r**2 * (1 - 2*M/r)))) == 0
    assert simplify(christoffel[1, 0, 0] - (M*(1 - 2*M/r) / r**2)) == 0
    assert simplify(christoffel[1, 1, 1] - (-M / (r**2 * (1 - 2*M/r)))) == 0
    assert simplify(christoffel[1, 2, 2] - (-(r - 2*M))) == 0
    assert simplify(christoffel[2, 1, 2] - (1/r)) == 0
    assert simplify(christoffel[2, 2, 1] - (1/r)) == 0
    assert simplify(christoffel[3, 3, 1] - (1/r)) == 0
    assert simplify(christoffel[3, 1, 3] - (1/r)) == 0
    assert simplify(christoffel[3, 3, 2] - (cos(theta)/sin(theta))) == 0
    assert simplify(christoffel[3, 2, 3] - (cos(theta)/sin(theta))) == 0

def test_schwarzschild_christoffel_zero_values(schwarzschild_metric, schwarzschild_inverse_metric):
    """Test some Christoffel symbols expected to be zero for Schwarzschild."""
    g_inv_matrix = Matrix(schwarzschild_inverse_metric)
    christoffel, _ = calculate_christoffel_symbols(schwarzschild_metric, g_inv_matrix, coords_list)
    
    # Check some values expected to be zero
    assert simplify(christoffel[0, 0, 0]) == 0
    assert simplify(christoffel[1, 0, 1]) == 0
    assert simplify(christoffel[2, 0, 0]) == 0
    assert simplify(christoffel[3, 1, 2]) == 0
    
# TODO: Add tests for other core functions (Riemann, Ricci, Einstein, Embedding, Geodesic ODE)
# TODO: Add tests for edge cases (e.g., Minkowski metric) 