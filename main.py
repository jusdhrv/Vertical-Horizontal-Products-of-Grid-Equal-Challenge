import math, time
from datetime import timedelta


def format_time(sec):
    td = timedelta(seconds=sec)
    return td


def permutation(lst):
    if len(lst) == 0:
        return []
    if len(lst) == 1:
        return [lst]
    l = []
    for i in range(len(lst)):
        m = lst[i]
        remLst = lst[:i] + lst[i + 1 :]
        for p in permutation(remLst):
            l.append([m] + p)
    return l


def list_multiple(lst):
    product = 1
    for i in lst:
        product *= i
    return product


def cleanup(lst):
    lst1 = list(set(lst))
    lst2 = sorted(lst1)

    return lst2


def log_append(data):
    file1 = open("logs.txt", "a")
    file1.write(data)
    file1.write("\n")
    file1.close()


def find_grids_n(n):
    log_append("For, n = " + str(n))
    possible_vals = []
    for i in range(n * n):
        possible_vals.append(int(i + 1))

    log_append("Possible values of the grid cells are: " + str(possible_vals) + "\n")
    n_start_time = time.time()

    start_indices = []
    end_indices = []
    for j in range(0, n):
        start_index = j * n
        end_index = start_index + n
        start_indices.append(start_index)
        end_indices.append(end_index)

    h_products = []
    v_products = []

    total_p = math.factorial(n * n)
    p_count = 1
    for p in permutation(possible_vals):

        print(
            "Executing Permutation "
            + str(p_count)
            + " of "
            + str(total_p)
            + " for n="
            + str(n)
            + "..."
        )
        p_count += 1

        h_product = []
        v_product = []

        for k in range(0, n):
            h_prod = list_multiple(p[start_indices[k] : end_indices[k]])
            h_product.append(h_prod)

        for l in range(0, n):
            v_list = []
            for m in range(0, n):
                v_list.append(p[l + m * n])

            v_prod = list_multiple(v_list)
            v_product.append(v_prod)

        s_h_product = sorted(h_product)
        s_v_product = sorted(v_product)

        h_products.append(s_h_product)
        v_products.append(s_v_product)

        if s_h_product == s_v_product:
            log_append(str(p) + " " + str(h_product) + " " + str(v_product))
    log_append("\nExecution Time: " + str(format_time(time.time() - n_start_time)))
    log_append("\n---\n")
    print(
        "Finished executing for:",
        n,
        ", Execution Time: " + str(format_time(time.time() - n_start_time)),
    )


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
            find_grids_n(grid_size)
            grid_size += 1

    elif n_max > 0:
        for grid_size in range(1, n_max + 1):
            find_grids_n(grid_size)

    print("\nFinished execution...")
    print("Total Execution Time: " + str(format_time(time.time() - main_start_time)))

except KeyboardInterrupt:
    print("\nExiting the program...")
