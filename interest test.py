import unittest
from unittest.mock import patch

class TestBank(unittest.TestCase):
    def test_update_savings_account_interest(self):
        # Create a Bank and add a Savings Account
        bank = Bank()
        savings_account = bank.open_account("savings", 1000, interest_rate=0.01)
        # Verify that interest is added correctly
        bank.update()
        self.assertEqual(savings_account.balance, 1010)

    @patch('builtins.print')
    def test_update_current_account_overdraft(self, mock_print):
        # Create a Bank and add a Current Account with overdraft
        bank = Bank()
        current_account = bank.open_account("current", -100, overdraft_limit=500)
        # Call update and verify print was called
        bank.update()
        mock_print.assert_called_with(f"Notice: Account current #{current_account.account_number} is in overdraft.")

if __name__ == "__main__":
    unittest.main()