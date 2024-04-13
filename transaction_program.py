def transaction():
    # Define the inner function for deposit
    def deposit(amount):
        nonlocal balance  # Use the nonlocal balance variable
        balance += amount  # Add the amount to the balance
        print(f"Deposit successful. New balance: {balance}")

    # Define the inner function for withdrawal
    def withdrawal(amount):
        nonlocal balance  # Use the nonlocal balance variable
        if amount > balance:
            print("Withdrawal amount exceeds the current balance. Transaction declined.")
        else:
            balance -= amount  # Subtract the amount from the balance
            print(f"Withdrawal successful. New balance: {balance}")

    balance = float(input("Enter your starting balance: "))  # User sets the initial balance
    _type = input("Enter transaction type (deposit or withdrawal): ").lower()  # Get the transaction type
    amount = float(input("Enter the amount for the transaction: "))  # Get the transaction amount

    # Check the type of transaction and call the appropriate function
    if _type == "deposit":
        deposit(amount)
    elif _type == "withdrawal":
        withdrawal(amount)
    else:
        print("Invalid transaction type. Please choose 'deposit' or 'withdrawal'.")

if __name__ == "__main__":
    transaction()  # Start the transaction process
