from itertools import permutations, chain, islice
from time import time
from os import remove, makedirs, path
from multiprocessing import Pool, cpu_count, Manager, Value, Process
from math import factorial
from modules import (
    canonical_form, format_time, save_json_output, create_solution_dict,
    parse_solution_string, list_multiple, memoized_indices, get_session_file
)


def check_permutation_all(args):
    """Check permutation for all solutions mode."""
    p, n, row_indices, col_indices, worker_id = args
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        return canonical_p, h_product, v_product, worker_id
    return None


def check_permutation_single(args):
    """Check permutation for single solution mode."""
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


def chunked_permutations(possible_vals, num_chunks):
    """Yield num_chunks chunks of permutations of possible_vals."""
    perms = permutations(possible_vals)
    total_perms = factorial(len(possible_vals))
    chunk_size = max(total_perms // num_chunks, 1)
    for _ in range(num_chunks):
        yield list(islice(perms, chunk_size))


def process_permutations_all(n, possible_vals, row_indices, col_indices, log_queue):
    """Process permutations for all solutions mode using in-memory chunking."""
    num_workers = cpu_count()
    chunks = list(chunked_permutations(possible_vals, num_workers))

    def worker(chunk, n, row_indices, col_indices, worker_id, log_queue):
        for perm in chunk:
            h_product = [list_multiple([perm[idx] for idx in row]) for row in row_indices]
            v_product = [list_multiple([perm[idx] for idx in col]) for col in col_indices]
            if set(h_product) == set(v_product):
                canonical_p = canonical_form(perm, n)
                log_queue.put(f"{canonical_p} {h_product} {v_product}")

    processes = []
    for worker_id, chunk in enumerate(chunks):
        p = Process(target=worker, args=(chunk, n, row_indices, col_indices, worker_id, log_queue))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


def process_permutations_single(n, possible_vals, row_indices, col_indices, log_queue, found_solution):
    """Process permutations for single solution mode using in-memory chunking."""
    num_workers = cpu_count()
    chunks = list(chunked_permutations(possible_vals, num_workers))

    def worker(chunk, n, row_indices, col_indices, worker_id, found_solution, log_queue):
        for perm in chunk:
            if found_solution.value:
                break
            h_product = [list_multiple([perm[idx] for idx in row]) for row in row_indices]
            v_product = [list_multiple([perm[idx] for idx in col]) for col in col_indices]
            if set(h_product) == set(v_product):
                canonical_p = canonical_form(perm, n)
                found_solution.value = True
                log_queue.put(f"{canonical_p} {h_product} {v_product}")

    processes = []
    for worker_id, chunk in enumerate(chunks):
        p = Process(target=worker, args=(chunk, n, row_indices, col_indices, worker_id, found_solution, log_queue))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


def log_worker(log_queue):
    while True:
        data = log_queue.get()
        if data == "DONE":
            break
        # Store solutions for JSON output instead of logging to file
        log_queue.solutions.append(data)


def find_grids_n(n, single_solution=False, session_file=None):
    """Find grid solutions for given n, with option to find single or all solutions."""
    mode = "single solution" if single_solution else "all solutions"
    print(f"\nBegin execution for n = {n} (Mode: {mode})")
    possible_vals = list(range(1, n * n + 1))

    print(f"| Possible values of the grid cells are: {possible_vals}")
    n_start_time = time()

    row_indices, col_indices = memoized_indices(n)

    manager = Manager()
    log_queue = manager.Queue()
    log_queue.solutions = []  # Store solutions here

    log_process = Pool(1, log_worker, (log_queue,))
    
    if single_solution:
        found_solution = manager.Value("i", False)
        process_permutations_single(n, possible_vals, row_indices, col_indices, log_queue, found_solution)
    else:
        process_permutations_all(n, possible_vals, row_indices, col_indices, log_queue)

    log_queue.put("DONE")
    log_process.close()
    log_process.join()

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

    execution_time = time() - n_start_time
    
    # Don't save JSON output here if using session file
    if not session_file:
        save_json_output(n, solutions, execution_time)
    
    print(f"\nFinished executing for: {n}, Execution Time: {format_time(execution_time)}")
    return {"n": n, "solutions": solutions, "execution_time": format_time(execution_time)}


# Example usage
if __name__ == "__main__":
    print(
        "This programme executes the memory-safe grid finder from 1 up to a maximum 'n' of your choice..."
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
    
    main_start_time = time()
    
    # Get session file for this execution
    session_file = get_session_file()
    all_results = []

    if n_max < 0:
        print("\nInvalid value provided. Must be a natural number")

    elif n_max == 0:
        grid_size = 1
        while True:
            try:
                result = find_grids_n(grid_size, single_solution, session_file)
                if result:
                    all_results.append(result)
                grid_size += 1
            except KeyboardInterrupt:
                print("\nExecution interrupted by user.")
                break

    elif n_max > 0:
        try:
            for grid_size in range(1, n_max + 1):
                result = find_grids_n(grid_size, single_solution, session_file)
                if result:
                    all_results.append(result)
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")

    # Save all results to the session file
    if all_results:
        total_execution_time = time() - main_start_time
        save_json_output("multiple", all_results, total_execution_time, session_file)
    
    print(f"\n\nTotal Execution Time: {format_time(time() - main_start_time)}") 