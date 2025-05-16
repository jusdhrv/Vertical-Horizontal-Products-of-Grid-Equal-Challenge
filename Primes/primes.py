import os


def read_last_n_value(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 2

    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in reversed(lines):
            if line.startswith("For n="):
                return int(line.split("=")[1].split(":")[0].strip()) + 1
    return 2


def sieve_of_eratosthenes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False  # 0 and 1 are not prime numbers

    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False

    return [num for num, prime in enumerate(is_prime) if prime]


def log_append(data):
    with open("primes_greater.txt", "a") as file1:
        file1.write(data + "\n")


def primes_in_range(n):
    lower_bound = (n**2) // 2
    upper_bound = n**2

    primes = sieve_of_eratosthenes(upper_bound)
    primes_in_range = [prime for prime in primes if lower_bound < prime < upper_bound]

    return primes_in_range


def execution(n):
    primes = primes_in_range(n)
    if len(primes) > n:
        print(
            "\nFor n="
            + str(n)
            + ": "
            + str(len(primes))
            #+ str(primes)
            + "\n---"
        )
        log_append(
            "\nFor n="
            + str(n)
            + ": "
            + str(len(primes))
            + str(primes)
            + "\n---"
        )


if __name__ == "__main__":
    try:
        n_start = read_last_n_value("primes_greater.txt")
        n_max = int(input("Enter value for 'n': "))

        if n_max < 0:
            print("\nInvalid value provided. Must be a natural number")

        elif n_max == 0:
            n = n_start
            while True:
                try:
                    execution(n)
                    n += 1
                except KeyboardInterrupt:
                    print("\nExecution interrupted by user.")
                    break

        elif n_max > 0:
            try:
                for n in range(n_start, n_max + 1):
                    execution(n)
            except KeyboardInterrupt:
                print("\nExecution interrupted by user.")

    except ValueError:
        print("\nInvalid input. Please enter a valid integer.")
