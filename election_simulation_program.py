
import random

def receive_input():
    num_regions = int(input("Enter the number of regions: "))
    ratings = []
    for i in range(1, num_regions + 1):
        rating = float(input(f"Enter a rating for 1st candidate in region {i}: "))
        ratings.append(rating)
    return ratings

def simulate_region_election(rating):
    votes_for_first = 0
    total_voters = 10000
    for _ in range(total_voters):
        if random.random() * 100 < rating:
            votes_for_first += 1
    votes_for_second = total_voters - votes_for_first
    return votes_for_first, votes_for_second

def simulate_election(input_data):
    election_results = []
    for rating in input_data:
        region_result = simulate_region_election(rating)
        election_results.append(region_result)
    return election_results

def calculate_result(election_result):
    total_votes_first = sum(result[0] for result in election_result)
    total_votes_second = sum(result[1] for result in election_result)
    total_votes = total_votes_first + total_votes_second
    winner = "1st" if total_votes_first > total_votes_second else "2nd"
    percentage = (max(total_votes_first, total_votes_second) / total_votes) * 100
    return winner, total_votes_first, total_votes_second, percentage

def announce_result(result):
    winner, total_votes_first, total_votes_second, percentage = result
    print(f"Result: {winner} candidate won with {total_votes_first + total_votes_second} votes and {percentage:.1f}% of all votes")

input_data = receive_input()
election_result = simulate_election(input_data)
result = calculate_result(election_result)
announce_result(result)
