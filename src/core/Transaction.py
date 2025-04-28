import uuid
from datetime import datetime


class Transaction:
    """
    transaction class representing financial transactions
    """

    TRANSACTION_TYPES = ['deposit', 'withdrawal', 'transfer']

    def __init__(self, account_id, transaction_type, amount, description=None,
                 destination_account_id=None, transaction_id=None, created_at=None):
        """
        inti Transaction obj

        args:
            account_id (str): id of the acc involved in the transaction
            transaction_type (str): Type of transaction ('deposit', 'withdrawal', 'transfer')
            amount (float): Transaction amount
            description (str, optional): Transaction description, default si None.
            destination_account_id (str, optional): ID of destination acc for transfers, default is None.
            transaction_id (str, optional): Unique identifier, default is None (generates UUID).
            created_at (str, optional): Transaction timestamp, defautl is None (current time).
        """
        if transaction_type not in self.TRANSACTION_TYPES:
            raise ValueError(f"Transaction type must be one of {self.TRANSACTION_TYPES}")

        self.transaction_id = transaction_id if transaction_id else str(uuid.uuid4())
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.amount = float(amount)
        self.description = description
        self.destination_account_id = destination_account_id
        self.created_at = created_at if created_at else datetime.now().isoformat()

    def to_dict(self):
        """
        convert transaction to dict

        returns: dict -- transac data as dict
        """
        return {
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'destination_account_id': self.destination_account_id,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """
        create transaction from dict

        args: data (dict): transaction data dict

        returns: transac -- transac obj
        """
        return cls(
            account_id=data['account_id'],
            transaction_type=data['transaction_type'],
            amount=data['amount'],
            description=data.get('description'),
            destination_account_id=data.get('destination_account_id'),
            transaction_id=data.get('transaction_id'),
            created_at=data.get('created_at')
        )