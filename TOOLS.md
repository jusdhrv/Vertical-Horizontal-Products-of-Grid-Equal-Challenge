# TOOLS.md

## Overview

This codebase is designed to solve the "Vertical Horizontal Products of Grid Equal Challenge". The main goal is to find all possible ways to fill an n×n grid with the numbers 1 to n² such that the set of products of each row equals the set of products of each column. The codebase uses brute-force and parallel computation to search for solutions, and includes several utility scripts for data and log management.

---

## Main Scripts

### 1. `main_all.py`

- **Purpose:**
  - Brute-force search for all possible grid arrangements for a given n.
  - Uses multiprocessing to parallelize the search across CPU cores.
  - Splits permutations into worker files for distributed processing.
  - Logs all valid solutions and execution times.
- **Key Functions:**
  - `find_grids_n(n)`: Main entry point for a given n.
  - `split_permutations_to_files(...)`: Divides the permutation space for parallel processing.
  - `process_permutations(...)`: Checks each permutation for the solution property.
  - `log_worker(...)`: Handles logging from multiple processes.
- **Output:**
  - Appends results to `Data/*-logs.txt` files.
  - Each solution is logged as `[Grid] [Horizontal Products] [Vertical Products]`.

### 2. `main_single.py`

- **Purpose:**
  - Similar to `main_all.py`, but appears to be optimized for finding a single solution (stops after the first is found).
  - Uses a shared `found_solution` flag to halt computation early.
- **Key Functions:**
  - Similar structure to `main_all.py`, but with early exit logic.

---

## Utility Scripts

### 3. `clear_logs.py`

- **Purpose:**
  - Deletes all log files in the `Data/` directory that end with `-logs.txt`.
  - Useful for cleaning up before/after runs.

### 4. `clear_workers.py`

- **Purpose:**
  - Deletes all worker files in `Data/Workers/` that start with `worker_`.
  - Used to clean up intermediate files from parallel runs.

---

## Primes Tool

### 5. `Primes/primes.py`

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

## Proposed Improvements

### 1. Worker File Management Optimization

**Current Issue:** Worker files are written and deleted for each run.
**Proposed Solution:** Streamline to use in-memory processing or temporary files that are automatically cleaned up.
**Benefits:**

- Reduced I/O overhead
- Faster execution
- Less disk space usage
- Cleaner codebase

### 2. Alternative Output Formats

**Current Format:** Plain text with specific formatting
**Proposed Formats:**

#### JSON Format

```json
{
  "n": 3,
  "solutions": [
    {
      "grid": [1, 5, 8, 6, 4, 7, 9, 2, 3],
      "horizontal_products": [40, 168, 54],
      "vertical_products": [54, 40, 168],
      "canonical_form": [1, 5, 8, 6, 4, 7, 9, 2, 3]
    }
  ],
  "execution_time": "00:00:11",
  "total_solutions": 1
}
```

**Benefits:**

- Easy parsing and analysis
- Structured data for further processing
- Better integration with other tools

#### CSV Format

```csv
n,grid,horizontal_products,vertical_products,execution_time
3,"[1, 5, 8, 6, 4, 7, 9, 2, 3]","[40, 168, 54]","[54, 40, 168]",00:00:11
```

**Benefits:**

- Easy import into spreadsheet applications
- Simple to process with standard tools
- Human-readable

#### YAML Format

```yaml
n: 3
solutions:
  - grid: [1, 5, 8, 6, 4, 7, 9, 2, 3]
    horizontal_products: [40, 168, 54]
    vertical_products: [54, 40, 168]
execution_time: 00:00:11
```

**Benefits:**

- Human-readable
- Good for configuration files
- Easy to edit manually

### 3. Performance Monitoring

**Proposed Addition:** Real-time progress tracking and performance metrics.
**Benefits:**

- Better user experience
- Ability to estimate completion times
- Performance optimization insights

---

## Proposed Heuristics for Runtime Optimization

### 1. Early Pruning Strategies

#### Product-Based Pruning

- **Idea:** Check row/column products as they're being built and stop if they exceed reasonable bounds.
- **Implementation:** Track partial products and compare against known constraints.
- **Benefit:** Eliminate invalid permutations early, reducing computation by 50-80%.

#### Symmetry-Based Pruning

- **Idea:** Exploit grid symmetries to avoid checking equivalent permutations.
- **Implementation:** Use canonical forms and skip permutations that are rotations/reflections.
- **Benefit:** Reduce search space by factor of 8 (for square grids).

#### Mathematical Constraints

- **Idea:** Use number theory to identify impossible configurations.
- **Implementation:** Check prime factorizations and divisibility rules.
- **Benefit:** Eliminate mathematically impossible cases early.

### 2. Smart Permutation Generation

#### Constraint-Satisfying Permutation

- **Idea:** Generate permutations that are more likely to satisfy the product constraint.
- **Implementation:** Use backtracking with early constraint checking.
- **Benefit:** Focus computation on promising candidates.

#### Incremental Building

- **Idea:** Build the grid incrementally, checking constraints at each step.
- **Implementation:** Place numbers one by one, checking row/column products.
- **Benefit:** Early termination of invalid partial solutions.

### 3. Parallelization Improvements

#### Dynamic Load Balancing

- **Idea:** Distribute work more evenly across processors.
- **Implementation:** Use work-stealing algorithms or adaptive chunk sizes.
- **Benefit:** Better CPU utilization, especially for irregular workloads.

#### Memory-Efficient Parallelization

- **Idea:** Reduce memory overhead in parallel processing.
- **Implementation:** Use generators and streaming instead of storing all permutations.
- **Benefit:** Handle larger problem sizes without memory issues.

### 4. Mathematical Shortcuts

#### Known Solutions for Small n

- **Idea:** Pre-compute and cache solutions for small values of n.
- **Implementation:** Store known solutions in a lookup table.
- **Benefit:** Instant results for small grids, useful for testing.

#### Pattern Recognition

- **Idea:** Identify patterns in solutions that can be generalized.
- **Implementation:** Analyze existing solutions for mathematical patterns.
- **Benefit:** Potential for closed-form solutions or faster algorithms.

---

## Additional Suggestions

### 1. Configuration Management

- Add a configuration file for parameters like chunk size, number of workers, output format
- Allow command-line arguments for common options

### 2. Error Handling and Recovery

- Add robust error handling for file operations
- Implement checkpointing for long-running computations
- Add graceful shutdown handling

### 3. Documentation and Testing

- Add docstrings to all functions
- Create unit tests for core algorithms
- Add integration tests for end-to-end functionality

### 4. Performance Profiling

- Add timing information for different parts of the algorithm
- Create performance benchmarks
- Add memory usage monitoring

### 5. User Interface Improvements

- Add progress bars for long-running computations
- Provide estimated time to completion
- Add interactive mode for exploration

---

## Summary Table

| Script/Tool         | Purpose/Functionality                                      |
|---------------------|-----------------------------------------------------------|
| main_all.py         | Brute-force, parallel grid search for all solutions        |
| main_single.py      | Brute-force, parallel grid search for a single solution    |
| clear_logs.py       | Delete all log files in Data/                              |
| clear_workers.py    | Delete all worker files in Data/Workers/                   |
| Primes/primes.py    | Analyze primes in (n²/2, n²) for mathematical context      |
| Reference Outputs/  | Store reference outputs for validation                     |

---

# End of TOOLS.md
