import pytest
from unittest.mock import patch, MagicMock
from src.managers.AccountManager import AccountManager
from src.core.Account import Account
from src.core.Transaction import Transaction


class TestAccountManager:
    @pytest.fixture
    def mock_accounts_data(self):
        """ sample account data """
        return [
            {
                "account_id": "acc-1",
                "user_id": "user-1",
                "account_type": "Checking",
                "balance": 1000.0,
                "account_number": "1000001",
                "created_at": "2025-01-01T00:00:00",
                "active": True
            },
            {
                "account_id": "acc-2",
                "user_id": "user-1",
                "account_type": "Savings",
                "balance": 5000.0,
                "account_number": "1000002",
                "created_at": "2025-01-02T00:00:00",
                "active": True
            },
            {
                "account_id": "acc-3",
                "user_id": "user-2",
                "account_type": "Checking",
                "balance": 2500.0,
                "account_number": "1000003",
                "created_at": "2025-01-03T00:00:00",
                "active": True
            }
        ]

    @pytest.fixture
    def mock_transactions_data(self):
        """ sample transac data """
        return [
            {
                "transaction_id": "trans-1",
                "account_id": "acc-1",
                "transaction_type": "deposit",
                "amount": 500.0,
                "description": "Initial deposit",
                "created_at": "2025-01-01T12:00:00"
            },
            {
                "transaction_id": "trans-2",
                "account_id": "acc-1",
                "transaction_type": "withdrawal",
                "amount": 200.0,
                "description": "ATM withdrawal",
                "created_at": "2025-01-02T14:30:00"
            },
            {
                "transaction_id": "trans-3",
                "account_id": "acc-1",
                "transac_type": "transfer",
                "amount": 300.0,
                "description": "Transfer to savings",
                "destination_account_id": "acc-2",
                "created_at": "2025-01-03T10:15:00"
            }
        ]

    @patch('src.utils.json_utils.load_json')
    def test_get_all_accounts(self, mock_load_json, mock_accounts_data):
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()
        accs = acc_manager.get_all_accounts()

        assert len(accs) == 3
        assert isinstance(accs[0], Account)
        assert accs[0].account_id == "acc-1"
        assert accs[1].account_id == "acc-2"
        assert accs[2].account_id == "acc-3"

        mock_load_json.assert_called_once_with('accounts.json')

    @patch('src.utils.json_utils.load_json')
    def test_get_account_by_id(self, mock_load_json, mock_accounts_data):
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()
        acc = acc_manager.get_account_by_id("acc-2")

        assert acc is not None
        assert acc.account_id == "acc-2"
        assert acc.account_type == "Savings"
        assert acc.balance == 5000.0
        assert acc.user_id == "user-1"

    @patch('src.utils.json_utils.load_json')
    def test_get_account_by_id_not_found(self, mock_load_json, mock_accounts_data):
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()
        acc = acc_manager.get_account_by_id("dne-id")

        assert acc is None

    @patch('src.utils.json_utils.load_json')
    def test_get_user_accounts(self, mock_load_json, mock_accounts_data):
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()
        user_accounts = acc_manager.get_user_accounts("user-1")

        assert len(user_accounts) == 2
        assert all(acc.user_id == "user-1" for acc in user_accounts)

        account_ids = [acc.account_id for acc in user_accounts]
        assert "acc-1" in account_ids
        assert "acc-2" in account_ids

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_create_account(self, mock_save_json, mock_load_json, mock_accounts_data):
        mock_load_json.side_effect = [
            mock_accounts_data,
            []  # for transacs -- init deposit
        ]
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        acc_data = {
            "user_id": "user-3",
            "account_type": "Checking",
            "balance": 100.0
        }

        account_id = acc_manager.create_account(acc_data)

        assert account_id is not None
        assert mock_save_json.call_count == 2

        accs_save_call = mock_save_json.call_args_list[0]
        savd_accs = accs_save_call[0][1]
        assert len(savd_accs) == 4

        new_acc = savd_accs[3]
        assert new_acc["user_id"] == "user-3"
        assert new_acc["account_type"] == "Checking"
        assert new_acc["balance"] == 100.0
        assert "account_number" in new_acc
        assert new_acc["active"] is True

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_create_account_with_zero_balance(self, mock_save_json, mock_load_json, mock_accounts_data):
        """ create acc with zero balance (no init deposit) """
        mock_load_json.return_value = mock_accounts_data
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        acc_data = {
            "user_id": "user-3",
            "account_type": "Savings",
            "balance": 0.0
        }

        account_id = acc_manager.create_account(acc_data)

        assert account_id is not None
        assert mock_save_json.call_count == 1  # just acc save, no transac

        # verify account data
        savd_accs = mock_save_json.call_args[0][1]
        new_acc = savd_accs[3]
        assert new_acc["balance"] == 0.0

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_update_account(self, mock_save_json, mock_load_json, mock_accounts_data):
        """ update existing account """
        mock_load_json.return_value = mock_accounts_data
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        # balance should NOT be directly updatable
        upd_data = {
            "account_type": "Premium Checking",
            "balance": 9999.99,  # should be ignored
            "active": False
        }

        result = acc_manager.update_account("acc-1", upd_data)

        assert result is True
        mock_save_json.assert_called_once()

        saved_data = mock_save_json.call_args[0][1]
        upd_acc = next((acc for acc in saved_data if acc["account_id"] == "acc-1"), None)
        assert upd_acc["account_type"] == "Premium Checking"
        assert upd_acc["balance"] == 1000.0
        assert upd_acc["active"] is False

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_update_account_not_found(self, mock_save_json, mock_load_json, mock_accounts_data):
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()
        result = acc_manager.update_account("dne-id", {"account_type": "Premium"})

        assert result is False
        mock_save_json.assert_not_called()

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_close_account(self, mock_save_json, mock_load_json, mock_accounts_data):
        """ close account with zero balance """
        mock_accounts_data[0]["balance"] = 0.0
        mock_load_json.return_value = mock_accounts_data
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        result = acc_manager.close_account("acc-1")

        assert result is True
        mock_save_json.assert_called_once()

        saved_data = mock_save_json.call_args[0][1]
        closed_account = next((acc for acc in saved_data if acc["account_id"] == "acc-1"), None)
        assert closed_account["active"] is False

    @patch('src.utils.json_utils.load_json')
    def test_close_account_with_balance(self, mock_load_json, mock_accounts_data):
        """ close account with nonzero balance should fail """
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()

        with pytest.raises(ValueError) as e:
            acc_manager.close_account("acc-1")  # acc-1 has 1000 on balance

        assert "cannot close account with non-zero balance" in str(e.value).lower()

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_deposit(self, mock_save_json, mock_load_json, mock_accounts_data, mock_transactions_data):
        """ deposit to account """
        mock_load_json.side_effect = [
            mock_accounts_data, 
            mock_transactions_data
        ]
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        new_balance = acc_manager.deposit("acc-1", 500.0, "test deposit")

        assert new_balance == 1500.0
        assert mock_save_json.call_count == 2

        accs_save_call = mock_save_json.call_args_list[0]
        savd_accs = accs_save_call[0][1]
        upd_acc = next((acc for acc in savd_accs if acc["account_id"] == "acc-1"), None)
        assert upd_acc["balance"] == 1500.0

        transacs_save_call = mock_save_json.call_args_list[1]
        saved_transacs = transacs_save_call[0][1]
        new_transac = saved_transacs[3]  # 3 + 1
        assert new_transac["account_id"] == "acc-1"
        assert new_transac["transaction_type"] == "deposit"
        assert new_transac["amount"] == 500.0
        assert new_transac["description"] == "test deposit"

    @patch('src.utils.json_utils.load_json')
    def test_deposit_to_inactive_account(self, mock_load_json, mock_accounts_data):
        """ deposit to inactive account should fail """
        mock_accounts_data[0]["active"] = False
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()

        with pytest.raises(ValueError) as e:
            acc_manager.deposit("acc-1", 500.0, "test deposit")

        assert "cannot deposit to inactive account" in str(e.value).lower()

    @patch('src.utils.json_utils.load_json')
    def test_deposit_negative_amount(self, mock_load_json, mock_accounts_data):
        """ deposit negative amount should fail """
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()

        with pytest.raises(ValueError) as e:
            acc_manager.deposit("acc-1", -500.0, "negative deposit")

        assert "must be positive" in str(e.value).lower()

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_withdraw(self, mock_save_json, mock_load_json, mock_accounts_data, mock_transactions_data):
        """ withdraw from account """
        mock_load_json.side_effect = [
            mock_accounts_data,
            mock_transactions_data
        ]
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        new_balance = acc_manager.withdraw("acc-1", 300.0, "test withdrawal")

        assert new_balance == 700.0 
        assert mock_save_json.call_count == 2  

        accs_save_call = mock_save_json.call_args_list[0]
        savd_accs = accs_save_call[0][1]
        upd_acc = next((acc for acc in savd_accs if acc["account_id"] == "acc-1"), None)
        assert upd_acc["balance"] == 700.0

        transacs_save_call = mock_save_json.call_args_list[1]
        saved_transacs = transacs_save_call[0][1]
        new_transac = saved_transacs[3]
        assert new_transac["account_id"] == "acc-1"
        assert new_transac["transaction_type"] == "withdrawal"
        assert new_transac["amount"] == 300.0
        assert new_transac["description"] == "test withdrawal"

    @patch('src.utils.json_utils.load_json')
    def test_withdraw_insufficient_funds(self, mock_load_json, mock_accounts_data):
        """ withdraw more than balance should fail """
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()

        with pytest.raises(ValueError) as e:
            acc_manager.withdraw("acc-1", 1500.0, "too much")  # acc-1 has 1000.0

        assert "insufficient funds" in str(e.value).lower()

    @patch('src.utils.json_utils.load_json')
    def test_withdraw_from_inactive_account(self, mock_load_json, mock_accounts_data):
        """ withdraw from inactive acc should fail """
        mock_accounts_data[0]["active"] = False
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()

        with pytest.raises(ValueError) as e:
            acc_manager.withdraw("acc-1", 100.0, "test withdrawal")

        assert "cannot withdraw from inactive account" in str(e.value).lower()

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_transfer(self, mock_save_json, mock_load_json, mock_accounts_data, mock_transactions_data):
        """ transfer between accs """
        mock_load_json.side_effect = [
            mock_accounts_data,  # for accs -- withdraw
            mock_accounts_data,  # for accs -- upd-d after withdraw
            mock_transactions_data  # for transacs
        ]
        mock_save_json.return_value = True

        acc_manager = AccountManager()

        result = acc_manager.transfer("acc-1", "acc-2", 500.0, "test transfer")

        assert result is True
        assert mock_save_json.call_count == 2  # once for accs once for transacs

        # verify accs upd
        accs_save_call = mock_save_json.call_args_list[0]
        savd_accs = accs_save_call[0][1]

        from_account = next((acc for acc in savd_accs if acc["account_id"] == "acc-1"), None)
        to_account = next((acc for acc in savd_accs if acc["account_id"] == "acc-2"), None)

        assert from_account["balance"] == 500.0  # 1000 - 500
        assert to_account["balance"] == 5500.0  # 5000 + 500

        # verify transac created
        transacs_save_call = mock_save_json.call_args_list[1]
        saved_transacs = transacs_save_call[0][1]
        new_transac = saved_transacs[3]

        assert new_transac["account_id"] == "acc-1"
        assert new_transac["transaction_type"] == "transfer"
        assert new_transac["amount"] == 500.0
        assert new_transac["description"] == "test transfer"
        assert new_transac["destination_account_id"] == "acc-2"

    @patch('src.utils.json_utils.load_json')
    def test_transfer_to_inactive_account(self, mock_load_json, mock_accounts_data):
        """ transfer to inactive account should fail """
        # set 2nd account to inactive
        mock_accounts_data[1]["active"] = False
        mock_load_json.return_value = mock_accounts_data

        acc_manager = AccountManager()

        with pytest.raises(ValueError) as e:
            acc_manager.transfer("acc-1", "acc-2", 500.0, "test transfer")

        assert "inactive account" in str(e.value).lower()

    @patch('src.utils.json_utils.load_json')
    def test_get_transactions(self, mock_load_json, mock_transactions_data):
        """ get transacs by account """
        mock_load_json.return_value = mock_transactions_data

        acc_manager = AccountManager()

        # get transacs for acc-1
        transacs = acc_manager.get_transactions(account_id="acc-1")

        assert len(transacs) == 3
        assert all(isinstance(t, Transaction) for t in transacs)
        assert all(t.account_id == "acc-1" for t in transacs)

        transac_types = [t.transaction_type for t in transacs]
        assert "deposit" in transac_types
        assert "withdrawal" in transac_types
        assert "transfer" in transac_types

    @patch('src.utils.json_utils.load_json')
    def test_get_transactions_by_user(self, mock_load_json, mock_accounts_data, mock_transactions_data):
        """ get transacs by user """
        mock_load_json.side_effect = [
            mock_accounts_data,
            mock_transactions_data
        ]

        acc_manager = AccountManager()

        # get transacs for user-1 -- which got acc-1 n acc-2
        transacs = acc_manager.get_transactions(user_id="user-1")

        assert len(transacs) == 3  # all transacs belong to acc-1 | if we added another user, his transacs would show up as well