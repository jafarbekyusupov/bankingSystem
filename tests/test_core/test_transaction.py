import pytest
from src.core.Transaction import Transaction


class TestTransaction:
    def test_init(self):
        transaction = Transaction(
            account_id="test-account-id",
            transaction_type="deposit",
            amount=100.50,
            description="Test deposit"
        )

        assert transaction.account_id == "test-account-id"
        assert transaction.transaction_type == "deposit"
        assert transaction.amount == 100.50
        assert transaction.description == "Test deposit"
        assert transaction.destination_account_id is None
        assert transaction.transaction_id is not None
        assert transaction.created_at is not None

    def test_init_transfer(self):
        transaction = Transaction(
            account_id="source-account-id",
            transaction_type="transfer",
            amount=500.0,
            description="Test transfer",
            destination_account_id="dest-account-id"
        )

        assert transaction.account_id == "source-account-id"
        assert transaction.transaction_type == "transfer"
        assert transaction.amount == 500.0
        assert transaction.description == "Test transfer"
        assert transaction.destination_account_id == "dest-account-id"

    def test_init_with_custom_id_and_timestamp(self):
        custom_id = "custom-transac-id"
        timestamp = "2025-01-01T12:00:00"

        transaction = Transaction(
            account_id="test-account-id",
            transaction_type="withdrawal",
            amount=200.75,
            description="Test withdrawal",
            transaction_id=custom_id,
            created_at=timestamp
        )

        assert transaction.transaction_id == custom_id
        assert transaction.created_at == timestamp

    def test_init_invalid_transaction_type(self):
        """ invalid transac type => valueError """
        with pytest.raises(ValueError):
            Transaction(
                account_id="test-account-id",
                transaction_type="invalid_type",
                amount=100.0
            )

    def test_to_dict(self):
        """ transaction => dict """
        transac = Transaction(
            account_id="test-account-id",
            transaction_type="deposit",
            amount=100.50,
            description="Test deposit",
            destination_account_id=None,
            transaction_id="test-transaction-id",
            created_at="2025-01-01T12:00:00"
        )

        transac_dict = transac.to_dict()

        assert transac_dict["transaction_id"] == "test-transaction-id"
        assert transac_dict["account_id"] == "test-account-id"
        assert transac_dict["transaction_type"] == "deposit"
        assert transac_dict["amount"] == 100.50
        assert transac_dict["description"] == "Test deposit"
        assert transac_dict["destination_account_id"] is None
        assert transac_dict["created_at"] == "2025-01-01T12:00:00"

    def test_from_dict(self):
        """ dict => transaction """
        transaction_data = {
            "transaction_id": "test-transaction-id",
            "account_id": "test-account-id",
            "transaction_type": "withdrawal",
            "amount": 200.75,
            "description": "Test withdrawal",
            "destination_account_id": None,
            "created_at": "2025-01-01T12:00:00"
        }

        transac = Transaction.from_dict(transaction_data)

        assert transac.transaction_id == "test-transaction-id"
        assert transac.account_id == "test-account-id"
        assert transac.transaction_type == "withdrawal"
        assert transac.amount == 200.75
        assert transac.description == "Test withdrawal"
        assert transac.destination_account_id is None
        assert transac.created_at == "2025-01-01T12:00:00"

    def test_from_dict_transfer(self):
        """ creating transfer transaction from dict """
        transaction_data = {
            "transaction_id": "test-transaction-id",
            "account_id": "source-account-id",
            "transaction_type": "transfer",
            "amount": 500.0,
            "description": "Test transfer",
            "destination_account_id": "dest-account-id",
            "created_at": "2025-01-01T12:00:00"
        }

        transac = Transaction.from_dict(transaction_data)

        assert transac.transaction_id == "test-transaction-id"
        assert transac.account_id == "source-account-id"
        assert transac.transaction_type == "transfer"
        assert transac.amount == 500.0
        assert transac.description == "Test transfer"
        assert transac.destination_account_id == "dest-account-id"
        assert transac.created_at == "2025-01-01T12:00:00"

    def test_amount_as_float(self):
        """ test that amount is stored as float """
        # int
        transac1 = Transaction(
            account_id="test-account-id",
            transaction_type="deposit",
            amount=100
        )
        assert isinstance(transac1.amount, float)
        assert transac1.amount == 100.0

        # string
        transac2 = Transaction(
            account_id="test-account-id",
            transaction_type="deposit",
            amount="200.50"
        )
        assert isinstance(transac2.amount, float)
        assert transac2.amount == 200.50