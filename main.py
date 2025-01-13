import itertools
import math
import time
import pickle
import numpy as np
from multiprocessing import Pool, cpu_count, current_process

memo = {}
index_memo = {}
dp_memo = {}
processed_permutations = set()


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
    with open("Data/logs.txt", "a") as file1:
        file1.write(data + "\n")


def generate_equivalent_permutations(grid, n):
    grids = set()
    grid = [grid[i : i + n] for i in range(0, len(grid), n)]
    grids.add(tuple(itertools.chain(*grid)))
    for _ in range(3):
        grid = list(zip(*grid[::-1]))
        grids.add(tuple(itertools.chain(*grid)))
    for g in list(grids):
        grid = [list(g[i : i + n]) for i in range(0, len(g), n)]
        for _ in range(n):
            grid = grid[1:] + grid[:1]
            grids.add(tuple(itertools.chain(*grid)))
        for _ in range(n):
            grid = list(zip(*grid))
            grid = grid[1:] + grid[:1]
            grid = list(zip(*grid))
            grids.add(tuple(itertools.chain(*grid)))
    return grids


def canonical_form(grid, n):
    grid = [grid[i : i + n] for i in range(0, len(grid), n)]
    grid = sorted(grid)
    grid = list(zip(*grid))
    grid = sorted(grid)
    grid = list(zip(*grid))
    return tuple(itertools.chain(*grid))


def dp_product(indices, p):
    key = tuple(indices)
    if key not in dp_memo:
        dp_memo[key] = list_multiple([p[idx] for idx in indices])
    return dp_memo[key]


def is_prime(num):
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True


def primes_with_odd_powers(n):
    primes = [i for i in range(2, n * n + 1) if is_prime(i)]
    odd_power_primes = [p for p in primes if p % 2 != 0]
    return odd_power_primes


def check_odd_power_prime_placement(p, n):
    odd_power_primes = primes_with_odd_powers(n)
    row_indices, col_indices = memoized_indices(n)
    for prime in odd_power_primes:
        positions = [i for i, x in enumerate(p) if x == prime]
        for pos in positions:
            row = pos // n
            col = pos % n
            row_product = memoized_list_multiple(
                [p[idx] for idx in row_indices[row] if idx != pos]
            )
            col_product = memoized_list_multiple(
                [p[idx] for idx in col_indices[col] if idx != pos]
            )
            if row_product != col_product:
                return False
    return True


def check_permutation(args):
    p, n, total_p, p_count = args
    if (p_count % 100000) == 0:
        worker_id = current_process().name
        print(
            f"|  Permutation #{p_count} of {total_p} ({round((p_count/total_p)*100, 2)} %) for n={n} ... [{str(worker_id)[16:]}]"
        )

    if not check_odd_power_prime_placement(p, n):
        return None

    row_indices, col_indices = memoized_indices(n)
    h_product = [dp_product(row, p) for row in row_indices]
    v_product = [dp_product(col, p) for col in col_indices]

    if set(h_product) == set(v_product):
        equivalent_permutations = generate_equivalent_permutations(p, n)
        return equivalent_permutations
    return None


def prune_permutations(permutations, n):
    pruned_permutations = []
    for p in permutations:
        row_indices, col_indices = memoized_indices(n)
        h_product = [dp_product(row, p) for row in row_indices]
        v_product = [dp_product(col, p) for col in col_indices]
        if set(h_product) == set(v_product):
            pruned_permutations.append(p)
    return pruned_permutations


def heuristic_permutation_generator(possible_vals, n):
    odd_power_primes = primes_with_odd_powers(n)
    for p in itertools.permutations(possible_vals):
        canonical_p = canonical_form(p, n)
        if canonical_p not in processed_permutations:
            processed_permutations.add(canonical_p)
            yield p


def branch_and_bound(p, n, row_indices, col_indices):
    h_product = [dp_product(row, p) for row in row_indices]
    v_product = [dp_product(col, p) for col in col_indices]
    return set(h_product) == set(v_product)


def incremental_search(p, n, row_indices, col_indices, depth=0):
    if depth == n:
        return branch_and_bound(p, n, row_indices, col_indices)
    for i in range(depth, n):
        p[depth], p[i] = p[i], p[depth]
        if incremental_search(p, n, row_indices, col_indices, depth + 1):
            return True
        p[depth], p[i] = p[i], p[depth]
    return False


def find_grids_n(n):
    log_append(f"For, n = {n}")
    possible_vals = list(range(1, n * n + 1))

    log_append(f"Possible values of the grid cells are: {possible_vals}\n")
    n_start_time = time.time()

    total_p = math.factorial(n * n)
    p_count = 1

    valid_permutations = set()

    def permutation_generator():
        for i, p in enumerate(heuristic_permutation_generator(possible_vals, n)):
            canonical_p = canonical_form(p, n)
            if canonical_p not in processed_permutations:
                processed_permutations.add(canonical_p)
                yield (p, n, total_p, p_count + i)

    row_indices, col_indices = memoized_indices(n)
    with Pool(cpu_count()) as pool:
        results = pool.imap_unordered(
            check_permutation, permutation_generator(), chunksize=1000
        )

        for result in results:
            if result:
                for perm in result:
                    log_append(str(perm))

    log_append(f"\nExecution Time: {format_time(time.time() - n_start_time)}")
    log_append("\n---\n")
    print(
        f"\nFinished executing for: {n}, Execution Time: {format_time(time.time() - n_start_time)}"
    )


def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def save_memoized_data():
    with open("Data/memo_data.pkl", "wb") as f:
        pickle.dump((memo, index_memo, dp_memo, processed_permutations), f)


def load_memoized_data():
    global memo, index_memo, dp_memo, processed_permutations
    try:
        with open("Data/memo_data.pkl", "rb") as f:
            memo, index_memo, dp_memo, processed_permutations = pickle.load(f)
    except FileNotFoundError:
        pass


# Example usage
if __name__ == "__main__":
    try:
        load_memoized_data()
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

        print(f"\n\nTotal Execution Time: {format_time(time.time() - main_start_time)}")

    except ValueError:
        print("\nInvalid input. Please enter a valid integer.")
    finally:
        save_memoized_data()
