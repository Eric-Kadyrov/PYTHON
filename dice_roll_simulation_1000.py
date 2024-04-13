import random

def roll_dice():
    """Simulate rolling a six-sided dice and return the result."""
    return random.randint(1, 6)

def simulate_dice_rolls(n):
    """Simulate 'n' dice rolls and print the frequency of each result."""
    results = [roll_dice() for _ in range(n)]
    frequencies = {i: results.count(i) for i in range(1, 7)}

    print(f"Simulating {n} dice rolls:")
    for number, frequency in frequencies.items():
        print(f"Number {number}: {frequency} times")

# Simulate 1000 dice rolls
simulate_dice_rolls(1000)
