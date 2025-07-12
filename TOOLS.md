# TOOLS.md

## Overview

This codebase is designed to solve the "Vertical Horizontal Products of Grid Equal Challenge". The main goal is to find all possible ways to fill an n×n grid with the numbers 1 to n² such that the set of products of each row equals the set of products of each column. The codebase uses brute-force and parallel computation to search for solutions, and includes several utility scripts for data and log management.

---

## Main Scripts

### 1. `main.py`

- **Purpose:**
  - Unified script that can find either all solutions or a single solution for a given n.
  - Uses multiprocessing to parallelize the search across CPU cores.
  - Splits permutations into worker files for distributed processing.
  - Logs valid solutions and execution times.
  - Interactive mode selection during execution.
- **Key Functions:**
  - `find_grids_n(n, single_solution=False)`: Main entry point with mode selection.
  - `check_permutation_all(args)`: Check permutation for all solutions mode.
  - `check_permutation_single(args)`: Check permutation for single solution mode with early termination.
  - `process_permutations_all(...)`: Process all permutations for complete search.
  - `process_permutations_single(...)`: Process permutations with early termination after first solution.
  - `split_permutations_to_files(...)`: Divides the permutation space for parallel processing.
  - `log_worker(...)`: Handles logging from multiple processes.
- **Usage:**
  - Run `python main.py`
  - Enter the value for 'n'
  - Choose execution mode:
    - Option 1: Find all possible solutions
    - Option 2: Find single solution (stop after first)
- **Output:**
  - Appends results to `Data/*-logs.txt` files.
  - Each solution is logged as `[Grid] [Horizontal Products] [Vertical Products]`.
  - Includes mode information in logs.

---

## Utility Scripts

### 2. `clear_logs.py`

- **Purpose:**
  - Deletes all log files in the `Data/` directory that end with `-logs.txt`.
  - Useful for cleaning up before/after runs.

### 3. `clear_workers.py`

- **Purpose:**
  - Deletes all worker files in `Data/Workers/` that start with `worker_`.
  - Used to clean up intermediate files from parallel runs.

---

## Primes Tool

### 4. `Primes/primes.py`

- **Purpose:**
  - Computes and logs the number of primes in the interval ((n²)/2, n²) for a given n.
  - Uses the Sieve of Eratosthenes for prime generation.
  - Appends results to `primes_greater.txt`.
- **Status:**
  - Separate mathematical exploration for heuristic development.
  - Can be safely ignored for main grid search functionality.

---

## Data and Output

- **Data Directory:**
  - `Data/`: Stores log files and worker files.
  - `Data/Workers/`: Stores intermediate files for parallel processing.
- **Reference Outputs:**
  - `Reference Outputs/`: Contains reference output files for different versions/optimizations of the solver.
  - Useful for verifying correctness and performance.

---

## Summary Table

| Script/Tool         | Purpose/Functionality                                      |
|---------------------|-----------------------------------------------------------|
| main.py             | Unified grid search with single/all solutions mode        |
| clear_logs.py       | Delete all log files in Data/                              |
| clear_workers.py    | Delete all worker files in Data/Workers/                   |
| Primes/primes.py    | Analyze primes in (n²/2, n²) for mathematical context      |
| Reference Outputs/  | Store reference outputs for validation                     |

---
