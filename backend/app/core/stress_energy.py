import sympy
from sympy import Matrix, symbols, diag, simplify, Expr
from typing import List, Union

# Import metric if needed for specific types like perfect fluid
from .metric import create_metric_tensor # Assuming this might be needed

# Define common symbols used in stress-energy tensors
rho, p = symbols('rho p') # Density, Pressure

def create_stress_energy_tensor_from_components(
    components: List[List[Union[Expr, Number, str]]]
) -> Matrix:
    """
    Creates a SymPy Matrix representing the Stress-Energy tensor T_munu 
    from user-provided components.

    Args:
        components: A 4x4 list of lists containing SymPy expressions (or strings 
                    that can be parsed into expressions) for each T_munu component.

    Returns:
        A SymPy Matrix representing the stress-energy tensor.

    Raises:
        ValueError: If the components list is not 4x4.
        sympy.SympifyError: If components contain invalid expressions.
    """
    if len(components) != 4 or not all(len(row) == 4 for row in components):
        raise ValueError("Stress-Energy tensor components must be a 4x4 list of lists.")

    # Attempt to sympify all components
    sympified_components = [[sympy.sympify(comp) for comp in row] for row in components]

    tensor = Matrix(sympified_components)
    # Note: Symmetry T_munu = T_numu is usually assumed for standard matter.
    # We could add a check here if desired.
    # if not tensor.is_symmetric():
    #     print("Warning: Provided stress-energy components are not symmetric.")
    return tensor

def create_vacuum_tensor() -> Matrix:
    """
    Creates the Stress-Energy tensor for vacuum (T_munu = 0).

    Returns:
        A 4x4 zero SymPy Matrix.
    """
    return Matrix.zeros(4, 4)

def create_dust_tensor(
    density: Union[Expr, Number, str] = rho,
    four_velocity: List[Union[Expr, Number, str]] = [-1, 0, 0, 0]
) -> Matrix:
    """
    Creates the Stress-Energy tensor for pressureless dust.

    Formula: T_munu = density * u_mu * u_nu

    Args:
        density: The density (rho) as a SymPy expression, number, or string. Defaults to symbol 'rho'.
        four_velocity: The 4-velocity vector u_mu = [u_t, u_r, u_theta, u_phi] as a list of 
                       SymPy expressions, numbers, or strings. 
                       Defaults to [-1, 0, 0, 0] (comoving observer in standard coordinates,
                       assuming g_00 approx -1 or normalization handled elsewhere).
                       *Note: Proper normalization u_mu * u^mu = -1 depends on the metric.* 

    Returns:
        A SymPy Matrix representing the dust stress-energy tensor.

    Raises:
        ValueError: If four_velocity is not a list of length 4.
        sympy.SympifyError: If inputs cannot be parsed into expressions.
    """
    if len(four_velocity) != 4:
        raise ValueError("Four-velocity must be a list of 4 components.")
    
    sym_density = sympy.sympify(density)
    sym_u = [sympy.sympify(comp) for comp in four_velocity]
    
    tensor = Matrix.zeros(4, 4)
    for mu in range(4):
        for nu in range(4):
            tensor[mu, nu] = sym_density * sym_u[mu] * sym_u[nu]
            
    return tensor

def create_perfect_fluid_tensor(
    metric: Matrix,
    density: Union[Expr, Number, str] = rho,
    pressure: Union[Expr, Number, str] = p,
    four_velocity: List[Union[Expr, Number, str]] = [-1, 0, 0, 0]
) -> Matrix:
    """
    Creates the Stress-Energy tensor for a perfect fluid.

    Formula: T_munu = (density + pressure) * u_mu * u_nu + pressure * g_munu

    Args:
        metric: The metric tensor g_munu (4x4 SymPy Matrix). Needed for the second term.
        density: The density (rho). Defaults to symbol 'rho'.
        pressure: The pressure (p). Defaults to symbol 'p'.
        four_velocity: The 4-velocity vector u_mu. Defaults to [-1, 0, 0, 0].
                       *See note in create_dust_tensor about normalization.*

    Returns:
        A SymPy Matrix representing the perfect fluid stress-energy tensor.
        
    Raises:
        ValueError: If inputs have incorrect dimensions/types.
        sympy.SympifyError: If inputs cannot be parsed into expressions.
    """
    if not isinstance(metric, Matrix) or metric.shape != (4, 4):
        raise ValueError("Metric must be a 4x4 SymPy Matrix.")
    if len(four_velocity) != 4:
        raise ValueError("Four-velocity must be a list of 4 components.")

    sym_density = sympy.sympify(density)
    sym_pressure = sympy.sympify(pressure)
    sym_u = [sympy.sympify(comp) for comp in four_velocity]

    tensor = Matrix.zeros(4, 4)
    for mu in range(4):
        for nu in range(4):
            # First term: (rho + p) * u_mu * u_nu
            term1 = (sym_density + sym_pressure) * sym_u[mu] * sym_u[nu]
            # Second term: p * g_munu
            term2 = sym_pressure * metric[mu, nu]
            tensor[mu, nu] = term1 + term2
            
    return tensor

# Example Usage
if __name__ == '__main__':
    print("Vacuum Tensor T_munu:")
    T_vac = create_vacuum_tensor()
    sympy.pprint(T_vac)

    print("\nDust Tensor T_munu (default rho, default u_mu):")
    T_dust = create_dust_tensor()
    sympy.pprint(T_dust)
    
    # Example Perfect Fluid requires a metric. Let's use Minkowski for simplicity.
    t, x, y, z = symbols('t x y z')
    minkowski_metric = diag(-1, 1, 1, 1) 
    
    print("\nPerfect Fluid Tensor T_munu (default rho, p, default u_mu, Minkowski metric):")
    T_fluid = create_perfect_fluid_tensor(minkowski_metric)
    sympy.pprint(T_fluid.applyfunc(simplify))

    print("\nCustom Tensor T_munu:")
    custom_components = [
        ['rho', '0', '0', '0'],
        ['0', 'p_r', '0', '0'],
        ['0', '0', 'p_t', '0'],
        ['0', '0', '0', 'p_t'] # Example anisotropic pressure
    ]
    p_r, p_t = symbols('p_r p_t')
    try:
        T_custom = create_stress_energy_tensor_from_components(custom_components)
        sympy.pprint(T_custom)
    except (ValueError, sympy.SympifyError) as e:
        print(f"Error creating custom tensor: {e}") 