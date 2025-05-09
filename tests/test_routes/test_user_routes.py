import pytest
import json

class TestUserRoutes:
    def test_register_user(self, client):
        ''' test user registration '''

        nUser = client.post("/api/v1/users/register", json = {
            "username" : "nUser",
            "password" : "pwd-nUser-123",
            "email" : "nuser@exmaple.com",
            "full_name" : "New Usr"
        })

        assert nUser.status_code == 201
        data = json.loads(nUser.data)
        assert data["username"] == "nUser"
        assert "user_id" in data
        assert data["message"] == "user registered successfully"

    def test_reg_user_missing_fields(self, client):
        ''' test user registration with unfilled fields '''
        nUser = client.post("/api/v1/users/register", json = {
            "username" : "nUser",
            "password" : "pwd-nUser-123",
            # no email and full_name passed
        })

        assert nUser.status_code == 400
        data = json.loads(nUser.data)
        assert "error" in data

    def test_login_user(self, client):
        ''' test successful login process '''
        # sign up | regstration
        client.post("api/v1/users/login", json = {
            "username" : "log-test",
            "password" : "pwd-log-test",
            "email" : "login@example.com",
            "full_name" : "Login Test"
        })

        # login
        login = client.post("/api/v1/users/login", json = { "username" : "log-test", "password" : "pwd-log-test" })

        assert login.status_code == 200
        data = json.loads(login.data)
        assert data["username"] == "log-test"
        assert "token" in data #jwt token was created for session, thus login successful
        assert data["message"] == "login successful"
        assert data["user"]["username"] == "log-test"

    def test_login_invalid_credentials(self, client):
        ''' login with inval credentials '''

        invalog = client.post("/api/v1/users/login", json={"username": "dne-log", "password": "dne-pwd"})

        assert invalog.status_code == 401
        data = json.loads(invalog.data)
        assert "error" in data

    def test_get_profile(self, client, auth_header):
        ''' getting user profile '''
        get_profile = client.get("api/v1/uers/profile", headers=auth_header)

        assert get_profile.status_code == 200
        data = json.loads(get_profile.data)
        assert data["username"] == "testadmin"
        assert data["role"] == "admin"

    def test_update_profile(self, client, auth_header):
        ''' test upd-ing user profile '''
        user_upd = client.put("/api/v1/users/profile", headers = auth_header, json = { "email" : "newmail@exmaple.com", "full_name" : "New Naem"})

        assert user_upd.status_code == 200

        # making sure profile was upd-d
        updd_profile = client.get("api/v1/users/profile", headers=auth_header)
        data = json.loads(updd_profile.data)
        assert data["email"] == "newmail@exmaple.com"
        assert data["full_name"] == "New Naem"

