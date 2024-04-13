
def get_user_input():
    """Function to get a string and an integer input from the user."""
    user_string = input("Please enter a string: ")
    n = input("Please enter an integer: ")
    return user_string, n

def print_char_at_index(user_string, n):
    """Function to print the character at index n of the user_string."""
    while True:
        try:
            index = int(n)
            print(f"The character at index {index} is: '{user_string[index]}'")
            break  # Exit the loop if successful
        except ValueError:
            print("The index provided is not a valid integer. Please try again.")
        except IndexError:
            print("The index is out of range for the provided string. Please try again.")
        user_string, n = get_user_input()  # Re-prompt the user for input

while True:
    user_string, n = get_user_input()  # Get user input
    print_char_at_index(user_string, n)  # Attempt to print the character at index n
    break  # Exit the loop and end the program after printing the character
