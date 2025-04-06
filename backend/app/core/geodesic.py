import numpy as np
import sympy
from sympy import Array, lambdify, symbols, Expr, Symbol
from scipy.integrate import solve_ivp
from typing import List, Dict, Callable, Tuple

# Import necessary core components if running standalone tests
# from .metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
# from .christoffel import calculate_christoffel_symbols

# Define symbols for state variables if needed globally
# state_t, state_r, state_theta, state_phi = symbols('state_t state_r state_theta state_phi')
# state_dt, state_dr, state_dtheta, state_dphi = symbols('state_dt state_dr state_dtheta state_dphi')

def _geodesic_ode_system(
    christoffel_lambdified: List[List[List[Callable]]],
    coords: List[Symbol]
) -> Callable:
    """
    Creates the function defining the system of first-order ODEs for geodesics.

    The state vector `y` is [x^0, x^1, x^2, x^3, dx^0/dtau, dx^1/dtau, dx^2/dtau, dx^3/dtau].
    The system is:
        d(x^lambda)/dtau = u^lambda  (where u^lambda = dx^lambda/dtau)
        d(u^lambda)/dtau = - Gamma^lambda_mu_nu * u^mu * u^nu

    Args:
        christoffel_lambdified: A 3D list/array where each element [lam][mu][nu] is a 
                                callable function `f(*coords)` that evaluates 
                                Gamma^lambda_mu_nu numerically.
        coords: The list of coordinate symbols (e.g., [t, r, theta, phi]).

    Returns:
        A callable function `ode_func(tau, y)` that computes the derivatives dy/dtau.
    """
    n = len(coords)
    if n != 4:
        raise ValueError("Currently only supports 4D spacetime.")

    def ode_func(tau, y):
        """The ODE function for solve_ivp.
        Args:
            tau: Proper time/affine parameter (independent variable).
            y: State vector [x^0, ..., x^3, u^0, ..., u^3].
        Returns:
            dydtau: Derivatives of the state vector.
        """
        dydtau = np.zeros_like(y)
        current_coords = y[:n] # x^0 to x^3
        current_vel = y[n:]    # u^0 to u^3

        # First part: d(x^lambda)/dtau = u^lambda
        dydtau[:n] = current_vel

        # Second part: d(u^lambda)/dtau = - Gamma^lambda_mu_nu * u^mu * u^nu
        # Calculate Christoffel symbols at the current coordinates
        gamma_values = np.zeros((n, n, n))
        try:
            for lam in range(n):
                for mu in range(n):
                    for nu in range(n):
                        # Evaluate the lambdified function with current coords
                        gamma_values[lam, mu, nu] = christoffel_lambdified[lam][mu][nu](*current_coords)
        except Exception as e:
            # Handle potential errors during evaluation (e.g., division by zero at singularity)
            # print(f"Warning: Error evaluating Christoffel symbols at {current_coords}: {e}")
            # Return high values to potentially halt integration or NaN
            # return np.full_like(y, np.nan)
            # For now, let it propagate, might need better handling
            raise RuntimeError(f"Error evaluating Christoffel symbol at {coords}={current_coords}") from e
            
        # Calculate the acceleration term d(u^lambda)/dtau
        for lam in range(n):
            acceleration = 0
            for mu in range(n):
                for nu in range(n):
                    acceleration -= gamma_values[lam, mu, nu] * current_vel[mu] * current_vel[nu]
            dydtau[n + lam] = acceleration

        return dydtau

    return ode_func

