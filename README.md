# Vertical Horizontal Products of Grid Equal Challenge

Brute force generation of possible solutions to the vertical product = horizontal product of NxN grid. (See below instructions for the challenge's statement)

- Create a 'Data/' directory in the same folder as the main.py file.
- You are now free to start executing the code!

## The Challenge Statement

Arun has to fill in a n × n grid with the numbers 1, 2, . . . , n^2.
Tejas writes down the 'n' numbers obtained by multiplying the numbers in each horizontal row.
Meanwhile, Ganesh writes down the 'n' numbers obtained by multiplying the numbers in each vertical column.

- Can Arun fill in the grid in such a way that Tejas and Ganesh obtain the same lists of 'n' numbers?
- Can you find any conditions on n that guarantee that it is possible or any conditions that guarantee that it is impossible?

## Usage

### Recommended: Optimized Version

For best performance, use the optimized version:

```bash
python main_optimized.py
```

### Standard Version

For the standard implementation:

```bash
python main.py
```

The program will prompt you for:

1. The value of 'n' (grid size)
2. Execution mode:
   - Option 1: Find all possible solutions
   - Option 2: Find single solution (stop after first)

## Performance Differences

- **main_optimized.py**: Automatically chooses the best approach based on grid size
  - n ≤ 3: Fast in-memory processing with memoization (~20 seconds for n=3)
  - n ≥ 4: Memory-safe file-based processing to handle large permutations
- **main.py**: Uses file-based processing for all grid sizes (slower for small n)

### Notes on output

- The programme appends all possible solutions (along with the respective products formed) to the logs.txt.
- The format for the data is: [Grid] [Horizontal Products] [Vertical Products]
- The grid is displayed as a Python 'list' in such a way that the first 'n'-entries constitute the first row and the next 'n'-entries form the second row and so on.
- Consequently, alternate values, i.e. [0, n, 2n...], form the first column and [1, n+1, 2n+1...] form the second column and so on (taking the first value, the top-left value in grid arrangement, as 0th index and bottom-right value in grid arrangement as the (n^2-1)th index)
