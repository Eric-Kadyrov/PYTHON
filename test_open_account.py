import unittest

class Account:
    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def __str__(self):
        return f"Account Number: {self.account_number}, Balance: ${self.balance:.2f}"

class SavingsAccount(Account):
    def __init__(self, account_number, balance, interest_rate):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate

    def __str__(self):
        return f"Savings {super().__str__()}, Interest rate: {self.interest_rate:.2%}"

class CurrentAccount(Account):
    def __init__(self, account_number, balance, overdraft_limit):
        super().__init__(account_number, balance)
        self.overdraft_limit = overdraft_limit

    def __str__(self):
        return f"Current {super().__str__()}, Overdraft limit: ${self.overdraft_limit:.2f}"

class Bank:
    def __init__(self):
        self.accounts = []
        self.next_account_number = 1

    def open_account(self, account_type, balance, interest_rate=0.01, overdraft_limit=500):
        if account_type == "savings":
            new_account = SavingsAccount(self.next_account_counter(), balance, interest_rate)
        elif account_type == "current":
            new_account = CurrentAccount(self.next_account_counter(), balance, overdraft_limit)
        else:
            return None
        self.accounts.append(new_account)
        return new_account

    def next_account_counter(self):
        self.next_account_number += 1
        return self.next_account_number - 1

    def __str__(self):
        return '\n'.join(str(account) for account in self.accounts)

# Unit tests for the Bank class
class TestBank(unittest.TestCase):
    def test_open_account(self):
        # Initialize a Bank
        bank = Bank()

        # Test opening a savings account
        savings_account = bank.open_account("savings", 1000, interest_rate=0.05)
        self.assertIsInstance(savings_account, SavingsAccount)
        self.assertEqual(savings_account.balance, 1000)
        self.assertEqual(savings_account.interest_rate, 0.05)

        # Test opening a current account
        current_account = bank.open_account("current", 500, overdraft_limit=1000)
        self.assertIsInstance(current_account, CurrentAccount)
        self.assertEqual(current_account.balance, 500)
        self.assertEqual(current_account.overdraft_limit, 1000)

        # Test opening an invalid account type
        no_account = bank.open_account("checking", 200)
        self.assertIsNone(no_account)

if __name__ == "__main__":
    unittest.main()