import itertools
import math
import time
from multiprocessing import Pool, cpu_count, Manager, Value, Process
from os import remove, makedirs, path
from itertools import permutations, chain, islice
from modules import (
    canonical_form, format_time, save_json_output, create_solution_dict,
    parse_solution_string, list_multiple, memoized_indices, get_session_file
)

# Memoization dictionaries for performance
memo = {}
index_memo = {}

def progress_monitor(total, counter, start_time, stop_flag):
    """Print progress and ETA every second until stop_flag is set."""
    while not stop_flag.value:
        checked = counter.value
        percent = (checked / total) * 100 if total else 0
        elapsed = time.time() - start_time
        eta = (elapsed / checked * (total - checked)) if checked else 0
        print(f"\rProgress: {checked:,}/{total:,} ({percent:.2f}%) | Elapsed: {format_time(elapsed)} | ETA: {format_time(eta)}", end="", flush=True)
        time.sleep(1)
    # Print final state
    checked = counter.value
    percent = (checked / total) * 100 if total else 0
    elapsed = time.time() - start_time
    print(f"\rProgress: {checked:,}/{total:,} ({percent:.2f}%) | Elapsed: {format_time(elapsed)} | ETA: 00:00:00", flush=True)

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


def check_permutation_fast(p, n, single_solution=False, found_solution=None, progress_counter=None):
    """Fast permutation checker using memoization (for smaller n values)."""
    if single_solution and found_solution and found_solution.value:
        return None
    row_indices, col_indices = memoized_indices_cached(n)
    h_product = [memoized_list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [memoized_list_multiple([p[idx] for idx in col]) for col in col_indices]
    if progress_counter is not None:
        progress_counter.value += 1
    if set(h_product) == set(v_product):
        if single_solution and found_solution:
            found_solution.value = True
        return (p, h_product, v_product)
    return None


def check_permutation_memory_safe(args):
    """Memory-safe permutation checker for larger n values."""
    p, n, row_indices, col_indices, worker_id, progress_counter = args
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]
    if progress_counter is not None:
        progress_counter.value += 1
    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        return canonical_p, h_product, v_product, worker_id
def check_permutation_memory_safe_single(args):
    """Memory-safe permutation checker for single solution mode."""
    p, n, row_indices, col_indices, worker_id, found_solution, progress_counter = args
    if found_solution.value:
        return None
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]
    if progress_counter is not None:
        progress_counter.value += 1
    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        found_solution.value = True
        return canonical_p, h_product, v_product, worker_id
    return None


