def get_user_input():
    """Function to get input from the user."""
    return input("Please enter an integer: ")

def convert_to_int(user_input):
    """Function to convert the input to an integer, with error handling."""
    while True:
        try:
            user_int = int(user_input)
            print(f"The integer you entered is: {user_int}")
            break  # Exit the loop if conversion is successful
        except ValueError:  # Catch the error if conversion fails
            user_input = input("That's not an integer. Please enter an integer: ")

user_input = get_user_input()  # Get user input
convert_to_int(user_input)  # Convert the input to an int and handle errors
