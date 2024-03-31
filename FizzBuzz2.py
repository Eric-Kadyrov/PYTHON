def fizz_buzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)

def main():
    # Take input from the user
    n = int(input("Enter a number: "))

    # Run the fizz_buzz function and print the results
    fizz_buzz(n)

# Call the main function
if __name__ == "__main__":
    main()