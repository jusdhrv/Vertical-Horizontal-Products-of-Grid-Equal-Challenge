import itertools
import math
import time
from multiprocessing import Pool, cpu_count, Manager, Value
from os import remove, makedirs, path
from itertools import permutations, chain, islice
from modules import (
    canonical_form, format_time, save_json_output, create_solution_dict,
    parse_solution_string, list_multiple, memoized_indices, get_session_file
)

# Memoization dictionaries for performance
memo = {}
index_memo = {}


def memoized_list_multiple(sublist):
    """Memoized version of list multiplication for repeated calculations."""
    key = tuple(sublist)
    if key not in memo:
        memo[key] = list_multiple(sublist)
    return memo[key]


def memoized_indices_cached(n):
    """Memoized version of index calculation."""
    if n not in index_memo:
        index_memo[n] = memoized_indices(n)
    return index_memo[n]


def check_permutation_fast(p, n, single_solution=False, found_solution=None):
    """Fast permutation checker using memoization (for smaller n values)."""
    if single_solution and found_solution and found_solution.value:
        return None
        
    row_indices, col_indices = memoized_indices_cached(n)
    h_product = [memoized_list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [memoized_list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        if single_solution and found_solution:
            found_solution.value = True
        return (p, h_product, v_product)
    return None


def check_permutation_memory_safe(args):
    """Memory-safe permutation checker for larger n values."""
    p, n, row_indices, col_indices, worker_id = args
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        return canonical_p, h_product, v_product, worker_id
    return None


def check_permutation_memory_safe_single(args):
    """Memory-safe permutation checker for single solution mode."""
    p, n, row_indices, col_indices, worker_id, found_solution = args
    if found_solution.value:
        return None
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        found_solution.value = True
        return canonical_p, h_product, v_product, worker_id
    return None


def write_worker_file(worker_id, perms, chunk_size, n):
    """Write worker file for memory-safe processing."""
    worker_file = f"Data/Workers/worker_{n}_{worker_id}.txt"
    if path.exists(worker_file):
        with open(worker_file, "r") as f:
            lines = f.readlines()
            if lines and lines[-1].strip() == "&end&":
                print(f"| Worker {worker_id} file for n={n} already set up.")
                return

    with open(worker_file, "w") as f:
        for perm in islice(perms, chunk_size):
            f.write(",".join(map(str, perm)) + "\n")
        f.write("&end&\n")
    print(f"| Worker {worker_id} file setup complete for n={n}.")


def split_permutations_to_files(possible_vals, num_workers, n):
    """Split permutations into worker files for memory-safe processing."""
    perms = permutations(possible_vals)
    total_perms = math.factorial(len(possible_vals))
    chunk_size = max(total_perms // num_workers, 1)

    print(f"\nSetting up worker files for n={n}...")
    makedirs("Data/Workers", exist_ok=True)
    with Pool(num_workers) as pool:
        pool.starmap(
            write_worker_file, [(i, perms, chunk_size, n) for i in range(num_workers)]
        )


def process_permutations_memory_safe(n, possible_vals, row_indices, col_indices, log_queue, single_solution=False, found_solution=None):
    """Process permutations using memory-safe approach."""
    def generate_permutations():
        for perm in permutations(possible_vals):
            yield perm

    if single_solution:
        with Pool(cpu_count()) as pool:
            results = pool.imap_unordered(
                check_permutation_memory_safe_single,
                (
                    (perm, n, row_indices, col_indices, worker_id, found_solution)
                    for worker_id in range(cpu_count())
                    for perm in generate_permutations()
                ),
                chunksize=1000,
            )

            for result in results:
                if result:
                    canonical_p, h_product, v_product, worker_id = result
                    log_queue.put(f"{canonical_p} {h_product} {v_product}")
                    if found_solution.value:
                        break
    else:
        with Pool(cpu_count()) as pool:
            results = pool.imap_unordered(
                check_permutation_memory_safe,
                (
                    (perm, n, row_indices, col_indices, worker_id)
                    for worker_id in range(cpu_count())
                    for perm in generate_permutations()
                ),
                chunksize=1000,
            )

            for result in results:
                if result:
                    canonical_p, h_product, v_product, worker_id = result
                    log_queue.put(f"{canonical_p} {h_product} {v_product}")


def delete_evaluated_permutation(n, worker_id, perm):
    """Delete evaluated permutation from worker file."""
    worker_file = f"Data/Workers/worker_{n}_{worker_id}.txt"
    with open(worker_file, "r") as f:
        lines = f.readlines()
    with open(worker_file, "w") as f:
        f.writelines(line for line in lines if line.strip() != ",".join(map(str, perm)))


def log_worker(log_queue):
    """Worker process for handling logging."""
    while True:
        data = log_queue.get()
        if data == "DONE":
            break
        # Store solutions for JSON output instead of logging to file
        log_queue.solutions.append(data)


def find_grids_n_optimized(n, single_solution=False, session_file=None):
    """Optimized grid finder that chooses the best approach based on n value."""
    mode = "single solution" if single_solution else "all solutions"
    print(f"\nBegin execution for n = {n} (Mode: {mode})")
    possible_vals = list(range(1, n * n + 1))

    print(f"| Possible values of the grid cells are: {possible_vals}")
    n_start_time = time.time()

    # Choose approach based on n value
    # For n <= 3, use fast in-memory approach
    # For n >= 4, use memory-safe file-based approach
    use_fast_approach = n <= 3
    
    if use_fast_approach:
        print(f"| Using fast in-memory approach for n={n}")
        # Fast approach (like main_P-M.py)
        total_p = math.factorial(n * n)
        print(f"| Total permutations to check: {total_p:,}")
        
        valid_permutations = []
        solutions = []
        
        if single_solution:
            # Single solution mode with early termination
            manager = Manager()
            found_solution = manager.Value("i", False)
            
            with Pool(cpu_count()) as pool:
                results = pool.starmap(
                    check_permutation_fast, 
                    [(p, n, True, found_solution) for p in itertools.permutations(possible_vals)]
                )
                
            for result in results:
                if result:
                    # result is a tuple: (p, h_product, v_product)
                    grid, h_products, v_products = result
                    solution_dict = create_solution_dict(grid, h_products, v_products, n)
                    solutions.append(solution_dict)
                    break  # Stop after first solution
        else:
            # All solutions mode
            with Pool(cpu_count()) as pool:
                results = pool.starmap(
                    check_permutation_fast, 
                    [(p, n, False, None) for p in itertools.permutations(possible_vals)]
                )
                
            for result in results:
                if result:
                    grid, h_products, v_products = result
                    solution_dict = create_solution_dict(grid, h_products, v_products, n)
                    solutions.append(solution_dict)

    else:
        print(f"| Using memory-safe file-based approach for n={n}")
        # Memory-safe approach (like current main.py)
        row_indices, col_indices = memoized_indices_cached(n)
        
        manager = Manager()
        log_queue = manager.Queue()
        log_queue.solutions = []  # Store solutions here
        
        log_process = Pool(1, log_worker, (log_queue,))
        split_permutations_to_files(possible_vals, cpu_count(), n)
        
        if single_solution:
            found_solution = manager.Value("i", False)
            process_permutations_memory_safe(n, possible_vals, row_indices, col_indices, log_queue, True, found_solution)
        else:
            process_permutations_memory_safe(n, possible_vals, row_indices, col_indices, log_queue, False, None)
        
        log_queue.put("DONE")
        log_process.close()
        log_process.join()
        
        # Delete worker files after processing
        for worker_id in range(cpu_count()):
            worker_file = f"Data/Workers/worker_{n}_{worker_id}.txt"
            if path.exists(worker_file):
                remove(worker_file)
        
        # Convert solutions to JSON format
        solutions = []
        for solution_str in log_queue.solutions:
            # Parse the solution string format: "canonical_p h_product v_product"
            parts = solution_str.split(' ', 2)
            if len(parts) == 3:
                canonical_p_str, h_str, v_str = parts
                try:
                    # Convert string representations to actual Python objects
                    grid = eval(canonical_p_str)
                    h_products = eval(h_str)
                    v_products = eval(v_str)
                    solution_dict = create_solution_dict(grid, h_products, v_products, n)
                    solutions.append(solution_dict)
                except (ValueError, SyntaxError) as e:
                    print(f"Warning: Could not parse solution string: {solution_str}")
                    print(f"Error: {e}")
                    continue

    execution_time = time.time() - n_start_time
    
    # Don't save JSON output here if using session file
    if not session_file:
        save_json_output(n, solutions, execution_time)
    
    print(f"\nFinished executing for: {n}, Execution Time: {format_time(execution_time)}")
    return {"n": n, "solutions": solutions, "execution_time": format_time(execution_time)}


# Example usage
if __name__ == "__main__":
    print(
        "This programme executes the optimized grid finder from 1 up to a maximum 'n' of your choice..."
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
    
    # Get session file for this execution
    session_file = get_session_file()
    all_results = []

    if n_max < 0:
        print("\nInvalid value provided. Must be a natural number")

    elif n_max == 0:
        grid_size = 1
        while True:
            try:
                result = find_grids_n_optimized(grid_size, single_solution, session_file)
                if result:
                    all_results.append(result)
                grid_size += 1
            except KeyboardInterrupt:
                print("\nExecution interrupted by user.")
                break

    elif n_max > 0:
        try:
            for grid_size in range(1, n_max + 1):
                result = find_grids_n_optimized(grid_size, single_solution, session_file)
                if result:
                    all_results.append(result)
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")

    # Save all results to the session file
    if all_results:
        total_execution_time = time.time() - main_start_time
        save_json_output("multiple", all_results, total_execution_time, session_file)
    
    print(f"\n\nTotal Execution Time: {format_time(time.time() - main_start_time)}") 