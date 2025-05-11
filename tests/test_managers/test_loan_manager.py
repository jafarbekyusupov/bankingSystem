import pytest
from unittest.mock import patch
from src.managers.LoanManager import LoanManager
from src.core.Loan import Loan

class TestLoanManager:
    @pytest.fixture
    def mock_loans_data(self):
        """ sample loan data """
        return [
            {
                "loan_id": "loan-1",
                "user_id": "user-1",
                "loan_type": "Personal",
                "amount": 5000.0,
                "interest_rate": 5.5,
                "term_months": 24,
                "purpose": "Test loan 1",
                "status": "pending",
                "created_at": "2025-01-01T00:00:00",
                "approved_at": None,
                "balance": 5000.0
            },
            {
                "loan_id": "loan-2",
                "user_id": "user-2",
                "loan_type": "Home",
                "amount": 200000.0,
                "interest_rate": 3.2,
                "term_months": 360,
                "purpose": "Test loan 2",
                "status": "approved",
                "created_at": "2025-01-02T00:00:00",
                "approved_at": "2025-01-03T00:00:00",
                "balance": 200000.0
            },
            {
                "loan_id": "loan-3",
                "user_id": "user-1",
                "loan_type": "Auto",
                "amount": 15000.0,
                "interest_rate": 4.5,
                "term_months": 60,
                "purpose": "Test loan 3",
                "status": "active",
                "created_at": "2025-01-04T00:00:00",
                "approved_at": "2025-01-05T00:00:00",
                "balance": 14000.0
            }
        ]


    @patch('src.utils.json_utils.load_json')
    def test_get_all_loans_loads_json(self, mock_load_json, mock_loans_data):
        """ testing that get_all_loans loads from json correctly """
        mock_load_json.return_value = mock_loans_data

        loan_manager = LoanManager()
        loans = loan_manager.get_all_loans()

        mock_load_json.assert_called_once_with('loans.json')

        assert len(loans) == 3
        assert all(isinstance(loan, Loan) for loan in loans)

    @patch('src.utils.json_utils.load_json')
    def test_get_user_loans_filtering(self, mock_load_json, mock_loans_data):
        """ test that get_user_loans correctly filters by user_id """
        mock_load_json.return_value = mock_loans_data

        loan_manager = LoanManager()
        user_loans = loan_manager.get_user_loans("user-1")

        # verfiy filtering logic
        assert len(user_loans) == 2
        assert all(loan.user_id == "user-1" for loan in user_loans)

        # verify that correct loans were returned
        loan_ids = [loan.loan_id for loan in user_loans]
        assert "loan-1" in loan_ids
        assert "loan-3" in loan_ids

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_create_loan_application_saves_correctly(self, mock_save_json, mock_load_json, mock_loans_data):
        """ create_loan_application should save data correctly """
        mock_load_json.return_value = mock_loans_data
        mock_save_json.return_value = True

        loan_manager = LoanManager()

        loan_data = {
            "user_id": "user-3",
            "loan_type": "Personal",
            "amount": 10000.0,
            "interest_rate": 6.0,
            "term_months": 36,
            "purpose": "New test loan"
        }

        loan_id = loan_manager.create_loan_application(loan_data)

        assert loan_id is not None

        # make sure json was saved
        mock_save_json.assert_called_once()

        # data struct should be saved
        saved_data = mock_save_json.call_args[0][1]
        assert len(saved_data) == 4  # Original 3 + 1 new

        # new loan data should be correct
        new_loan = saved_data[3]
        assert new_loan["user_id"] == "user-3"
        assert new_loan["loan_type"] == "Personal"
        assert new_loan["amount"] == 10000.0
        assert new_loan["status"] == "pending"
        assert "loan_id" in new_loan

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_update_loan_permissions_by_status(self, mock_save_json, mock_load_json, mock_loans_data):
        """ test upd permissions differs based on loan status """
        mock_load_json.return_value = mock_loans_data
        mock_save_json.return_value = True

        loan_manager = LoanManager()

        # upd-ng pending loan => should allow more fields to be upd-d
        pending_update = {
            "loan_type": "Education",
            "amount": 7500.0,
            "interest_rate": 4.0,
            "purpose": "Updated purpose"
        }

        # upd approved loan - more restricted
        approved_update = {
            "loan_type": "Business",  # should be ignored
            "amount": 250000.0,  # should be ignored
            "purpose": "New purpose"  # should be upd-d
        }

        #pending loan upd
        loan_manager.update_loan("loan-1", pending_update)

        # approved loan upd
        loan_manager.update_loan("loan-2", approved_update)

        # make sure both r saved
        assert mock_save_json.call_count == 2

        # get saved data from both calls
        first_call_data = mock_save_json.call_args_list[0][0][1]
        second_call_data = mock_save_json.call_args_list[1][0][1]

        # find upd loans
        pending_loan = next((l for l in first_call_data if l["loan_id"] == "loan-1"), None)
        approved_loan = next((l for l in second_call_data if l["loan_id"] == "loan-2"), None)

        # verify that pending loan allowed all updates
        assert pending_loan["loan_type"] == "Education"
        assert pending_loan["amount"] == 7500.0
        assert pending_loan["interest_rate"] == 4.0
        assert pending_loan["purpose"] == "Updated purpose"

        # verify approved loan restricted updates
        assert approved_loan["loan_type"] == "Home"  # UNCHANGED
        assert approved_loan["amount"] == 200000.0  # UNCHANGED
        assert approved_loan["purpose"] == "New purpose"  # upd-d

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_load_save_integration(self, mock_save_json, mock_load_json, mock_loans_data):
        """ test that manager loads n saves correctly during oper-s """
        mock_load_json.return_value = mock_loans_data
        mock_save_json.return_value = True

        loan_manager = LoanManager()

        # simulating complete process -- approve -> activate -> make payment
        loan_manager.approve_loan("loan-1")
        loan_manager.activate_loan("loan-1")
        loan_manager.make_payment("loan-1", 1000.0)

        # make sure load_json called for each oper-n
        assert mock_load_json.call_count == 3

        # make sure save_json called for each oper-n
        assert mock_save_json.call_count == 3

        # get data from final save
        final_save_data = mock_save_json.call_args[0][1]
        updated_loan = next((l for l in final_save_data if l["loan_id"] == "loan-1"), None)

        # make sure loan went thru the ENTIRE process
        assert updated_loan["status"] == "active"
        assert updated_loan["balance"] == 4000.0  # 5k - 1k
        assert updated_loan["approved_at"] is not None

    @patch('src.utils.json_utils.load_json')
    @patch('src.utils.json_utils.save_json')
    def test_error_handling_when_save_fails(self, mock_save_json, mock_load_json, mock_loans_data):
        """ test error handling when save_json returns false """
        mock_load_json.return_value = mock_loans_data
        mock_save_json.return_value = False  # simulating save failure

        loan_manager = LoanManager()

        # op-s that should fail with save
        create_result = loan_manager.create_loan_application({
            "user_id": "user-3",
            "loan_type": "Personal",
            "amount": 10000.0,
            "interest_rate": 6.0,
            "term_months": 36
        })

        update_result = loan_manager.update_loan("loan-1", {"purpose": "Updated"})

        payment_result = loan_manager.make_payment("loan-3", 1000.0)

        # ALL op-s should return failure indicators
        assert create_result is None
        assert update_result is False
        assert payment_result is None

    @patch('src.utils.json_utils.load_json')
    def test_empty_data_handling(self, mock_load_json):
        """ test behavior with mpty data """
        mock_load_json.return_value = []  # no data

        loan_manager = LoanManager()

        # test methods with empty data
        all_loans = loan_manager.get_all_loans()
        user_loans = loan_manager.get_user_loans("any-user")
        loan_by_id = loan_manager.get_loan_by_id("any-id")

        # make that all return correct empty resp-s
        assert len(all_loans) == 0
        assert len(user_loans) == 0
        assert loan_by_id is None

    @patch('src.utils.json_utils.load_json')
    def test_loan_not_found_handling(self, mock_load_json, mock_loans_data):
        """ behavior when loan is not found """
        mock_load_json.return_value = mock_loans_data

        loan_manager = LoanManager()

        # methods with non existent loan_id
        with pytest.raises(ValueError) as err1:
            loan_manager.approve_loan("non-existent-id")
        assert "loan not found" in str(err1.value)

        with pytest.raises(ValueError) as err2:
            loan_manager.make_payment("non-existent-id", 100.0)
        assert "loan not found" in str(err2.value)

        with pytest.raises(ValueError) as err3:
            loan_manager.calculate_payment("non-existent-id")
        assert "loan not found" in str(err3.value)