class Account:
    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"${amount} deposited. New balance: ${self.balance:.2f}")
        else:
            print("Invalid amount for deposit.")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            print(f"${amount} withdrawn. New balance: ${self.balance:.2f}")
        else:
            print("Insufficient funds for this withdrawal.")

    def __str__(self):
        return f"Account Number: {self.account_number}, Balance: ${self.balance:.2f}"

class SavingsAccount(Account):
    def __init__(self, account_number, balance, interest_rate):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate

    def add_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        print(f"Interest added: ${interest:.2f}. New balance: ${self.balance:.2f}")

class CurrentAccount(Account):
    def __init__(self, account_number, balance, overdraft_limit):
        super().__init__(account_number, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if 0 < amount <= self.balance + self.overdraft_limit:
            self.balance -= amount
            print(f"${amount} withdrawn. New balance: ${self.balance:.2f}")
        else:
            print("Insufficient funds, even considering overdraft limit.")

class Bank:
    def __init__(self):
        self.accounts = []
        self.next_account_number = 1

    def open_account(self):
        account_type = input("Enter account type (savings/current): ").strip().lower()
        balance = float(input("Initial deposit amount: "))
        if account_type == "savings":
            interest_rate = float(input("Enter the interest rate (as a decimal): "))
            new_account = SavingsAccount(self.next_account_counter(), balance, interest_rate)
        elif account_type == "current":
            overdraft_limit = float(input("Enter overdraft limit: "))
            new_account = CurrentAccount(self.next_account_counter(), balance, overdraft_limit)
        else:
            print("Invalid account type.")
            return
        self.accounts.append(new_account)
        print(f"{account_type.capitalize()} account opened with account number {new_account.account_number}.")

    def next_account_counter(self):
        self.next_account_number += 1
        return self.next_account_number - 1

    def account_operations(self):
        account_number = int(input("Enter your account number: "))
        account = next((acc for acc in self.accounts if acc.account_number == account_number), None)
        if account is not None:
            action = input("Choose an action (deposit/withdraw): ").strip().lower()
            amount = float(input("Enter the amount: "))
            if action == "deposit":
                account.deposit(amount)
            elif action == "withdraw":
                account.withdraw(amount)
            else:
                print("Invalid action.")
        else:
            print("Account not found.")

    def __str__(self):
        return '\n'.join(str(account) for account in self.accounts)

# Main program flow
bank = Bank()
while True:
    command = input("Do you want to open an account or perform an action? (open/action/exit): ").strip().lower()
    if command == "open":
        bank.open_account()
    elif command == "action":
        bank.account_operations()
    elif command == "exit":
        print("Exiting the bank system.")
        break
    else:
        print("Invalid command. Please try again.")