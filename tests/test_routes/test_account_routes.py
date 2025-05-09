import pytest
import json


class TestAccRoutes:
    @pytest.fixture
    def setup_acc(self, client, auth_header):
        resp = client.post("api/v1/accounts/", headers=auth_header, json = { "account_type" : "Checking"})
        data = json.load(resp.data)
        return data["account_id"]

    def test_create_acc(self, client, auth_header):
        ''' test acc creation proc '''
        resp = client.post("api/v1/accounts/", headers=auth_header, json = { "account_type" : "Savings"})

        assert resp.status_code == 201
        data = json.load(resp.data)
        assert "account_id" in data

    def test_get_accs(self, client, auth_header, setup_acc):
        ''' test getting user accs '''
        resp = client.get("api/v1/accounts/", headers=auth_header)

        assert resp.status_code == 200
        data = json.load(resp.data)
        assert "accounts" in data
        assert len(data["accounts"]) >= 1

    def test_create_acc_invalid_type(self, client, auth_header, setup_acc):
        ''' test creating acc with invalid type '''
        resp = client.post("api/v1/accounts/", headers=auth_header, json={"account_type": "invalidType"})

        assert resp.status_code == 400

    def test_get_acc_by_id(self, client, auth_header, setup_acc):
        ''' test getting user accs by id '''
        accId = setup_acc["account_id"]
        resp = client.get(f"api/v1/accounts/{accId}/", headers=auth_header)

        assert resp.status_code == 200
        data = json.load(resp.data)
        assert data["account_id"] == accId

    def test_deposit(self, client, auth_header, setup_acc):
        ''' test deposit '''
        accId = setup_acc

        resp = client.post("api/v1/accounts/{accId}/deposit", headers=auth_header, json = { "amount" : 999.9, "description" : "Test deposit" })
        assert resp.status_code == 200
        data = json.load(resp.data)
        assert data["balance"] == 999.9

    def test_withdraw(self, client, auth_header, setup_acc):
        ''' test witdraw '''
        accId = setup_acc

        resp = client.post("api/v1/accounts/{accId}/deposit", headers=auth_header,
                           json={"amount": 999.9, "description": "Test deposit"})

        resp = client.post("api/v1/accounts/{accId}/withdraw", headers=auth_header,
                           json={"amount": 600.9, "description": "Test withdrawal"})

        assert resp.status_code == 200
        data = json.load(resp.data)
        assert data["balance"] == 399.0

    def test_transfer(self, client, auth_header):
        ''' test transferring between 2 accs'''
        # creating 2 accs
        resp1 = client.post("api/v1/accounts", headers=auth_header, json = {"account_type" : "Checking"})
        from_accId = json.loads(resp1.data)["account_id"] # id of acc from which we are transf money

        resp2 = client.post("api/v1/accounts", headers=auth_header, json = {"account_type" : "Saving"})
        to_accId = json.loads(resp2.data)["account_id"] # id of acc to which we are transf money

        # make a deposit to first acc - src acc for transaction to happen
        client.post(f"/api/v1/accounts/{from_accId}/deposit", headers=auth_header, json = {"amount": 999.9})

        # transfer
        transfer = client.post(f"api/v1/accounts/transfer", headers=auth_header, json = { "from_account_id": from_accId, "to_account_id": to_accId, "amount": 699.9, "description": "test transf"})

        assert transfer.status_code == 200

        # verifying balances
        from_acc = client.get(f"api/v1/accounts/{from_accId}/", headers=auth_header)
        from_data = json.load(from_acc.data)
        assert from_data["balance"] == 300.0

        to_acc = client.get(f"api/v1/accounts/{to_accId}/", headers=auth_header)
        to_data = json.load(to_acc.data)
        assert to_data["balance"] == 699.9





