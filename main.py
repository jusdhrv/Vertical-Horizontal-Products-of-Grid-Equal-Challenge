from itertools import permutations, chain
from math import factorial
from time import time, strftime, gmtime
from os import listdir, path
from multiprocessing import Pool, cpu_count

def list_multiple(lst):
    product = 1
    for i in lst:
        product *= i
    return product

def memoized_indices(n):
    start_indices = [j * n for j in range(n)]
    end_indices = [start_index + n for start_index in start_indices]
    row_indices = [
        list(range(start, end)) for start, end in zip(start_indices, end_indices)
    ]
    col_indices = [[l + m * n for m in range(n)] for l in range(n)]
    return row_indices, col_indices

def get_next_log_file():
    log_dir = "Data"
    log_suffix = "-logs.txt"
    existing_logs = [f for f in listdir(log_dir) if f.endswith(log_suffix)]

    if not existing_logs:
        return path.join(log_dir, f"1{log_suffix}")

    log_numbers = [int(f[: -len(log_suffix)]) for f in existing_logs]
    latest_log_number = max(log_numbers, default=0)
    latest_log_file = path.join(log_dir, f"{latest_log_number}{log_suffix}")

    # Check if the latest log file ends with '&end&'
    with open(latest_log_file, "r") as file:
        lines = file.readlines()
        if lines and lines[-1].strip() == "&end&":
            next_log_number = latest_log_number + 1
            return path.join(log_dir, f"{next_log_number}{log_suffix}")
        else:
            return latest_log_file

def log_append(data):
    log_file_path = get_next_log_file()
    with open(log_file_path, "a") as file1:
        file1.write(data + "\n")

def canonical_form(grid, n):
    grid = [grid[i : i + n] for i in range(0, len(grid), n)]
    grid = sorted(grid)
    grid = list(zip(*grid))
    grid = sorted(grid)
    grid = list(zip(*grid))
    return tuple(chain(*grid))

def heuristic_permutation_generator(possible_vals, n):
    for p in permutations(possible_vals):
        yield p

def check_permutation(args):
    p, n, row_indices, col_indices, total_p, p_count, start_time = args
    if (p_count % 100000) == 0:
        elapsed_time = format_time(time() - start_time)
        print(
            f"|  Permutation #{p_count} of {total_p} ({round((p_count/total_p)*100, 2)} %) for n={n} ... ({elapsed_time})"
        )
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        return [(canonical_p, h_product, v_product)]
    return []

def find_grids_n(n):
    log_append(f"For, n = {n}")
    possible_vals = list(range(1, n * n + 1))

    log_append(f"Possible values of the grid cells are: {possible_vals}\n")
    n_start_time = time()

    total_p = factorial(n * n)
    p_count = 1

    row_indices, col_indices = memoized_indices(n)

    with Pool(cpu_count()) as pool:
        results = pool.imap_unordered(
            check_permutation,
            (
                (p, n, row_indices, col_indices, total_p, p_count, n_start_time)
                for p in heuristic_permutation_generator(possible_vals, n)
            ),
            chunksize=1000,
        )

        log_data = []
        for result in results:
            for perm, h_product, v_product in result:
                log_data.append(f"{perm} {h_product} {v_product}")
                if len(log_data) >= 1000:
                    log_append("\n".join(log_data))
                    log_data = []

        if log_data:
            log_append("\n".join(log_data))

    log_append(f"\nExecution Time: {format_time(time() - n_start_time)}")
    log_append("\n---\n")
    print(
        f"\nFinished executing for: {n}, Execution Time: {format_time(time() - n_start_time)}"
    )

def format_time(seconds):
    return strftime("%H:%M:%S", gmtime(seconds))


if __name__ == "__main__":
    print(
        "This programme executes the possible grid finder from 1 up to a maximum 'n' of your choice..."
    )
    n_max = int(input("Enter the value for 'n' to use: "))
    main_start_time = time()

    if n_max < 0:
        print("\nInvalid value provided. Must be a natural number")

    elif n_max == 0:
        grid_size = 1
        while True:
            try:
                find_grids_n(grid_size)
                grid_size += 1
            except KeyboardInterrupt:
                print("\nExecution interrupted by user.")
                break

    elif n_max > 0:
        try:
            for grid_size in range(1, n_max + 1):
                find_grids_n(grid_size)
        except KeyboardInterrupt:
            print("\nExecution interrupted by user.")

    print(f"\n\nTotal Execution Time: {format_time(time() - main_start_time)}")
    log_append("&end&")