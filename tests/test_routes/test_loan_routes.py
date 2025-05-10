import pytest
import json
from datetime import datetime

from numba.core.imputils import call_len


class TestLoanRoutes:
    @pytest.fixture #(autouse=True)
    def user_auth_headers(self, client):
        ''' creating user and get auth headers '''
        # regist a regular user
        client.post("/api/v1/users/register", json = {
            "username" : "tuser",
            "password" : "pwd-tuser",
            "email" : "tuser@example.com",
            "full_name" : "Test User",
        })

        # login
        login = client.post("/api/v1/users/login", json = { "username" : "tuser", "password" : "pwd-tuser" })

        data = json.loads(login.data)
        return {"Authorization" : f"Bearer {data['access_token']}"}

    @pytest.fixture
    def user_loan_id(self, client, user_auth_headers):
        ''' creating a test loan for user '''
        loan_data = {
            "loan_type" : "Personal",
            "amount" : 99000.9,
            "interest_rate" : 24.5,
            "term_months" : 36,
            "purpose" : "Test LOan"
        }

        loan = client.post("/api/v1/loans/", headers = user_auth_headers,  json = loan_data)
        data = json.loads(loan.data)
        return data["loan_id"]

    @pytest.fixture
    def admin_loan_id(self, client, auth_headers):
        ''' creating test loan for admin user '''
        loan_data = {
            "loan_type": "Business",
            "amount": 99000.9,
            "interest_rate": 2.5,
            "term_months": 24,
            "purpose": "Test Admin Loan"
        }

        admin_loan = client.post("api/v1/loans", headers = auth_headers, json = loan_data)
        data = json.loads(admin_loan.data)
        return data["loan_id"]

    def test_create_loan(self, client, user_auth_headers, user_loan_id):
        ''' test creating loan app '''
        loan_data = {
            "loan_type": "Personal",
            "amount": 9000.9,
            "interest_rate": 8.5,
            "term_months": 28,
            "purpose": "Gambling"
        }

        loan = client.post("/api/v1/loans", headers = user_auth_headers, json = loan_data)
        assert loan.status_code == 200
        data = json.loads(loan.data)
        assert "loan_id" in data
        assert data["loan_id"] == user_loan_id
        assert data["message"] == "loan application submitted successfully"

    def test_create_loan_missing_fields(self, client, user_auth_headers, user_loan_id):
        ''' creating loan with missing fields '''
        loan_data = {
            "loan_type": "Personal",
            "purpose" : "Test incomplete loan app"
        }

        loan = client.post("/api/v1/loans", headers = user_auth_headers, json = loan_data)

        assert loan.status_code == 400
        data = json.loads(loan.data)
        assert "error" in data
        assert "missing requiring field" in data["error"]

    def test_create_loan_invalid_type(self, client, user_auth_headers, user_loan_id):
        ''' creating loan with invalid type '''
        loan_data = {
            "loan_type": "InvalidType",
            "amount" : 6666.6,
            "interest_rate" : 2.5,
            "term_months" : 24,
            "purpose" : "Inval Test Loan"
        }

        invaloan = client.post("/api/v1/loans", headers = user_auth_headers, json = loan_data)

        assert invaloan.status_code == 400
        data = json.loads(invaloan.data)
        assert "error" in data
        assert "loan type" in data["error"].lower()

    # -------------- GETTER TESTS -------------- #

    def test_get_loans(self, client, user_auth_headers, user_loan_id):
        ''' getting users loans '''
        get_loans = client.get("/api/v1/loans", headers = user_auth_headers)

        assert get_loans.status_code == 200
        data = json.loads(get_loans.data)
        assert "loans" in data
        assert len(data["loans"]) >= 1

        # check if test loan is in results
        isfound = False
        for l in data["laons"]:
            if l["loan_id"] == user_loan_id:
                isfound = True
                break

        assert isfound, "Created loan not found in users loans"

    def test_get_all_loans_as_admin(self, client, auth_headers, user_auth_headers, user_loan_id, admin_loan_id):
        ''' test getting all user loans as admin '''
        all_loans = client.get("/api/v1/loans?all=true", headers = auth_headers)

        assert all_loans.status_code == 200
        data = json.loads(all_loans.data)
        assert "loans" in data

        # should find both admins and users loan
        loan_ids = [ loan["loan_id"] for loan in data["loans"]]
        assert admin_loan_id in loan_ids, "Admin Loan not found in admins view"
        assert user_loan_id in loan_ids, "User Loan not found in admins view"

    def test_get_loan_by_id(self, client, user_auth_headers, user_loan_id):
        ''' get loan by id '''
        loan_by_id = client.get(f"/api/v1/loans/{user_loan_id}", headers = user_auth_headers)

        assert loan_by_id.status == 200
        loan = json.loads(loan_by_id.data)
        assert loan["loan_id"] == user_loan_id
        assert loan["status"] == "pending"

    def test_get_loan_not_found(self, client, user_auth_headers):
        ''' getting loan that does not exist '''
        dne_loan = client.get(f"/api/v1/laons/nonexistent-id", headers = user_auth_headers)

        assert dne_loan.status_code == 404
        data = json.loads(dne_loan.data)
        assert "error" in data
        assert "not found" in data["error"]

    def test_unauth_loan_access(self, client, auth_headers, user_auth_headers, user_loan_id, admin_loan_id):
        ''' make sure user cannot access another users loan '''
        unauth_loan_access = client.get(f"/api/v1/loans/{admin_loan_id}", headers = user_auth_headers)

        assert unauth_loan_access.status_code == 403
        data = json.loads(unauth_loan_access.data)
        assert "error" in data
        assert "unauthorized access" in data["error"]

    # ============== END OF GETTER TESTS ============== #

    def test_update_loan(self, client, user_auth_headers, user_loan_id):
        ''' test updating loan in PENDING status '''
        upd_data = {
            "purpose" : "Updated purpose",
            "amount" : 1700.7,
            "term_months" : 10,
            #"interest_rate" : 9.5,
        }

        upd_loan = client.put(f"/api/v1/loans/{user_loan_id}", headers = user_auth_headers, json = upd_data)

        assert upd_loan.status_code == 200
        data = json.loads(upd_loan.data)
        assert data["message"] == "loan updated successfully"

        # verfy changes
        check_upds_of_loan = client.get(f"/api/v1/loans/{user_loan_id}", headers = user_auth_headers)

        upd_loan = json.loads(check_upds_of_loan.data)
        assert upd_loan["purpose"] == "Updated purpose"
        assert upd_loan["amount"] == 1700.7
        assert upd_loan["term_months"] == 10
        assert upd_loan["status"] == "pending"

    def test_admin_approve_loan(self, client, auth_headers, user_loan_id):
        ''' test loan approval process done by admin '''
        approve_loan = client.post(f"/api/v1/loans/{user_loan_id}/approve", headers = auth_headers)

        assert approve_loan.status_code == 200
        data = json.loads(approve_loan.data)
        assert data["message"] == "loan approved successfully"

        # verify status changed
        check_loan_status = client.get(f"/api/v1/loans/{user_loan_id}", headers = auth_headers)
        loan = json.loads(check_loan_status.data)
        assert loan["status"] == "approved"
        assert loan["approved_at"] is not None

    def test_admin_reject_loan(self, client, auth_headers, user_loan_id):
        ''' test loan rejection process done by admin '''
        approve_loan = client.post(f"/api/v1/loans/{user_loan_id}/reject", headers = auth_headers)

        assert approve_loan.status_code == 200
        data = json.loads(approve_loan.data)
        assert data["message"] == "loan rejected successfully"

        # verify status changed
        check_loan_status = client.get(f"/api/v1/loans/{user_loan_id}", headers = auth_headers)
        loan = json.loads(check_loan_status.data)
        assert loan["status"] == "rejected"

    def test_non_admin_cannot_approve_loan(self, client, user_auth_headers, user_loan_id):
        ''' make sure regular users cannot approve loans '''
        user_trying_to_approve_loan = client.post(f"/api/v1/loans/{user_loan_id}/approve", headers = user_auth_headers)

        assert user_trying_to_approve_loan.status_code == 403

    def test_admin_activate_loan(self, client, auth_headers, user_loan_id):
        ''' admin activating loan | after approval process '''
        # approve loan first
        client.post(f"/api/v1/loans/{user_loan_id}/approve", headers = auth_headers)

        activation = client.post(f"/api/v1/loans/{user_loan_id}/activate", headers = auth_headers)

        assert activation.status_code == 200
        data = json.loads(activation.data)
        assert data["message"] == "loan activated successfully"

        # verify status changed
        check_loan_status = client.get(f"/api/v1/loans/{user_loan_id}", headers=auth_headers)
        loan = json.loads(check_loan_status.data)
        assert loan["status"] == "active"

    def test_loan_payment(self, client, auth_headers, user_auth_headers, user_loan_id):
        ''' test payment process on active loan done by user '''
        # approve n activate the loan first
        client.post(f"/api/v1/loans/{user_loan_id}/approve", headers = auth_headers)
        client.post(f"/api/v1/loans/{user_loan_id}/activate", headers = auth_headers)

        # making payment
        payment_data = { "amount" : 500.0 }

        payment = client.post(f"/api/v1/loans/{user_loan_id}/payment", headers = auth_headers, json = payment_data)

        assert payment.status_code == 200
        data = json.loads(payment.data)
        assert data["message"] == "payment successful"
        assert "balance" in data

        # access loan to verify that balance decreased
        get_loan = client.get(f"/api/v1/loans/{user_loan_id}", headers = auth_headers)
        loan = json.loads(get_loan.data)

        assert loan["balance"] < loan["amount"]

    def test_invalid_payment_amount(self, client, auth_headers, user_auth_headers, user_loan_id):
        ''' payment with invalid amount '''

        client.post(f"/api/v1/loans/{user_loan_id}/approve", headers=auth_headers)
        client.post(f"/api/v1/loans/{user_loan_id}/activate", headers=auth_headers)

        payment_data = {"amount": -500.0}

        payment = client.post(f"/api/v1/loans/{user_loan_id}/payment", headers=auth_headers, json=payment_data)

        assert payment.status_code == 400
        data = json.loads(payment.data)
        assert "error" in data
        assert "positive" in data["error"]

    def test_payment_inactive_loan(self, client, user_auth_headers, user_loan_id):
        ''' payment on a loan thats not active (in pending status) '''

        payment_data = {"amount": 100.0}

        payment = client.post(f"/api/v1/loans/{user_loan_id}/payment", headers=user_auth_headers, json=payment_data)

        assert payment.status_code == 400
        data = json.loads(payment.data)
        assert "error" in data
        assert "status" in data["error"]

    def test_calculate_payment(self, client, auth_headers, user_auth_headers, user_loan_id):
        ''' test calculating payment amount '''

        client.post(f"/api/v1/loans/{user_loan_id}/approve", headers=auth_headers)
        client.post(f"/api/v1/loans/{user_loan_id}/activate", headers=auth_headers)

        payment_amount = client.get(f"/api/v1/loans/{user_loan_id}/payment-amount", headers=user_auth_headers)

        assert payment_amount.status_code == 200
        data = json.loads(payment_amount.data)

        assert "payment_amount" in data

        assert "term_months" in data
        assert "interest_rate" in data
        assert "principal" in data
        assert "remaining_balance" in data

        assert data["payment_amount"] > 0
        assert data["payment_amount"] * data["term_months"] > data["principal"] # due to interest