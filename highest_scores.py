import csv

# Read scores from the game_scores.csv file
def read_scores(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        scores = {}
        for row in reader:
            player, score = row
            score = int(score)
            if player in scores:
                if scores[player] < score:
                    scores[player] = score
            else:
                scores[player] = score
        return scores

# Retrieve and sort the scores
scores = read_scores('game_scores.csv')
sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Write the highest scores to high_scores.csv
with open('high_scores.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Player name", "Highest score"])  # Writing the header
    for player, score in sorted_scores:
        writer.writerow([player, score])

print("High scores have been saved to 'high_scores.csv'.")