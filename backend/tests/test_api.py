import requests
import json
from typing import Dict, Any, List

# Base URL for the API
BASE_URL = "http://localhost:5000/api/v1/calculations"

def print_response(response: requests.Response) -> None:
    """Helper function to print response details"""
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_create_calculation(calculation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test creating a new calculation"""
    print("\nTesting POST /calculations/")
    response = requests.post(BASE_URL, json=calculation_data)
    print_response(response)
    return response.json()

def test_get_calculations(
    skip: int = 0,
    limit: int = 100,
    metric_name: str = None,
    calculation_type: str = None
) -> None:
    """Test getting all calculations with optional filtering"""
    print("\nTesting GET /calculations/ with filters")
    params = {
        "skip": skip,
        "limit": limit,
        "metric_name": metric_name,
        "calculation_type": calculation_type
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    response = requests.get(BASE_URL, params=params)
    print_response(response)

def test_get_calculation(calculation_id: int) -> None:
    """Test getting a specific calculation"""
    print(f"\nTesting GET /calculations/{calculation_id}")
    response = requests.get(f"{BASE_URL}/{calculation_id}")
    print_response(response)

def test_update_calculation_result(calculation_id: int, result_data: Dict[str, Any]) -> None:
    """Test updating a calculation's result"""
    print(f"\nTesting PUT /calculations/{calculation_id}/result")
    response = requests.put(f"{BASE_URL}/{calculation_id}/result", json=result_data)
    print_response(response)

def test_delete_calculation(calculation_id: int) -> None:
    """Test deleting a calculation"""
    print(f"\nTesting DELETE /calculations/{calculation_id}")
    response = requests.delete(f"{BASE_URL}/{calculation_id}")
    print_response(response)

def test_invalid_calculation_id() -> None:
    """Test operations with invalid calculation ID"""
    print("\nTesting operations with invalid calculation ID")
    invalid_id = 999999
    
    # Test GET with invalid ID
    print("\nTesting GET with invalid ID")
    response = requests.get(f"{BASE_URL}/{invalid_id}")
    print_response(response)
    
    # Test PUT with invalid ID
    print("\nTesting PUT with invalid ID")
    result_data = {"status": "error", "message": "Invalid calculation"}
    response = requests.put(f"{BASE_URL}/{invalid_id}/result", json=result_data)
    print_response(response)
    
    # Test DELETE with invalid ID
    print("\nTesting DELETE with invalid ID")
    response = requests.delete(f"{BASE_URL}/{invalid_id}")
    print_response(response)

def test_invalid_input_data() -> None:
    """Test creating calculation with invalid input data"""
    print("\nTesting POST with invalid input data")
    
    # Missing required fields
    invalid_data = {
        "metric_name": "schwarzschild"
        # Missing calculation_type and input_parameters
    }
    response = requests.post(BASE_URL, json=invalid_data)
    print_response(response)
    
    # Invalid metric name
    invalid_data = {
        "metric_name": "invalid_metric",
        "calculation_type": "geodesic",
        "input_parameters": {"mass": 1.0}
    }
    response = requests.post(BASE_URL, json=invalid_data)
    print_response(response)

def test_pagination() -> None:
    """Test pagination functionality"""
    print("\nTesting pagination")
    
    # Create multiple calculations
    calculations = []
    for i in range(5):
        calculation_data = {
            "metric_name": "schwarzschild",
            "calculation_type": "geodesic",
            "input_parameters": {
                "mass": 1.0,
                "initial_position": [1.0, 0.0, 0.0],
                "initial_velocity": [0.0, 0.1, 0.0]
            }
        }
        calculation = test_create_calculation(calculation_data)
        calculations.append(calculation)
    
    # Test different page sizes
    print("\nTesting different page sizes")
    test_get_calculations(limit=2)  # First page
    test_get_calculations(skip=2, limit=2)  # Second page
    
    # Clean up
    for calculation in calculations:
        test_delete_calculation(calculation["id"])

def test_filtering() -> None:
    """Test filtering calculations"""
    print("\nTesting filtering")
    
    # Create calculations with different types
    calculation_data = {
        "metric_name": "schwarzschild",
        "calculation_type": "geodesic",
        "input_parameters": {"mass": 1.0}
    }
    geodesic_calc = test_create_calculation(calculation_data)
    
    calculation_data["calculation_type"] = "curvature"
    curvature_calc = test_create_calculation(calculation_data)
    
    # Test filtering by calculation type
    print("\nTesting filter by calculation_type")
    test_get_calculations(calculation_type="geodesic")
    test_get_calculations(calculation_type="curvature")
    
    # Test filtering by metric name
    print("\nTesting filter by metric_name")
    test_get_calculations(metric_name="schwarzschild")
    
    # Clean up
    test_delete_calculation(geodesic_calc["id"])
    test_delete_calculation(curvature_calc["id"])

def main():
    """Run all test cases"""
    try:
        # Test basic CRUD operations
        print("\n=== Testing Basic CRUD Operations ===")
        calculation_data = {
            "metric_name": "schwarzschild",
            "calculation_type": "geodesic",
            "input_parameters": {
                "mass": 1.0,
                "initial_position": [1.0, 0.0, 0.0],
                "initial_velocity": [0.0, 0.1, 0.0]
            }
        }
        calculation = test_create_calculation(calculation_data)
        calculation_id = calculation["id"]
        
        test_get_calculations()
        test_get_calculation(calculation_id)
        
        result_data = {
            "geodesic_path": [
                {"t": 0.0, "x": 1.0, "y": 0.0, "z": 0.0},
                {"t": 1.0, "x": 0.9, "y": 0.1, "z": 0.0}
            ],
            "status": "completed",
            "computation_time": 0.5
        }
        test_update_calculation_result(calculation_id, result_data)
        test_delete_calculation(calculation_id)
        
        # Test edge cases
        print("\n=== Testing Edge Cases ===")
        test_invalid_calculation_id()
        test_invalid_input_data()
        
        # Test advanced features
        print("\n=== Testing Advanced Features ===")
        test_pagination()
        test_filtering()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 