def chunked_permutations(possible_vals, num_chunks):
    """Yield num_chunks chunks of permutations of possible_vals."""
    perms = permutations(possible_vals)
    total_perms = math.factorial(len(possible_vals))
    chunk_size = max(total_perms // num_chunks, 1)
    for _ in range(num_chunks):
        yield list(islice(perms, chunk_size))


def process_permutations_memory_safe(n, possible_vals, row_indices, col_indices, log_queue, progress_counter, single_solution=False, found_solution=None):
    """Process permutations using memory-safe approach with in-memory chunking."""
    num_workers = cpu_count()
    chunks = list(chunked_permutations(possible_vals, num_workers))
    def worker(chunk, n, row_indices, col_indices, worker_id, single_solution, found_solution, log_queue, progress_counter):
        for perm in chunk:
            if single_solution and found_solution and found_solution.value:
                break
            h_product = [list_multiple([perm[idx] for idx in row]) for row in row_indices]
            v_product = [list_multiple([perm[idx] for idx in col]) for col in col_indices]
            progress_counter.value += 1
            if set(h_product) == set(v_product):
                canonical_p = canonical_form(perm, n)
                if single_solution and found_solution:
                    found_solution.value = True
                log_queue.put(f"{canonical_p} {h_product} {v_product}")
    processes = []
    for worker_id, chunk in enumerate(chunks):
        p = Process(target=worker, args=(chunk, n, row_indices, col_indices, worker_id, single_solution, found_solution, log_queue, progress_counter))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


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
    use_fast_approach = n <= 3
    total_p = math.factorial(n * n)
    progress_manager = Manager()
    progress_counter = progress_manager.Value('i', 0)
    stop_flag = progress_manager.Value('i', 0)
    progress_proc = Process(target=progress_monitor, args=(total_p, progress_counter, n_start_time, stop_flag))
    progress_proc.start()
    if use_fast_approach:
        print(f"| Using fast in-memory approach for n={n}")
        solutions = []
        if single_solution:
            manager = Manager()
            found_solution = manager.Value("i", False)
            with Pool(cpu_count()) as pool:
                results = pool.starmap(
                    check_permutation_fast, 
                    [(p, n, True, found_solution, progress_counter) for p in itertools.permutations(possible_vals)]
                )
            for result in results:
                if result:
                    grid, h_products, v_products = result
                    solution_dict = create_solution_dict(grid, h_products, v_products, n)
                    solutions.append(solution_dict)
                    break
        else:
            with Pool(cpu_count()) as pool:
                results = pool.starmap(
                    check_permutation_fast, 
                    [(p, n, False, None, progress_counter) for p in itertools.permutations(possible_vals)]
                )
            for result in results:
                if result:
                    grid, h_products, v_products = result
                    solution_dict = create_solution_dict(grid, h_products, v_products, n)
                    solutions.append(solution_dict)
    else:
        print(f"| Using memory-safe file-based approach for n={n}")
        row_indices, col_indices = memoized_indices_cached(n)
        manager = Manager()
        log_queue = manager.Queue()
        log_queue.solutions = []
        log_process = Pool(1, log_worker, (log_queue,))
        if single_solution:
            found_solution = manager.Value("i", False)
            process_permutations_memory_safe(n, possible_vals, row_indices, col_indices, log_queue, progress_counter, True, found_solution)
        else:
            process_permutations_memory_safe(n, possible_vals, row_indices, col_indices, log_queue, progress_counter, False, None)
        log_queue.put("DONE")
        log_process.close()
        log_process.join()
        solutions = []
        for solution_str in log_queue.solutions:
            parts = solution_str.split(' ', 2)
            if len(parts) == 3:
                canonical_p_str, h_str, v_str = parts
                try:
                    grid = eval(canonical_p_str)
                    h_products = eval(h_str)
                    v_products = eval(v_str)
                    solution_dict = create_solution_dict(grid, h_products, v_products, n)
                    solutions.append(solution_dict)
                except (ValueError, SyntaxError) as e:
                    print(f"Warning: Could not parse solution string: {solution_str}")
                    print(f"Error: {e}")
                    continue
    stop_flag.value = 1
    progress_proc.join()
    execution_time = time.time() - n_start_time
    if not session_file:
        save_json_output(n, solutions, execution_time)
    print(f"\nFinished executing for: {n}, Execution Time: {format_time(execution_time)}")
    print(f"Total permutations checked: {progress_counter.value:,}")
    if progress_counter.value > 0:
        print(f"Average time per permutation: {execution_time / progress_counter.value:.6f} seconds")
    return {"n": n, "solutions": solutions, "execution_time": format_time(execution_time)}


# Example usage
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) >= 1:
        try:
            n_max = int(args[0])
        except Exception:
            n_max = None
    else:
        n_max = None
    if len(args) >= 2:
        mode_choice = args[1]
        if mode_choice.lower() in ["all", "1"]:
            single_solution = False
        elif mode_choice.lower() in ["single", "2"]:
            single_solution = True
        else:
            single_solution = False
    else:
        mode_choice = None
        single_solution = None

    print(
        "This programme executes the optimized grid finder from 1 up to a maximum 'n' of your choice..."
    )
    if n_max is None:
        n_max = int(input("Enter the value for 'n' to use: "))
    if single_solution is None:
        print("\nChoose execution mode:")
        print("1. Find all possible solutions")
        print("2. Find single solution (stop after first)")
        mode_choice = input("Enter your choice (1 or 2): ").strip()
        single_solution = mode_choice == "2"
    mode_str = "single solution" if single_solution else "all solutions"
    print(f"\nSelected mode: {mode_str}")
    main_start_time = time.time()
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
    if all_results:
        total_execution_time = time.time() - main_start_time
        save_json_output("multiple", all_results, total_execution_time, session_file)
    print(f"\n\nTotal Execution Time: {format_time(time.time() - main_start_time)}") 