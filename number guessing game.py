import random

def number_guessing_game():
    # Generate a random number between 1 and 100
    hidden_number = random.randint(1, 100)
    attempts = 10

    print("Welcome to the Number Guessing Game!")
    print("I have selected a number between 1 and 100.")
    print(f"You have {attempts} attempts to guess the correct number.")

    # Loop through the allowed number of attempts
    for attempt in range(1, attempts + 1):
        guess = int(input(f"Attempt {attempt}: Enter your guess: "))

        if guess < hidden_number:
            print("Too low! Try again.")
        elif guess > hidden_number:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You've guessed the number in {attempt} attempts.")
            break
    else:
        # This block runs if the loop completes without a break
        print(f"Sorry, you've used all your attempts. The correct number was {hidden_number}.")

# Execute the game
if __name__ == "__main__":
    number_guessing_game()