import pytest
from src.core.Account import Account

class TestAccount:
    def test_init(self):
        acc  = Account(
            user_id = "test-uid",
            account_type = "Checking",
            balance = 9999.9,
            account_number= "123456789"
        )

        assert acc.user_id == "test-uid"
        assert acc.account_type == "Checking"
        assert acc.balance == 9999.9
        assert acc.account_number == "123456789"
        assert acc.active is True
        assert acc.account_id is not None

    def test_init_invalid_acc_type(self):
        ''' to test that invalid acc type raises ValueError '''
        with pytest.raises(ValueError):
            Account(user_id = "test-uid", account_type = "InvalidType")

    def test_deposit(self):
        acc = Account(
            user_id = "test-uid",
            account_type = "Checking",
            balance = 99.9
        )

        newBalance = acc.deposit(69.0)
        assert newBalance == 168.9
        assert acc.balance == 168.9

    def test_deposit_neg_amount(self):
        ''' making sure that neg deposit value raise valueError '''
        acc = Account(
            user_id="test-uid",
            account_type="Checking",
            balance=99.9
        )

        with pytest.raises(ValueError):
            acc.deposit(-99.99)

    def test_withdraw(self):
        ''' to test withdraw funcs'''
        acc = Account(
            user_id="test-uid",
            account_type="Checking",
            balance=99.9
        )

        newBalance = acc.withdraw(69.9)
        assert newBalance == 30
        assert acc.balance == 30

    def test_withdraw_neg_amount(self):
        acc = Account(
            user_id="test-uid",
            account_type="Checking",
            balance=99.9
        )

        with pytest.raises(ValueError):
            acc.withdraw(-99.9)

    def test_withdraw_insufficient_funds(self):
        ''' withdrawal xceeding balande results in valueError '''
        acc = Account(
            user_id="test-uid",
            account_type="Checking",
            balance=99.9
        )

        with pytest.raises(ValueError):
            acc.withdraw(999.9)