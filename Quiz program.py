# Quiz data
quiz_questions = [
    ("What is the capital of France?", ["Berlin", "Paris", "Madrid", "Rome"], 2),
    ("Which planet is known as the Red Planet?", ["Earth", "Venus", "Mars", "Jupiter"], 3),
    ("What is the chemical symbol for water?", ["H2O", "O2", "CO2", "H2"], 1),
]

def run_quiz(questions):
    score = 0  # Initialize score
    for i, (question, choices, correct_answer) in enumerate(questions):
        # Display the question and choices
        print(f"\nQuestion {i + 1}: {question}")
        for idx, choice in enumerate(choices, 1):
            print(f"{idx}. {choice}")

        # Get the user's answer
        try:
            user_answer = int(input("Enter the number of your answer (1-4): "))
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 4.")
            continue

        # Check if the user's answer is correct
        if user_answer == correct_answer:
            print("Correct!")
            score += 1
        else:
            print("Wrong answer.")

    # Print the final score
    print(f"\nYour total score is: {score}/{len(questions)}")

# Run the quiz
if __name__ == "__main__":
    run_quiz(quiz_questions)