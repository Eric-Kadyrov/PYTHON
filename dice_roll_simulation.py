import random

def roll_dice():
    return random.randint(1, 6)

# Example usage
result = roll_dice()
print(f"Dice roll result: {result}")
