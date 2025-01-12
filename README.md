# Grid Multiple Challenge
Brute force generation of possible solutions to the vertical=horizontal product of NxN grid.

- To execute code, create a logs.txt file in the directory of the main.py.
- The programme appends all possible solutions (along with the respective products formed) to the logs.txt.
- The format for the data is: [Grid] [Horizontal Products] [Vertical Products]
- The grid is displayed in such a way that the first 'n'-entries constitute the first row and the next 'n'-entries form the second row and so on.
- Consequently, alternate values, i.e. [ [0, n, 2n...], [1, n+1, 2n+1...], ...] form the vertical rows. (taking the first value as 0-index.
