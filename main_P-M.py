import itertools
import math
import time
from multiprocessing import Pool, cpu_count
from os import listdir, path

# Memoization dictionaries
memo = {}
index_memo = {}


def list_multiple(lst):
    product = 1
    for i in lst:
        product *= i
    return product


def memoized_list_multiple(sublist):
    key = tuple(sublist)
    if key not in memo:
        memo[key] = list_multiple(sublist)
    return memo[key]


def memoized_indices(n):
    if n not in index_memo:
        start_indices = [j * n for j in range(n)]
        end_indices = [start_index + n for start_index in start_indices]
        row_indices = [
            list(range(start, end)) for start, end in zip(start_indices, end_indices)
        ]
        col_indices = [[l + m * n for m in range(n)] for l in range(n)]
        index_memo[n] = (row_indices, col_indices)
    return index_memo[n]


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


def check_permutation(p, n):
    row_indices, col_indices = memoized_indices(n)
    h_product = [memoized_list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [memoized_list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        return str(p) + " " + str(h_product) + " " + str(v_product)
    return None


def find_grids_n(n):
    log_append("For, n = " + str(n))
    possible_vals = list(range(1, n * n + 1))

    log_append("Possible values of the grid cells are: " + str(possible_vals) + "\n")
    n_start_time = time.time()

    total_p = math.factorial(n * n)
    p_count = 1

    valid_permutations = []

    with Pool(cpu_count()) as pool:
        results = pool.starmap(
            check_permutation, [(p, n) for p in itertools.permutations(possible_vals)]
        )

    for result in results:
        if result:
            valid_permutations.append(result)

    for valid_permutation in valid_permutations:
        log_append(valid_permutation)

    log_append("\nExecution Time: " + str(format_time(time.time() - n_start_time)))
    log_append("\n---\n")
    print(
        "Finished executing for:",
        n,
        ", Execution Time: " + str(format_time(time.time() - n_start_time)),
    )


def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


# Example usage
if __name__ == "__main__":
    try:
        print(
            "This programme executes the possible grid finder from 1 up to a maximum 'n' of your choice..."
        )
        n_max = int(input("Enter the value for 'n' to use: "))
        main_start_time = time.time()

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

        print(
            "Total Execution Time: " + str(format_time(time.time() - main_start_time))
        )

    except ValueError:
        print("\nInvalid input. Please enter a valid integer.")
