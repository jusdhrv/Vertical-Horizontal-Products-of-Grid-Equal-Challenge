import itertools
import math
import time
from multiprocessing import Pool, cpu_count
from modules import (
    canonical_form, format_time, save_json_output, create_solution_dict,
    parse_solution_string, list_multiple, memoized_indices
)

# Memoization dictionaries
memo = {}
index_memo = {}


def memoized_list_multiple(sublist):
    key = tuple(sublist)
    if key not in memo:
        memo[key] = list_multiple(sublist)
    return memo[key]


def memoized_indices_cached(n):
    if n not in index_memo:
        index_memo[n] = memoized_indices(n)
    return index_memo[n]


def check_permutation(p, n, single_solution=False, found_solution=None):
    if single_solution and found_solution and found_solution.value:
        return None
        
    row_indices, col_indices = memoized_indices_cached(n)
    h_product = [memoized_list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [memoized_list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        if single_solution and found_solution:
            found_solution.value = True
        return str(p) + " " + str(h_product) + " " + str(v_product)
    return None


def find_grids_n(n, single_solution=False):
    mode = "single solution" if single_solution else "all solutions"
    print(f"\nBegin execution for n = {n} (Mode: {mode})")
    possible_vals = list(range(1, n * n + 1))

    print(f"| Possible values of the grid cells are: {possible_vals}")
    n_start_time = time.time()

    total_p = math.factorial(n * n)
    print(f"| Total permutations to check: {total_p:,}")

    valid_permutations = []

    if single_solution:
        # Single solution mode with early termination
        from multiprocessing import Manager
        manager = Manager()
        found_solution = manager.Value("i", False)
        
        with Pool(cpu_count()) as pool:
            results = pool.starmap(
                check_permutation, 
                [(p, n, True, found_solution) for p in itertools.permutations(possible_vals)]
            )
            
        for result in results:
            if result:
                valid_permutations.append(result)
                break  # Stop after first solution
    else:
        # All solutions mode
        with Pool(cpu_count()) as pool:
            results = pool.starmap(
                check_permutation, 
                [(p, n, False, None) for p in itertools.permutations(possible_vals)]
            )
            
        for result in results:
            if result:
                valid_permutations.append(result)

    # Convert to solution dictionaries for JSON output
    solutions = []
    for valid_permutation in valid_permutations:
        # Use the parse_solution_string function from modules
        grid, h_products, v_products = parse_solution_string(valid_permutation)
        if grid is not None:
            solution_dict = create_solution_dict(grid, h_products, v_products, n)
            solutions.append(solution_dict)

    execution_time = time.time() - n_start_time
    
    # Save JSON output
    save_json_output(n, solutions, execution_time)
    
    print(f"\nFinished executing for: {n}, Execution Time: {format_time(execution_time)}")


# Example usage
if __name__ == "__main__":
    print(
        "This programme executes the fast memoized grid finder from 1 up to a maximum 'n' of your choice..."
    )
    n_max = int(input("Enter the value for 'n' to use: "))
    
    # Ask user for mode
    print("\nChoose execution mode:")
    print("1. Find all possible solutions")
    print("2. Find single solution (stop after first)")
    mode_choice = input("Enter your choice (1 or 2): ").strip()
    
    single_solution = mode_choice == "2"
    mode_str = "single solution" if single_solution else "all solutions"
    print(f"\nSelected mode: {mode_str}")
    
    main_start_time = time.time()

    if n_max < 0:
        print("\nInvalid value provided. Must be a natural number")

    elif n_max == 0:
        grid_size = 1
        while True:
            try:
                find_grids_n(grid_size, single_solution)
                grid_size += 1
            except KeyboardInterrupt:
                print("\nExecution interrupted by user.")
                break

    elif n_max > 0:
        try:
            for grid_size in range(1, n_max + 1):
                find_grids_n(grid_size, single_solution)
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")

    print(f"\n\nTotal Execution Time: {format_time(time.time() - main_start_time)}")
