import itertools
import math
import time
from multiprocessing import Pool, cpu_count, current_process

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


def log_append(data):
    with open("logs.txt", "a") as file1:
        file1.write(data + "\n")


def generate_equivalent_permutations(grid, n):
    # Generate all equivalent permutations by rotating and shifting rows and columns
    grids = set()
    grid = [grid[i : i + n] for i in range(0, len(grid), n)]

    # Add original grid
    grids.add(tuple(itertools.chain(*grid)))

    # Add rotated grids
    for _ in range(3):
        grid = list(zip(*grid[::-1]))  # Rotate 90 degrees
        grids.add(tuple(itertools.chain(*grid)))

    # Add row and column shifts
    for g in list(grids):
        grid = [list(g[i : i + n]) for i in range(0, len(g), n)]
        for _ in range(n):
            grid = grid[1:] + grid[:1]  # Shift rows
            grids.add(tuple(itertools.chain(*grid)))
        for _ in range(n):
            grid = list(zip(*grid))  # Transpose to shift columns
            grid = grid[1:] + grid[:1]
            grid = list(zip(*grid))  # Transpose back
            grids.add(tuple(itertools.chain(*grid)))

    return grids


def canonical_form(grid, n):
    # Convert grid to canonical form by sorting rows and columns
    grid = [grid[i : i + n] for i in range(0, len(grid), n)]
    grid = sorted(grid)
    grid = list(zip(*grid))  # Transpose to sort columns
    grid = sorted(grid)
    grid = list(zip(*grid))  # Transpose back
    return tuple(itertools.chain(*grid))


def check_permutation(args):
    p, n, total_p, p_count = args
    if (p_count % 100000) == 0:  # Print every 100,000 permutations verified
        worker_id = current_process().name
        print(
            f"|  Permutation #{p_count} of {total_p} ({round((p_count/total_p)*100, 2)} %) for n={n} ... [{str(worker_id)[16:]}]"
        )

    row_indices, col_indices = memoized_indices(n)
    h_product = [memoized_list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [memoized_list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        equivalent_permutations = generate_equivalent_permutations(p, n)
        return equivalent_permutations
    return None


def find_grids_n(n):
    log_append("For, n = " + str(n))
    possible_vals = list(range(1, n * n + 1))

    log_append("Possible values of the grid cells are: " + str(possible_vals) + "\n")
    n_start_time = time.time()

    total_p = math.factorial(n * n)
    p_count = 1

    valid_permutations = set()

    def permutation_generator():
        for i, p in enumerate(itertools.permutations(possible_vals)):
            canonical_p = canonical_form(p, n)
            if canonical_p not in valid_permutations:
                valid_permutations.add(canonical_p)
                yield (p, n, total_p, p_count + i)

    with Pool(cpu_count()) as pool:
        results = pool.imap_unordered(
            check_permutation, permutation_generator(), chunksize=1000
        )

        for result in results:
            if result:
                for perm in result:
                    log_append(str(perm))

    log_append("\nExecution Time: " + str(format_time(time.time() - n_start_time)))
    log_append("\n---\n")
    print(
        "\nFinished executing for:",
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
            "\n\nTotal Execution Time: "
            + str(format_time(time.time() - main_start_time))
        )

    except ValueError:
        print("\nInvalid input. Please enter a valid integer.")
