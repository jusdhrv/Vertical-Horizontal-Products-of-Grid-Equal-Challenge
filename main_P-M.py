import itertools
import math
import time
from multiprocessing import Pool, cpu_count, Manager, Value, Process
from modules import (
    canonical_form, format_time, save_json_output, create_solution_dict,
    parse_solution_string, list_multiple, memoized_indices, get_session_file
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


def progress_monitor(total, counter, start_time, stop_flag):
    while not stop_flag.value:
        checked = counter.value
        percent = (checked / total) * 100 if total else 0
        elapsed = time.time() - start_time
        eta = (elapsed / checked * (total - checked)) if checked else 0
        print(f"\rProgress: {checked:,}/{total:,} ({percent:.2f}%) | Elapsed: {format_time(elapsed)} | ETA: {format_time(eta)}", end="", flush=True)
        time.sleep(1)
    checked = counter.value
    percent = (checked / total) * 100 if total else 0
    elapsed = time.time() - start_time
    print(f"\rProgress: {checked:,}/{total:,} ({percent:.2f}%) | Elapsed: {format_time(elapsed)} | ETA: 00:00:00", flush=True)


def check_permutation(p, n, single_solution=False, found_solution=None, progress_counter=None):
    if single_solution and found_solution and found_solution.value:
        return None
        
    row_indices, col_indices = memoized_indices(n)
    h_product = [memoized_list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [memoized_list_multiple([p[idx] for idx in col]) for col in col_indices]

    if progress_counter is not None:
        progress_counter.value += 1

    if set(h_product) == set(v_product):
        if single_solution and found_solution:
            found_solution.value = True
        return (p, h_product, v_product)
    return None


def find_grids_n(n, single_solution=False, session_file=None):
    mode = "single solution" if single_solution else "all solutions"
    print(f"\nBegin execution for n = {n} (Mode: {mode})")
    possible_vals = list(range(1, n * n + 1))

    print(f"| Possible values of the grid cells are: {possible_vals}")
    n_start_time = time.time()

    total_p = math.factorial(n * n)
    print(f"| Total permutations to check: {total_p:,}")

    progress_manager = Manager()
    progress_counter = progress_manager.Value('i', 0)
    stop_flag = progress_manager.Value('i', 0)
    progress_proc = Process(target=progress_monitor, args=(total_p, progress_counter, n_start_time, stop_flag))
    progress_proc.start()

    solutions = []

    if single_solution:
        # Single solution mode with early termination
        manager = Manager()
        found_solution = manager.Value("i", False)
        
        with Pool(cpu_count()) as pool:
            results = pool.starmap(
                check_permutation, 
                [(p, n, True, found_solution, progress_counter) for p in itertools.permutations(possible_vals)]
            )
            
        for result in results:
            if result:
                grid, h_products, v_products = result
                solution_dict = create_solution_dict(grid, h_products, v_products, n)
                solutions.append(solution_dict)
                break  # Stop after first solution
    else:
        # All solutions mode
        with Pool(cpu_count()) as pool:
            results = pool.starmap(
                check_permutation, 
                [(p, n, False, None, progress_counter) for p in itertools.permutations(possible_vals)]
            )
            
        for result in results:
            if result:
                grid, h_products, v_products = result
                solution_dict = create_solution_dict(grid, h_products, v_products, n)
                solutions.append(solution_dict)

    stop_flag.value = 1
    progress_proc.join()
    
    execution_time = time.time() - n_start_time
    
    # Don't save JSON output here if using session file
    if not session_file:
        save_json_output(n, solutions, execution_time)
    
    print(f"\nFinished executing for: {n}, Execution Time: {format_time(execution_time)}")
    print(f"Total permutations checked: {progress_counter.value:,}")
    if progress_counter.value > 0:
        print(f"Average time per permutation: {execution_time / progress_counter.value:.6f} seconds")
    return {"n": n, "solutions": solutions, "execution_time": format_time(execution_time)}


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
        total_execution_time = time.time() - main_start_time
        save_json_output("multiple", all_results, total_execution_time, session_file)
    
    print(f"\n\nTotal Execution Time: {format_time(time.time() - main_start_time)}")
