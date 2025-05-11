import pytest
from src.core.Loan import Loan
from datetime import datetime

class TestLoan:
    def test_init(self):
        """ testing init process for Loan obj with basic params """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36,
            purpose="Test loan"
        )

        assert loan.user_id == "test-uid"
        assert loan.loan_type == "Personal"
        assert loan.amount == 10000.0
        assert loan.interest_rate == 5.5
        assert loan.term_months == 36
        assert loan.purpose == "Test loan"
        assert loan.status == "pending"
        assert loan.balance == 10000.0
        assert loan.approved_at is None
        assert loan.loan_id is not None

    def test_init_invalid_loan_type(self):
        """ invalid loan type raises valueError """
        with pytest.raises(ValueError):
            Loan(
                user_id="test-uid",
                loan_type="InvalidType",
                amount=10000.0,
                interest_rate=5.5,
                term_months=36
            )

    def test_init_invalid_status(self):
        """ invalid loan status raises valueError """
        with pytest.raises(ValueError):
            Loan(
                user_id="test-uid",
                loan_type="Personal",
                amount=10000.0,
                interest_rate=5.5,
                term_months=36,
                status="InvalidStatus"
            )

    def test_calculate_monthly_payment_with_interest(self):
        """ monthly payment calculation with interest tested w/ manual calculation """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=12000.0,
            interest_rate=6.0,
            term_months=24
        )

        # manual calcs
        monthly_rate = 6.0 / 100 / 12
        expect_pay = (12000.0 * monthly_rate) / (1 - (1 + monthly_rate) ** -24)
        expect_pay = round(expect_pay, 2)

        assert loan.calculate_monthly_payment() == expect_pay

    def test_calculate_monthly_payment_zero_interest(self):
        """ monthly payment calculation with 0 interest """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=12000.0,
            interest_rate=0.0,
            term_months=24
        )

        expect_pay = 12000.0 / 24

        assert loan.calculate_monthly_payment() == expect_pay

    def test_approve_loan(self):
        """ testing loan approval process """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36
        )

        result = loan.approve_loan()

        assert result is True
        assert loan.status == "approved"
        assert loan.approved_at is not None

    def test_approve_non_pending_loan(self):
        """ test - approving not pending (active or alr approved) loan raises valueError """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36,
            status="rejected"
        )

        with pytest.raises(ValueError): loan.approve_loan()

    def test_activate_loan(self):
        """ activating approved loan """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36,
            status="approved",
            approved_at=datetime.now().isoformat()
        )

        result = loan.activate_loan()

        assert result is True
        assert loan.status == "active"

    def test_activate_non_approved_loan(self):
        """ activating not approved loan raises valueError """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36
        )

        with pytest.raises(ValueError):
            loan.activate_loan()

    def test_reject_loan(self):
        """ loan rejection process """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36
        )

        result = loan.reject_loan()

        assert result is True
        assert loan.status == "rejected"

    def test_reject_non_pending_loan(self):
        """ rejecting not pending (active or approved) loan raises valueError """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36,
            status="approved"
        )

        with pytest.raises(ValueError):
            loan.reject_loan()

    def test_make_payment(self):
        """ making payment on loan """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36,
            status="active"
        )

        new_balance = loan.make_payment(1000.0)

        assert new_balance == 9000.0
        assert loan.balance == 9000.0
        assert loan.status == "active"

    def test_make_payment_paid_off(self):
        """ paying off loan completely """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=1000.0,
            interest_rate=5.5,
            term_months=12,
            status="active"
        )

        new_balance = loan.make_payment(1000.0)

        assert new_balance == 0.0
        assert loan.balance == 0.0
        assert loan.status == "paid_off"

    def test_make_payment_overpay(self):
        """ test cases of overpaying a loan -- should set balance to zero """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=1000.0,
            interest_rate=5.5,
            term_months=12,
            status="active"
        )

        new_balance = loan.make_payment(1500.0)  # more than owed

        assert new_balance == 0.0
        assert loan.balance == 0.0
        assert loan.status == "paid_off"

    def test_make_payment_invalid_amount(self):
        """ payment with negative amount => valueError """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=1000.0,
            interest_rate=5.5,
            term_months=12,
            status="active"
        )

        with pytest.raises(ValueError):
            loan.make_payment(-100.0)

    def test_make_payment_inactive_loan(self):
        """ payment on inactive(pending) loan => valueError """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=1000.0,
            interest_rate=5.5,
            term_months=12,
            status="pending"
        )

        with pytest.raises(ValueError):
            loan.make_payment(100.0)

    def test_to_dict(self):
        """ converting loan to dict """
        loan = Loan(
            user_id="test-uid",
            loan_type="Personal",
            amount=10000.0,
            interest_rate=5.5,
            term_months=36,
            purpose="Test purpose",
            loan_id="test-loan-id",
            created_at="2025-01-01T12:00:00",
            approved_at="2025-01-02T12:00:00",
            balance=9500.0,
            status="active"
        )

        loan_dict = loan.to_dict()

        assert loan_dict["loan_id"] == "test-loan-id"
        assert loan_dict["user_id"] == "test-uid"
        assert loan_dict["loan_type"] == "Personal"
        assert loan_dict["amount"] == 10000.0
        assert loan_dict["interest_rate"] == 5.5
        assert loan_dict["term_months"] == 36
        assert loan_dict["purpose"] == "Test purpose"
        assert loan_dict["status"] == "active"
        assert loan_dict["created_at"] == "2025-01-01T12:00:00"
        assert loan_dict["approved_at"] == "2025-01-02T12:00:00"
        assert loan_dict["balance"] == 9500.0

    def test_from_dict(self):
        """ creating loan from dict """
        loan_data = {
            "loan_id": "test-loan-id",
            "user_id": "test-uid",
            "loan_type": "Personal",
            "amount": 10000.0,
            "interest_rate": 5.5,
            "term_months": 36,
            "purpose": "Test purpose",
            "status": "active",
            "created_at": "2025-01-01T12:00:00",
            "approved_at": "2025-01-02T12:00:00",
            "balance": 9500.0
        }

        loan = Loan.from_dict(loan_data)

        assert loan.loan_id == "test-loan-id"
        assert loan.user_id == "test-uid"
        assert loan.loan_type == "Personal"
        assert loan.amount == 10000.0
        assert loan.interest_rate == 5.5
        assert loan.term_months == 36
        assert loan.purpose == "Test purpose"
        assert loan.status == "active"
        assert loan.created_at == "2025-01-01T12:00:00"
        assert loan.approved_at == "2025-01-02T12:00:00"
        assert loan.balance == 9500.0