def cats_with_hats(num_rounds, num_cats):
    # Create an array to represent the state of hats on cats
    hats = [False] * num_cats

    # Perform the given number of rounds
    for round in range(1, num_rounds + 1):
        # Toggle every k-th cat based on the current round
        for cat in range(round, num_cats + 1, round):
            hats[cat - 1] = not hats[cat - 1]

    # Determine which cats have hats at the end
    cats_with_hats = []
    for cat_index in range(num_cats):
        if hats[cat_index]:
            cats_with_hats.append(cat_index + 1)

    return cats_with_hats


# Using 100 rounds and 100 cats
cats = cats_with_hats(100, 100)
print("Cats with hats:", cats)
