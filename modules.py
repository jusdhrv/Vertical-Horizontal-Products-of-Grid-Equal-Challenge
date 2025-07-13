import json
import time
from os import listdir, path, makedirs
from itertools import chain
from math import factorial

# Global session counter for unique file naming
_session_counter = 0

def get_session_file():
    """Get a unique file path for the current execution session."""
    global _session_counter
    _session_counter += 1
    output_dir = "Data"
    makedirs(output_dir, exist_ok=True)
    return path.join(output_dir, f"session_{_session_counter}-output.json")


def get_next_json_file():
    """Get the next available JSON output file number."""
    output_dir = "Data"
    json_suffix = "-output.json"
    
    # Ensure Data directory exists
    makedirs(output_dir, exist_ok=True)
    
    existing_files = [f for f in listdir(output_dir) if f.endswith(json_suffix)]

    if not existing_files:
        return path.join(output_dir, f"1{json_suffix}")

    # Extract file numbers and find the next one
    file_numbers = []
    for f in existing_files:
        try:
            # Extract number from filename like "1-output.json" -> 1
            number = int(f.split('-')[0])
            file_numbers.append(number)
        except (ValueError, IndexError):
            continue
    
    if not file_numbers:
        return path.join(output_dir, f"1{json_suffix}")
    
    next_file_number = max(file_numbers) + 1
    return path.join(output_dir, f"{next_file_number}{json_suffix}")


def canonical_form(grid, n):
    """Convert grid to canonical form to identify equivalent solutions."""
    grid = [grid[i : i + n] for i in range(0, len(grid), n)]
    grid = sorted(grid)
    grid = list(zip(*grid))
    grid = sorted(grid)
    grid = list(zip(*grid))
    return list(chain(*grid))


def format_time(seconds):
    """Format time in HH:MM:SS."""
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def save_json_output(n, solutions, execution_time, output_file_path=None):
    """
    Save results in JSON format.
    
    Args:
        n: Grid size
        solutions: List of solution dictionaries
        execution_time: Execution time in seconds
        output_file_path: Optional specific file path
    """
    if output_file_path is None:
        output_file_path = get_next_json_file()
    
    # Ensure Data directory exists
    makedirs("Data", exist_ok=True)
    
    output_data = {
        "n": n,
        "solutions": solutions,
        "execution_time": format_time(execution_time),
        "total_solutions": len(solutions)
    }
    
    with open(output_file_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"| JSON output saved to: {output_file_path}")
    return output_file_path


def create_solution_dict(grid, horizontal_products, vertical_products, n):
    """
    Create a solution dictionary for JSON output.
    
    Args:
        grid: The grid as a list
        horizontal_products: List of horizontal row products
        vertical_products: List of vertical column products
        n: Grid size
    
    Returns:
        Dictionary representing the solution
    """
    return {
        "grid": list(grid),
        "horizontal_products": horizontal_products,
        "vertical_products": vertical_products,
        "canonical_form": canonical_form(grid, n)
    }


def parse_solution_string(solution_str):
    """
    Parse a solution string from the legacy format to extract components.
    
    Args:
        solution_str: String in format "grid horizontal_products vertical_products"
    
    Returns:
        Tuple of (grid, horizontal_products, vertical_products)
    """
    try:
        # Find the end of the grid tuple (first closing parenthesis)
        grid_end = solution_str.find(")")
        if grid_end == -1:
            return None, None, None
        
        # Extract grid part
        grid_str = solution_str[:grid_end + 1]
        remaining_str = solution_str[grid_end + 1:].strip()
        
        # Parse grid
        if grid_str.startswith("(") and grid_str.endswith(")"):
            grid_str = grid_str[1:-1]  # Remove parentheses
        # Split by comma and clean up each element
        grid_elements = [x.strip() for x in grid_str.split(",")]
        grid = [int(x) for x in grid_elements if x]
        
        # Split remaining string into horizontal and vertical products
        parts = remaining_str.split(" ", 1)
        if len(parts) != 2:
            return None, None, None
        
        # Parse horizontal products (first part)
        h_products_str = parts[0]
        if h_products_str.startswith("[") and h_products_str.endswith("]"):
            h_products_str = h_products_str[1:-1]  # Remove brackets
        horizontal_products = [int(x.strip()) for x in h_products_str.split(",")]
        
        # Parse vertical products (second part)
        v_products_str = parts[1]
        if v_products_str.startswith("[") and v_products_str.endswith("]"):
            v_products_str = v_products_str[1:-1]  # Remove brackets
        vertical_products = [int(x.strip()) for x in v_products_str.split(",")]
        
        return grid, horizontal_products, vertical_products
        
    except (ValueError, IndexError) as e:
        print(f"Warning: Could not parse solution string: {solution_str}")
        print(f"Error: {e}")
        return None, None, None


def list_multiple(lst):
    """Calculate product of list elements efficiently."""
    product = 1
    for i in lst:
        product *= i
    return product


def memoized_indices(n):
    """Calculate row and column indices for an n×n grid."""
    start_indices = [j * n for j in range(n)]
    end_indices = [start_index + n for start_index in start_indices]
    row_indices = [
        list(range(start, end)) for start, end in zip(start_indices, end_indices)
    ]
    col_indices = [[l + m * n for m in range(n)] for l in range(n)]
    return row_indices, col_indices 