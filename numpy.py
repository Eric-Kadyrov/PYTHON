import numpy as np

# Part 1: Create arrays
def create_arrays():
    zeros_array = np.zero((4, 3))
    ones_array = np.ones((4, 3))
    range_array = np.arange(12).reshape((4, 3))
    print("Array of zeros:\n", zeros_array)
    print("Array of ones:\n", ones_array)
    print("Array of numbers from 0 to 11:\n", range_array)

# Part 2: Tabulate F(x) = 2x^2 + 5 for x in [1, 100]
def tabulate_quadratic():
    x_values = np.arange(1, 101)
    function_values = 2 * x_values**2 + 5
    print("Values of F(x) = 2x^2 + 5 from x=1 to x=100:")
    for x, fx in zip(x_values, function_values):
        print(f"F({x}) = {fx}")

# Part 3: Tabulate F(x) = e^−x for x in [−10, 10]
def tabulate_exponential():
    x_values = np.arange(-10, 11)
    function_values = np.exp(-x_values)
    print("Values of F(x) = e^-x from x=-10 to x=10:")
    for x, fx in zip(x_values, function_values):
        print(f"F({x}) = {fx}")

# Execute the functions
create_arrays()
tabulate_quadratic()
tabulate_exponential()