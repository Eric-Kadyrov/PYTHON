import csv
import random

# List of player names
players = ["Josh", "Luke", "Kate", "Mark", "Mary"]

# Function to simulate scores for each player across 100 rounds
def simulate_scores(players):
    results = []
    for _ in range(100):  # 100 rounds
        for player in players:
            score = random.randint(0, 1000)  # Score between 0 and 1000
            results.append([player, score])
    return results

# Simulate the game scores
game_results = simulate_scores(players)

# Write the results to a CSV file
with open('game_scores.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Player name", "Score"])  # Writing the header
    writer.writerows(game_results)  # Writing the data

print("Scores have been saved to 'game_scores.csv'.")