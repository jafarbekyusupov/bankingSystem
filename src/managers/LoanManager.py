from src.core.Loan import Loan
from src.utils.json_utils import load_json, save_json


class LoanManager:
    """ manager class for handling loan operations """

    def __init__(self):
        """
        initialiize the loanmanager
        """
        self.loans_file = 'loans.json'

    def get_all_loans(self):
        """
        get all loans

        returns: list -- list of loan objects
        """
        loans_data = load_json(self.loans_file)
        return [Loan.from_dict(loan_data) for loan_data in loans_data]

    def get_loan_by_id(self, loan_id):
        """
        get a loan by id

        args: loan_id (str): loan id

        returns: Loan -- loan object if found else none
        """
        loans = self.get_all_loans()
        for loan in loans:
            if loan.loan_id == loan_id:
                return loan
        return None

    def get_user_loans(self, user_id):
        """
        get all loans for a user

        args: user_id (str): user id

        returns: list of loan objects belonging to the user
        """
        loans = self.get_all_loans()
        return [loan for loan in loans if loan.user_id == user_id]

    def create_loan_application(self, loan_data):
        """
        create a new loan application

        args: loan_data (dict): loan data dictionary

        returns: str -- loan id if successful else none
        """
        # new loan
        loan = Loan(
            user_id=loan_data['user_id'],
            loan_type=loan_data['loan_type'],
            amount=loan_data['amount'],
            interest_rate=loan_data['interest_rate'],
            term_months=loan_data['term_months'],
            purpose=loan_data.get('purpose')
        )

        # save loan
        loans_data = load_json(self.loans_file)
        loans_data.append(loan.to_dict())

        if save_json(self.loans_file, loans_data):
            return loan.loan_id
        return None

    def update_loan(self, loan_id, loan_data):
        """
        upd an existing loan

        args:
            loan_id (str): loan id
            loan_data (dict): updated loan data

        returns: bool -- true if successful else false
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return False

        # only certain fields can be updated based on loan status
        if loan.status == 'pending':
            # more fields can be updated while pending
            allowed_fields = ['loan_type', 'amount', 'interest_rate', 'term_months', 'purpose']
        else:
            # limited fields can be updated after approval
            allowed_fields = ['purpose']

        # update loan fields
        for key, value in loan_data.items():
            if hasattr(loan, key) and key in allowed_fields:
                setattr(loan, key, value)

        # save updated loan
        loans_data = load_json(self.loans_file)

        # find & replace loan in the list
        for i, l in enumerate(loans_data):
            if l['loan_id'] == loan_id:
                loans_data[i] = loan.to_dict()
                break

        return save_json(self.loans_file, loans_data)

    def approve_loan(self, loan_id):
        """
        approve a loan application

        args: loan_id (str): loan id

        returns: bool -- true if successful else false

        raises: ValueError -- if loan not found or not in pending status
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("loan not found")

        try:
            loan.approve_loan()

            # save updated loan
            loans_data = load_json(self.loans_file)

            # find & replace loan in the list
            for i, l in enumerate(loans_data):
                if l['loan_id'] == loan_id:
                    loans_data[i] = loan.to_dict()
                    break

            return save_json(self.loans_file, loans_data)
        except ValueError as e:
            raise e

    def reject_loan(self, loan_id):
        """
        reject a loan application

        args: loan_id (str): loan id

        returns: bool -- true if successful else false

        raises: ValueError -- if loan not found or not in pending status
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("loan not found")

        try:
            loan.reject_loan()

            # save upd loan
            loans_data = load_json(self.loans_file)

            # find & replace loan in the list
            for i, l in enumerate(loans_data):
                if l['loan_id'] == loan_id:
                    loans_data[i] = loan.to_dict()
                    break

            return save_json(self.loans_file, loans_data)
        except ValueError as e:
            raise e

    def activate_loan(self, loan_id):
        """
        activate an approved loan

        args: loan_id (str): loan id

        returns: bool -- true if successful else false

        raises: ValueError -- if loan not found or not in approved status
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("loan not found")

        try:
            loan.activate_loan()

            # save upd loan
            loans_data = load_json(self.loans_file)

            # find & replace loan in list
            for i, l in enumerate(loans_data):
                if l['loan_id'] == loan_id:
                    loans_data[i] = loan.to_dict()
                    break

            return save_json(self.loans_file, loans_data)
        except ValueError as e:
            raise e

    def make_payment(self, loan_id, amount):
        """
        make a payment on a loan

        args:
            loan_id (str): loan id
            amount (float): payment amount

        returns: float -- remaining balance if successful else none

        raises: ValueError -- if loan not found, not active, or amount is invalid
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("loan not found")

        try:
            new_balance = loan.make_payment(amount)

            # save upd loan
            loans_data = load_json(self.loans_file)

            # find & replace loan in the list
            for i, l in enumerate(loans_data):
                if l['loan_id'] == loan_id:
                    loans_data[i] = loan.to_dict()
                    break

            if save_json(self.loans_file, loans_data):
                return new_balance
        except ValueError as e:
            raise e

        return None

    def calculate_payment(self, loan_id):
        """
        calculate monthly payment for a loan

        args: loan_id (str): loan id

        returns: float -- monthly payment amount

        raises: ValueError -- if loan not found
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            raise ValueError("loan not found")

        return loan.calculate_monthly_payment()