def calculate_geodesic(
    christoffel: Array,
    coords: List[Symbol],
    initial_pos: List[float],
    initial_vel: List[float],
    t_span: Tuple[float, float],
    t_eval: np.ndarray,
    **solve_ivp_kwargs
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Numerically computes a geodesic path.

    Args:
        christoffel: The Christoffel symbols (Gamma^lambda_mu_nu) as a SymPy Array.
        coords: List of coordinate symbols.
        initial_pos: Initial position [x^0(0), x^1(0), x^2(0), x^3(0)].
        initial_vel: Initial 4-velocity [dx^0/dtau(0), ..., dx^3/dtau(0)]. 
                     (Need careful normalization for timelike/null).
        t_span: Integration interval (tau_min, tau_max) for proper time/affine parameter.
        t_eval: Array of time points where the solution is desired.
        **solve_ivp_kwargs: Additional keyword arguments passed to scipy.integrate.solve_ivp.

    Returns:        
        A tuple (tau_values, state_vectors):
        - tau_values: Array of time points corresponding to the solution points.
        - state_vectors: Array where each row is the state vector [x0..x3, u0..u3] at a time point.
        
    Raises:
        ValueError: If input dimensions are incorrect.
        ImportError: If scipy is not installed.
        RuntimeError: If numerical integration fails or Christoffel evaluation fails.
    """
    n = len(coords)
    if len(initial_pos) != n or len(initial_vel) != n:
        raise ValueError(f"Initial position and velocity must have {n} components.")
    if not isinstance(christoffel, (Array, sympy.tensor.array.dense_ndim_array.ImmutableDenseNDimArray)) or christoffel.rank() != 3 or christoffel.shape != (n, n, n):
         raise ValueError("Christoffel symbols must be a 3-rank SymPy Array with shape (4, 4, 4).")

    # Lambdify Christoffel symbols for numerical evaluation
    # We need a 3D list of callable functions
    christoffel_lambdified = [[[
            lambdify(coords, christoffel[lam, mu, nu], modules=['numpy', {'ImmutableDenseNDimArray': np.array}])
            for nu in range(n)] 
            for mu in range(n)] 
            for lam in range(n)]
    
    # Create the ODE function
    ode_func = _geodesic_ode_system(christoffel_lambdified, coords)

    # Set up initial state vector
    y0 = np.concatenate([initial_pos, initial_vel])

    # Solve the ODE system
    try:
        sol = solve_ivp(
            ode_func,
            t_span,
            y0,
            t_eval=t_eval,
            **solve_ivp_kwargs
        )

        if not sol.success:
            raise RuntimeError(f"solve_ivp failed: {sol.message}")

        # Return times and the solution array (transpose of sol.y)
        return sol.t, sol.y.T

    except Exception as e:
        # Catch potential errors from ode_func or solve_ivp
        raise RuntimeError(f"Error during geodesic calculation: {e}") from e

# Example Usage (requires imports from core modules)
if __name__ == '__main__':
    try:
        from metric import DEFAULT_COORDS, create_metric_tensor, calculate_inverse_metric
        from christoffel import calculate_christoffel_symbols

        # Example: Geodesic in Schwarzschild spacetime
        t, r, theta, phi = DEFAULT_COORDS
        M = symbols('M')
        schwarzschild_components = [
            [-(1 - 2*M/r), 0, 0, 0],
            [0, 1/(1 - 2*M/r), 0, 0],
            [0, 0, r**2, 0],
            [0, 0, 0, r**2 * sympy.sin(theta)**2]
        ]

        # Substitute numerical value for M for calculation
        M_val = 1.0
        schwarzschild_components_num = [[comp.subs(M, M_val) for comp in row] 
                                       for row in schwarzschild_components]

        g = create_metric_tensor(schwarzschild_components_num, DEFAULT_COORDS)
        g_inv = calculate_inverse_metric(g)
        gamma = calculate_christoffel_symbols(g, g_inv, DEFAULT_COORDS)
        
        # Simplify gamma before lambdifying (can be crucial for performance/stability)
        # gamma_simplified = gamma.applyfunc(simplify) # This can take time!
        gamma_simplified = gamma # Use unsimplified for now
        
        # Initial conditions: Particle starting at r=10, theta=pi/2, phi=0, falling radially inwards
        # Let's start from rest relative to distant observer initially? Not quite right for GR.
        # Define initial velocity carefully. For radial infall from large r: 
        # Need to satisfy normalization g_munu u^mu u^nu = -1 (timelike)
        # Let's set initial 4-velocity components (example values, may need adjustment) 
        r_start = 10.0
        # From normalization: g_tt (u^t)^2 + g_rr (u^r)^2 = -1. Assume u^theta=u^phi=0.
        # -(1-2M/r_start)*(u^t)^2 + (1/(1-2M/r_start))*(u^r)^2 = -1
        # Let u^r = 0 initially (momentarily at rest at r_start)
        # -(1-2M/r_start)*(u^t)^2 = -1 => u^t = 1 / sqrt(1 - 2M/r_start)
        u_t_start = 1 / np.sqrt(1 - 2*M_val/r_start)
        u_r_start = 0.0 
        
        initial_pos = [0.0, r_start, np.pi/2, 0.0] # t, r, theta, phi
        initial_vel = [u_t_start, u_r_start, 0.0, 0.0] # dt/dtau, dr/dtau, dtheta/dtau, dphi/dtau
        
        print(f"Initial Position: {initial_pos}")
        print(f"Initial Velocity: {initial_vel}")

        # Integration parameters
        tau_max = 50.0 
        t_span = (0, tau_max)
        t_eval = np.linspace(t_span[0], t_span[1], 500) # Evaluate at 500 points

        print("\nCalculating geodesic...")
        # Use a stricter solver and tolerances if needed, e.g., method='Radau'
        tau_vals, states = calculate_geodesic(
            gamma_simplified, DEFAULT_COORDS, initial_pos, initial_vel,
            t_span, t_eval, method='RK45', rtol=1e-6, atol=1e-9
        )
        print("Calculation complete.")

        # Extract position coordinates
        t_coords = states[:, 0]
        r_coords = states[:, 1]
        theta_coords = states[:, 2]
        phi_coords = states[:, 3]

        # Basic plotting (requires matplotlib)
        try:
            import matplotlib.pyplot as plt
            
            # Plot r vs t (coordinate time)
            plt.figure(figsize=(10, 6))
            plt.plot(t_coords, r_coords, label='r(t)')
            plt.title('Radial Geodesic in Schwarzschild Spacetime (r vs t)')
            plt.xlabel('Coordinate Time (t)')
            plt.ylabel('Radial Coordinate (r)')
            plt.grid(True)
            plt.legend()
            plt.axhline(2*M_val, color='red', linestyle='--', label='Event Horizon (r=2M)')
            plt.ylim(bottom=0) # Ensure r doesn't go below 0 visually
            plt.show()
            
            # Plot path in equatorial plane (x-y projection)
            x_coords = r_coords * np.cos(phi_coords) # Assuming theta=pi/2 remains constant
            y_coords = r_coords * np.sin(phi_coords)
            plt.figure(figsize=(8, 8))
            plt.plot(x_coords, y_coords, label='Path')
            plt.scatter([0], [0], color='black', s=100, label='Singularity (r=0)')
            horizon = plt.Circle((0, 0), 2*M_val, color='red', fill=False, linestyle='--', label='Event Horizon')
            plt.gca().add_patch(horizon)
            plt.title('Geodesic Path in Equatorial Plane (Schwarzschild)')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.axis('equal')
            plt.grid(True)
            plt.legend()
            plt.show()

        except ImportError:
            print("\nMatplotlib not found. Cannot plot results.")
            print("First few state vectors:")
            print(states[:5, :])

    except ImportError as e:
        print(f"Import error: {e}. Ensure core modules and SciPy/NumPy are installed.")
    except ValueError as e:
        print(f"Input error: {e}")
    except RuntimeError as e:
        print(f"Runtime error during calculation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 