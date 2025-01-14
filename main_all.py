from itertools import permutations, chain, islice
from time import time, strftime, gmtime
from os import listdir, path, remove, makedirs
from multiprocessing import Pool, cpu_count, Manager
from math import factorial


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


def check_permutation(args):
    p, n, row_indices, col_indices, worker_id = args
    h_product = [list_multiple([p[idx] for idx in row]) for row in row_indices]
    v_product = [list_multiple([p[idx] for idx in col]) for col in col_indices]

    if set(h_product) == set(v_product):
        canonical_p = canonical_form(p, n)
        return canonical_p, h_product, v_product, worker_id
    return None


def write_worker_file(worker_id, perms, chunk_size, n):
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
    perms = permutations(possible_vals)
    total_perms = factorial(len(possible_vals))
    chunk_size = total_perms // num_workers

    print(f"\nSetting up worker files for n={n}...")
    makedirs("Data/Workers", exist_ok=True)
    with Pool(num_workers) as pool:
        pool.starmap(
            write_worker_file, [(i, perms, chunk_size, n) for i in range(num_workers)]
        )


def process_permutations(n, possible_vals, row_indices, col_indices, log_queue):
    def generate_permutations():
        for perm in permutations(possible_vals):
            yield perm

    with Pool(cpu_count()) as pool:
        results = pool.imap_unordered(
            check_permutation,
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
                delete_evaluated_permutation(n, worker_id, canonical_p)


def delete_evaluated_permutation(n, worker_id, perm):
    worker_file = f"Data/Workers/worker_{n}_{worker_id}.txt"
    with open(worker_file, "r") as f:
        lines = f.readlines()
    with open(worker_file, "w") as f:
        f.writelines(line for line in lines if line.strip() != ",".join(map(str, perm)))


def log_worker(log_queue):
    while True:
        data = log_queue.get()
        if data == "DONE":
            break
        log_append(data)


def find_grids_n(n):
    log_append(f"For, n = {n}")
    print(f"\nBegin execution for n = {n}")
    possible_vals = list(range(1, n * n + 1))

    log_append(f"| Possible values of the grid cells are: {possible_vals}\n")
    print(f"| Possible values of the grid cells are: {possible_vals}")
    n_start_time = time()

    row_indices, col_indices = memoized_indices(n)

    manager = Manager()
    log_queue = manager.Queue()

    log_process = Pool(1, log_worker, (log_queue,))
    split_permutations_to_files(possible_vals, cpu_count(), n)
    process_permutations(n, possible_vals, row_indices, col_indices, log_queue)

    log_queue.put("DONE")
    log_process.close()
    log_process.join()

    # Delete worker files after processing
    for worker_id in range(cpu_count()):
        worker_file = f"Data/Workers/worker_{n}_{worker_id}.txt"
        if path.exists(worker_file):
            remove(worker_file)

    log_append(f"\nExecution Time: {format_time(time() - n_start_time)}")
    log_append("\n---\n")
    print(
        f"\nFinished executing for: {n}, Execution Time: {format_time(time() - n_start_time)}"
    )


def format_time(seconds):
    return strftime("%H:%M:%S", gmtime(seconds))


# Example usage
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
